import json
import os
from typing import Dict, Any, List, Optional
from functools import lru_cache

KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base")


@lru_cache(maxsize=None)
def load_category_knowledge(category: str) -> Optional[Dict[str, Any]]:
    """Load the laws.json for a given legal category. Cached after first load."""
    file_path = os.path.join(KNOWLEDGE_BASE_PATH, category, "laws.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_categories() -> List[str]:
    return ["criminal", "property", "family", "consumer", "labor", "cyber", "administrative"]


def get_all_knowledge() -> Dict[str, Any]:
    """Load all categories into a single dict."""
    result = {}
    for cat in get_all_categories():
        data = load_category_knowledge(cat)
        if data:
            result[cat] = data
    return result


def get_laws_for_category(category: str) -> List[Dict[str, Any]]:
    data = load_category_knowledge(category)
    if data:
        return data.get("laws", [])
    return []


def get_questions_for_category(category: str) -> List[Dict[str, Any]]:
    data = load_category_knowledge(category)
    if data:
        return data.get("questions", [])
    return []


def get_evidence_list_for_category(category: str) -> List[Dict[str, Any]]:
    data = load_category_knowledge(category)
    if data:
        return data.get("evidence_list", [])
    return []


def get_recommended_actions_for_category(category: str) -> List[str]:
    data = load_category_knowledge(category)
    if data:
        return data.get("recommended_actions", [])
    return []


def keyword_match_laws(text: str, category: str) -> List[Dict[str, Any]]:
    """Rule-based: return laws whose keywords appear in the text."""
    text_lower = text.lower()
    laws = get_laws_for_category(category)
    matched = []
    for law in laws:
        keywords = law.get("keywords", [])
        match_count = sum(1 for kw in keywords if kw.lower() in text_lower)
        if match_count > 0:
            matched.append({**law, "_match_count": match_count})
    matched.sort(key=lambda x: x["_match_count"], reverse=True)
    return matched
