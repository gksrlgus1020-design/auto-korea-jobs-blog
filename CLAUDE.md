# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요
AI 자동화 WordPress 블로그 — 한국 직업 정보를 Claude API로 생성해 하루 2회 자동 포스팅.

목표: SEO 최적화, 사람처럼 보이는 운영 패턴, 토큰 최소화, 기능 단위 작업.

## 실행 명령

```bash
pip install -r requirements.txt

# 로컬 테스트
cp .env.example .env          # API 키 입력 후
python src/main.py --dry-run  # 본문만 출력 (포스팅 없음)
python src/main.py --test     # WordPress 임시저장(draft)으로 포스팅
python src/main.py            # 실제 발행
```

## 환경 변수 (.env)
| 변수 | 설명 |
|------|------|
| `ANTHROPIC_API_KEY` | Claude API 키 |
| `WP_URL` | WordPress 블로그 주소 |
| `WP_USERNAME` | WordPress 관리자 아이디 |
| `WP_APP_PASSWORD` | WordPress 애플리케이션 비밀번호 |

## 아키텍처

```
main.py → job_picker.py → content_gen.py → wp_poster.py
                ↓
        published/published_jobs.json  (발행 이력, GitHub에 commit)
```

### 데이터 흐름
1. `job_picker.pick_job()` — `data/jobs.json`에서 미발행 직업 무작위 선택
2. `content_gen.generate_content(job)` — Claude API로 `(title, html)` 튜플 반환
3. `wp_poster.post_to_wordpress()` — WordPress REST API로 포스팅, 카테고리/태그 자동 생성
4. `job_picker.mark_published()` — `published/published_jobs.json` 업데이트

### 발행 이력 관리
- `published/published_jobs.json` — 발행된 job id 목록, 중복 방지
- `published/last_published.txt` — git commit 메시지용 직업명
- GitHub Actions가 포스팅 후 `published/` 폴더를 자동 commit & push

### Claude API 프롬프트 (content_gen.py)
- 모델: `claude-opus-4-7`
- 출력 형식: `TITLE: [제목]\n---\n[HTML 본문]`
- 섹션 구조: 도입 → 업무 → 역량/자격증 → 연봉 → 장점 → 단점 → 취업방법 → 미래전망 → 마무리

### GitHub Actions 스케줄 (.github/workflows/post.yml)
- `cron: '0 1 * * *'` — 매일 오전 10시 KST
- `cron: '0 5 * * *'` — 매일 오후 2시 KST
- Secrets 필요: `ANTHROPIC_API_KEY`, `WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`

## 직업 데이터 추가 (data/jobs.json)
```json
{
  "id": "109",
  "name": "직업명",
  "category": "카테고리",
  "avg_salary": 5000,
  "salary_min": 3000,
  "salary_max": 10000,
  "salary_source": "출처, 연도",
  "employment_outlook": "증가",
  "required_education": "대졸 이상"
}
```

## 작업 원칙
- 기능 단위로 작업 — 전체 재분석 하지 않기
- Claude API 호출은 `content_gen.py`에서만
- WordPress API 호출은 `wp_poster.py`에서만
- 토큰 최소화: 프롬프트 수정 시 불필요한 섹션 제거 우선
