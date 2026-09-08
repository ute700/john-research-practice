import csv
import math
from pathlib import Path

import streamlit as st


# 1. 자료를 숫자로 변환합니다.
def parse_number(value):
    if value is None or value.strip() == "":
        return None, "자료 누락"

    try:
        number = float(value.replace(",", ""))
    except ValueError:
        return None, "숫자 변환 실패"

    if not math.isfinite(number):
        return None, "유효하지 않은 숫자"

    return number, "정상"


# 2. 기업 한 곳의 영업이익률을 계산합니다.
def analyze_company(company):
    revenue, revenue_status = parse_number(company.get("revenue"))
    profit, profit_status = parse_number(company.get("operating_profit"))

    margin = None

    if revenue_status != "정상":
        status = f"매출액: {revenue_status}"
    elif profit_status != "정상":
        status = f"영업이익: {profit_status}"
    elif revenue == 0:
        status = "매출액 0: 계산 불가"
    elif revenue < 0:
        status = "음수 매출액: 원본 검토 필요"
    else:
        margin = profit / revenue * 100
        status = "정상"

    return {
        "기업명": company.get("name", ""),
        "매출액(억원)": revenue,
        "영업이익(억원)": profit,
        "영업이익률(%)": margin,
        "처리 상태": status,
    }


# 3. app.py와 같은 폴더의 CSV 파일을 읽습니다.
st.set_page_config(page_title="기업분석 연습", layout="wide")
st.title("나의 첫 기업자동분석 플랫폼")
st.caption("가상 기업 데이터로 만든 학습용 앱 · 금액 단위: 억 원")

data_path = Path(__file__).parent / "companies.csv"

if not data_path.exists():
    st.error("app.py와 같은 폴더에 companies.csv를 저장해 주세요.")
    st.stop()

with data_path.open("r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    required_columns = {"name", "revenue", "operating_profit"}
    if not required_columns.issubset(reader.fieldnames or []):
        st.error("CSV 첫 줄의 열 이름을 확인해 주세요.")
        st.stop()

    companies = list(reader)

results = []
for company in companies:
    results.append(analyze_company(company))


# 4. 분석 결과와 검색·다운로드 기능을 화면에 표시합니다.
st.subheader("전체 기업 분석 결과")
st.dataframe(results, hide_index=True, use_container_width=True)

minimum_margin = st.number_input(
    "최소 영업이익률(%)",
    min_value=0.0,
    max_value=100.0,
    value=10.0,
    step=1.0,
)

selected = []
for result in results:
    if result["처리 상태"] == "정상":
        if result["영업이익률(%)"] >= minimum_margin:
            selected.append(result)

st.subheader(f"조건검색 결과: {len(selected)}개 기업")

if selected:
    st.dataframe(selected, hide_index=True, use_container_width=True)

    import io

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(selected[0].keys()))
    writer.writeheader()
    writer.writerows(selected)

    st.download_button(
        label="검색 결과 CSV 다운로드",
        data=output.getvalue().encode("utf-8-sig"),
        file_name="screening_results.csv",
        mime="text/csv",
    )
else:
    st.info("조건을 충족하는 기업이 없습니다.")