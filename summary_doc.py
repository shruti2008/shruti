#!/usr/bin/env python3
"""Generate a concise summary document from a source document."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Iterable


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "such",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "to",
    "was",
    "will",
    "with",
}

WORD_RE = re.compile(r"[A-Za-z0-9']+")


def strip_markdown(markdown_text: str) -> str:
    """Remove most markdown syntax while preserving readable text."""
    text = re.sub(r"```.*?```", " ", markdown_text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[>*_~|]", " ", text)
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"(?<=[.!?])\n+", " ", text)
    text = re.sub(r"(?<![.!?])\n+", ". ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    """Split normalized text into sentence-like chunks."""
    raw_sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in raw_sentences if len(sentence.split()) >= 5]


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words."""
    return [token.lower() for token in WORD_RE.findall(text)]


def score_sentences(sentences: Iterable[str]) -> dict[int, float]:
    """Score sentences using normalized term frequency."""
    indexed_sentences = list(sentences)
    term_frequency: Counter[str] = Counter()

    for sentence in indexed_sentences:
        for token in tokenize(sentence):
            if token in STOP_WORDS or token.isdigit():
                continue
            term_frequency[token] += 1

    if not term_frequency:
        return {idx: float(len(tokenize(sentence))) for idx, sentence in enumerate(indexed_sentences)}

    max_frequency = max(term_frequency.values())
    normalized_frequency = {
        token: frequency / max_frequency for token, frequency in term_frequency.items()
    }

    sentence_scores: dict[int, float] = {}
    for idx, sentence in enumerate(indexed_sentences):
        sentence_tokens = [token for token in tokenize(sentence) if token in normalized_frequency]
        if not sentence_tokens:
            continue
        score = sum(normalized_frequency[token] for token in sentence_tokens) / len(sentence_tokens)
        sentence_scores[idx] = score

    return sentence_scores


def select_summary_sentences(sentences: list[str], sentence_budget: int) -> list[str]:
    """Select top-ranked sentences and keep their original order."""
    if not sentences:
        return []

    budget = max(1, min(sentence_budget, len(sentences)))
    scores = score_sentences(sentences)
    if not scores:
        return sentences[:budget]

    top_indices = sorted(sorted(scores, key=scores.get, reverse=True)[:budget])
    return [sentences[index] for index in top_indices]


def build_summary_markdown(
    input_path: Path, source_text: str, summary_sentences: list[str], sentence_budget: int
) -> str:
    """Render summary output as markdown."""
    lines = [
        f"# Summary of `{input_path.name}`",
        "",
        f"- Generated on: {date.today().isoformat()}",
        f"- Source word count: {len(tokenize(source_text))}",
        f"- Sentence budget: {sentence_budget}",
        "",
        "## Key points",
        "",
    ]

    if summary_sentences:
        lines.extend(f"- {sentence}" for sentence in summary_sentences)
    else:
        lines.append("- No summary was generated because the source was empty.")

    lines.append("")
    return "\n".join(lines)


def generate_summary_document(
    input_path: Path, output_path: Path, sentence_budget: int = 5
) -> str:
    """Generate a markdown summary document from an input document."""
    if sentence_budget <= 0:
        raise ValueError("sentence_budget must be greater than zero.")

    source_text = input_path.read_text(encoding="utf-8")
    cleaned_text = strip_markdown(source_text)
    sentences = split_sentences(cleaned_text)
    summary_sentences = select_summary_sentences(sentences, sentence_budget)
    summary_markdown = build_summary_markdown(
        input_path=input_path,
        source_text=cleaned_text,
        summary_sentences=summary_sentences,
        sentence_budget=sentence_budget,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary_markdown, encoding="utf-8")
    return summary_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a summary markdown document from an input document."
    )
    parser.add_argument("input", type=Path, help="Path to the source document.")
    parser.add_argument("output", type=Path, help="Path for the generated summary markdown.")
    parser.add_argument(
        "-n",
        "--sentences",
        type=int,
        default=5,
        help="Number of summary sentences to include (default: 5).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_summary_document(
        input_path=args.input,
        output_path=args.output,
        sentence_budget=args.sentences,
    )


if __name__ == "__main__":
    main()
