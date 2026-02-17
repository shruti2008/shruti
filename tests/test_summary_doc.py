from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from summary_doc import generate_summary_document, select_summary_sentences, strip_markdown


class SummaryDocTests(unittest.TestCase):
    def test_strip_markdown_keeps_text(self) -> None:
        source = "# Title\nA [linked sentence](https://example.com) with `code`.\n- Bullet point."
        result = strip_markdown(source)

        self.assertIn("Title", result)
        self.assertIn("linked sentence", result)
        self.assertNotIn("[", result)
        self.assertNotIn("`", result)

    def test_select_summary_sentences_prefers_repeated_topics(self) -> None:
        sentences = [
            "Automation introduced reliable document summaries for every team.",
            "Automation now scans each document and ranks key findings.",
            "The redesign also changed icon colors in the dashboard.",
            "Document summaries help teammates understand updates faster.",
            "Automation for summaries reduced review time by forty percent.",
        ]

        selected = select_summary_sentences(sentences, sentence_budget=2)

        self.assertEqual(len(selected), 2)
        self.assertNotIn(sentences[2], selected)

    def test_generate_summary_document_writes_markdown(self) -> None:
        source = (
            "The launch plan includes updates to onboarding docs for all teams. "
            "Teams previously searched many pages before they found the right guide. "
            "A shared search index now improves document discovery across products. "
            "Faster discovery reduced onboarding time by thirty five percent. "
            "The next milestone adds automatic summaries for long technical documents."
        )

        with TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "source.md"
            output_path = Path(temp_dir) / "summary.md"
            input_path.write_text(source, encoding="utf-8")

            summary_content = generate_summary_document(
                input_path=input_path,
                output_path=output_path,
                sentence_budget=3,
            )
            written_content = output_path.read_text(encoding="utf-8")

        self.assertEqual(summary_content, written_content)
        self.assertIn("# Summary of `source.md`", written_content)
        self.assertIn("## Key points", written_content)

        summary_section = written_content.split("## Key points", maxsplit=1)[1]
        key_point_lines = [line for line in summary_section.splitlines() if line.startswith("- ")]
        self.assertEqual(len(key_point_lines), 3)


if __name__ == "__main__":
    unittest.main()
