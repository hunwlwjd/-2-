import re
from dataclasses import dataclass, asdict

MAX = {'a':1,'b':1,'view':2,'multi':3}

def norm(s):
    return re.sub(r'\s+', '', (s or '').lower()).replace('％','%')

def has(s, *terms):
    x=norm(s)
    return any(norm(t) in x for t in terms)

def all_has(s, groups):
    return all(has(s,*g) for g in groups)

def outcome(score, reason, review=False, flags=None):
    return {'score':score,'reason':reason,'review':review,'flags':flags or []}

# A and B are intentionally narrower than a general semantic classifier.
def grade_a(s):
    if not s.strip(): return outcome(0,'미작성')
    if has(s,'기부할 필요성을 느끼지','기부의 필요성을 느끼지','기부 방법을 모르','기부하는 방법을 모르','기부 단체를 믿지','기부단체를 믿지'):
        return outcome(0,'관심 부족이 아닌 다른 원인을 제시함')
    if all_has(s,[['기부'],['관심','무관심','흥미']]) and has(s,'없','부족','적','무관심','낮','떨어','가지지','못','않'):
        return outcome(1,'기부에 대한 관심 부족을 표현함')
    return outcome(0,'기부에 대한 관심 부족이 명확하지 않음',True)

def grade_b(s):
    if not s.strip(): return outcome(0,'미작성')
    if has(s,'소액 기부 방식 확대','소액기부방식확대','크라우드 펀딩 활성화','크라우드펀딩활성화') and not has(s,'다양','여러','여러가지','부담'):
        return outcome(0,'특정 사례에 한정되어 상위 범주의 방안을 제시하지 않음')
    if not has(s,'기부'): return outcome(0,'기부 방식에 관한 답이 아님')
    financial = has(s,'경제적 부담','금전적 부담','비용 부담','돈 부담','돈이 들지','돈을 들이지','비용이 들지','부담 없이','부담없이','부담을 줄','부담을 낮','부담을 덜','적은 비용','적은 금액','큰돈 없이','무료로','돈 없이')
    method = has(s,'방법','방식','수단','형태','경로')
    expand = has(s,'확대','늘리','늘어','다양','많아','마련','제공','활성화','확충','개발','만들')
    if financial and method and expand:
        return outcome(1,'경제적 부담을 줄이는 기부 방법의 확대를 표현함')
    if financial and method:
        return outcome(0,'경제적 부담과 방법은 있으나 확대·마련의 의미가 불명확함',True)
    return outcome(0,'경제적 부담 완화와 다양한 방법 확대라는 상위 개념을 모두 충족하지 않음')

def grade_view(s):
    if not s.strip(): return outcome(0,'미작성',flags=['인식 개선 0/1','참여 촉구 0/1'])
    # Both views are separately scored. The 'can easily practice' construction is a pre-agreed exception.
    misconception = has(s,'어렵고 거창한 것이 아니','어렵고 거창한 일이 아니','어렵고 거창하지 않','어려운 일이 아니','특별한 일이 아니','특별하거나 어려운 행동이 아니','쉽게 할 수 있','쉽게 실천할 수 있','부담스럽지 않','부담을 덜','부담을 줄','부담 없이','부담없이','인식을 바꾸','인식 개선','인식을 개선','어렵게 생각하지','거창하게 생각하지','특별하게 생각하지','어렵다고 생각하지','어려운 행동이라고 생각하지 않')
    everyday = has(s,'일상','생활 속','생활속','평소','누구나','쉽게','가볍게')
    participate = has(s,'기부') and has(s,'실천','참여','동참','기부하','기부를 하','기부해')
    appeal = has(s,'하자','해 보자','해보자','해야 한다','해야한다','필요하다','참여하길','동참하길','실천하길','권하','촉구','권유','동참하자','실천하자')
    # Avoid confusing a proposal for methods with an appeal to readers to donate.
    method_only = has(s,'방법을 제시','방법을 마련','방법을 확대','방식을 확대','방법을 개발','기회를 마련','방안을 마련') and not has(s,'기부에 참여하','기부를 실천하','기부하자','기부해 보자','기부해보자','기부에 동참하')
    exceptional = has(s,'일상에서 쉽고 즐겁게 실천할 수 있는 일','일상에서 쉽고 즐겁게 실천할 수 있','일상에서 쉽게 실천할 수 있는 일') and has(s,'기부')
    first = int(misconception)
    second = int((everyday and participate and appeal and not method_only) or exceptional)
    # Some imperative sentences are lexically unclear; mark rather than assume.
    review = (not second and everyday and participate and not method_only) or (first and has(s,'기부는 반드시 어렵','기부는 거창해야'))
    return outcome(first+second, f'인식 개선 {first}/1, 일상 속 기부 참여 촉구 {second}/1',review,[f'인식 개선 {first}/1',f'참여 촉구 {second}/1'])

