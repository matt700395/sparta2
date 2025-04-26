# components/header.py

import streamlit as st

def show_header():
    st.markdown(
        """
        <div style='text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 10px;'>
            🏝️ 쇼생크 랩스 챗
        </div>
        <div style='text-align: center; font-size: 16px; color: gray; margin-bottom: 30px;'>
            퇴사는 감정이 아니라 전략입니다.<br>당신만의 자와타네호를 향해 떠나보세요.
        </div>
        """,
        unsafe_allow_html=True
    )
