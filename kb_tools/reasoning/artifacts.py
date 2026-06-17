"""Artifact generation — study guides, timelines, comparisons, doctrinal briefs."""

from __future__ import annotations

from kb_tools.config import Config
from kb_tools.reasoning.generator import Generator
from kb_tools.search.engine import SearchEngine


class ArtifactGenerator:
    """Generate structured markdown artifacts from the knowledge base."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self._search = SearchEngine(self.config)
        self._generator = Generator(self.config)

    def generate(self, topic: str, artifact_type: str) -> str:
        """Generate an artifact and save to outputs/."""
        context = self._search.search_with_context(
            topic, top_k=10, max_tokens=5000
        )
        prompt = self._artifact_prompt(topic, artifact_type, context)
        response = self._generator.generate(prompt, context)

        filename = f"{topic.lower().replace(' ', '-')}.md"
        dir_name = artifact_type.replace("-", "_").rstrip("s") + "s"
        output_dir = self.config.outputs_dir / dir_name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        output_path.write_text(response)
        return str(output_path)

    def _artifact_prompt(
        self, topic: str, artifact_type: str, context: str
    ) -> str:
        prompts = {
            "study-guide": (
                f"Create a comprehensive study guide on "
                f"'{topic}' using the provided sources.\n"
                "Include: Title, Summary, Key Points, "
                "Detailed Sections, Sources, "
                "Scriptural References, and Discussion Questions."
            ),
            "timeline": (
                f"Create a chronological timeline of the "
                f"development of '{topic}' in Catholic teaching.\n"
                "Include: Title, Introduction, chronological "
                "entries with dates and source citations, "
                "and a Summary section."
            ),
            "comparison": (
                f"Compare different aspects or perspectives "
                f"of '{topic}' using the provided sources.\n"
                "Include: Title, Overview, Points of "
                "Comparison, Analysis, Conclusion, and Sources."
            ),
            "doctrinal-brief": (
                f"Write a doctrinal brief on '{topic}' "
                "using the provided sources.\n"
                "Include: Title, Summary, Official Teaching "
                "(with citations), Theological Development, "
                "Common Questions, and Sources."
            ),
        }
        return prompts.get(artifact_type, prompts["study-guide"])
