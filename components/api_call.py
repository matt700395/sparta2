# components/api_call.py

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

# OpenAI 클라이언트 생성
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_emotion(temp, emotions):
    prompt = f"""
    다음은 사용자가 선택한 감정 키워드와 퇴사 욕구 온도입니다. 이 정보를 바탕으로 사용자의 현재 감정 상태를 1~2문장으로 요약해 주세요.
    - 퇴사 욕구 온도: {temp}도
    - 감정 키워드: {', '.join(emotions)}
    부드럽고 공감 가는 어조로 작성해 주세요.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        top_p=1.0,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

def summarize_impulse(user_text):
    prompt = f"""
    사용자가 퇴사하고 싶은 이유를 작성했습니다.
    이 글을 읽고 주된 감정과 퇴사 이유를 2~3줄로 부드럽게 요약해 주세요.
    사용자 입력: {user_text}
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        top_p=1.0,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def generate_step_response(step):
    """특정 스텝에 대한 OpenAI 기반 답변 생성"""
    user_context = st.session_state.responses  # 지금까지 모은 사용자 답변

    if step == 3:
        context = user_context.get("step_1_first", "") + " " + user_context.get("step_2_first", "")
        prompt = f"""
당신은 따뜻한 코치입니다.
사용자가 최근 퇴사를 고민하고 있습니다.

현재 상황:
{context}

이 상황을 바탕으로 다음과 같은 3단계 코칭 플랜을 작성해주세요.
1. 오늘 할 수 있는 아주 작은 행동
2. 이번 주 안에 달성할 작은 목표
3. 장기적으로 바라봐야 할 인생 방향

사람처럼 부드럽고 따뜻한 말투로 작성하세요.
"""
    elif step == 4:
        prompt = f"""
사용자는 현재 퇴사를 준비하고 있습니다.

오늘 하루 안에 아주 작게 실천할 수 있는 준비 행동 1가지를 추천해주세요.
예시는 구체적이고 부담이 없어야 합니다.
"""
    elif step == 5:
        user_emotion = user_context.get("step_5_first", "")
        prompt = f"""
사용자가 다음과 같은 감정을 털어놨습니다:
"{user_emotion}"

1. 이 감정을 따뜻하게 요약해 주세요.
2. 이어서 부드럽게 위로해 주세요.

기계적이지 말고 인간적인 말투로 작성하세요.
"""
    elif step == 6:
        chosen_path = user_context.get("step_6_first", "")
        prompt = f"""
사용자가 선택한 탈출 경로는 "{chosen_path}"입니다.

이 경로를 3개월, 6개월 안에 현실화할 수 있도록
작은 준비 플랜을 구체적으로 작성해주세요.
"""
    elif step == 7:
        exit_plan = user_context.get("step_6_first", "")
        prompt = f"""
사용자가 선택한 탈출 경로는 "{exit_plan}"입니다.

이 경로를 준비하기 위해 필요한 핵심 준비물 리스트 5개를 짧고 명확하게 작성해주세요.
"""
    elif step == 8:
        dream_job = user_context.get("step_8_first", "")
        prompt = f"""
사용자가 꿈꾸는 삶을 상상했습니다:
"{dream_job}"

이 삶을 아름답게 요약해 주세요.
긍정적이고 희망적인 말투로 3~5문장으로 작성하세요.
"""
    elif step == 9:
        prompt = """
퇴사를 고민하는 사용자에게 레드 스타일의 짧은 조언을 해주세요.
부드럽고 희망적인 느낌으로 간결하게 한 문장 작성하세요.
"""

    else:
        return "지원하지 않는 스텝입니다."

    # OpenAI 호출
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()


def generate_daily_plan(context):
    prompt = f"""
    사용자의 감정과 충동 요약입니다:
    감정: {context['emotion']}
    충동: {context['impulse']}
    
    오늘 하루 안에 실천할 수 있는 작고 부담 없는 준비 행동 하나를 추천해 주세요.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        top_p=1.0,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

def detox_emotion(user_text):
    prompt = f"""
    사용자가 감정을 털어놓은 글입니다.
    1. 이 감정을 한 문장으로 요약해 주세요.
    2. 부드럽고 위로가 되는 한 문장의 응원을 만들어 주세요.
    
    포맷:
    [감정 요약]: (문장)
    [응원 메시지]: (문장)
    
    사용자 입력: {user_text}
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        top_p=1.0,
        max_tokens=400
    )
    output_text = response.choices[0].message.content.strip()

    lines = output_text.split("\n")
    summary = ""
    comfort = ""
    for line in lines:
        if line.startswith("[감정 요약]"):
            summary = line.replace("[감정 요약]:", "").strip()
        elif line.startswith("[응원 메시지]"):
            comfort = line.replace("[응원 메시지]:", "").strip()

    return {"summary": summary, "comfort": comfort}

def plan_escape_route(option):
    prompt = f"""
    사용자가 선택한 비상구 옵션은 다음과 같습니다:
    {option}
    
    이 옵션을 3개월, 6개월 안에 현실화할 수 있도록
    실천 가능한 플랜을 제안해 주세요.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        top_p=1.0,
        max_tokens=400
    )
    return response.choices[0].message.content.strip()

def generate_escape_checklist(exit_plan):
    prompt = f"""
    사용자의 비상구 플랜:
    {exit_plan}
    
    이 플랜을 성공시키기 위해 준비해야 할 필수 항목 5~7개를
    체크리스트 형태로 작성해 주세요. 항목은 간단명료하게.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        top_p=1.0,
        max_tokens=400
    )
    checklist_text = response.choices[0].message.content.strip()
    checklist_items = [item.strip("- ").strip() for item in checklist_text.split("\n") if item]
    return checklist_items

def define_zihuatanejo(job, place, routine):
    prompt = f"""
    사용자가 꿈꾸는 삶에 대해 답변했습니다.
    - 하고 싶은 일: {job}
    - 살고 싶은 장소: {place}
    - 원하는 하루 루틴: {routine}
    
    이 정보를 바탕으로 3~5문장으로 이상적인 삶을 요약해 주세요.
    긍정적이고 희망찬 어조로.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        top_p=1.0,
        max_tokens=400
    )
    return response.choices[0].message.content.strip()

def get_reds_advice():
    prompt = """
    퇴사를 고민하는 사용자에게 힘이 되는 짧은 한 문장의 조언을 해주세요.
    영화 '쇼생크 탈출'의 레드 스타일처럼, 부드럽고 희망찬 느낌으로.
    문장은 짧고 간결하게.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        top_p=1.0,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()
