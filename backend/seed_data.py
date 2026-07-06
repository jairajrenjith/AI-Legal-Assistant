"""
Seed the database with sample cases for demo/testing.
Run from the backend directory:
    python seed_data.py
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from app.database.database import SessionLocal, Base, engine
from app.models.models import Case, CaseStatus, CaseCategory
from app.services.case_service import (
    classify_case,
    identify_applicable_laws,
    generate_evidence_recommendations,
    generate_recommendations,
    compute_case_scores,
    generate_gap_analysis,
    generate_timeline,
)

Base.metadata.create_all(bind=engine)

SAMPLES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "sample_cases", "sample_cases.json"
)


def seed():
    db = SessionLocal()
    try:
        with open(SAMPLES_PATH, "r") as f:
            samples = json.load(f)

        existing = db.query(Case).count()
        if existing > 0:
            print(f"Database already has {existing} cases. Skipping seed.")
            return

        print(f"Seeding {len(samples)} sample cases...")
        for i, sample in enumerate(samples, 1):
            case = Case(
                title=sample["title"],
                description=sample["description"],
                status=CaseStatus.DRAFT,
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            print(f"  [{i}/{len(samples)}] Created: {case.title[:50]}… (ID={case.id})")

            try:
                classify_case(db, case.id)
                identify_applicable_laws(db, case.id)
                generate_evidence_recommendations(db, case.id)
                generate_recommendations(db, case.id)
                compute_case_scores(db, case.id)
                generate_gap_analysis(db, case.id)
                generate_timeline(db, case.id)
                print(f"             Analysis complete for case {case.id}")
            except Exception as e:
                print(f"             Analysis failed for case {case.id}: {e}")

        print(f"\n✓ Seeded {len(samples)} cases successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
