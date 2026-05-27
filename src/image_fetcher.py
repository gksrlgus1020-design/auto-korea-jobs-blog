import os
import requests

_FALLBACK_KEYWORDS = {
    "IT": "computer work office",
    "의료": "medical hospital healthcare",
    "교육": "education teaching classroom",
    "법률": "law justice court",
    "금융": "finance money business",
    "건설": "construction building worker",
    "제조": "factory manufacturing worker",
    "서비스": "service customer work",
    "예술": "art creative design",
    "농업": "agriculture farm nature",
}


def fetch_thumbnail(job_name: str, category: str) -> tuple[bytes, str] | tuple[None, None]:
    """Pexels에서 직업 관련 이미지 가져오기. (image_bytes, filename) 반환."""
    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        return None, None

    query = _FALLBACK_KEYWORDS.get(category, job_name)
    headers = {"Authorization": api_key}

    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 15, "orientation": "landscape"},
            headers=headers,
            timeout=10,
        )
        print(f"  Pexels 응답: {r.status_code} (query: {query})")
        if r.status_code != 200:
            print(f"  Pexels 오류: {r.text[:200]}")
            return None, None

        photos = r.json().get("photos", [])
        print(f"  Pexels 사진 수: {len(photos)}")
        if not photos:
            return None, None

        import random
        photo = random.choice(photos[:10])
        img_url = photo["src"]["large"]
        photographer = photo.get("photographer", "pexels")

        img_r = requests.get(img_url, timeout=15)
        if img_r.status_code == 200:
            filename = f"{job_name}_{photographer}.jpg".replace(" ", "_")
            return img_r.content, filename

    except Exception as e:
        print(f"  ⚠️ 이미지 가져오기 실패: {e}")

    return None, None
