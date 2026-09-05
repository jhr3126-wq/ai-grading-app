import streamlit as st
from grading_logic import Set1Grader, Set2Grader, Set3Grader, MODEL_ANSWERS, GradeResult

st.set_page_config(page_title="서논술형 자동 채점 시스템", layout="wide")

st.title("📝 서·논술형 문항 자동 채점 시스템")
st.caption("세트 1: 사회적 촉진과 억제 | 세트 2: 정전기의 특징 | 세트 3: AI가 그린 그림")

set_choice = st.sidebar.selectbox(
    "세트 선택",
    ["세트 1: 사회적 촉진과 억제", "세트 2: 정전기의 특징", "세트 3: AI가 그린 그림"]
)

show_model = st.sidebar.checkbox("모범 답안 함께 보기", value=True)


def show_result(result: GradeResult, model_text: str = None):
    if result.passed:
        st.success(result.summary())
    else:
        st.warning(result.summary())
    if model_text:
        with st.expander("📖 모범 답안 보기"):
            st.write(model_text)


# ============================================================
# 세트 1
# ============================================================
if set_choice.startswith("세트 1"):
    st.header("세트 1: 사회적 촉진과 억제")

    tab1, tab2, tab3 = st.tabs(["서·논술형 1 (표 완성)", "서·논술형 2 (문장 작성)", "서·논술형 3 (영상 기획)"])

    with tab1:
        st.subheader("㉠, ㉡, ㉢ 채점")
        ga = st.text_input("㉠ (쉬운 과제의 특성)", key="s1_ga")
        gb = st.text_input("㉡ (어려운 과제일 때 효율적 방법)", key="s1_gb")
        gg = st.text_input("㉢ (관련 심리 현상)", key="s1_gg")
        if st.button("채점하기", key="s1_1_btn"):
            r1 = Set1Grader.grade_1_1(ga)
            r2 = Set1Grader.grade_1_2(gb)
            r3 = Set1Grader.grade_1_3(gg)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**㉠ 결과**")
                show_result(r1, MODEL_ANSWERS["set1"]["1_1_ga"])
            with col2:
                st.write("**㉡ 결과**")
                show_result(r2, MODEL_ANSWERS["set1"]["1_2_gb"])
            with col3:
                st.write("**㉢ 결과**")
                show_result(r3, MODEL_ANSWERS["set1"]["1_3_gg"])
            total = r1.score + r2.score + r3.score
            st.info(f"### 총점: {total} / 6.0")

    with tab2:
        st.subheader("이어지는 문장 (1), (2) 작성")
        s1 = st.text_area("(1) 문장 (설명 방법 표기 포함)", key="s1_2_1")
        s2 = st.text_area("(2) 문장 (설명 방법 표기 포함)", key="s1_2_2")
        if st.button("채점하기", key="s1_2_btn"):
            result = Set1Grader.grade_2(s1, s2)
            show_result(result)
            st.markdown("**선택지별 모범 답안**")
            for k, v in MODEL_ANSWERS["set1"]["2"].items():
                st.write(f"- **{k}**: {v}")

    with tab3:
        st.subheader("영상 기획안 - 어려운 과제 장면")
        visual = st.text_area("시각 요소 (A)", key="s1_3_v")
        visual_eff = st.text_area("시각 요소 효과", key="s1_3_ve")
        audio = st.text_area("청각 요소 (B)", key="s1_3_a")
        audio_eff = st.text_area("청각 요소 효과", key="s1_3_ae")
        if st.button("채점하기", key="s1_3_btn"):
            result = Set1Grader.grade_3(visual, visual_eff, audio, audio_eff)
            show_result(result)
            st.markdown("**모범 답안 예시**")
            st.write(f"- 시각: {MODEL_ANSWERS['set1']['3']['시각_예시']}")
            st.write(f"- 청각: {MODEL_ANSWERS['set1']['3']['청각_예시']}")


