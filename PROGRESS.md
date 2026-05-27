# 직업백과.kr 블로그 자동화 — 진행 상황

## 완료된 것

- [x] 코드 전체 완성 (`src/`, `data/`, `.github/workflows/`)
- [x] GitHub 저장소 업로드 완료 (`gksrlgus1020-design/auto-korea-jobs-blog`)
- [x] 가비아 DNS 설정 — 직업백과.kr → 133.186.221.190 연결 완료

## 다음에 할 것 (pem 파일 가져온 후)

### 1단계 — SSH 접속
- 회사 컴퓨터에서 `.pem` 파일 카카오톡으로 자신한테 전송
- PowerShell로 서버 접속:
  ```
  ssh -i [pem파일경로] ubuntu@133.186.221.190
  ```

### 2단계 — 서버에 WordPress 설치
- 같은 서버(133.186.221.190)에 직업백과.kr WordPress 추가 설치
- ddingpick.co.kr과 동일 서버, 별도 사이트로 운영

### 3단계 — GitHub Secrets 등록
GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret

| 이름 | 값 |
|------|-----|
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `WP_URL` | https://직업백과.kr |
| `WP_USERNAME` | WordPress 관리자 아이디 |
| `WP_APP_PASSWORD` | WordPress 애플리케이션 비밀번호 |

### 4단계 — 테스트 실행
GitHub Actions → 직업 블로그 자동 포스팅 → Run workflow

---

## 서버 정보
- **호스팅**: NHN Cloud
- **IP**: 133.186.221.190
- **OS**: Ubuntu Server 22.04 LTS
- **사양**: t2.c1m1 (1vCPU, 1GB RAM, HDD 20GB)
- **키페어 이름**: pem (파일은 회사 컴퓨터에 있음)

## 도메인
- **직업백과.kr** — 가비아 등록, DNS 설정 완료

## GitHub
- **저장소**: https://github.com/gksrlgus1020-design/auto-korea-jobs-blog
- **자동 실행**: 매일 오전 10시, 오후 2시 (KST) 직업 1개씩 자동 포스팅
