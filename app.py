import streamlit as st
import pandas as pd
import pyodbc

st.set_page_config(layout="wide")

@st.cache_resource
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";PWD="
        + st.secrets["password"]
    )

conn = init_connection()

@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [column[0] for column in cur.description]  # 컬럼 이름 가져오기
        rows = cur.fetchall()  # 결과 가져오기
        return rows, columns  # 결과와 컬럼 이름 반환

# 사용자 입력을 위한 Streamlit 위젯
# st.title("CJ 3PL")


st.markdown(
    """
    <style>
    .box {
        padding: 20px;
        border-radius: 5px;
        color: white;
        margin-bottom: 10px;
    }
    .box1 {
        background-color: black; /* 검정색 */
    }
    .box2 {
        background-color: #2196F3; /* 파란색 */
    }
    .box3 {
        background-color: #FF9800; /* 오렌지색 */
    }
    .custom-table {
        border-collapse: collapse; /* 테두리 겹침 방지 */
        width: 100%; /* 전체 너비 사용 */
    }
    .custom-table th, .custom-table td {
        border: 1px solid #4CAF50; /* 원하는 테두리 색상 */
        padding: 8px; /* 셀 패딩 */
    }
    </style>
    """, unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["3PL Board", "Tab 2"])

with tab1:
    # 세로로 구역 나누기
    col1, col2, col3 = st.columns([1.2, 1, 1])

    with col1:
        
        st.markdown('<div class="box box1">Delivery Data</div>', unsafe_allow_html=True)

        # 쿼리 실행
        query = """
        SELECT * from openquery(CJ_3PL, '
        SELECT 
            CASE
                WHEN STR_EXT01 = ''Delivery01'' THEN ''CJ택배''
                WHEN STR_EXT01 = ''Delivery02'' THEN ''내일 꼭! 오네''
                WHEN STR_EXT01 = ''Delivery03'' THEN ''KEP수원''
                WHEN STR_EXT01 = ''Delivery04'' THEN ''LF DC1(직배송)''
                WHEN STR_EXT01 = ''Delivery05'' THEN ''SK기흥''
                WHEN STR_EXT01 = ''Delivery06'' THEN ''경동택배''
                WHEN STR_EXT01 = ''Delivery07'' THEN ''나비MRO(오산)''
                WHEN STR_EXT01 = ''Delivery08'' THEN ''로젠택배''
                WHEN STR_EXT01 = ''Delivery09'' THEN ''서브원산시배송''
                WHEN STR_EXT01 = ''Delivery10'' THEN ''서브원평택물류''
                WHEN STR_EXT01 = ''Delivery11'' THEN ''에버랜드배송''
                WHEN STR_EXT01 = ''Delivery12'' THEN ''직배''
                WHEN STR_EXT01 = ''Delivery13'' THEN ''직배(고객물류수령)''
                WHEN STR_EXT01 = ''Delivery14'' THEN ''직배(용차)''
                WHEN STR_EXT01 = ''Delivery15'' THEN ''천일택배''
                WHEN STR_EXT01 = ''Delivery16'' THEN ''한국니토옵티컬''
                WHEN STR_EXT01 = ''Delivery17'' THEN ''GS리테일''
                ELSE ''기타 배송사''
            END AS 배송사,
            COUNT(*) AS 연동라인수, 
            SUM(CASE WHEN TRANSSTATE = ''Y'' THEN 1 ELSE 0 END) AS CJ확인,
            SUM(CASE WHEN TRANSSTATE = ''N'' THEN 1 ELSE 0 END) AS CJ미확인,
            SUM(CASE WHEN RSLTSTATE = ''Y'' THEN 1 ELSE 0 END) AS CJ출고,
            SUM(CASE WHEN READSTATE = ''Y'' THEN 1 ELSE 0 END) AS CLOUD전송,
            SUM(CASE WHEN RSLTSTATE = ''N'' THEN 1 ELSE 0 END) AS CJ미출고,
            ROUND(SUM(CASE WHEN RSLTSTATE = ''Y'' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS 진척률
        FROM P1_V_ORDERS
        WHERE SUBSTR(ADDDATE, 1, 8) BETWEEN ''20241001'' AND ''20241017''
        GROUP BY STR_EXT01
        ORDER BY STR_EXT01
        ')
        """
        # 쿼리 실행
        rows, columns = run_query(query)

        # 결과를 리스트에 담기
        data = []
        for row in rows:
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            data.append(row_dict)

        df = pd.DataFrame(data)

        
        
        st.dataframe(df, height=600)




    with col2:
        st.markdown('<div class="box box2">구역 2: 통계 정보</div>', unsafe_allow_html=True)
        st.write("여기에 통계 정보를 추가하세요.")

    with col3:
        st.markdown('<div class="box box3">구역 3: 추가 정보</div>', unsafe_allow_html=True)
        st.write("여기에 추가 정보를 입력하세요.")