# ============================================================
# 세트 2
# ============================================================
elif set_choice.startswith("세트 2"):
    st.header("세트 2: 정전기의 특징")

    tab1, tab2, tab3 = st.tabs(["서·논술형 1 (표 완성)", "서·논술형 2 (문장 작성)", "서·논술형 3 (영상 기획)"])

    with tab1:
        st.subheader("㉠, ㉡, ㉢ 채점")
        ga = st.text_input("㉠ (정전기의 물 비유)", key="s2_ga")
        gb = st.text_input("㉡ (전하의 상태)", key="s2_gb")
        gg = st.text_input("㉢ (위험성)", key="s2_gg")
        if st.button("채점하기", key="s2_1_btn"):
            r1 = Set2Grader.grade_1_1(ga)
            r2 = Set2Grader.grade_1_2(gb)
            r3 = Set2Grader.grade_1_3(gg)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**㉠ 결과**")
                show_result(r1, MODEL_ANSWERS["set2"]["1_1_ga"])
            with col2:
                st.write("**㉡ 결과**")
                show_result(r2, MODEL_ANSWERS["set2"]["1_2_gb"])
            with col3:
                st.write("**㉢ 결과**")
                show_result(r3, MODEL_ANSWERS["set2"]["1_3_gg"])
            total = r1.score + r2.score + r3.score
            st.info(f"### 총점: {total} / 6.0")
            st.caption("⚠ ㉢(위험성) 항목은 원본 표 서식 확인이 필요합니다.")

    with tab2:
        st.subheader("이어지는 문장 (1), (2) 작성")
        s1 = st.text_area("(1) 문장 (설명 방법 표기 포함)", key="s2_2_1")
        s2 = st.text_area("(2) 문장 (설명 방법 표기 포함)", key="s2_2_2")
        if st.button("채점하기", key="s2_2_btn"):
            result = Set2Grader.grade_2(s1, s2)
            show_result(result)
            st.markdown("**선택지별 모범 답안**")
            for k, v in MODEL_ANSWERS["set2"]["2"].items():
                st.write(f"- **{k}**: {v}")

    with tab3:
        st.subheader("영상 기획안 - 정전기(고여있는 물) 장면")
        visual = st.text_area("시각 요소 (A)", key="s2_3_v")
        visual_eff = st.text_area("시각 요소 효과", key="s2_3_ve")
        audio = st.text_area("청각 요소 (B)", key="s2_3_a")
        audio_eff = st.text_area("청각 요소 효과", key="s2_3_ae")
        if st.button("채점하기", key="s2_3_btn"):
            result = Set2Grader.grade_3(visual, visual_eff, audio, audio_eff)
            show_result(result)
            st.markdown("**모범 답안 예시**")
            st.write(f"- 시각: {MODEL_ANSWERS['set2']['3']['시각_예시']}")
            st.write(f"- 청각: {MODEL_ANSWERS['set2']['3']['청각_예시']}")


# ============================================================
# 세트 3
# ============================================================
elif set_choice.startswith("세트 3"):
    st.header("세트 3: AI가 그린 그림")

    tab1, tab2, tab3 = st.tabs(["서·논술형 1 (표 완성)", "서·논술형 2 (문장 작성)", "서·논술형 3 (영상 기획)"])

    with tab1:
        st.subheader("㉠, ㉡, ㉢ 채점")
        ga = st.text_input("㉠ (AI 예술의 올림픽 비유)", key="s3_ga")
        gb = st.text_area("㉡ (예술로 볼 수 있는가 + 근거)", key="s3_gb")
        gg = st.text_area("㉢ (예술로서의 가치)", key="s3_gg")
        if st.button("채점하기", key="s3_1_btn"):
            r1 = Set3Grader.grade_1_1(ga)
            r2 = Set3Grader.grade_1_2(gb)
            r3 = Set3Grader.grade_1_3(gg)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**㉠ 결과**")
                show_result(r1, MODEL_ANSWERS["set3"]["1_1_ga"])
            with col2:
                st.write("**㉡ 결과**")
                show_result(r2, MODEL_ANSWERS["set3"]["1_2_gb"])
            with col3:
                st.write("**㉢ 결과**")
                show_result(r3, MODEL_ANSWERS["set3"]["1_3_gg"])
            total = r1.score + r2.score + r3.score
            st.info(f"### 총점: {total} / 6.0")

    with tab2:
        st.subheader("이어지는 문장 (1), (2) 작성")
        s1 = st.text_area("(1) 문장 (설명 방법 표기 포함)", key="s3_2_1")
        s2 = st.text_area("(2) 문장 (설명 방법 표기 포함)", key="s3_2_2")
        if st.button("채점하기", key="s3_2_btn"):
            result = Set3Grader.grade_2(s1, s2)
            show_result(result)
            st.markdown("**선택지별 모범 답안**")
            for k, v in MODEL_ANSWERS["set3"]["2"].items():
                st.write(f"- **{k}**: {v}")

    with tab3:
        st.subheader("영상 기획안 - 인간 예술(진정한 예술) 장면")
        visual = st.text_area("시각 요소 (A)", key="s3_3_v")
        visual_eff = st.text_area("시각 요소 효과", key="s3_3_ve")
        audio = st.text_area("청각 요소 (B)", key="s3_3_a")
        audio_eff = st.text_area("청각 요소 효과", key="s3_3_ae")
        if st.button("채점하기", key="s3_3_btn"):
            result = Set3Grader.grade_3(visual, visual_eff, audio, audio_eff)
            show_result(result)
            st.markdown("**모범 답안 예시**")
            st.write(f"- 시각: {MODEL_ANSWERS['set3']['3']['시각_예시']}")
            st.write(f"- 청각: {MODEL_ANSWERS['set3']['3']['청각_예시']}")


st.sidebar.markdown("---")
st.sidebar.caption("※ 본 채점 로직은 키워드/의미 기반 휴리스틱이며, 최종 판정은 교사 검토를 권장합니다.")