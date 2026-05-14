# PDF Partitioner

> Splits large PDFs into smaller parts — built for Citrix-hosted document systems that freeze or reject oversized uploads.

Each part is capped at a configurable size (default **60 KB**). No installation required to use the app.

---

## Quick Start — `pdf_splitter.exe`

**Double-click `pdf_splitter.exe`** to launch the interface. No Python, no command line, no setup.

| Field | What to do |
|:---|:---|
| **PDF File** | Click **Browse...** and select the PDF to split |
| **Output Folder** | Click **Browse...** to choose where parts are saved *(defaults to a `_chunks` folder next to the source file)* |
| **Max Size (KB)** | Size cap per part in kilobytes — set to `60` to match the Citrix limit |

Click **Split PDF** and wait for the progress bar to complete. The output folder will contain numbered parts ready to upload.

> **Output naming:** `<original_name>_part_001.pdf`, `_part_002.pdf`, … in page order.

---

## How It Works

1. Estimates a starting pages-per-chunk from the file's size-to-page ratio
2. Writes each chunk and measures its file size
3. Any chunk over the limit is deleted and recursively halved until it fits
4. Single pages that still exceed the limit (e.g. high-res scans) are kept as-is — they cannot be split further

---

## Command-Line Usage

Prefer the terminal? Both the exe and the raw script accept arguments.

**Executable**
```bat
"pdf_splitter.exe" input.pdf
"pdf_splitter.exe" input.pdf --output-dir C:\path\to\output
```

**Python script**
```bash
python PDFpart.py input.pdf
python PDFpart.py input.pdf --output-dir ./chunks
```

**Arguments**

| Argument | Required | Description |
|:---|:---:|:---|
| `input_pdf` | Yes | Path to the PDF to split |
| `--output-dir` | No | Output folder *(default: `<filename>_chunks/` next to source)* |

---

## Running from Source

> Requires **Python 3.10+**

**1. Install the dependency**
```bash
pip install pypdf
```

**2. Run**
```bash
python PDFpart.py input.pdf
```

---

## Building the Executable

Produces a single standalone `pdf_splitter.exe` with no external dependencies.

**1. Install build tools**
```bash
pip install pyinstaller pypdf
```

**2. Build**
```bash
pyinstaller --onefile --windowed --name "pdf_splitter" PDFpart.py
```

| Flag | Effect |
|:---|:---|
| `--onefile` | Bundles everything into a single `.exe` |
| `--windowed` | Suppresses the console window when the GUI runs |

**3. Collect the output**

The finished executable is at `dist\pdf_splitter.exe`. Copy it anywhere — no other files needed.
