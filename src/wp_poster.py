import base64
import os
import requests


def _auth_headers() -> dict:
    username = os.environ["WP_USERNAME"]
    password = os.environ["WP_APP_PASSWORD"]
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }


def _base_url() -> str:
    return os.environ["WP_URL"].rstrip("/")


def _get_or_create_term(endpoint: str, name: str) -> int:
    """카테고리 or 태그 ID 조회, 없으면 생성."""
    headers = _auth_headers()
    r = requests.get(endpoint, params={"search": name, "per_page": 5}, headers=headers, timeout=15)
    r.raise_for_status()
    items = r.json()
    for item in items:
        if item["name"] == name:
            return item["id"]

    r = requests.post(endpoint, json={"name": name}, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()["id"]


def _upload_image(image_bytes: bytes, filename: str) -> int | None:
    """이미지를 WordPress 미디어 라이브러리에 업로드하고 media_id 반환."""
    base = _base_url()
    username = os.environ["WP_USERNAME"]
    password = os.environ["WP_APP_PASSWORD"]
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    # Content-Disposition 헤더는 ASCII만 허용 — 한글 제거 후 사용
    safe_filename = filename.encode("ascii", "ignore").decode("ascii") or "thumbnail.jpg"
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Disposition": f"attachment; filename={safe_filename}",
        "Content-Type": "image/jpeg",
    }
    r = requests.post(f"{base}/wp-json/wp/v2/media", data=image_bytes, headers=headers, timeout=30)
    if r.status_code in (200, 201):
        return r.json()["id"]
    print(f"  ⚠️ 이미지 업로드 실패 {r.status_code}: {r.text[:200]}")
    return None


def post_to_wordpress(title: str, content: str, job: dict, status: str = "publish",
                      image_bytes: bytes | None = None, image_filename: str | None = None) -> int | None:
    """
    WordPress REST API로 포스팅.
    성공 시 post_id 반환, 실패 시 None.
    """
    base = _base_url()
    headers = _auth_headers()

    # 카테고리
    cat_endpoint = f"{base}/wp-json/wp/v2/categories"
    cat_id = _get_or_create_term(cat_endpoint, job["category"])

    # 태그
    tag_endpoint = f"{base}/wp-json/wp/v2/tags"
    tag_names = [job["name"], job["category"], "직업정보", "취업", "연봉", "진로"]
    tag_ids = [_get_or_create_term(tag_endpoint, t) for t in tag_names]

    payload = {
        "title":      title,
        "content":    content,
        "status":     status,
        "categories": [cat_id],
        "tags":       tag_ids,
    }

    # 대표 이미지 업로드
    if image_bytes and image_filename:
        media_id = _upload_image(image_bytes, image_filename)
        if media_id:
            payload["featured_media"] = media_id
            print(f"  🖼️  대표 이미지 설정 (media_id: {media_id})")

    r = requests.post(f"{base}/wp-json/wp/v2/posts", json=payload, headers=headers, timeout=30)

    if r.status_code in (200, 201):
        post_id = r.json()["id"]
        post_url = r.json().get("link", "")
        print(f"  📎 URL: {post_url}")
        return post_id
    else:
        print(f"  ❌ WordPress 오류 {r.status_code}: {r.text[:300]}")
        return None
