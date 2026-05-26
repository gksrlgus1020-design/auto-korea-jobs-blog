# 한국 직업 블로그 자동화

한국의 모든 직업을 소개하는 WordPress 블로그 자동 포스팅 시스템.

- Claude API로 직업별 본문 자동 생성
- GitHub Actions가 하루 2회 자동 실행
- 108개 직업 데이터 내장 (약 54일치)

---

## 시작하기

### 1. 저장소 포크 & 클론
```bash
git clone https://github.com/[본인ID]/korea-jobs-blog.git
cd korea-jobs-blog
```

### 2. GitHub Secrets 등록
GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret

| 이름 | 값 |
|------|----|
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `WP_URL` | WordPress 블로그 주소 (예: https://your-domain.com) |
| `WP_USERNAME` | WordPress 관리자 아이디 |
| `WP_APP_PASSWORD` | WordPress 애플리케이션 비밀번호 |

#### WordPress 애플리케이션 비밀번호 생성 방법
1. WordPress 관리자 로그인
2. 사용자 → 내 프로필
3. 아래로 스크롤 → **애플리케이션 비밀번호**
4. 이름 입력 (예: "GitHub Actions") → 생성
5. 표시된 비밀번호를 복사해서 Secrets에 저장

---

## 로컬 테스트

```bash
pip install -r requirements.txt

# .env 파일 생성
cp .env.example .env
# .env 파일에 실제 API 키 입력

# 본문만 미리보기 (포스팅 없음)
python src/main.py --dry-run

# 임시저장(draft)으로 테스트 포스팅
python src/main.py --test

# 실제 발행
python src/main.py
```

---

## 자동 실행 스케줄

| 시간 | 설명 |
|------|------|
| 매일 오전 10:00 KST | 직업 1개 자동 포스팅 |
| 매일 오후 2:00 KST | 직업 1개 자동 포스팅 |

수동 실행: GitHub 저장소 → Actions → 직업 블로그 자동 포스팅 → Run workflow

---

## 직업 데이터 추가

`data/jobs.json`에 항목 추가:
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
