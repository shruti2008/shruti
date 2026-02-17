# Summary Document Generator

Generate a concise markdown summary document from another markdown or text document.

## What this does

- Reads a source document.
- Extracts and scores sentence importance.
- Writes a summary markdown file with key bullet points.

## Usage

```bash
python3 summary_doc.py <input-doc> <output-summary-doc> --sentences 5
```

### Example

```bash
python3 summary_doc.py docs/source-document.md docs/source-document.summary.md --sentences 4
```

## Run tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