OPTIONS = {
 '문자 언어':{'model_role':'기부 실태, 기부하지 않는 이유, 새로운 기부 방식과 기부의 의미를 글로 설명한다.','model_effect':'기부에 대한 인식 개선과 일상 속 기부 참여의 필요성을 논리적으로 이해하도록 돕는다.'},
 '막대그래프(세계 기부 지수)':{'model_role':'국가별 세계 기부 지수와 순위를 수치와 막대그래프로 제시한다.','model_effect':'국가별 세계 기부 지수 순위를 비교하고 우리나라의 상대적으로 낮은 순위를 부각한다.'},
 '꺾은선그래프(기부 경험·의향)':{'model_role':'연도별 우리나라의 기부 참여율과 기부 의향의 변화를 수치와 꺾은선그래프로 제시한다.','model_effect':'기부 참여율과 기부 의향의 변화 추이를 파악하고 우리나라의 낮거나 감소하는 기부 참여율을 강조한다.'},
 '그림 자료(온라인 기부 사례)':{'model_role':'온라인 플랫폼을 활용해 어르신들에게 소화기를 기부하는 크라우드 펀딩 사례를 시각적으로 제시한다.','model_effect':'온라인 기부가 이루어지는 모습이나 크라우드 펀딩 운영 방식을 구체적이고 직관적으로 이해하도록 돕는다.'}
}

def pick_option(s):
    if has(s,'꺾은선','꺽은선','선그래프','선 그래프','선형 그래프','연도별 그래프'): return '꺾은선그래프(기부 경험·의향)'
    if has(s,'막대','세계 기부 지수 그래프','국가별 그래프'): return '막대그래프(세계 기부 지수)'
    if has(s,'사진','이미지','그림','삽화','화면 캡처','화면캡처','스크린샷'): return '그림 자료(온라인 기부 사례)'
    if has(s,'문자 언어','문자언어','글자','텍스트','문장'): return '문자 언어'
    return None

def graph_confusion(s, kind):
    if kind=='막대그래프(세계 기부 지수)':
        return has(s,'연도별','시간에 따른','변화 추이','감소 추이','참여율이 낮','참여율 감소','기부 참여율','기부 의향')
    if kind=='꺾은선그래프(기부 경험·의향)':
        return has(s,'세계 기부 지수','세계기부지수','국가별 순위','국가 간','국가간','79위','다른 나라와 비교')
    return False

