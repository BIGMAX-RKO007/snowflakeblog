import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# ==============================================================================
# 应用名称: Snowflake 仓内数据表动态探查器 (Schema Table Inspector)
# 核心特性:
#   1. 动态扫描数据库与 Schema，自动枚举所有数据表
#   2. 交互式点选表名，即时触发数据预览与元数据卡片
#   3. 全量启用 @st.cache_data(ttl=600)，彻底杜绝重复刷新消耗数仓 Credit
# ==============================================================================

# 1. 宽屏沉浸式页面配置
st.set_page_config(
    page_title="Snowflake 仓内数据表动态探查器",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Snowflake 仓内数据表动态探查器 (Schema Table Inspector)")
st.caption("基于 Streamlit in Snowflake 原生运行时 · 零密码免密鉴权 · 10 分钟内存缓存防刷保护")

# 2. 获取仓内当前活动会话
session = get_active_session()

# 3. 缓存函数：拉取可用数据库列表
@st.cache_data(ttl=600)
def get_databases():
    df = session.sql("SHOW DATABASES").to_pandas()
    # 过滤掉系统内部库
    dbs = [row['name'] for _, row in df.iterrows() if not row['name'].startswith('SNOWFLAKE')]
    return sorted(dbs)

# 4. 缓存函数：拉取指定数据库下的 Schema 列表
@st.cache_data(ttl=600)
def get_schemas(db_name):
    df = session.sql(f"SHOW SCHEMAS IN DATABASE \"{db_name}\"").to_pandas()
    schemas = [row['name'] for _, row in df.iterrows() if row['name'] != 'INFORMATION_SCHEMA']
    return sorted(schemas)

# 5. 缓存函数：动态扫描 Schema 下的所有数据表元数据
@st.cache_data(ttl=600)
def scan_tables_in_schema(db_name, schema_name):
    query = f"SHOW TABLES IN SCHEMA \"{db_name}\".\"{schema_name}\""
    df = session.sql(query).to_pandas()
    if df.empty:
        return pd.DataFrame()
    # 提取核心列
    cols_to_keep = ['name', 'rows', 'bytes', 'owner', 'created_on']
    available_cols = [c for c in cols_to_keep if c in df.columns]
    return df[available_cols]

# 6. 缓存函数：安全预览指定表数据（严格限流 LIMIT 50）
@st.cache_data(ttl=600)
def preview_table_data(db_name, schema_name, table_name, limit=50):
    query = f"SELECT * FROM \"{db_name}\".\"{schema_name}\".\"{table_name}\" LIMIT {limit}"
    return session.sql(query).to_pandas()

# 侧边栏：数据库与 Schema 导航
st.sidebar.header("🧭 数仓位置导航")
databases = get_databases()
selected_db = st.sidebar.selectbox("1. 选择数据库 (Database)：", databases, index=0 if 'AIRBNB' not in databases else databases.index('AIRBNB'))

schemas = get_schemas(selected_db)
selected_schema = st.sidebar.selectbox("2. 选择模式 (Schema)：", schemas, index=0 if 'RAW' not in schemas else schemas.index('RAW'))

st.sidebar.divider()

# 动态拉取数据表列表
tables_df = scan_tables_in_schema(selected_db, selected_schema)

if tables_df.empty:
    st.warning(f"在 {selected_db}.{selected_schema} 下未找到任何数据表。")
else:
    table_list = sorted(tables_df['name'].tolist())
    st.sidebar.subheader("📋 扫描到的数据表清单")
    selected_table = st.sidebar.selectbox("3. 选择目标表进行探查：", table_list)

    # 提取当前选中表的元数据
    current_meta = tables_df[tables_df['name'] == selected_table].iloc[0]
    row_count = int(current_meta.get('rows', 0)) if pd.notnull(current_meta.get('rows')) else 0
    size_bytes = int(current_meta.get('bytes', 0)) if pd.notnull(current_meta.get('bytes')) else 0
    size_kb = size_bytes / 1024.0
    owner = current_meta.get('owner', 'N/A')

    # 主界面：元数据 KPI 卡片
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.metric(label="当前探查数据表", value=selected_table)
    with kpi_col2:
        st.metric(label="总数据行数", value=f"{row_count:,} 行")
    with kpi_col3:
        st.metric(label="存储占用空间", value=f"{size_kb:.2f} KB")
    with kpi_col4:
        st.metric(label="所有者角色 (Owner)", value=str(owner))

    st.divider()

    # 数据实时预览
    st.subheader(f"📊 数据表 `{selected_table}` 实时样本数据 (前 50 行预览)")
    with st.spinner("正在加载数据预览..."):
        preview_df = preview_table_data(selected_db, selected_schema, selected_table, limit=50)

    st.dataframe(preview_df, use_container_width=True, hide_index=True)

    # 底部操作栏：数据下载与缓存刷新
    btn_col1, btn_col2, _ = st.columns([2, 2, 6])
    with btn_col1:
        csv_data = preview_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 下载前 50 行样本为 CSV",
            data=csv_data,
            file_name=f"{selected_table}_sample.csv",
            mime="text/csv",
            use_container_width=True
        )
    with btn_col2:
        if st.button("🔄 清除缓存并重新扫描", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

# 底部成本安全警示横幅
st.info("💡 **成本防刷安全保障**：所有元数据与数据查询均配置 `@st.cache_data(ttl=600)` 10 分钟强缓存，用户切换表或筛选时直接读取内存，不触发虚拟仓库唤醒计费；虚拟仓库设定 `AUTO_SUSPEND = 60` 秒无操作自动休眠。")
