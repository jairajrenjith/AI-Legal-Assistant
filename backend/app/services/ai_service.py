import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI
from app.config import settings
from app.utils.knowledge_loader import get_all_categories, load_category_knowledge

_client: Optional[OpenAI] = None


def get_openai_client() -> Optional[OpenAI]:
    global _client
    if not settings.OPENAI_API_KEY:
        return None
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def classify_case_with_ai(title: str, description: str) -> Dict[str, Any]:
    """
    Classify a case using OpenAI if key is available, else rule-based fallback.
    Returns: category, subcategory, confidence, summary, entities, reasoning
    """
    client = get_openai_client()
    if client:
        return _classify_with_openai(client, title, description)
    return _classify_rule_based(title, description)


def _classify_with_openai(client: OpenAI, title: str, description: str) -> Dict[str, Any]:
    categories_info = []
    for cat in get_all_categories():
        data = load_category_knowledge(cat)
        if data:
            subcats = data.get("subcategories", [])
            categories_info.append(f"{cat}: {', '.join(subcats)}")

    prompt = f"""You are a legal classification expert for Indian law. Analyze the following legal case and return a JSON response.

CASE TITLE: {title}
CASE DESCRIPTION: {description}

Available categories and subcategories:
{chr(10).join(categories_info)}

Return a JSON object with these exact keys:
{{
  "category": "<one of: criminal, property, family, consumer, labor, cyber, administrative, unknown>",
  "subcategory": "<specific subcategory string>",
  "confidence": <float between 0.0 and 1.0>,
  "summary": "<2-3 sentence neutral case summary>",
  "extracted_entities": {{
    "persons": ["<names or roles mentioned>"],
    "locations": ["<locations mentioned>"],
    "dates": ["<dates/time periods mentioned>"],
    "amounts": ["<monetary amounts mentioned>"],
    "organizations": ["<organizations mentioned>"]
  }},
  "reasoning": "<1-2 sentences explaining why this category was chosen>"
}}

Return only the JSON, no other text."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json\n?|\n?```", "", raw).strip()
    result = json.loads(raw)
    return result


def _classify_rule_based(title: str, description: str) -> Dict[str, Any]:
    """Keyword-based classification fallback when no OpenAI key is set."""
    text = f"{title} {description}".lower()

    category_keywords = {
        "criminal": ["murder", "theft", "robbery", "assault", "rape", "fir", "police", "accused", "victim", "crime", "offence", "hurt", "attack", "beat", "stabbed", "shot", "killed"],
        "property": ["land", "property", "encroachment", "house", "plot", "title deed", "sale deed", "tenant", "landlord", "survey", "boundary", "trespass", "possession"],
        "family": ["divorce", "marriage", "husband", "wife", "child custody", "maintenance", "alimony", "dowry", "domestic violence", "matrimonial", "in-laws"],
        "consumer": ["product", "defect", "consumer", "warranty", "refund", "company", "service", "deficiency", "e-commerce", "bank fraud", "insurance claim"],
        "labor": ["salary", "employer", "employee", "fired", "terminated", "pf", "gratuity", "wages", "labour", "job", "workplace", "harassment at work"],
        "cyber": ["online", "internet", "hacked", "cyber", "fraud call", "otp", "phishing", "social media", "whatsapp", "email fraud", "deepfake", "digital"],
        "administrative": ["government", "bribe", "corruption", "rti", "public servant", "department", "official", "grievance", "scheme", "benefit denied"],
    }

    scores: Dict[str, int] = {cat: 0 for cat in category_keywords}
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in text:
                scores[cat] += 1

    best_cat = max(scores, key=lambda c: scores[c])
    best_score = scores[best_cat]

    if best_score == 0:
        return {
            "category": "unknown",
            "subcategory": "Unclassified",
            "confidence": 0.0,
            "summary": f"Case titled '{title}' has been submitted. Manual review required for classification.",
            "extracted_entities": {"persons": [], "locations": [], "dates": [], "amounts": [], "organizations": []},
            "reasoning": "No strong keyword matches found. Manual review recommended.",
        }

    total = sum(scores.values())
    confidence = round(best_score / max(total, 1), 2)
    confidence = min(confidence, 0.85)  # Cap rule-based confidence

    data = load_category_knowledge(best_cat)
    subcategory = data["subcategories"][0] if data and data.get("subcategories") else "General"

    return {
        "category": best_cat,
        "subcategory": subcategory,
        "confidence": confidence,
        "summary": f"Case appears to relate to {data['display_name'] if data else best_cat} based on case description. Further details required from the questionnaire.",
        "extracted_entities": {"persons": [], "locations": [], "dates": [], "amounts": [], "organizations": []},
        "reasoning": f"Keyword analysis identified {best_score} matching terms for the '{best_cat}' category.",
    }


def generate_ai_analysis(prompt: str) -> str:
    """Generic AI text generation with fallback."""
    client = get_openai_client()
    if not client:
        return "AI analysis unavailable. Please configure OpenAI API key in settings."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1500,
    )
    return response.choices[0].message.content.strip()