def grade_multi(element,role,effect):
    kind=element if element in OPTIONS else pick_option(element)
    if not kind:
        return {'score':0,'element_score':0,'role_score':0,'effect_score':0,'reason':'표현 요소를 식별할 수 없음','review':bool(element.strip()),'kind':None}
    r=role or ''; e=effect or ''
    if kind=='막대그래프(세계 기부 지수)':
        role_ok=has(r,'세계 기부 지수','세계기부지수','국가별 기부 지수','나라별 기부 지수','국가별 순위','기부 지수 순위') and has(r,'제시','나타','보여','표현','비교','표시','정리','드러')
        effect_ok=(has(e,'국가별','나라별','국가 간','국가간','각국','다른 나라','여러 나라') and has(e,'비교','순위','차이','대조')) or (has(e,'우리나라','한국','대한민국') and has(e,'순위','79위','세계 기부 지수') and has(e,'낮','하위','뒤처','저조','부각','강조'))
        if has(e,'우리나라의 기부 수준을 한눈에 파악','우리나라 기부 수준을 한눈에 파악'):effect_ok=False
    elif kind=='꺾은선그래프(기부 경험·의향)':
        role_ok=has(r,'기부 참여','기부 경험','기부 의향','기부율') and has(r,'연도','연도별','시간','변화','추이','2013','2023') and has(r,'제시','나타','보여','표현','표시','정리','드러')
        effect_ok=has(e,'기부 참여','기부 경험','기부 의향','기부율') and has(e,'변화','추이','감소','낮','줄','하락','증감','비교','차이') and has(e,'파악','이해','한눈','강조','부각','드러','알 수','보여','확인','비교')
    elif kind=='그림 자료(온라인 기부 사례)':
        role_ok=has(r,'크라우드 펀딩','크라우드펀딩','온라인 기부','온라인 플랫폼','인터넷 기부','소화기 기부','어르신에게 소화기','노인에게 소화기') and has(r,'제시','나타','보여','표현','담','소개','시각','사진','화면')
        effect_ok=has(e,'크라우드 펀딩','크라우드펀딩','온라인 기부','온라인 플랫폼','기부 방식','기부 과정','기부가 이루어지는') and has(e,'이해','파악','직관','구체','생생','알 수','확인')
        if has(e,'기부 참여 의식','참여 의식','기부에 참여할 수 있다는 인식','참여를 촉구') and not has(e,'방식','과정','이루어지는'):effect_ok=False
    else:
        role_ok=has(r,'기부') and has(r,'실태','현황','이유','원인','방식','방법','의미','필요성','참여율','지수','인식','사례') and has(r,'설명','서술','전달','제시','나열','풀어','알려','기술','소개')
        effect_ok=has(e,'기부') and has(e,'인식','필요성','의미','방식','방법','이유','실태','현황','참여') and has(e,'이해','납득','논리','파악','알 수','설득')
    wrong_role=graph_confusion(r,kind)
    wrong_effect=graph_confusion(e,kind)
    role_score=int(role_ok and not wrong_role)
    effect_score=int(effect_ok and not wrong_effect)
    # If effect explicitly describes another graph, score 0 even if it contains other plausible words.
    review=bool((r.strip() and not role_score and not wrong_role) or (e.strip() and not effect_score and not wrong_effect))
    return {'score':1+role_score+effect_score,'element_score':1,'role_score':role_score,'effect_score':effect_score,'reason':f'{kind}: 표현 요소 1/1, 역할 {role_score}/1, 효과 {effect_score}/1'+(' (그래프 혼동 감지)' if wrong_role or wrong_effect else ''),'review':review,'kind':kind}

def grade_all(a,b,view,element,role,effect):
    parts={'a':grade_a(a),'b':grade_b(b),'view':grade_view(view),'multi':grade_multi(element,role,effect)}
    return {'total':sum(v['score'] for v in parts.values()),'review':any(v['review'] for v in parts.values()),'parts':parts}


# Streamlit user interface
import csv
import io
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title='기부 문화 서답형 채점',page_icon='📝',layout='wide')
st.title('기부 문화 | 서답형 답안 연습·채점')
st.caption('〈기부의 새로운 풍경〉 · 7점 만점 · 의미 요소 중심 규칙 기반 채점(교사 최종 확인)')

