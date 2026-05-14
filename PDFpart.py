"""
PDF Chunker for Database Ingestion
------------------------------------------------
Splits a large PDF into chunks capped at 60 KB each.
Chunks that exceed the limit are recursively halved until they fit.

Usage:
    python PDFpart.py input.pdf
    python PDFpart.py input.pdf --output-dir ./chunks

Requirements:
    pip install pypdf
"""

import argparse
import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter

MAX_CHUNK_KB = 60
MAX_CHUNK_BYTES = MAX_CHUNK_KB * 1024


def format_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def write_chunk(reader: PdfReader, start: int, end: int, output_path: Path) -> int:
    writer = PdfWriter()
    for i in range(start, end):
        writer.add_page(reader.pages[i])
    if reader.metadata:
        writer.add_metadata(reader.metadata)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path.stat().st_size


def _split_to_fit(reader, start, end, output_dir, base_name, counter):
    """Write pages [start, end); recursively halve if the chunk exceeds MAX_CHUNK_BYTES."""
    num_pages = end - start
    chunk_path = output_dir / f"{base_name}_part_{counter[0]:03d}.pdf"
    size_bytes = write_chunk(reader, start, end, chunk_path)

    if size_bytes <= MAX_CHUNK_BYTES or num_pages == 1:
        label = f"  [{counter[0]:03d}] pages {start + 1}-{end} ({num_pages} pages, {format_size(size_bytes)})"
        if size_bytes > MAX_CHUNK_BYTES:
            label += "  [single-page exceeds limit — kept as-is]"
        print(label)
        sys.stdout.flush()
        counter[0] += 1
        return

    # Oversized — delete and split in half
    chunk_path.unlink()
    mid = start + num_pages // 2
    _split_to_fit(reader, start, mid, output_dir, base_name, counter)
    _split_to_fit(reader, mid, end, output_dir, base_name, counter)


def chunk_pdf(input_pdf: Path, output_dir: Path) -> None:
    reader = PdfReader(str(input_pdf))
    total_pages = len(reader.pages)
    base_name = input_pdf.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    # Estimate a starting pages-per-chunk so the recursion converges quickly
    file_size = input_pdf.stat().st_size
    est_pages = max(1, int(total_pages * MAX_CHUNK_BYTES / file_size)) if file_size else 1

    print(f"\nSource:     {input_pdf.name}")
    print(f"Pages:      {total_pages}")
    print(f"Cap:        {MAX_CHUNK_KB} KB per part")
    print(f"Output:     {output_dir.resolve()}\n")
    print("-" * 60)

    counter = [1]
    page_idx = 0
    while page_idx < total_pages:
        end_idx = min(page_idx + est_pages, total_pages)
        _split_to_fit(reader, page_idx, end_idx, output_dir, base_name, counter)
        page_idx = end_idx

    chunks = list(output_dir.glob(f"{base_name}_part_*.pdf"))
    total_size = sum(p.stat().st_size for p in chunks)
    print("-" * 60)
    print(f"\nDone. {len(chunks)} parts, {format_size(total_size)} total.\n")


def main():
    parser = argparse.ArgumentParser(
        description=f"Split a PDF into parts capped at {MAX_CHUNK_KB} KB each.",
    )
    parser.add_argument("input_pdf", help="Path to the source PDF")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: <name>_chunks/ next to source file)",
    )
    args = parser.parse_args()

    input_pdf = Path(args.input_pdf)
    if not input_pdf.exists():
        print(f"Error: file not found: {input_pdf}", file=sys.stderr)
        sys.exit(1)
    if input_pdf.suffix.lower() != ".pdf":
        print(f"Error: expected a .pdf file, got: {input_pdf.suffix}", file=sys.stderr)
        sys.exit(1)

    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else input_pdf.parent / f"{input_pdf.stem}_chunks"
    )

    try:
        chunk_pdf(input_pdf, output_dir)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