with tab2:
    # 첫 번째 탭에 내용 추가
    st.header("Tab 2")
    st.write("여기에 Tab 2의 내용을 추가하세요.")

    # 현재 날짜를 기본값으로 설정
    today = pd.to_datetime("today").date()

    # 두 개의 열을 생성하여 입력 필드를 배치
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = st.columns(12)

    with col1:
        start_date = st.date_input("시작 날짜 입력", value=pd.to_datetime("2024-07-22"))  # 기본 날짜 설정
    with col2:
        end_date = st.date_input("종료 날짜 입력", value=today)  # 기본 날짜 설정


    query = """
    SELECT * from openquery(CJ_3PL, '
        SELECT SUBSTR(ADDDATE, 1, 8) AS 전송일,
                COUNT(*) AS 연동라인수, 
                SUM(CASE WHEN TRANSSTATE = ''Y'' THEN 1 ELSE 0 END) AS CJ확인,
                SUM(CASE WHEN TRANSSTATE = ''N'' THEN 1 ELSE 0 END) AS CJ미확인,
                SUM(CASE WHEN RSLTSTATE = ''Y'' THEN 1 ELSE 0 END) AS CJ출고,
                SUM(CASE WHEN READSTATE = ''Y'' THEN 1 ELSE 0 END) AS CLOUD전송,
                COUNT(CASE WHEN RSLTSTATE = ''Y'' AND SHIPQTY != ''0'' THEN 1 END) AS 매출,
                COUNT(CASE WHEN RSLTSTATE = ''Y'' AND SHIPQTY = ''0'' THEN 1 END) AS 결품,
                SUM(CASE WHEN RSLTSTATE = ''N'' THEN 1 ELSE 0 END) AS CJ미출고
        FROM P1_V_ORDERS
        GROUP BY SUBSTR(ADDDATE, 1, 8)
        ORDER BY SUBSTR(ADDDATE, 1, 8) DESC
    ')
    """

    # 쿼리 실행
    rows, columns = run_query(query)

    # 결과를 리스트에 담기 (각 행을 딕셔너리로 변환)
    data = []
    for row in rows:
        row_dict = {columns[i]: row[i] for i in range(len(columns))}  # 각 행을 딕셔너리로 변환
        data.append(row_dict)  # 딕셔너리를 리스트에 추가

    # 리스트를 DataFrame으로 변환
    df = pd.DataFrame(data)

    # 퍼센트 계산 (예: CJ확인 비율)
    df['3PL출고율'] = (df['CJ출고'] / df['연동라인수'] * 100).round(1)

    # 퍼센트 값에 '%' 붙이기
    df['3PL출고율'] = df['3PL출고율'].astype(str) + '%'  # 문자열로 변환하고 '%' 추가

    # 결과를 Streamlit으로 표시
    st.dataframe(df)

    # 퍼센트 비율을 시각화
    st.bar_chart(df.set_index('전송일')['3PL출고율'])



