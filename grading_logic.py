"""
서·논술형 문항 자동 채점 로직
세트 1: 사회적 촉진과 억제
세트 2: 정전기의 특징
세트 3: 인공지능이 그린 그림
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


# ============================================================
# 공통 유틸리티
# ============================================================

def normalize(text: str) -> str:
    """공백/특수문자 정리 후 소문자화(한글은 영향 없음)"""
    if text is None:
        return ""
    text = re.sub(r"\s+", " ", text.strip())
    return text.lower()


def contains_any(text: str, keywords: List[str]) -> bool:
    """키워드 리스트 중 하나라도 포함되면 True"""
    norm = normalize(text)
    return any(normalize(kw) in norm for kw in keywords)


def contains_all(text: str, keyword_groups: List[List[str]]) -> Tuple[bool, List[str]]:
    """
    keyword_groups: [[동의어들1], [동의어들2], ...]
    각 그룹에서 하나 이상 포함되어야 전체 통과.
    반환: (전체통과여부, 통과하지 못한 그룹 설명 리스트)
    """
    missing = []
    for i, group in enumerate(keyword_groups):
        if not contains_any(text, group):
            missing.append(" / ".join(group))
    return (len(missing) == 0, missing)


@dataclass
class GradeResult:
    score: float
    max_score: float
    passed: bool
    feedback: List[str] = field(default_factory=list)
    matched: List[str] = field(default_factory=list)
    misconception_flag: bool = False

    def summary(self) -> str:
        status = "✅ 통과" if self.passed else "❌ 미통과/부분점수"
        lines = [f"{status}  ( {self.score} / {self.max_score} 점 )"]
        if self.matched:
            lines.append("【반영된 요소】")
            for m in self.matched:
                lines.append(f"  - {m}")
        if self.feedback:
            lines.append("【피드백】")
            for f in self.feedback:
                lines.append(f"  - {f}")
        if self.misconception_flag:
            lines.append("⚠️ 오개념 의심: 다른 개념의 특성이 혼용된 것으로 보입니다.")
        return "\n".join(lines)


# ============================================================
# 오개념(개념 혼용) 판정용 반의어 쌍 정의
# ============================================================

MISCONCEPTION_PAIRS = {
    "set1_easy_task": ["어렵거나", "도전이 필요한", "충분히 연습", "익숙해질 때까지"],
    "set1_hard_task": ["커피숍", "도서관", "모임", "다른 사람들과 함께"],
    "set2_static": ["전하가 이동함", "전하가 이동한다", "이동하는 전기"],
    "set2_current": ["전하가 이동하지 않", "머물러 있", "정지 상태"],
    "set2_danger_wrong": ["감전", "위험이 있음", "위험하다"],
    "set3_ai_no_emotion_wrong": ["감정이 있다", "감정을 느낀다", "철학이 있다"],
    "set3_human_has_emotion": ["감정이 없다", "철학이 없다"],
}


# ============================================================
# 세트 1: 사회적 촉진과 억제
# ============================================================

class Set1Grader:

    @staticmethod
    def grade_1_1(answer_gap: str) -> GradeResult:
        """서·논술형 1 - ㉠ (쉬운 과제 특성)"""
        groups = [["쉬운", "큰 노력을 들일 필요가 없는", "부담이 적은", "간단한"]]
        ok, missing = contains_all(answer_gap, groups)
        misconception = contains_any(answer_gap, MISCONCEPTION_PAIRS["set1_easy_task"])
        score = 2.0 if ok and not misconception else (1.0 if ok else 0.0)
        fb = []
        if not ok:
            fb.append("‘쉬운 과제/큰 노력이 필요 없는 과제’라는 의미가 필요합니다.")
        if misconception:
            fb.append("어려운 과제(사회적 억제)의 특성이 섞여 있습니다.")
        return GradeResult(score, 2.0, ok and not misconception, fb,
                            matched=["쉬운 과제 의미 포함"] if ok else [],
                            misconception_flag=misconception)

    @staticmethod
    def grade_1_2(answer_gb: str) -> GradeResult:
        """서·논술형 1 - ㉡ (어려운 과제일 때 효율적 방법)"""
        groups = [["충분히 연습", "익숙해질 때까지"],
                   ["혼자", "차분하게", "집중"]]
        ok, missing = contains_all(answer_gb, groups)
        misconception = contains_any(answer_gb, MISCONCEPTION_PAIRS["set1_hard_task"])
        score = 2.0 if ok and not misconception else (1.0 if not misconception and len(missing) <= 1 else 0.0)
        fb = []
        if missing:
            fb.append(f"다음 요소가 빠졌습니다: {', '.join(missing)}")
        if misconception:
            fb.append("‘함께/모임’ 등 사회적 촉진 관련 표현이 섞여 오개념으로 처리됩니다.")
        return GradeResult(score, 2.0, ok and not misconception, fb,
                            matched=["혼자 집중 + 충분한 연습 의미 포함"] if ok else [],
                            misconception_flag=misconception)

    @staticmethod
    def grade_1_3(answer_gg: str) -> GradeResult:
        """서·논술형 1 - ㉢ (관련 심리 현상 명칭)"""
        ok = contains_any(answer_gg, ["사회적 억제"])
        wrong = contains_any(answer_gg, ["사회적 촉진"]) and not ok
        score = 2.0 if ok else 0.0
        fb = [] if ok else ["‘사회적 억제’라는 용어가 필요합니다."]
        if wrong:
            fb.append("‘사회적 촉진’은 반대 개념이므로 오답입니다.")
        return GradeResult(score, 2.0, ok, fb,
                            matched=["사회적 억제 명시"] if ok else [],
                            misconception_flag=wrong)

    @staticmethod
    def grade_2(sentence1: str, sentence2: str) -> GradeResult:
        """
        서·논술형 2 - 이어지는 문장 (1),(2)
        조건: 서로 다른 설명방법 2가지, 지문 내용만 활용, 논리적 흐름
        """
        fb, matched = [], []
        score = 0.0
        max_score = 6.0

        method_signatures = {
            "정의": ["란", "말한다", "뜻한다", "개념"],
            "예시": ["예를 들어", "예컨대", "도서관", "커피숍", "모임"],
            "인과": ["때문에", "그래서", "따라서", "이로 인해"],
            "분석": ["부분", "요소로 이루어"],
            "비교": ["공통점", "~와 달리", "~와 마찬가지로"],
            "대조": ["반면", "달리", "차이", "~지만"],
            "분류": ["나뉘며", "묶이고"],
            "구분": ["나뉘어", "구분"],
        }

        def detect_method(sentence: str) -> List[str]:
            found = []
            explicit = re.findall(r"\(([^)]+)\)\s*$", sentence.strip())
            for e in explicit:
                for m in method_signatures:
                    if m in e:
                        found.append(m)
            for m, sigs in method_signatures.items():
                if contains_any(sentence, sigs) and m not in found:
                    found.append(m)
            return found

        methods1 = detect_method(sentence1)
        methods2 = detect_method(sentence2)

        s1_ok = contains_any(sentence1, ["커피숍", "도서관", "모임"])
        s2_ok = contains_all(sentence2, [["혼자", "차분하게", "집중"]])[0]

        if s1_ok:
            score += 1.5
            matched.append("(1) 쉬운 과제 환경 요소 포함")
        else:
            fb.append("(1)에 ‘커피숍/도서관/모임’ 관련 내용이 필요합니다.")

        if s2_ok:
            score += 1.5
            matched.append("(2) 어려운 과제 환경 요소 포함")
        else:
            fb.append("(2)에 ‘혼자/차분하게/집중’ 관련 내용이 필요합니다.")

        if methods1 and methods2:
            distinct = set(methods1) != set(methods2) or (len(methods1) > 0 and len(methods2) > 0 and methods1[0] != methods2[0])
            if distinct:
                score += 2.0
                matched.append(f"서로 다른 설명 방법 확인: (1)~{methods1}, (2)~{methods2}")
            else:
                score += 0.5
                fb.append("두 문장의 설명 방법이 같아 보입니다. 서로 다른 방법을 사용하세요.")
        else:
            fb.append("설명 방법(용어 또는 그 의미)이 명확히 드러나지 않습니다.")

        external_flag_words = ["유튜브", "챗지피티", "메타인지", "뽀모도로"]
        if contains_any(sentence1 + sentence2, external_flag_words):
            score -= 1.0
            fb.append("지문에 없는 외부 배경지식이 감지되어 감점되었습니다.")

        score = max(0.0, min(score, max_score))
        passed = score >= max_score * 0.8
        return GradeResult(score, max_score, passed, fb, matched)

    @staticmethod
    def grade_3(visual: str, visual_effect: str, audio: str, audio_effect: str) -> GradeResult:
        """서·논술형 3 - 영상 기획안 (어려운 과제 장면)"""
        fb, matched = [], []
        score = 0.0
        max_score = 6.0

        visual_ok = contains_any(visual, ["혼자", "개인", "1인"]) and contains_any(visual, ["집중", "몰입", "조용"])
        audio_ok = contains_any(audio, ["조용", "정적", "무음", "소음 최소", "낮은"])

        misconception_visual = contains_any(visual, ["친구들과", "여러 명", "함께"])
        misconception_audio = contains_any(audio, ["경쾌", "리듬감", "발소리", "책장 넘기는"])

        if visual_ok and not misconception_visual:
            score += 1.5
            matched.append("시각 요소: 혼자/집중 의미 반영")
        else:
            fb.append("시각 요소에 ‘혼자 집중하는 모습’이 드러나야 합니다.")
        if misconception_visual:
            fb.append("⚠ 시각 요소에 ‘여러 사람과 함께’(사회적 촉진 특성)가 섞여 오개념입니다.")

        if audio_ok and not misconception_audio:
            score += 1.5
            matched.append("청각 요소: 조용함/정적 의미 반영")
        else:
            fb.append("청각 요소에 ‘조용함/정적’ 의미가 드러나야 합니다.")
        if misconception_audio:
            fb.append("⚠ 청각 요소에 ‘경쾌한 소리’(사회적 촉진 특성)가 섞여 오개념입니다.")

        effect_ok = contains_any(visual_effect + audio_effect,
                                  ["어려운", "충분히 연습", "익숙해질 때까지", "집중", "차분"])
        if effect_ok:
            score += 3.0
            matched.append("효과 서술에 지문 근거 반영")
        else:
            fb.append("효과 서술에 ‘어려운 과제일수록 혼자 차분히 집중해야 한다’는 지문 근거가 필요합니다.")

        misconception = misconception_visual or misconception_audio
        score = max(0.0, min(score, max_score))
        passed = score >= max_score * 0.8 and not misconception
        return GradeResult(score, max_score, passed, fb, matched, misconception_flag=misconception)


# ============================================================
# 세트 2: 정전기의 특징
# ============================================================

class Set2Grader:

    @staticmethod
    def grade_1_1(answer_ga: str) -> GradeResult:
        """㉠: 정전기의 물 비유"""
        ok = contains_all(answer_ga, [["높은 곳", "높은 위치"], ["고여 있는", "고인"]])[0]
        misconception = contains_any(answer_ga, ["흐르는 물"])
        score = 2.0 if ok and not misconception else 0.0
        fb = [] if ok else ["‘높은 곳에 고여 있는 물’이라는 의미가 필요합니다."]
        if misconception:
            fb.append("‘흐르는 물’은 실생활 전기의 비유이므로 오답입니다.")
        return GradeResult(score, 2.0, ok and not misconception, fb,
                            matched=["높은 곳에 고여있는 물 의미 포함"] if ok else [],
                            misconception_flag=misconception)

    @staticmethod
    def grade_1_2(answer_gb: str) -> GradeResult:
        """㉡: 정전기의 전하 상태"""
        ok = contains_any(answer_gb, ["이동하지 않", "머물러 있", "정지 상태", "정지해"])
        misconception = contains_any(answer_gb, ["전하가 이동함", "전하가 이동한다"]) and not ok
        score = 2.0 if ok else 0.0
        fb = [] if ok else ["‘전하가 이동하지 않고 머물러 있다’는 의미가 필요합니다."]
        if misconception:
            fb.append("‘전하가 이동함’은 실생활 전기 특성이므로 오답입니다.")
        return GradeResult(score, 2.0, ok, fb,
                            matched=["전하 정지 상태 의미 포함"] if ok else [],
                            misconception_flag=misconception)

    @staticmethod
    def grade_1_3(answer_gg: str) -> GradeResult:
        """㉢: 정전기의 위험성 (지문 근거상 '위험하지 않음'이 정답 방향)"""
        ok = contains_any(answer_gg, ["위험하지 않", "위험이 없", "안전"])
        misconception = contains_any(answer_gg, ["감전", "위험이 있", "위험하다"]) and not ok
        score = 2.0 if ok else 0.0
        fb = [] if ok else ["‘전압은 높지만 위험하지 않다’는 결론이 필요합니다. (원본 표 서식 재확인 권장)"]
        if misconception:
            fb.append("‘위험이 있다’는 지문 내용(위험 없음)과 반대되므로 오답입니다.")
        return GradeResult(score, 2.0, ok, fb,
                            matched=["위험하지 않음 명시"] if ok else [],
                            misconception_flag=misconception)

    @staticmethod
    def grade_2(sentence1: str, sentence2: str) -> GradeResult:
        """서·논술형 2 - 정전기 정의 + 대조 문장"""
        fb, matched = [], []
        score = 0.0
        max_score = 6.0

        s1_ok = contains_any(sentence1, ["정지 상태", "머물러 있", "이동하지 않"]) and \
                contains_any(sentence1, ["란", "말한다", "뜻한다"])
        s2_ok = contains_all(sentence2, [["흐르는 물", "고여 있는 물"], ["위험", "감전"]])[0]

        if s1_ok:
            score += 2.5
            matched.append("(1) 정전기 정의(정지 상태) 반영")
        else:
            fb.append("(1)에 ‘정전기란 전하가 정지 상태로 있는 것’이라는 정의가 필요합니다.")

        if s2_ok:
            score += 2.5
            matched.append("(2) 물 비유 + 위험성 대조 반영")
        else:
            fb.append("(2)에 ‘흐르는 물 vs 고여 있는 물’ 비유와 위험성 차이 대조가 필요합니다.")

        if contains_any(sentence1, ["정의"]) or contains_any(sentence2, ["대조", "비교"]):
            score += 1.0
            matched.append("설명 방법 명칭 표기 확인")
        else:
            fb.append("문장 끝에 설명 방법 명칭(정의/대조 등)을 괄호로 표기하세요.")

        score = max(0.0, min(score, max_score))
        passed = score >= max_score * 0.8
        return GradeResult(score, max_score, passed, fb, matched)

    @staticmethod
    def grade_3(visual: str, visual_effect: str, audio: str, audio_effect: str) -> GradeResult:
        """서·논술형 3 - 정전기(고여있는 물) 장면"""
        fb, matched = [], []
        score = 0.0
        max_score = 6.0

        visual_ok_high = contains_any(visual, ["높은 곳", "절벽", "높은 위치"])
        visual_ok_static = contains_any(visual, ["고여", "정지", "흐르지 않", "잔잔"])
        misconception_visual = contains_any(visual, ["폭포", "쏟아", "흘러넘"])

        if visual_ok_high and visual_ok_static and not misconception_visual:
            score += 2.0
            matched.append("시각 요소: 높은 곳 + 정지 상태 모두 반영")
        elif (visual_ok_high or visual_ok_static) and not misconception_visual:
            score += 1.0
            fb.append("‘높은 곳’과 ‘정지 상태(고여있음)’ 중 한 요소만 반영되었습니다.")
        else:
            fb.append("‘높은 곳에 고여있어 흐르지 않는’ 모습이 필요합니다.")
        if misconception_visual:
            fb.append("⚠ ‘흐르는 물’(실생활 전기) 특성이 섞여 오개념입니다.")

        audio_ok = contains_any(audio, ["조용", "정적", "무음", "고요"])
        misconception_audio = contains_any(audio, ["웅장", "큰 소리", "부딪히는"])

        if audio_ok and not misconception_audio:
            score += 2.0
            matched.append("청각 요소: 고요함/정적 반영")
        else:
            fb.append("청각 요소에 ‘고요함/정적’ 의미가 필요합니다.")
        if misconception_audio:
            fb.append("⚠ ‘웅장한 소리’(실생활 전기 특성)가 섞여 오개념입니다.")

        effect_ok = contains_any(visual_effect + audio_effect, ["위험하지 않", "위험이 없", "안전"])
        if effect_ok:
            score += 2.0
            matched.append("효과 서술에 ‘위험하지 않음’ 근거 반영")
        else:
            fb.append("효과 서술에 ‘전압은 높지만 위험하지 않다’는 지문 근거가 필요합니다.")

        misconception = misconception_visual or misconception_audio
        score = max(0.0, min(score, max_score))
        passed = score >= max_score * 0.8 and not misconception
        return GradeResult(score, max_score, passed, fb, matched, misconception_flag=misconception)


# ============================================================
# 세트 3: 인공지능이 그린 그림
# ============================================================

class Set3Grader:

    @staticmethod
    def grade_1_1(answer_ga: str) -> GradeResult:
        """㉠: AI 예술의 올림픽 비유"""
        ok = contains_any(answer_ga, ["완벽하게", "실수 없이", "실수없이"]) and \
             contains_any(answer_ga, ["로봇", "피겨"])
        bonus = contains_any(answer_ga, ["울리지 못", "감동을 주지 못", "울리지 않"])
        score = 2.0 if ok else 0.0
        if ok and bonus:
            score = 2.0
        elif ok:
            score = 1.5
        fb = [] if ok else ["‘로봇이 완벽하게 피겨 스케이팅을 해냄’이라는 내용이 필요합니다."]
        if ok and not bonus:
            fb.append("‘마음을 울리지 못한다’는 대조 요소를 추가하면 더 완전합니다.")
        return GradeResult(score, 2.0, ok, fb,
                            matched=["완벽한 수행 의미 포함"] if ok else [])

    @staticmethod
    def grade_1_2(answer_gb: str) -> GradeResult:
        """㉡: AI 예술 여부 판단 + 근거"""
        reason_ok = contains_any(answer_gb, ["감정"]) and contains_any(answer_gb, ["철학", "이야기"])
        conclusion_ok = contains_any(answer_gb, ["예술로 보기 어렵", "예술이 아니", "예술로 볼 수 없"])
        misconception = contains_any(answer_gb, ["감정이 있다", "감정을 느낀다"])

        score = 0.0
        if reason_ok:
            score += 1.0
        if conclusion_ok:
            score += 1.0

        fb = []
        if not reason_ok:
            fb.append("근거(‘감정을 느끼지 못하고 철학/이야기가 없음’)가 필요합니다.")
        if not conclusion_ok:
            fb.append("결론(‘예술로 보기 어렵다’)이 명확히 드러나야 합니다.")
        if misconception:
            fb.append("⚠ AI가 감정을 느낀다는 서술은 지문과 반대되는 오개념입니다.")

        passed = reason_ok and conclusion_ok and not misconception
        score = 0.0 if misconception else score
        return GradeResult(score, 2.0, passed, fb,
                            matched=["근거+결론 포함"] if passed else [],
                            misconception_flag=misconception)

    @staticmethod
    def grade_1_3(answer_gg: str) -> GradeResult:
        """㉢: AI 예술로서의 가치"""
        v1 = contains_any(answer_gg, ["미술계", "변화"])
        v2 = contains_any(answer_gg, ["범주", "확장", "상징적"])
        misconception = contains_any(answer_gg, ["가치가 없", "의미가 없"])

        score = 0.0
        if v1:
            score += 1.0
        if v2:
            score += 1.0
        score = 0.0 if misconception else score

        fb = []
        if not (v1 and v2):
            fb.append("‘미술계 변화’와 ‘예술 범주 확장(상징적 가치)’ 중 누락된 요소를 보완하세요.")
        if misconception:
            fb.append("⚠ 지문은 ‘상징적 가치가 있다’는 입장이므로 반대 서술은 오답입니다.")

        passed = v1 and v2 and not misconception
        return GradeResult(score, 2.0, passed, fb,
                            matched=[x for x, ok in [("미술계 변화", v1), ("범주 확장/상징적 가치", v2)] if ok])

    @staticmethod
    def grade_2(sentence1: str, sentence2: str) -> GradeResult:
        """서·논술형 2 - 예시문장 + 대조문장"""
        fb, matched = [], []
        score = 0.0
        max_score = 6.0

        s1_ok = contains_any(sentence1, ["에드몽 드 벨라미", "1만 5,000", "43만 2,000"])
        s2_ok = contains_all(sentence2, [["감정", "철학", "경험"], ["감정을 느끼지 못", "철학이나 이야기가 없", "감정이 없"]])[0]

        if s1_ok:
            score += 2.5
            matched.append("(1) 구체적 작품/수치 예시 포함")
        else:
            fb.append("(1)에 ‘에드몽 드 벨라미’ 등 지문의 구체적 사례가 필요합니다.")

        if s2_ok:
            score += 2.5
            matched.append("(2) 인간 vs AI 대조 요소 포함")
        else:
            fb.append("(2)에 인간(감정·철학·경험)과 AI(감정·철학 없음)의 대조가 필요합니다.")

        if contains_any(sentence1, ["예시"]) or contains_any(sentence2, ["대조", "비교"]):
            score += 1.0
            matched.append("설명 방법 명칭 표기 확인")
        else:
            fb.append("문장 끝에 설명 방법 명칭(예시/대조 등)을 표기하세요.")

        external_flag_words = ["딥페이크", "챗지피티", "미드저니", "달리"]
        if contains_any(sentence1 + sentence2, external_flag_words):
            score -= 1.0
            fb.append("지문에 없는 외부 배경지식이 감지되어 감점되었습니다.")

        score = max(0.0, min(score, max_score))
        passed = score >= max_score * 0.8
        return GradeResult(score, max_score, passed, fb, matched)

    @staticmethod
    def grade_3(visual: str, visual_effect: str, audio: str, audio_effect: str) -> GradeResult:
        """서·논술형 3 - 인간 예술(장면2) 시청각 요소"""
        fb, matched = [], []
        score = 0.0
        max_score = 6.0

        creation_process = contains_any(visual, ["경험", "삶", "화가", "창작"])
        audience_reaction = contains_any(visual, ["감동", "울림", "눈물", "몰입"])
        misconception_visual = contains_any(visual, ["완벽하게", "실수 없이", "로봇"])

        if (creation_process or audience_reaction) and not misconception_visual:
            score += 2.0 if (creation_process and audience_reaction) else 1.0
            matched.append("시각 요소: 창작과정/감상자반응 중 반영")
        else:
            fb.append("시각 요소에 ‘화가의 경험이 담긴 창작’ 또는 ‘감상자의 감동 반응’이 필요합니다.")
        if misconception_visual:
            fb.append("⚠ ‘로봇/완벽한 수행’(AI 특성)이 섞여 오개념입니다.")

        audio_ok = contains_any(audio, ["감성", "따뜻", "잔잔", "선율"])
        misconception_audio = contains_any(audio, ["기계음", "메트로놈", "차갑"])

        if audio_ok and not misconception_audio:
            score += 2.0
            matched.append("청각 요소: 감성적 음악 반영")
        else:
            fb.append("청각 요소에 ‘감성적이고 따뜻한 음악’ 의미가 필요합니다.")
        if misconception_audio:
            fb.append("⚠ ‘기계음/메트로놈’(AI 특성)이 섞여 오개념입니다.")

        effect_ok = contains_any(visual_effect + audio_effect,
                                  ["감정", "철학", "경험", "감동", "울림"])
        if effect_ok:
            score += 2.0
            matched.append("효과 서술에 지문 근거(감정/철학/경험) 반영")
        else:
            fb.append("효과 서술에 ‘작가의 감정·철학·경험이 담겨 감동을 준다’는 지문 근거가 필요합니다.")

        misconception = misconception_visual or misconception_audio
        score = max(0.0, min(score, max_score))
        passed = score >= max_score * 0.8 and not misconception
        return GradeResult(score, max_score, passed, fb, matched, misconception_flag=misconception)


# ============================================================
# 선택지별 모범 답안 (표시용)
# ============================================================

MODEL_ANSWERS = {
    "set1": {
        "1_1_ga": "쉬운 과제 / 큰 노력을 들일 필요가 없는 과제",
        "1_2_gb": "충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가짐",
        "1_3_gg": "사회적 억제",
        "2": {
            "쉬운_과제_선택": "(1) 비교적 쉬운 과제나 취미 생활을 할 때는 커피숍이나 도서관에서 하거나, 친숙한 과목이라면 공부 모임을 만들어 다른 사람들과 함께 하는 것이 효율적이다. (예시)",
            "어려운_과제_선택": "(2) 반면 어렵고 복잡한 과제를 할 때는 충분히 연습하여 익숙해질 때까지 차분하게 혼자 집중하는 시간을 갖는 것이 좋다. (대조)"
        },
        "3": {
            "시각_예시": "조용한 개인 독서실에서 혼자 반복 학습하는 모습(클로즈업)",
            "청각_예시": "무음 또는 최소한의 백색소음만 사용"
        }
    },
    "set2": {
        "1_1_ga": "높은 곳에 고여 있는 물",
        "1_2_gb": "전하가 이동하지 않고 머물러 있음",
        "1_3_gg": "위험하지 않음(위험이 없음)",
        "2": {
            "정의_선택": "(1) 정전기란 전하가 정지 상태로 있어 그 분포가 시간적으로 변화하지 않는 전기 현상을 말한다. (정의)",
            "대조_선택": "(2) 흐르는 물은 전하가 이동하여 위험하지만, 고여 있는 물은 전하가 이동하지 않아 위험하지 않다. (대조)"
        },
        "3": {
            "시각_예시": "높은 절벽 위 저수지에 물이 고여 있으나 흐르지 않는 잔잔한 모습",
            "청각_예시": "무음 또는 아주 낮은 정적음"
        }
    },
    "set3": {
        "1_1_ga": "실수 없이 완벽하게 피겨 스케이팅을 해내지만 마음을 울리지 못하는 로봇",
        "1_2_gb": "감정을 느끼지 못하고 독자적인 철학이나 이야기가 없기 때문에 예술로 보기 어렵다",
        "1_3_gg": "기존 미술계에 변화를 가져오고 예술의 범주를 확장할 수 있다는 상징적 가치를 지닌다",
        "2": {
            "예시_선택": "(1) 대표적으로 「에드몽 드 벨라미」는 14~20세기 초상화 1만 5,000점을 토대로 그려져 43만 2,000달러에 판매되었다. (예시)",
            "대조_선택": "(2) 인간의 예술에는 작가의 감정, 철학, 경험이 담기지만, AI는 감정을 느끼지 못하고 철학이 없다는 차이가 있다. (대조)"
        },
        "3": {
            "시각_예시": "화가가 자신의 경험을 담아 그림을 완성하고 관람객이 감동받는 모습",
            "청각_예시": "잔잔한 피아노 선율과 관람객의 옅은 탄성"
        }
    }
}