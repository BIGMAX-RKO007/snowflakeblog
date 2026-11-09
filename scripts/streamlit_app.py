import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Snowflake API 监控看板", layout="wide")
st.title("📊 Snowflake API 调用与业务监控实时看板")

session = get_active_session()

@st.cache_data(ttl=600)
def load_data():
    sql = """
        SELECT 
            date,
            category,
            revenue,
            api_call_count
        FROM DEV_DEMO_DB.API_INTEGRATION.test_sales_metrics
        ORDER BY date ASC
    """
    return session.sql(sql).to_pandas()

raw_df = load_data()

st.sidebar.header("🔍 多维数据下钻筛选")
categories = ["全部 (All)"] + sorted(list(raw_df["CATEGORY"].unique()))
selected_category = st.sidebar.selectbox("选择业务分类：", categories)

if selected_category != "全部 (All)":
    df = raw_df[raw_df["CATEGORY"] == selected_category]
else:
    df = raw_df

kpi1, kpi2, kpi3 = st.columns(3)
total_revenue = df["REVENUE"].sum()
total_api_calls = df["API_CALL_COUNT"].sum()
avg_revenue_per_call = total_revenue / total_api_calls if total_api_calls > 0 else 0

with kpi1:
    st.metric(label="总营收金额 (USD)", value=f"${total_revenue:,.2f}", delta="+8.5%")
with kpi2:
    st.metric(label="外部 API 调用总次数", value=f"{total_api_calls:,}", delta="+120")
with kpi3:
    st.metric(label="单次调用产出比", value=f"${avg_revenue_per_call:.2f}")

st.divider()

chart_col, table_col = st.columns([3, 2])

with chart_col:
    st.subheader("📈 每日营收趋势折线图")
    chart_data = df.groupby("DATE")["REVENUE"].sum().reset_index()
    st.line_chart(chart_data.set_index("DATE")["REVENUE"])

with table_col:
    st.subheader("📋 实时底层数据台账")
    st.dataframe(df, use_container_width=True, hide_index=True)

if st.button("🔄 清除应用缓存并强制重新拉取"):
    st.cache_data.clear()
    st.rerun()
