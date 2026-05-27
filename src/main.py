"""
한국 직업 블로그 자동 포스터
Usage:
  python src/main.py             # 실제 발행
  python src/main.py --dry-run   # 본문만 출력 (포스팅 없음)
  python src/main.py --test      # 임시저장(draft)으로 포스팅
"""
import argparse
import os
import sys

# .env 파일 자동 로드 (로컬 테스트 시 편의)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from job_picker import pick_job, mark_published, remaining_count
from content_gen import generate_content
from wp_poster import post_to_wordpress
from image_fetcher import fetch_thumbnail


def main() -> None:
    parser = argparse.ArgumentParser(description="한국 직업 블로그 자동 포스터")
    parser.add_argument("--dry-run", action="store_true", help="포스팅 없이 본문만 출력")
    parser.add_argument("--test",    action="store_true", help="임시저장(draft)으로 포스팅")
    args = parser.parse_args()

    # ── 1. 미발행 직업 선택 ───────────────────────────────────────────────────
    job = pick_job()
    if not job:
        print("🎉 모든 직업 포스팅이 완료되었습니다!")
        sys.exit(0)

    remaining = remaining_count()
    print(f"📌 선택된 직업: {job['name']}  ({job['category']})")
    print(f"   평균 연봉: {job['avg_salary']:,}만원  |  남은 직업: {remaining}개")

    # ── 2. 본문 생성 ──────────────────────────────────────────────────────────
    print("✍️  Claude API로 본문 생성 중...")
    title, content, image_query = generate_content(job)
    print(f"📄 제목: {title}")
    print(f"🔍 이미지 검색어: {image_query}")

    if args.dry_run:
        print("\n" + "─" * 60)
        print(content[:800])
        print("─" * 60)
        print("(--dry-run 모드: 포스팅하지 않았습니다)")
        return

    # ── 3. 이미지 가져오기 ────────────────────────────────────────────────────
    print("🖼️  Pexels에서 이미지 가져오는 중...")
    image_bytes, image_filename = fetch_thumbnail(job["name"], job["category"], image_query)
    if image_bytes:
        print(f"  ✅ 이미지 준비 완료: {image_filename}")
    else:
        print("  ⚠️ 이미지 없음 (이미지 없이 포스팅)")

    # ── 4. WordPress 포스팅 ───────────────────────────────────────────────────
    status = "draft" if args.test else "publish"
    print(f"📤 WordPress에 포스팅 중... (상태: {status})")
    post_id = post_to_wordpress(title, content, job, status, image_bytes, image_filename)

    if not post_id:
        print("❌ 포스팅 실패. 종료합니다.")
        sys.exit(1)

    # ── 5. 발행 이력 저장 ─────────────────────────────────────────────────────
    mark_published(job["id"], post_id, job["name"])
    print(f"✅ 완료!  포스트 ID: {post_id}  |  직업: {job['name']}")


if __name__ == "__main__":
    main()
