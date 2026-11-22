.condition-box p{margin:8px 0;line-height:1.75}
.question{font-size:1.08rem;line-height:1.8;margin:22px 0 8px}
.reset-hint{font-size:.78rem;color:#68788c;text-align:right}
div[data-testid="stButton"] button[kind="secondary"]{color:#2472c5;border-color:#bcd9f6;font-size:.78rem}
</style>''',unsafe_allow_html=True)

if 'answer' not in st.session_state: st.session_state.answer=''
if 'submitted' not in st.session_state: st.session_state.submitted=False
if 'result' not in st.session_state: st.session_state.result=None
if 'history' not in st.session_state: st.session_state.history=[]

left,right=st.columns([5.8,1.1],vertical_alignment='bottom')
with left:
    st.markdown('<div class="reset-hint">모든 문제를 제출하면 복습할 내용 탭에서 틀린 개념을 확인할 수 있어요. 답안을 초기화하고 처음부터 다시 풀고 싶다면 다음의 버튼을 누르세요.</div>',unsafe_allow_html=True)
with right:
    if st.button('처음부터 다시 풀기',key='restart',use_container_width=True):
        st.session_state.answer=''
        st.session_state.submitted=False
        st.session_state.result=None
        st.rerun()

st.title('서답형 작성 연습 | 기부의 새로운 풍경')
st.caption('복합양식 텍스트 읽기 · 7점 만점')
problem,review=st.tabs(['문제 풀기','복습할 내용'])
with problem:
    st.markdown('<div class="source-box"><h3>📖 자료 | 기부의 새로운 풍경</h3><p>아래는 제시문의 원문과 그래프, 온라인 기부 사례입니다. 자료를 읽고 질문에 답하세요.</p></div>',unsafe_allow_html=True)
    with st.container(key='source_images'):
        for encoded_image in SOURCE_IMAGES:
            st.image(io.BytesIO(base64.b64decode(encoded_image)),use_container_width=True)
    st.markdown('''<div class="source-box">
    <h3>📋 자료 | 주요 내용 정리 &lt;보기&gt;</h3>
    <p><b>우리나라의 기부 실태</b><br>① 2023년 세계 기부 지수에서 우리나라는 조사 대상 142개국 중 79위임.<br>② 우리나라의 기부 참여율은 2013년 34.6%에서 2023년 23.7%로 감소함.</p>
    <p><b>기부 참여율이 낮은 이유</b><br>① 경제적 여유가 없어서<br>② ⓐ (빈칸)<br>③ 기부 단체에 대한 불신</p>
    <p><b>기부 참여율을 높이기 위한 방안</b><br>① 의미와 재미를 찾을 수 있는 기부 방식 확대<br>② ⓑ (빈칸)<br>③ 기부자와 신뢰를 쌓는 기부 단체의 변화</p>
    <p><b>기부의 의미</b><br>기부에 참여하여 기쁨을 느끼고, 다른 사람에게 도움을 주며, 더 나아가 좋은 사회를 만들어 가는 데 이바지할 수 있음. 이러한 변화는 결국 우리 자신에게 돌아옴.</p>
    </div>''',unsafe_allow_html=True)
    st.markdown('<p class="question"><b>[서답형 1]</b> 위 복합양식 자료에 담긴 관점과 표현 방법을 &lt;조건&gt;에 맞게 서술하시오. <b>[7점, 부분 점수 있음.]</b></p>',unsafe_allow_html=True)
    st.markdown('''<div class="condition-box"><b>조건</b>
    <p>❗ <b>1.</b> 자료의 주요 내용을 정리한 &lt;보기&gt;에서 ⓐ, ⓑ에 들어갈 적절한 말을 찾아 서술할 것. (각 1점, 총 2점)</p>
    <p>❗ <b>2.</b> 이 자료에 내재된 ‘기부’에 대한 필자의 관점을 서술할 것. (2점)</p>
    <p>❗ <b>3.</b> 이 자료에 사용된 복합양식 표현 요소를 한 가지 제시하고, 해당 표현 요소의 역할과 효과를 서술할 것. (3점)</p>
    </div>''',unsafe_allow_html=True)
    st.markdown('#### 답안 작성')
    st.caption('한 칸에 답안을 모두 작성하세요. 자동 채점을 위해 ⓐ, ⓑ, 관점, 표현 요소, 역할, 효과를 구분해 적어 주세요. 별도의 입력칸은 없습니다.')
    answer=st.text_area('서답형 답안',key='answer',height=245,placeholder='ⓐ ...\nⓑ ...\n관점: ...\n표현 요소: ...\n역할: ...\n효과: ...',label_visibility='collapsed')

    def parse_answer(text):
        """Parse labeled portions from a single essay box; ambiguous parsing requires review."""
        import re
        patterns={
            'a':r'(?:ⓐ|㉠|\(a\)|\ba\s*[:：])\s*[:：]?\s*',
            'b':r'(?:ⓑ|㉡|\(b\)|\bb\s*[:：])\s*[:：]?\s*',
            'view':r'(?:필자의\s*관점|관점)\s*[:：]\s*',
            'element':r'(?:표현\s*요소|양식)\s*[:：]\s*',
            'role':r'(?:역할)\s*[:：]\s*',
            'effect':r'(?:효과)\s*[:：]\s*',
        }
        combined=re.compile('|'.join(f'(?P<{k}>{v})' for k,v in patterns.items()),re.I)
        matches=list(combined.finditer(text))
        fields={k:'' for k in patterns}
        for idx,m in enumerate(matches):
            k=m.lastgroup
            v=text[m.end():matches[idx+1].start() if idx+1<len(matches) else len(text)].strip(' \n\t,;。')
            if v: fields[k]=(fields[k]+' '+v).strip()
        # If student writes the element within the role sentence, infer only the named element.
        if not fields['element']:
            fields['element']=pick_option(fields['role']) or ''
        return fields, [k for k in ('a','b','view','role','effect') if not fields[k]]

    if st.button('답안 제출 및 채점',type='primary',use_container_width=True):
        if not answer.strip():
            st.warning('답안을 작성한 뒤 제출해 주세요.')
        else:
            fields,missing=parse_answer(answer)
            r=grade_all(fields['a'],fields['b'],fields['view'],fields['element'],fields['role'],fields['effect'])
            if missing:r['review']=True
            st.session_state.result={'grade':r,'fields':fields,'missing':missing,'original':answer}
            st.session_state.submitted=True
            st.rerun()
    if st.session_state.submitted and st.session_state.result:
        r=st.session_state.result['grade']
        st.success(f'자동 채점 결과: {r["total"]} / 7점')
        if st.session_state.result['missing']:
            st.warning('일부 항목을 구분하지 못했어요. 자동 채점이 누락되었을 수 있으므로 복습할 내용 탭에서 확인해 주세요.')
        st.info('복습할 내용 탭에서 문항별 점수와 보완할 개념을 확인할 수 있어요.')

with review:
    if not st.session_state.submitted or not st.session_state.result:
        st.info('문제 풀기 탭에서 답안을 제출하면 채점 결과와 복습할 개념이 나타나요.')
    else:
        saved=st.session_state.result
        r=saved['grade']; parts=r['parts']
        st.metric('자동 채점 총점',f'{r["total"]} / 7점')
        names={'a':'ⓐ 기부하지 않는 이유','b':'ⓑ 기부 참여율을 높이는 방안','view':'필자의 관점','multi':'복합양식 표현 요소·역할·효과'}
        for k in ('a','b','view','multi'):
            v=parts[k]; cap=MAX[k]
            with st.expander(f'{names[k]} — {v["score"]}/{cap}점',expanded=v['score']<cap):
                st.write(v['reason'])
                if k=='a':st.write('핵심 개념: 기부에 대한 관심 부족. 필요성을 느끼지 못한다는 답은 인정하지 않아요.')
                elif k=='b':st.write('핵심 개념: 경제적 부담을 줄이는 다양한 기부 방식의 확대. 소액 기부나 크라우드 펀딩만 제시하면 범위가 좁아요.')
                elif k=='view':st.write('핵심 개념: 기부에 대한 인식 개선과 일상 속 기부 참여 촉구는 서로 다른 채점 요소예요.')
                else:
                    st.write('핵심 개념: 표현 요소를 정확히 지목하고, 역할과 효과가 같은 자료를 설명해야 해요.')
                    for opt,model in OPTIONS.items():
                        st.markdown(f'**{opt}**')
                        st.write('역할: '+model['model_role'])
                        st.write('효과: '+model['model_effect'])
        if r['review']:st.warning('일부 답안은 자동 판정에 한계가 있어 교사의 확인이 필요해요.')
        with st.expander('교사용 점수 확인 및 수정'):
            with st.form('teacher_adjust'):
                cols=st.columns(4)
                adjusted={}
                for col,k in zip(cols,('a','b','view','multi')):
                    with col:adjusted[k]=st.number_input(names[k],0,MAX[k],int(parts[k]['score']),1)
                memo=st.text_input('교사 메모')
                if st.form_submit_button('최종 점수 기록'):
                    st.session_state.history.append({'답안':saved['original'],'자동 점수':r['total'],'최종 점수':sum(adjusted.values()),'ⓐ':adjusted['a'],'ⓑ':adjusted['b'],'관점':adjusted['view'],'표현':adjusted['multi'],'메모':memo})
                    st.success('최종 점수를 기록했어요.')
        if st.session_state.history:
            st.download_button('채점 기록 CSV 내려받기',pd.DataFrame(st.session_state.history).to_csv(index=False).encode('utf-8-sig'),'기부_채점기록.csv','text/csv')
st.caption('자동 채점은 규칙 기반의 참고 결과입니다. 최종 평가는 교사의 확인이 필요합니다.')
