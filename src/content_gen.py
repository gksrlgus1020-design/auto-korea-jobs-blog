import os
import anthropic

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def generate_content(job: dict) -> tuple[str, str]:
    """
    직업 데이터를 받아 (제목, HTML 본문) 튜플을 반환.
    """
    prompt = f"""당신은 한국의 직업 정보를 전문적으로 다루는 블로그 작가입니다.
취업을 준비하는 사람들이 다양한 직업을 탐색하고 진로를 결정하는 데 도움을 주는 글을 씁니다.

다음 직업에 대한 상세한 블로그 포스트를 작성해주세요.

[직업 정보]
- 직업명: {job['name']}
- 카테고리: {job['category']}
- 평균 연봉: 약 {job['avg_salary']:,}만원
- 연봉 범위: {job.get('salary_min', 0):,}만원 ~ {job.get('salary_max', 0):,}만원
- 연봉 출처: {job.get('salary_source', '고용노동부 임금구조기본통계')}
- 고용 전망: {job.get('employment_outlook', '보통')}
- 요구 학력: {job.get('required_education', '대졸 이상')}

[작성 요청]
아래 섹션을 포함한 HTML 블로그 포스트를 작성해주세요.

1. 도입부 — 이 직업의 매력과 사회적 가치를 담은 흥미로운 소개 문단
2. <h2>'{job['name']}'은 어떤 일을 하나요?</h2> — 구체적인 업무 설명
3. <h2>필요한 역량과 자격증</h2> — 학력, 핵심 기술, 관련 자격증 목록
4. <h2>평균 연봉은 얼마인가요?</h2> — 제공된 연봉 데이터 활용, 경력에 따른 변화
5. <h2>이 직업의 장점</h2> — 5가지 이상 구체적 장점 (ul/li)
6. <h2>이 직업의 단점과 어려운 점</h2> — 3~4가지 솔직한 단점 (ul/li)
7. <h2>어떻게 이 직업을 가질 수 있나요?</h2> — 취업 경로, 준비 방법
8. <h2>2025~2030년 미래 전망</h2> — AI·기술 변화와 함께 전망 분석
9. 마무리 — 독자에게 용기를 주는 따뜻한 문단

[작성 지침]
- 한국어로 작성
- 2000~2500자 내외
- h2, h3, p, ul, li 태그 사용
- 객관적이고 실용적인 정보 제공
- 밝고 격려적인 톤 유지
- SEO에 적합한 자연스러운 문체

응답은 반드시 아래 형식으로 작성:
TITLE: [SEO 최적화된 블로그 제목 — 직업명, 연봉, 전망 키워드 포함]
---
[HTML 본문]"""

    message = _get_client().messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_response(message.content[0].text, job["name"])


def _parse_response(response: str, job_name: str) -> tuple[str, str]:
    title = f"{job_name} 직업 완벽 가이드 | 연봉, 전망, 취업 방법 총정리"
    content = response

    if "TITLE:" in response:
        parts = response.split("---", 1)
        title_raw = parts[0].strip()
        for line in title_raw.splitlines():
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                break
        if len(parts) > 1:
            content = parts[1].strip()

    return title, content
