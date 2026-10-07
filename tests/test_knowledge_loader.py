from src.rag.knowledge_loader import load_knowledge_base, RunbookDoc


def test_load_knowledge_base():
    docs = load_knowledge_base()
    assert len(docs) >= 10, f"Expected at least 10 runbooks, found {len(docs)}"

    for doc in docs:
        assert isinstance(doc, RunbookDoc)
        assert doc.id
        assert doc.title
        assert doc.category
        assert len(doc.symptoms) > 0
        assert doc.root_cause
        assert len(doc.remediation_commands) > 0
        assert len(doc.searchable_text) > 50


def test_categories_covered():
    docs = load_knowledge_base()
    categories = {doc.category for doc in docs}
    assert "systemd" in categories
    assert "networking" in categories
    assert "storage" in categories
    assert "memory" in categories
    assert "permissions" in categories
