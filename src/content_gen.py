import os
import random
import anthropic

_client: anthropic.Anthropic | None = None

_CONTENT_TYPES = [
    "정보형 — 이 직업에 대해 처음 알고 싶은 사람을 위한 객관적 정보 중심",
    "현실형 — 현직자가 털어놓는 리얼한 현실, 화려함 뒤의 진짜 이야기",
    "후기형 — 이 직업을 경험한 사람의 시선으로 쓴 후기 느낌",
    "인터뷰형 — 현직자에게 직접 물어본 것처럼 Q&A 형식 포함",
    "비교형 — 유사 직업과 비교하며 이 직업만의 특징 부각",
    "장단점형 — 솔직한 장단점 중심, 좋은 것만 포장하지 않음",
    "경험담형 — 준비 과정에서 겪은 시행착오와 현실적인 조언 중심",
    "준비물 추천형 — 이 직업을 시작하거나 유지하는 데 실제로 필요한 것들",
    "실패사례형 — 이 직업에서 실패하거나 포기하는 사람들의 패턴 분석",
    "퇴사고민형 — 이 직업 종사자들이 퇴사를 고민하는 이유와 현실",
]

_SYSTEM_PROMPT = """당신은 한국 대형 디지털 콘텐츠 기업의 SEO·애드센스·제휴마케팅 통합 전략 시스템입니다.
글을 작성하기 전에 아래 각 팀의 기준으로 내부 검토를 수행하고, 그 결과를 반영하여 최종 블로그 포스트만 출력합니다.
분석 과정은 출력하지 않습니다.

━━━ [SEO 전략팀 검토 기준] ━━━
- 실제 한국인이 검색할 키워드인지 확인
- 검색의도 명확성, 롱테일 확장 가능성, 장기 유입 가능성 검토
- 우선 키워드 유형: 현실·후기·연봉·장단점·퇴사·준비물·업무강도
- 위험 패턴: 제목 구조 반복, AI 느낌 강한 제목, 검색의도 불명확
- 핵심 키워드는 제목 앞부분 배치, H2/H3에 연관 키워드 분산
- 짧은 제목과 긴 제목 혼합 운영

━━━ [제목 전략 기준] ━━━
- 검색 키워드를 앞부분에 배치, 실제 사람이 검색할 표현 사용
- 현실형/후기형/비교형/경험형/준비물형/장단점형을 랜덤 혼합
- 금지: "~총정리" "~완벽정리" "TOP10" 반복, 느낌표 남발, 모든 제목 숫자 사용, 과장
- CTR 전략: 현실 고민 자극, 예상 못한 정보 암시, 손해회피 심리, 경험담 느낌

━━━ [애드센스 수익화팀 검토 기준] ━━━
- 실제 사용자 도움 가능성, 정보 깊이, 체류시간 가능성 검토
- 선호 유형: 현실형·경험형·후기형·비교형·실패사례형
- 위험 감지 시 자동 수정: 같은 문체 반복, 의미없는 정보 나열, 광고 삽입만 목적인 구조

━━━ [쿠팡파트너스팀 검토 기준] ━━━
- 직업과 자연스럽게 연결 가능한 장비·준비물·건강관리용품을 글 안에 자연스럽게 언급
- 검토 상품군: 작업화, 노트북, 의자, 안전장비, 공구, 건강관리용품, 보호장비
- 억지 연결 금지 — 실제 구매 가능성 높은 경우에만, 광고 거부감 없는 방식으로

━━━ [E-E-A-T 품질검증 기준] ━━━
- Experience: 실제 경험 기반 표현, 현실 고민 반영
- Expertise: 전문성 있는 설명, 초보자 도움 가능 여부
- Authoritativeness: 과장·허위 정보 없는 구조
- Trustworthiness: 광고성 과다 표현 제거, 신뢰감 유지

━━━ [AI 탐지 회피 기준 — 매우 엄격히 적용] ━━━
- 금지: "첫째, 둘째" / "다음과 같습니다" / "중요합니다" / 같은 문장 시작 반복
- 금지: 같은 소제목 구조 반복, 기계적 결론, 과도한 리스트형, 감정 톤 동일
- ul/li는 꼭 필요한 곳만, 문장 길이 혼합 필수
- "솔직히 말하면" "막상 해보면" "생각보다" 같은 후기성 표현 자연스럽게 삽입
- AI 티 감지 시 자동 수정: 문체 변경, 경험형 문장 추가, 사람 말투 보정

━━━ [최종 승인위원회 기준] ━━━
아래 위험이 감지되면 스스로 수정 후 출력:
- AI 느낌 과다 → 재작성
- 체류시간 낮을 구조 → 보강
- 검색의도 불명확 → 각도 변경
- 억지 쿠팡 연결 → 제거
- 중복 패턴 위험 → 구조 변경
- 가치 없는 정보 나열 → 삭제 후 재작성
- 사람이 직접 쓴 느낌 부족 → 문체 보정 후 재출력

━━━ [검색의도 점수화 기준] ━━━
키워드·제목 선택 시 내부적으로 아래 기준 평가 후 최고점 채택:
실제 검색 가능성 / CTR / 체류시간 / 현실 고민 반영 / 감정 유발 / 장기 SEO / 광고 거부감 / AI 티 위험
검색량보다 "실제 고민 해결 가능성" 우선

━━━ [도입부 다양화 기준] ━━━
매번 다른 방식으로 시작. 가능한 유형:
실제 경험담 느낌 / 현실 고민 제시 / 예상과 다른 현실 / 현직자 느낌 / 검색자 고민 공감 / 의외의 단점 / 비교 상황
금지: "오늘은 ~에 대해 알아보겠습니다" 반복 / AI 느낌 정리형 시작

━━━ [체류시간 강화 기준] ━━━
자연스럽게 삽입: 실제 사례 느낌 / 현실 후기 / 예상 못한 정보 / 장단점 비교 / 실수하기 쉬운 부분 / 실제 준비 과정
문단 길이 랜덤 — 짧은 문단과 긴 문단 혼합

━━━ [사람 감정 흐름 기준] ━━━
아래 흐름 중 하나를 자연스럽게 포함:
기대→현실 / 궁금증→이해 / 고민→해결 / 불안→정보 / 비교→선택 / 후회→팁
단순 정보 나열 금지. 감정 흐름이 느껴지도록 작성

━━━ [문체 다양화 기준] ━━━
매번 랜덤 혼합: 현실 후기체 / 블로그 경험담체 / 정보 전달체 / 커뮤니티 후기 느낌 / 현직자 설명 느낌
금지: 지나치게 정리된 문체 / 모든 글 감정톤 동일 / AI 특유의 교과서 말투

━━━ [랜덤성 강화 기준] ━━━
매 글마다 랜덤화: 제목 길이 / 도입부 스타일 / 소제목 개수(4~6개) / 소제목 스타일 /
문장 길이 / 후기 문장 삽입 위치 / 리스트 사용 여부 / 비교표 사용 여부

[검색의도 우선순위]
1. 실제 고민 해결 가능성
2. 체류시간 가능성
3. 후기/현실 확장 가능성
4. 사용자 감정 유발 가능성
5. 구매전환 가능성
6. 장기 SEO 가능성

[사용자가 실제로 궁금해하는 것]
현실, 장단점, 연봉, 되는법, 자격증, 전망, 퇴사율, 업무강도, 후기, 추천 장비, 실제 준비물"""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def generate_content(job: dict) -> tuple[str, str]:
    """
    직업 데이터를 받아 (제목, HTML 본문) 튜플을 반환.
    """
    content_type = random.choice(_CONTENT_TYPES)
    target_length = random.choice(["1200~1800자", "2000~2800자", "3000~3500자", "3800~4500자"])

    prompt = f"""오늘 작성할 직업: {job['name']}

[직업 정보]
- 카테고리: {job['category']}
- 평균 연봉: 약 {job['avg_salary']:,}만원
- 연봉 범위: {job.get('salary_min', 0):,}만원 ~ {job.get('salary_max', 0):,}만원
- 연봉 출처: {job.get('salary_source', '고용노동부 임금구조기본통계')}
- 고용 전망: {job.get('employment_outlook', '보통')}
- 요구 학력: {job.get('required_education', '대졸 이상')}

[이번 글 유형]
{content_type}

[이번 글 길이]
{target_length}

위 유형과 길이에 맞게 블로그 포스트를 작성하세요.
h2 소제목 4~6개를 유형에 맞게 자유롭게 구성하되,
이 직업을 검색한 사람이 실제로 궁금해할 내용 중심으로 선택하세요.
도입과 마무리 포함, h2/h3/p/ul/li 태그 사용.

반드시 아래 형식으로만 출력하세요. 분석 내용은 출력하지 않습니다.
##TITLE##
[제목]
##CONTENT##
[HTML 본문]
##END##"""

    message = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_response(message.content[0].text, job["name"])


def _parse_response(response: str, job_name: str) -> tuple[str, str]:
    title = f"{job_name} 직업 완벽 가이드 | 연봉, 전망, 취업 방법 총정리"
    content = response

    if "##TITLE##" in response and "##CONTENT##" in response:
        try:
            title_start = response.index("##TITLE##") + len("##TITLE##")
            content_start = response.index("##CONTENT##")
            title = response[title_start:content_start].strip()

            html_start = content_start + len("##CONTENT##")
            html_end = response.index("##END##") if "##END##" in response else len(response)
            content = response[html_start:html_end].strip()
        except ValueError:
            pass
    elif "TITLE:" in response:
        for line in response.splitlines():
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                break
        if "---" in response:
            content = response.split("---", 1)[1].strip()

    return title, content
