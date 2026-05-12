import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. 페이지 설정 (웹 브라우저 탭 이름과 아이콘)
st.set_page_config(
    page_title="지역별 문화 인프라 & 소비 분석",
    page_icon="🎭",
    layout="wide"
)

# 2. 데이터베이스 연결 함수
def get_connection():
    db_path = '문화데이터_대시보드DB.db'
    # 파일이 존재하는지 확인 (초보자를 위한 안전장치)
    if not os.path.exists(db_path):
        st.error(f"데이터베이스 파일({db_path})을 찾을 수 없습니다. 폴더 구조를 확인해주세요.")
        return None
    return sqlite3.connect(db_path)

# 3. 데이터 불러오기 함수 (캐싱 처리로 속도 향상)
@st.cache_data
def run_query(query):
    conn = get_connection()
    if conn:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

# --- 대시보드 제목 및 설명 ---
st.title("🎭 지역별 문화 인프라와 공연 소비 패턴 분석")
st.markdown("""
이 대시보드는 공공데이터를 활용하여 **지역별 문화 시설 현황**과 **시민들의 공연 소비 행태**를 분석합니다. 
데이터를 통해 문화 접근성이 소비에 미치는 영향을 확인해 보세요.
""")
st.divider()

# --- [차트 1] 연령대별 공연 장르 선호 분석 ---
st.header("1. 연령대별 공연 장르 선호도")
col1_sql = """
SELECT 연령대, 장르명, COUNT(*) as 예매건수 
FROM 예매데이터 
GROUP BY 연령대, 장르명
ORDER BY 연령대, 예매건수 DESC
"""
df1 = run_query(col1_sql)

if not df1.empty:
    # 시각화: 스택 막대 그래프
    fig1 = px.bar(df1, x="연령대", y="예매건수", color="장르명", 
                 title="연령대별 선호 장르 (스택 막대그래프)",
                 barmode="stack",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1, use_container_width=True)
    
    # SQL 설명 및 인사이트
    with st.expander("사용한 SQL 및 인사이트 보기"):
        st.code(col1_sql, language='sql')
        st.info("""
        **인사이트:**
        - 특정 연령대(예: 2030)에서 대중음악이나 뮤지컬의 비중이 월등히 높게 나타납니다.
        - 고연령층으로 갈수록 클래식이나 국악의 선호도가 증가하는 경향을 확인할 수 있습니다.
        """)

# --- [차트 2] 지역 소득 수준과 평균 결제금액 관계 분석 ---
st.header("2. 소득 수준과 공연 소비 금액의 관계")
col2_sql = """
SELECT m.소득순위, AVG(b.결제금액) as 평균결제금액
FROM 예매데이터 b
JOIN 문화시설매출데이터 m ON b.지역 = m.지역
GROUP BY m.소득순위
ORDER BY m.소득순위
"""
df2 = run_query(col2_sql)

if not df2.empty:
    # 시각화: 산점도
    fig2 = px.scatter(df2, x="소득순위", y="평균결제금액", 
                     title="지역별 소득순위 대비 평균 결제금액",
                     labels={"소득순위": "소득 순위 (낮을수록 고소득)", "평균결제금액": "평균 결제 금액(원)"},
                     size="평균결제금액", color="평균결제금액",
                     color_continuous_scale=px.colors.sequential.Viridis)
    st.plotly_chart(fig2, use_container_width=True)
    
    with st.expander("사용한 SQL 및 인사이트 보기"):
        st.code(col2_sql, language='sql')
        st.info("""
        **인사이트:**
        - 소득 순위가 높은(숫자가 작은) 지역일수록 평균 공연 결제 금액이 높은 양의 상관관계를 보입니다.
        - 이는 고소득 지역의 소비자가 상대적으로 고가의 공연 좌석을 예매하는 경향이 있음을 시사합니다.
        """)

# --- [차트 3] 문화접근성과 공연 소비 관계 분석 ---
st.header("3. 문화접근성에 따른 지역별 공연 소비")
col3_sql = """
SELECT a.지역, a.문화접근성지수, COUNT(b.공연명) as 예매건수, a."2030인구수"
FROM 문화역세권데이터 a
JOIN 예매데이터 b ON a.지역 = b.지역
GROUP BY a.지역
"""
df3 = run_query(col3_sql)

if not df3.empty:
    # 시각화: 버블 차트
    fig3 = px.scatter(df3, x="문화접근성지수", y="예매건수", 
                     size="2030인구수", color="지역", hover_name="지역",
                     title="문화접근성지수 vs 예매건수 (버블 크기: 2030 인구수)",
                     size_max=60)
    st.plotly_chart(fig3, use_container_width=True)
    
    with st.expander("사용한 SQL 및 인사이트 보기"):
        st.code(col3_sql, language='sql')
        st.info("""
        **인사이트:**
        - 문화접근성지수가 높은 지역일수록 실제 공연 예매 건수가 활발하게 일어납니다.
        - 특히 2030 인구수가 많은 지역(버블이 큰 곳)에서 접근성 대비 소비 효율이 극대화되는 모습을 보입니다.
        """)

# 푸터 정보
st.divider()
st.caption("데이터 출처: 공공데이터포털 | 제작: 초보 데이터 분석가")