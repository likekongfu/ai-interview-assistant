import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = BACKEND_ROOT / "data" / "quiz-questions.json"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from db.database import SessionLocal
from models import QuizQuestion

OPTION_KEYS = {"A", "B", "C", "D"}


@dataclass
class ImportStats:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0

    def as_dict(self):
        return {
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "failed": self.failed,
        }


def stable_public_id(item: dict) -> str:
    explicit = item.get("public_id") or item.get("source_id") or item.get("id")
    if explicit:
        return str(explicit)
    fingerprint = json.dumps(
        {
            "category": item.get("category") or item.get("topic") or "",
            "stem": item.get("stem") or "",
            "options": item.get("options") or [],
            "correct_answer": item.get("correct_answer") or "",
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:24]


def load_questions(source: Path) -> list[dict]:
    if not source.exists():
        raise FileNotFoundError(f"quiz question source not found: {source}")
    with source.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("quiz question source must be a JSON array")
    return data


def validate_choice_question(item: dict):
    options = item.get("options")
    answer = item.get("correct_answer")
    if answer not in OPTION_KEYS:
        raise ValueError("correct_answer must be one of A/B/C/D")
    if not isinstance(options, list) or len(options) != 4:
        raise ValueError("options must contain exactly four items")
    keys = {option.get("key") for option in options if isinstance(option, dict)}
    if keys != OPTION_KEYS:
        raise ValueError("options keys must be A/B/C/D")
    if not item.get("stem"):
        raise ValueError("stem is required")
    if not item.get("explanation"):
        raise ValueError("explanation is required")


def normalize_question(item: dict) -> dict:
    validate_choice_question(item)
    return {
        "source_id": stable_public_id(item),
        "category": item.get("category") or item.get("topic") or "未分类",
        "stem": item["stem"],
        "options_json": json.dumps(item["options"], ensure_ascii=False),
        "correct_answer": item["correct_answer"],
        "explanation": item["explanation"],
        "knowledge_point": item.get("knowledge_point") or item.get("tags") or "",
        "difficulty": item.get("difficulty") or "medium",
        "status": item.get("status") or "active",
    }


def has_changes(question: QuizQuestion, payload: dict) -> bool:
    return any(getattr(question, key) != value for key, value in payload.items())


def apply_payload(question: QuizQuestion, payload: dict):
    for key, value in payload.items():
        setattr(question, key, value)


def import_questions(items: list[dict], dry_run: bool = False, session_local=SessionLocal) -> ImportStats:
    stats = ImportStats()
    payloads = []
    seen = set()

    for item in items:
        try:
            payload = normalize_question(item)
            if payload["source_id"] in seen:
                stats.skipped += 1
                continue
            seen.add(payload["source_id"])
            payloads.append(payload)
        except Exception:
            stats.failed += 1

    with session_local() as db:
        try:
            for payload in payloads:
                existing = (
                    db.query(QuizQuestion)
                    .filter(QuizQuestion.source_id == payload["source_id"])
                    .first()
                )
                if not existing:
                    stats.created += 1
                    if not dry_run:
                        db.add(QuizQuestion(**payload))
                    continue
                if has_changes(existing, payload):
                    stats.updated += 1
                    if not dry_run:
                        apply_payload(existing, payload)
                else:
                    stats.skipped += 1
            if dry_run:
                db.rollback()
            else:
                db.commit()
        except SQLAlchemyError:
            db.rollback()
            if dry_run:
                stats.created += len(payloads)
                return stats
            raise
    return stats


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Import quiz choice questions.")
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="JSON source path, default backend/data/quiz-questions.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and count changes without writing database",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    items = load_questions(args.source)
    stats = import_questions(items, dry_run=args.dry_run)
    print(
        "created={created} updated={updated} skipped={skipped} failed={failed}".format(
            **stats.as_dict()
        )
    )
    if stats.failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
