import streamlit as st
from openai import OpenAI

# secrets.toml에서 환경설정 읽기
API_KEY = st.secrets["API_KEY"]
OPENAI_MODEL = st.secrets["OPENAI_MODEL"]
DEFAULT_TEMPERATURE = st.secrets.get("DEFAULT_TEMPERATURE", 0.5)
DEFAULT_TOP_P = st.secrets.get("DEFAULT_TOP_P", 1.0)
DEFAULT_MAX_TOKENS = st.secrets.get("DEFAULT_MAX_TOKENS", 300)

# OpenAI 클라이언트 생성
client = OpenAI(api_key=API_KEY)

# Streamlit 앱 설정
st.set_page_config(page_title="쇼생크 랩스 챗", page_icon="🏝️")

def show_header():
    st.markdown(
        """
        <div style='text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 10px;'>
            🏝️ 쇼생크 랩스 챗
        </div>
        <div style='text-align: center; font-size: 16px; color: gray; margin-bottom: 30px;'>
            퇴사는 감정이 아니라 전략입니다.<br>아마다르 자와타네호를 향해 떠나보세요.
        </div>
        """,
        unsafe_allow_html=True
    )

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
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

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("지금 느끼는 감정이나 고민을 자유롭게 입력해주세요."):
        handle_user_input(prompt)

def handle_user_input(user_input):
    step = st.session_state.step
    substep = st.session_state.substep

    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

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
    guide_text = get_follow_up_guide(step)
    system_prompt = f"""
    답변자: 트위터와 같은 가능성이 있고, 당신의 감정에 공감할 수 있는 챗을 해주세요.
    
    다음 행동: {guide_text}
    """
    return call_gpt_with_context(system_prompt)

def generate_bridge_message(step):
    guide_text = get_bridge_guide(step)
    system_prompt = f"""
    답변자: 트위터처럼 부드럽고 편안한 메시지를 써주세요.
    
    다음 행동: {guide_text}
    """
    return call_gpt_with_context(system_prompt)

def generate_step_response(step):
    return call_gpt_with_context(get_step_prompt(step))

def get_follow_up_guide(step):
    guides = {1: "퇴사고민 정도 감정", 2: "이유 구체화", 5: "감정 기억 구체화", 6: "탈출의 가운데", 8: "미래의 사기"}
    return guides.get(step, "자유롭게 화해")

def get_bridge_guide(step):
    guides = {1: "감정이유 다녀가기", 2: "이유 피방차트", 5: "관계성 계산", 6: "탈출 계획", 8: "예상 설명"}
    return guides.get(step, "계속 연결")

def get_step_prompt(step):
    prompts = {
        3: "3단계 코친 플랜 제안",
        4: "오늘 행동 가운데",
        5: "감정회 및 위로", 
        6: "건강화 탈출 계획",
        7: "허용 체크리스트",
        8: "이상적인 사기 요약",
        9: "레드의 의견"
    }
    return prompts.get(step, "")

def call_gpt_with_context(system_prompt):
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
