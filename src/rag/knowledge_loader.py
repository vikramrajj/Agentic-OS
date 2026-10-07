import json
from dataclasses import dataclass
from pathlib import Path
from src.core.config import settings
from src.core.logger import logger


@dataclass
class RunbookDoc:
    id: str
    title: str
    category: str
    symptoms: list[str]
    root_cause: str
    diagnostic_steps: list[str]
    remediation_commands: list[str]

    @property
    def searchable_text(self) -> str:
        return (
            f"{self.title}\n"
            f"Category: {self.category}\n"
            f"Symptoms: {', '.join(self.symptoms)}\n"
            f"Root Cause: {self.root_cause}\n"
            f"Diagnostics: {' '.join(self.diagnostic_steps)}\n"
            f"Remediation: {' '.join(self.remediation_commands)}"
        )


def load_knowledge_base(knowledge_dir: Path = settings.knowledge_dir) -> list[RunbookDoc]:
    """Load all Linux troubleshooting runbooks from JSON knowledge directory."""
    documents: list[RunbookDoc] = []

    if not knowledge_dir.exists():
        logger.warning(f"Knowledge directory {knowledge_dir} does not exist.")
        return documents

    for file_path in sorted(knowledge_dir.glob("*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                entries = json.load(f)

            if isinstance(entries, list):
                for item in entries:
                    doc = RunbookDoc(
                        id=item.get("id", file_path.stem),
                        title=item.get("title", "Untitled Runbook"),
                        category=item.get("category", "general"),
                        symptoms=item.get("symptoms", []),
                        root_cause=item.get("root_cause", ""),
                        diagnostic_steps=item.get("diagnostic_steps", []),
                        remediation_commands=item.get("remediation_commands", [])
                    )
                    documents.append(doc)
            logger.info(f"Loaded {len(entries)} runbooks from {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to load knowledge file {file_path}: {e}")

    logger.info(f"Total knowledge base documents loaded: {len(documents)}")
    return documents
