# chat.py

import streamlit as st
from openai import OpenAI
from components.header import show_header

# secrets.toml에서 환경설정 읽기
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENAI_MODEL = st.secrets["OPENAI_MODEL"]
DEFAULT_TEMPERATURE = st.secrets.get("DEFAULT_TEMPERATURE", 0.5)
DEFAULT_TOP_P = st.secrets.get("DEFAULT_TOP_P", 1.0)
DEFAULT_MAX_TOKENS = st.secrets.get("DEFAULT_MAX_TOKENS", 300)

# OpenAI 클라이언트 생성
client = OpenAI(api_key=OPENAI_API_KEY)

# Streamlit 앱 설정
st.set_page_config(page_title="쇼생크 랩스 챗", page_icon="🏝️")

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # 고정 인삿말 추가
        st.session_state.messages.append({
            "role": "assistant",
            "content": "🏝️ 쇼생크 랩스 챗에 오신 걸 환영합니다!\n\n지금 느끼는 감정이나 고민을 자유롭게 적어주세요. 아주 사소한 이야기라도 괜찮아요. 당신의 이야기를 듣고 함께 고민해드릴게요."
        })
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "substep" not in st.session_state:
        st.session_state.substep = 1
    if "responses" not in st.session_state:
        st.session_state.responses = {}

def main():
    st.title("🏝️ 쇼생크 랩스 챗")
    show_header()
    initialize_session()

    # 이전 대화 기록 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 사용자 입력 받기
    if prompt := st.chat_input("지금 느끼는 감정이나 고민을 자유롭게 입력해주세요."):
        handle_user_input(prompt)

def handle_user_input(user_input):
    """사용자 입력을 받아 즉시 출력하고, 이어서 GPT가 질문 생성"""
    step = st.session_state.step
    substep = st.session_state.substep

    # 1. 사용자 입력 출력
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. GPT 호출로 에이전트 답변 생성
    if substep == 1:
        assistant_reply = generate_follow_up_question(step)
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        st.session_state.substep = 2

    elif substep == 2:
        bridge_reply = generate_bridge_message(step)
        with st.chat_message("assistant"):
            st.markdown(bridge_reply)
        st.session_state.messages.append({"role": "assistant", "content": bridge_reply})

        if step in [3, 4, 5, 6, 7, 8, 9]:
            final_reply = generate_step_response(step)
            with st.chat_message("assistant"):
                st.markdown(final_reply)
            st.session_state.messages.append({"role": "assistant", "content": final_reply})

        st.session_state.step += 1
        st.session_state.substep = 1

def generate_follow_up_question(step):
    """GPT를 호출해서 추가 질문 생성"""
    guide_text = get_follow_up_guide(step)
    system_prompt = f"""
당신은 따뜻하고 공감 능력이 뛰어난 대화 코치입니다.
지금까지의 대화 내용을 참고하여, 사용자가 조금 더 자세히 이야기할 수 있도록 자연스럽고 친절하게 추가 질문을 작성해주세요.

추가 질문의 목표:
{guide_text}
"""
    return call_gpt_with_context(system_prompt)

def generate_bridge_message(step):
    """GPT를 호출해서 다리 멘트 생성"""
    guide_text = get_bridge_guide(step)
    system_prompt = f"""
당신은 따뜻하고 친근한 대화 코치입니다.
지금까지의 대화 내용을 참고하여, 사용자의 답변을 공감해준 후 자연스럽게 다음 주제로 넘어가는 멘트를 작성해주세요.

다음 주제로 넘어가기 위한 가이드:
{guide_text}
"""
    return call_gpt_with_context(system_prompt)

