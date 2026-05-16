# Research Brief: 1. Data Acquisition & Parsing — FCA Handbook PDFs

**Issue:** JAM-238
**Tools used:** Linear MCP (JAM-238, JAM-237), GitHub MCP (`.claude/skills/` directory listing, `trade-off-analysis/SKILL.md`), Web Search (PDF parser comparisons, pymupdf4llm capabilities, FCA PDF URL structure, HTML scraping feasibility, boto3 S3 upload patterns)

---

## Summary

JAM-238 is the first concrete sub-task under the parent project JAM-237: building a public portfolio RAG system over FCA regulatory text, targeting an Anthropic hiring audience. This issue asks for downloading two large FCA Handbook PDFs (High Level Standards + Business Standards), parsing them into structured, chunk-ready JSONL with hierarchy metadata (Module → Chapter → Section → Rule/Guidance), and storing both raw PDFs and parsed output to S3. The key challenge is that FCA documents use a distinctive regulatory grammar — rule type markers (R/G/E/UK), inline cross-references like `■SYSC 10`, and a multi-level heading hierarchy — which vanilla PDF extraction will flatten or lose. The parent project is explicit: if PDF parsing produces garbage, fall back to HTML scraping. This issue includes a well-scoped spike (PRIN only) to test that gate before committing.

---

## Key Findings

1. **The FCA PDFs are available via direct public URLs on fca.org.uk.** The confirmed URL pattern is `https://www.fca.org.uk/publication/handbook/high-level-standards{release_number}.pdf`. Release 136 is confirmed accessible. There is no authentication or robots barrier. The Business Standards equivalent exists at the same domain. These are machine-generated digital PDFs (not scanned), meaning OCR is not needed.

2. **`pymupdf4llm` is the strongest primary tool for this use case.** It produces GitHub-compatible Markdown output with headings derived from font size hierarchy, structured output containing bounding box coordinates, layout element types, font metadata, and text content for every detected element. Critically, it supports custom header detection via `IdentifyHeaders` or `TocHeaders`, and configurable exclusion of repetitive page headers and footers. For the FCA PDFs, the TOC-driven header mode (`TocHeaders`) is the right approach since the FCA PDF embeds a proper Table of Contents — this uses the document's Table of Contents under the assumption that the bookmark text is also present as a header line on the page, and the callable checks whether the span text matches any TOC titles on the page — if so, it uses the TOC hierarchy level as the header level.

3. **pdfplumber is the better secondary tool for spot-checking and table detection.** Financial reports, bank statements, and regulatory filings often contain complex tables with merged cells, multi-line entries, and varying border styles — pdfplumber's sophisticated table detection and tolerance settings make it particularly well-suited for extracting this type of structured financial data. The FCA PDFs contain application tables in chapters like SYSC and COBS; pdfplumber handles these more reliably. The library works optimally with machine-generated PDFs rather than scanned documents, as it relies on underlying vector and text data rather than OCR.

4. **A comparative benchmark from an academic study confirms the tool choices.** For text extraction, PyMuPDF and pypdfium2 generally outperformed others across document categories. For the Law & Regulations category specifically, TATR (Table Transformer) excelled in table detection for Financial, Patent, Law & Regulations, and Scientific categories — but this is overkill for the FCA PDFs since their tables are rule-based, bordered, and not complex enough to need a transformer model.

5. **HTML scraping from handbook.fca.org.uk is a poor fallback, not a clean alternative.** The handbook.fca.org.uk site requires JavaScript to run properly — every module page returns no meaningful content to a plain HTTP request. Scraping would require a headless browser (Playwright/Selenium), adds complexity, and the page structure is a React SPA that would need reverse-engineering. The PDFs are the cleaner, more stable source.

6. **FCA Handbook structure is well-documented and parseable.** Each sourcebook or manual is divided into chapters and sections. The general structure of the majority of modules is: Application and purpose → Main content (substantive provisions) → Transitional provisions. This may include relevant annexes and forms. Rule type markers (R, G, E, UK) appear as bold inline annotations prefixing rule text. Cross-references use the canonical pattern `■MODULE CHAPTER.SECTION` (e.g., `■SYSC 10`). These can be extracted with regex after parsing.

7. **The PRIN spike is the right gate.** PRIN is 20–30 pages compared to SYSC's 300+ — small enough to inspect manually, but representative of the rule/guidance structure used across all modules. Validating hierarchy detection (Module → Chapter → Section) and cross-reference extraction on PRIN before tackling the full corpus is sound engineering.

8. **boto3 S3 upload is straightforward.** The `upload_file` method accepts a file name, a bucket name, and an object name, and handles large files by splitting them into smaller chunks and uploading each chunk in parallel. For JSONL output written in memory, `s3.put_object(Body=..., ContentType='application/x-ndjson')` is simpler than writing to disk first.

---

## Recommended Approach

### Phase 1 — Spike (PRIN only)