with st.expander('문항·모범답안·채점 기준 보기',expanded=False):
    st.markdown('**문항 1 (2점)**: ⓐ 기부에 대한 관심 부족 (1점), ⓑ 경제적 부담 없이 기부할 수 있는 다양한 방법 확대 (1점). ⓑ는 특정 사례(소액 기부, 크라우드 펀딩)만으로 대체 불가.')
    st.markdown('**문항 2 (2점)**: 기부를 어렵고 거창한 일로 여기는 인식을 바꾸고(1점), 일상에서 쉽고 즐겁게 기부에 참여하자(1점). 단순한 기부 방법 마련 주장은 참여 촉구가 아님.')
    st.markdown('**문항 3 (3점)**: 표현 요소(1점) + 해당 요소의 역할(1점) + 같은 요소의 효과(1점).')
    for name,models in OPTIONS.items():
        st.markdown(f'**{name}**  \n역할: {models["model_role"]}  \n효과: {models["model_effect"]}')
    st.info('표현의 토씨가 달라도 의미가 같으면 인정합니다. 다만 서로 다른 그래프의 특징을 혼합하면 해당 역할·효과 점수를 인정하지 않습니다. 규칙이 판단하기 어려운 답안은 교사 검토로 표시됩니다.')

if 'history' not in st.session_state:st.session_state.history=[]

with st.form('grading_form'):
    c1,c2=st.columns(2)
    with c1:
        student=st.text_input('학생 식별자(선택, 실명 대신 번호 권장)')
        a=st.text_area('문항 1 · ⓐ (1점)',height=85)
        b=st.text_area('문항 1 · ⓑ (1점)',height=85)
        view=st.text_area('문항 2 · 필자의 관점 (2점)',height=130)
    with c2:
        element=st.selectbox('문항 3 · 선택한 표현 요소 (1점)',list(OPTIONS))
        role=st.text_area('문항 3 · 표현 요소의 역할 (1점)',height=120)
        effect=st.text_area('문항 3 · 표현 요소의 효과 (1점)',height=120)
    submitted=st.form_submit_button('채점하기',type='primary')

if submitted:
    result=grade_all(a,b,view,element,role,effect)
    st.session_state.last={'student':student,'answers':{'a':a,'b':b,'view':view,'element':element,'role':role,'effect':effect},'result':result}

if 'last' in st.session_state:
    last=st.session_state.last
    result=last['result']
    st.subheader(f'자동 채점 결과: {result["total"]} / 7점')
    if result['review']:st.warning('일부 답안은 규칙만으로 확정하기 어려워 교사 검토가 필요합니다.')
    rows=[{'항목':name,'자동 점수':r['score'],'만점':{'a':1,'b':1,'view':2,'multi':3}[name],'판정 근거':r['reason'],'검토 필요':'예' if r['review'] else '아니요'} for name,r in result['parts'].items()]
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    st.markdown('**교사 최종 점수 수정**')
    with st.form('override_form'):
        cs=st.columns(4)
        scores={}
        for col,key,maxscore in zip(cs,['a','b','view','multi'],[1,1,2,3]):
            with col:scores[key]=st.number_input(f'{key} 최종 점수',0,maxscore,result['parts'][key]['score'],1)
        memo=st.text_input('수정 이유·메모(선택)')
        save=st.form_submit_button('최종 점수 기록')
    if save:
        record={'학생':last['student'],'ⓐ 답안':last['answers']['a'],'ⓑ 답안':last['answers']['b'],'관점 답안':last['answers']['view'],'표현 요소':last['answers']['element'],'역할 답안':last['answers']['role'],'효과 답안':last['answers']['effect'],'자동 총점':result['total'],'교사 최종 총점':sum(scores.values()),'ⓐ':scores['a'],'ⓑ':scores['b'],'관점':scores['view'],'표현':scores['multi'],'교사 메모':memo,'자동 검토 필요':result['review']}
        st.session_state.history.append(record)
        st.success(f'기록 완료: {sum(scores.values())} / 7점')

if st.session_state.history:
    st.divider()
    st.subheader('채점 기록')
    df=pd.DataFrame(st.session_state.history)
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button('CSV 내려받기 (Excel용 UTF-8 BOM)',data=df.to_csv(index=False).encode('utf-8-sig'),file_name='기부_서답형_채점결과.csv',mime='text/csv')
    if st.button('현재 세션 기록 초기화'):
        st.session_state.history=[]
        st.rerun()
st.caption('주의: 채점 기록은 현재 Streamlit 세션에만 저장됩니다. 종료 전 CSV를 내려받으세요. 학생 개인정보를 입력하지 않는 것을 권장합니다.')