def generate_step_response(step):
    """GPT를 호출해서 각 스텝별 주요 답변 생성 (대화 내역 반영)"""
    if step == 3:
        system_prompt = """
당신은 따뜻하고 긍정적인 대화 코치입니다.
지금까지의 대화 내용을 참고하여, 사용자의 퇴사 고민을 바탕으로 다음과 같은 3단계 코칭 플랜을 작성해주세요:

1. 오늘 할 수 있는 아주 작은 행동
2. 이번 주 안에 세울 수 있는 작은 목표
3. 장기적으로 설정할 수 있는 인생 방향

진심 어린 공감과 희망을 담아 작성해주세요.
"""
    elif step == 4:
        system_prompt = """
지금까지의 대화 내용을 참고하여, 사용자가 오늘 하루 안에 실천할 수 있는 작고 부담 없는 준비 행동 1가지를 추천해주세요.
"""
    elif step == 5:
        system_prompt = """
지금까지의 대화 내용을 참고하여,

1. 사용자의 감정을 부드럽게 한 문장으로 요약하고,
2. 이어서 따뜻한 위로의 문장을 하나 작성해주세요.
"""
    elif step == 6:
        system_prompt = """
지금까지의 대화 내용을 참고하여, 사용자가 선택한 탈출 경로(이직, 휴식 등)를 3개월, 6개월 안에 현실화할 수 있도록 구체적인 플랜을 제안해주세요.
"""
    elif step == 7:
        system_prompt = """
지금까지의 대화 내용을 참고하여, 사용자가 선택한 탈출 경로를 실행하기 위해 필요한 준비물 체크리스트를 5개 항목으로 작성해주세요.
"""
    elif step == 8:
        system_prompt = """
지금까지의 대화 내용을 참고하여, 사용자가 꿈꾸는 이상적인 삶을 3~5문장으로 아름답고 희망적으로 요약해주세요.
"""
    elif step == 9:
        system_prompt = """
지금까지의 대화 내용을 참고하여, 퇴사를 고민하는 사용자에게 영화 '쇼생크 탈출' 속 레드가 할 법한 짧고 희망적인 조언을 한 문장으로 작성해주세요.
"""
    else:
        return "지원하지 않는 단계입니다."

    return call_gpt_with_context(system_prompt)

def get_follow_up_guide(step):
    """각 스텝별 추가 질문 가이드"""
    guides = {
        1: "퇴사를 얼마나 고민하고 있는지 조금 더 구체적으로 이야기하도록 유도합니다.",
        2: "퇴사를 고민하는 이유를 구체적인 경험이나 상황으로 풀어낼 수 있도록 유도합니다.",
        5: "감정의 깊이와 원인을 더 깊게 이해할 수 있도록 질문합니다.",
        6: "선택한 탈출 경로에 대한 개인적인 동기를 더 깊이 파악하도록 유도합니다.",
        8: "꿈꾸는 이상적인 삶에 대해 더 구체적인 상상을 끌어냅니다.",
    }
    return guides.get(step, "사용자가 자신의 이야기를 조금 더 자세히 풀어내도록 유도합니다.")

def get_bridge_guide(step):
    """각 스텝별 다리 멘트 가이드"""
    guides = {
        1: "감정 온도 파악 후, 퇴사 고민 이유로 자연스럽게 넘어갑니다.",
        2: "퇴사 고민 이유 파악 후, 코칭 플랜 제안으로 자연스럽게 넘어갑니다.",
        5: "감정을 이해한 후, 다음 실질적 단계로 부드럽게 넘어갑니다.",
        6: "탈출 경로를 들은 후, 준비물 체크로 자연스럽게 넘어갑니다.",
        8: "꿈꾸는 삶을 들은 후, 마지막 조언으로 연결합니다.",
    }
    return guides.get(step, "사용자의 답변을 인정하고 다음 질문으로 자연스럽게 이어갑니다.")

def call_gpt_with_context(system_prompt):
    """OpenAI에 system prompt + 대화 히스토리를 보내 답변 생성"""
    messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
        top_p=DEFAULT_TOP_P,
        max_tokens=DEFAULT_MAX_TOKENS,
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    main()
