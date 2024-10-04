import streamlit as st
import pandas as pd

# 초기 상태 설정
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'time_unit' not in st.session_state:
    st.session_state['time_unit'] = None
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = '00:00'
if 'end_time' not in st.session_state:
    st.session_state['end_time'] = '23:59'


# 10분 단위의 시간범위 생성
def generate_time_range(start='00:00', end='23:50', freq='10T'):
    return pd.date_range(start=start, end=end, freq=freq).strftime('%H:%M').tolist()


# 초기 화면 (사용자명 및 시간 단위 선택)
if st.session_state['username'] == '':
    st.title("플래너 앱")

    # 사용자명 입력
    username = st.text_input("사용자명을 입력하세요:")
    # 시간 단위 선택
    time_unit = st.selectbox("플래너 단위를 선택하세요:", ['10분', '30분'])
    # 시작 시간 입력 (10분 단위)
    start_time = st.selectbox("시작 시간을 선택하세요:", generate_time_range(), index=36)  # default 06:00
    # 끝나는 시간 입력 (10분 단위)
    end_time = st.selectbox("끝나는 시간을 선택하세요:", generate_time_range(), index=132)  # default 22:00

    if st.button("확인"):
        if username and time_unit and start_time and end_time:
            st.session_state['username'] = username
            st.session_state['time_unit'] = time_unit
            st.session_state['start_time'] = start_time
            st.session_state['end_time'] = end_time
            st.success(f"어서오세요, {username}님!")

# 사용자명 입력 및 시간 단위 선택이 완료된 후 요일별 계획 입력 화면
if st.session_state['username'] != '' and st.session_state['time_unit']:

    time_freq = '10min' if st.session_state['time_unit'] == '10분' else '30min'

    st.title(f"{st.session_state['username']}님의 플래너")

    # 요일별 계획을 저장할 초기화
    if 'weekly_plan' not in st.session_state:
        time_index = pd.date_range(st.session_state['start_time'], st.session_state['end_time'], freq=time_freq).strftime('%H:%M')
        st.session_state['weekly_plan'] = {
            day: pd.DataFrame(index=time_index, columns=["계획", "색깔"]).fillna('') for day in ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        }

    days_of_week = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    selected_day = st.selectbox("요일을 선택하세요:", days_of_week)

    # 시간 선택 인터페이스
    time_slots = pd.date_range(st.session_state['start_time'], st.session_state['end_time'], freq=time_freq).strftime('%H:%M')

    start_time = st.selectbox("시작 시간을 선택하세요:", time_slots, key='start_time')
    end_time = st.selectbox("종료 시간을 선택하세요:", time_slots, key='end_time')
    daily_task = st.text_input("계획을 입력하세요:")
    task_color = st.color_picker("계획 색상을 선택하세요:", '#FFFF00')  # 기본 색상 노란색

    if st.button("계획 추가"):
        if daily_task and task_color:
            # 입력된 시간 범위 내의 계획을 추가
            start_idx = list(time_slots).index(start_time)
            end_idx = list(time_slots).index(end_time) + 1  # inclusive
            task_center_idx = (start_idx + end_idx) // 2  # 중앙 위치 계산
            for idx, t in enumerate(time_slots[start_idx:end_idx]):
                st.session_state['weekly_plan'][selected_day].loc[t, '계획'] = daily_task if start_idx + idx == task_center_idx else ''
                st.session_state['weekly_plan'][selected_day].loc[t, '색깔'] = task_color
            st.success(f"{selected_day} {start_time}부터 {end_time}까지의 계획이 추가되었습니다!")
        else:
            st.warning("모든 필드를 입력해주세요.")

    # 요일별 계획을 테이블 형태로 시각화
    st.subheader("주간 계획")
    raw_plan_table = pd.concat(st.session_state['weekly_plan'], axis=1)
    raw_plan_table.columns = pd.MultiIndex.from_product([days_of_week, ['계획', '색깔']])

    plan_table = raw_plan_table.xs('계획', axis=1, level=1)

    # 테이블의 색깔을 반영하여 스타일 적용
    chart_colors = raw_plan_table.xs('색깔', axis=1, level=1)

    def apply_color(row):
        color = chart_colors.loc[row.name]
        return [f'background-color: {color[col]}' for col in chart_colors.columns]

    styled_table = plan_table.style.apply(apply_color, axis=1)

    # 스타일링을 위해 각 단위에 따라 다른 높이 적용
    row_height = 10 if st.session_state['time_unit'] == '30분' else 3.33

    st.markdown(
        f"""
        <style>
        .dataframe tbody tr {{
            height: {row_height}px;
        }}
        .dataframe thead th {{
            width: 200px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(styled_table, height=800)

# 이 코드를 app.py 파일로 저장한 다음 Streamlit CLI로 다음 명령어를 실행하면 확인할 수 있습니다:
# streamlit run app.py
