import os
import requests

_CATEGORY_KEYWORDS = {
    "IT": "computer programming developer",
    "의료": "medical hospital doctor",
    "교육": "education teacher classroom",
    "법률": "lawyer law office",
    "금융": "finance accountant business",
    "건설": "construction worker building",
    "제조": "factory manufacturing",
    "서비스": "customer service work",
    "예술": "art creative studio",
    "농업": "agriculture farm",
}


def fetch_thumbnail(job_name: str, category: str) -> tuple[bytes, str] | tuple[None, None]:
    """직업명으로 Pexels 이미지 검색. 연관성 높은 첫 번째 사진 반환."""
    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        return None, None

    headers = {"Authorization": api_key}

    # 1차: 직업명(한국어)으로 검색
    result = _search(job_name, headers)

    # 2차: 카테고리 영어 키워드로 검색
    if not result:
        fallback = _CATEGORY_KEYWORDS.get(category, "professional work office")
        result = _search(fallback, headers)

    if not result:
        return None, None

    img_url, photographer = result
    try:
        img_r = requests.get(img_url, timeout=15)
        if img_r.status_code == 200:
            filename = f"{job_name}_{photographer}.jpg".replace(" ", "_")
            return img_r.content, filename
    except Exception as e:
        print(f"  ⚠️ 이미지 다운로드 실패: {e}")

    return None, None


def _search(query: str, headers: dict) -> tuple[str, str] | None:
    """Pexels 검색 후 가장 연관성 높은 첫 번째 사진의 (url, photographer) 반환."""
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            headers=headers,
            timeout=10,
        )
        if r.status_code != 200:
            return None
        photos = r.json().get("photos", [])
        if not photos:
            return None
        photo = photos[0]  # 연관성 가장 높은 첫 번째
        return photo["src"]["large"], photo.get("photographer", "pexels")
    except Exception as e:
        print(f"  ⚠️ 이미지 검색 실패 ({query}): {e}")
        return None