1. **Download the High Level Standards PDF** via `requests.get('https://www.fca.org.uk/publication/handbook/high-level-standards136.pdf')`. Check the release number is current and confirm the file is a clean digital PDF (not scanned).
2. **Extract with `pymupdf4llm`** using `TocHeaders` mode to derive heading levels from the embedded PDF TOC. Run `to_json()` to get bounding box and font metadata per element — this is more useful than Markdown for building the custom JSONL schema.
3. **Isolate PRIN pages** by slicing the page range (PRIN is typically the first module, pages 1–~30).
4. **Parse the text** with regex to extract: rule IDs (`PRIN 2.1.1 R`), rule type markers, and cross-references (`■SYSC 10`, `■GEN 2.2`).
5. **Spot-check 5 sections manually** against the FCA website to validate hierarchy detection and metadata extraction quality. Document failures.
6. **Decision gate**: if >90% of sections parse cleanly → proceed to full corpus. If significant issues → investigate pdfplumber as an alternative and document.

### Phase 2 — Full pipeline

7. **Download both PDFs** (High Level Standards and Business Standards) and upload raw files to S3 under `s3://fca-regulatory-rag-eval/raw/`.
8. **Run the parsing pipeline** over all pages of both PDFs. Use module boundary detection (TOC entries like "PRIN", "SYSC", "COBS") to set the `module` field in metadata.
9. **Write JSONL to S3** alongside the raw PDFs under `s3://fca-regulatory-rag-eval/parsed/`. One JSONL file per PDF, one line per section.
10. **Spot-check 10 random sections** (5 from each PDF) and log accuracy. Document any systematic failures (e.g., footnotes, multi-column annexes) for the parent project's README.

**Schema per JSONL record:**
```json
{
  "module": "SYSC",
  "chapter": "SYSC 4",
  "section": "SYSC 4.1",
  "rule_id": "SYSC 4.1.1",
  "rule_type": "R",
  "text": "A firm must have ...",
  "cross_references": ["GEN 2.2.23", "PRIN 3"],
  "source_pdf": "high-level-standards136.pdf",
  "page": 47
}
```

**Why this over alternatives:**
- `pymupdf4llm` over plain `PyMuPDF`: the LLM-optimised wrapper adds TOC-driven heading detection and header/footer suppression that would need to be hand-coded in plain PyMuPDF.
- PDF over HTML scraping: the handbook website is a JS SPA and returns nothing to plain HTTP. PDFs are stable, versioned, and require no browser automation.
- `pymupdf4llm` over `unstructured`: unstructured is heavier, slower (1.29s vs 0.12s per page), and its semantic chunking would conflict with the FCA-specific hierarchy the issue requires to preserve.

---

## Relevant Skills & Templates

**`.claude/skills/trade-off-analysis/SKILL.md`** — Highly relevant for the spike decision gate. When the PRIN spike results come in, this skill provides a structured framework to compare pymupdf4llm vs pdfplumber vs HTML scraping across dimensions like parsing accuracy, implementation complexity, and maintainability — producing a decisive recommendation and documenting it for the project README. The skill explicitly suits "should I use X or Y?" decisions with 2–3 known options, which is exactly what the spike is designed to inform.

No other skills in the repository are relevant to this issue. The data pipeline work here is concrete implementation, not architecture discovery or communication.

---

## Open Questions

1. **Which release number is current for the Business Standards PDF?** The High Level Standards URL pattern (`high-level-standards136.pdf`) includes a release number. The Business Standards PDF URL pattern needs verification — it may be `business-standards{N}.pdf` but this wasn't confirmed in research.

2. **How does the FCA encode rule type markers in the PDF text layer?** The markers (R, G, E, UK) appear visually as superscript or bold annotations. Whether these appear as parseable characters in the text layer, or are rendered as images/vector graphics, is unknown until the PDF is opened. This is the most critical unknown for the spike.

3. **Does PRIN have cross-references that use the `■` (block) character?** The `■` prefix on cross-references (`■SYSC 10`) may or may not survive PDF text extraction cleanly — some PDF renderers encode it as a glyph that doesn't map to Unicode. This should be verified in the spike.

4. **What AWS region and bucket name?** The parent issue architecture assumes S3 on AWS but doesn't specify a region. Given Bedrock dependency (parent project uses `us-east-1` implicitly for Titan/Claude), the S3 bucket should be co-located.

5. **License/ToU for FCA publications?** The PDFs are publicly accessible government publications. For a public portfolio project, using them is almost certainly fine under Open Government Licence, but this should be confirmed and noted in the README.

---

## Next Steps

1. **Confirm the Business Standards PDF URL** — open `https://www.fca.org.uk/publication/handbook/` in a browser and find the direct PDF download link; note the release number.
2. **Download and inspect both PDFs locally** — open in a PDF reader first, check TOC structure, and look at how rule type markers (R, G, E) appear visually. This takes 10 minutes and avoids surprises.
3. **Run the PRIN spike** — install `pymupdf4llm`, run `to_json()` on pages 1–30 of the HLS PDF, inspect the raw output, and write a minimal extraction script targeting PRIN sections.
4. **Validate cross-reference extraction** — write a regex for `■[A-Z]+\s+\d+` and run it against the PRIN text output; check that the `■` character survives extraction.
5. **If spike passes**: build the full pipeline script (`download_pdfs.py` → `parse_pdfs.py` → `upload_to_s3.py`).
6. **If spike fails on rule markers or hierarchy**: apply the `trade-off-analysis` skill to compare pdfplumber vs HTML-with-Playwright vs accepting partial metadata — document the decision for the project README.
7. **Create the `jacarty/fca-regulatory-rag-eval` GitHub repo** (if not yet done) and commit the pipeline scripts to `src/ingestion/`.
