import json
import os
import random
from datetime import datetime

_BASE = os.path.dirname(os.path.dirname(__file__))
DATA_PATH      = os.path.join(_BASE, "data", "jobs.json")
PUBLISHED_PATH = os.path.join(_BASE, "published", "published_jobs.json")
LAST_TXT_PATH  = os.path.join(_BASE, "published", "last_published.txt")


def pick_job() -> dict | None:
    """미발행 직업 중 하나를 무작위로 선택."""
    with open(DATA_PATH, encoding="utf-8") as f:
        jobs = json.load(f)

    published_ids = _load_published_ids()
    unpublished = [j for j in jobs if j["id"] not in published_ids]

    if not unpublished:
        return None

    return random.choice(unpublished)


def mark_published(job_id: str, wp_post_id: int, job_name: str) -> None:
    """발행 완료 처리 및 이력 저장."""
    data = _load_published_data()

    data["published_ids"].append(job_id)
    data["total_published"] = len(data["published_ids"])
    data["last_published"] = {
        "id": job_id,
        "name": job_name,
        "post_id": wp_post_id,
        "published_at": datetime.utcnow().isoformat(),
    }

    os.makedirs(os.path.dirname(PUBLISHED_PATH), exist_ok=True)
    with open(PUBLISHED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # git commit 메시지에 쓸 직업명 저장
    with open(LAST_TXT_PATH, "w", encoding="utf-8") as f:
        f.write(job_name)


def remaining_count() -> int:
    """아직 발행되지 않은 직업 수."""
    with open(DATA_PATH, encoding="utf-8") as f:
        jobs = json.load(f)
    return len(jobs) - len(_load_published_ids())


def _load_published_ids() -> list[str]:
    return _load_published_data().get("published_ids", [])


def _load_published_data() -> dict:
    if os.path.exists(PUBLISHED_PATH):
        with open(PUBLISHED_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"published_ids": [], "total_published": 0, "last_published": None}
