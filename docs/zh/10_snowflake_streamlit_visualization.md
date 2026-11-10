# 第 10 章：Streamlit in Snowflake (SiS) 数据可视化全流程实战 —— 从 API 台账到交互式看板

> 本章依据 **《尚硅谷技术讲义写作规范 (shangguigu-style)》** 深度编撰：开门见山直击本质、去业务化聚焦纯技术、实操步骤带真实回显、直面暗坑实战避险、环境前置零隐式假设。

---

## 引言：开门见山，极简心智模型

在完成了外部 API 数据摄取入仓后，摆在数据工程师面前的下一个核心挑战是：**如何将冷冰冰的 SQL 数据表，快速转化为具备交互能力、即时响应的可视化仪表盘？**

在过去，搭建一个可视化看板通常需要引入沉重的独立 BI 工具（如 Tableau、PowerBI、Metabase）或者自建 Web 全栈应用（Vue/React + FastAPI）。这不仅需要配置繁琐的 ODBC/JDBC 驱动，更致命的是需要**把数据库管理员账号密码配置在外部服务器中**，且数据每次刷新都要在互联网上来回搬运。

Snowflake 推出的 **Streamlit in Snowflake（简称 SiS）** 彻底打破了这一传统架构：它将主流的 Python 数据可视化框架 Streamlit **原生内嵌到了 Snowflake 核心计算引擎中**！

### 极简单明对比：传统外挂 BI vs Streamlit in Snowflake (SiS)

```
【传统外挂 BI 架构（长链路、暴露账号、数据外流）】
  ┌─────────────────┐      ODBC/JDBC 连接池       ┌──────────────────┐     公网传输     ┌─────────────────┐
  │  Snowflake 数仓  │ <═════════════════════════> │  外部 BI 服务器   │ ══════════════> │   最终用户浏览器  │
  └─────────────────┘                              └──────────────────┘                  └─────────────────┘
                                                     ▲ 维护连接账号密码，存在泄露风险
                                                     ▲ 报表加载延迟大，数据脱离数仓安全边界

【Streamlit in Snowflake 原生架构（零外设、零密码、仓内即时渲染）】
  ┌────────────────────────────────────────────────────────────────────────┐
  │ Snowflake 虚拟计算仓库 (Virtual Warehouse)                             │
  │                                                                        │
  │   Streamlit 运行时容器 (Python 3.10)                                   │
  │       │                                                                │
  │       ├───── 1. 免密获取上下文 ───────> session = get_active_session() │
  │       │                                                                │
  │       └───── 2. 仓内内存极速渲染 ─────> st.metric / st.line_chart       │
  │                       │                                                │
  └───────────────────────┼────────────────────────────────────────────────┘
                          ▼ 统一托管于 Snowsight Web 页面中内嵌呈现
                  ┌─────────────────┐
                  │   最终用户浏览器  │ (直接继承用户自身的 Snowflake RBAC 权限)
                  └─────────────────┘
```

- **核心疑问**：在 Snowflake 里写 Streamlit 代码，数据库账号密码写在哪里？用户拖动滑块时，SQL 查询会不会把数仓 Credit 刷爆？如何实现像写代码一样的自动化版本部署？
- **本章目标**：去除任何花哨的业务包装，聚焦纯技术本质。从搭建监控指标底表开始，到编写包含 **KPI 仪表卡片、动态筛选下拉框、营收趋势折线图、实时明细表** 的完整看板，再到通过 SQL/Stage 实现 DevOps 自动化部署与性能防刷治理，一站式全部跑通！

> 📖 **Snowflake & Streamlit 官方权威文档**：
> - [Streamlit in Snowflake (SiS) 架构总览与核心概念](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
> - [SiS 安全模型与必需角色权限 (Privileges Required)](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit#privileges-required-for-streamlit-in-snowflake)
> - [Streamlit 官方 API 手册 (Streamlit Documentation)](https://docs.streamlit.io/develop/api-reference)

---

## 一、环境与前置准备 (Prerequisites)

在开始实操前，请确认具备以下条件：

| 依赖组件 | 规格要求 / 权限 | 作用说明 |
| :--- | :--- | :--- |
| **执行角色** | `ACCOUNTADMIN`（或拥有 `CREATE STREAMLIT`、`CREATE STAGE` 的角色） | 创建内部暂存区 Stage 与 Streamlit 应用对象 |
| **计算仓库** | 任意运行中的 Virtual Warehouse（如 `COMPUTE_WH`） | 负责执行 SQL 查询和渲染 Streamlit Python 代码 |
| **测试数据库与 Schema** | 具备读写权限的库（本教程使用 `DEV_DEMO_DB.API_INTEGRATION`） | 存放业务指标底表及 Streamlit Python 源码文件 |
| **Python 基础** | 熟悉 Python 基础语法与 Pandas 数据操作 | 编写前端交互组件与数据处理逻辑 |

---

## 二、技术架构与数据流向

Streamlit in Snowflake 依托 Snowpark 框架实现了真正的仓内数据零拷贝。其完整的交互流转拓扑如下：

```mermaid
flowchart TD
    subgraph Storage["数据存储层 (Snowflake Storage)"]
        TBL[("业务底表 / API 监控表<br/>(DEV_DEMO_DB.API_INTEGRATION.test_sales_metrics)")]
        STG["内部 Stage 暂存区<br/>(存放 streamlit_app.py 与 environment.yml)"]
    end

    subgraph Warehouse["计算运行时 (Snowflake Compute Warehouse)"]
        CTX["Snowpark Context<br/>session = get_active_session()"]
        CACHE["缓存拦截层<br/>@st.cache_data(ttl=600)"]
        EXEC["SQL 引擎<br/>session.sql('SELECT ...').to_pandas()"]
        UI["Streamlit 渲染引擎<br/>• st.metric (KPI)<br/>• st.selectbox (交互)<br/>• st.line_chart (图表)<br/>• st.dataframe (表格)"]
    end

    subgraph Client["前端呈现 (Snowsight Browser)"]
        BROWSER["用户交互界面<br/>(安全内嵌渲染，零凭据外露)"]
    end

    STG --> UI
    CTX --> EXEC
    TBL --> EXEC
    EXEC --> CACHE
    CACHE --> UI
    UI <== "WebSocket 双向绑定" ==> BROWSER
```

### 深度剖析：存储 Python 脚本在 Stage 会产生费用吗？（Stage 存储 vs Warehouse 算力计费精算）

在采用 Stage 托管 Streamlit 脚本时，几乎所有开发者都会担心：**“把 Python 脚本保存在 Snowflake Stage 里面，究竟会不会持续扣费？会不会像有些云服务一样产生高昂的隐性账单？”**

> [!IMPORTANT] **核心结论：Stage 存储费用几乎为 0（可以完全忽略），真正的费用元凶是背后的 Virtual Warehouse 计算仓库！**

#### 1. 存储账单精算：每月不到 0.000001 美元（微乎其微）
- **计费模式**：Snowflake 内部 Stage 按照底层云厂商标准对象存储容量计费（通常约为 **$23.00 ~ $40.00 / TB / 月**，折合约 $0.000022 / MB / 月）；
- **文件体积**：一个完整的 Streamlit Python 脚本（如 `streamlit_app.py` 或 `streamlit_schema_inspector.py`）通常只有 **5 KB ~ 20 KB**；
- **数学精算**：
  $$\text{月度存储费用} = \frac{20 \text{ KB}}{1024 \times 1024 \times 1024 \text{ KB}} \times \$23.00 \approx \$0.00000043 \text{ 美元 / 月}$$
  哪怕在 Stage 里存放 **100 个** 复杂的 Python 数据看板脚本，整整存放一年的费用也**不到 1 美分（不足 0.07 元人民币）**！

#### 2. 真正扣费元凶：计算虚拟数仓（Virtual Warehouse）
- **计费真相**：Streamlit in Snowflake 不是无服务器静态托管，它依托底层的 **Virtual Warehouse** 作为 Python 容器与 SQL 查询的执行算力；
- **单价标准**：最小规格的 `X-Small` 虚拟仓库每运行 1 小时消耗 **1 个 Credit**（折合标准费率约为 **$2.00 ~ $3.00 / 小时**）；
- **重大扣费陷阱**：Streamlit 前端依托 **WebSocket 长连接保持心跳（Live Heartbeat）**。如果开发者在 Snowsight 网页中打开了看板，下班离开时**没有关闭浏览器标签页**，前端持续向后端发送探活心跳，虚拟仓库可能误以为“当前仍有交互请求”，阻碍自动休眠；
- **空转代价**：仓库一天 24 小时空转将吞噬 24 Credits（约 $48 ~ $72 美元），一周即可将试用账户赠送的 400 美元额度彻底耗尽！

#### 3. 官方原生防线：默认 15 分钟 WebSocket 超时断开与应用休眠机理

针对“用户开着页面不关导致数仓空转”的隐患，Snowflake 官方在平台层设计了一套专门的**会话生命周期与休眠机制（Sleep Timeout）**：

> 📖 **官方权威参考**：
> - [Manage sleep timeout for a Streamlit app using a warehouse runtime](https://docs.snowflake.com/en/developer-guide/streamlit/manage-sleep-timeout)
> - [About Streamlit in Snowflake - WebSocket timeout](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit#websocket-timeout)

- **默认 15 分钟 WebSocket 断开（WebSocket Timeout）**：
  当用户在浏览器中打开 Streamlit 看板时，前端与 Snowflake 后端建立 WebSocket 双向连接。在**账户级别（Account-level）**，默认设定了**约 15 分钟无活动自动超时（Approximately 15 minutes of inactivity）**。一旦超过 15 分钟未检测到任何有效操作，WebSocket 连接会被服务端主动断开，Streamlit 应用自动进入**挂起/休眠（Suspend/Sleep）**状态。
- **活跃行为判定（鼠标移动即可重置）**：
  官方文档明确指出：只要用户的鼠标光标在 Streamlit 画布区域内**晃动或移动（Mouse movement over the app）**，就会被前端探活引擎判定为活跃行为，**瞬间重置 15 分钟倒计时**。
- **浏览器后台标签页限频陷阱（Background Tab Throttling）**：
  如果用户将看板保留在浏览器后台标签页中，现代浏览器（Chrome、Edge）出于省电策略会自动限频后台 JavaScript 定时器与心跳，导致探活信号被中断，从而极易在后台直接触发 15 分钟超时断开。
- **应用级自定义休眠计时器 (`.streamlit/config.toml`)**：
  对于使用虚拟仓库运行的 SiS 应用，开发者无需联系客服，可直接在 Stage 根目录配置 `.streamlit/config.toml`，将休眠时间自定义在 **5 分钟 至 240 分钟（4 小时）** 之间：
  ```toml
  [snowflake.sleep]
  streamlitSleepTimeoutMinutes = 15  # 允许设置 5 ~ 240 分钟
  ```
  *(注：若需修改全账户级别的默认 15 分钟 WebSocket 超时，需联系 Snowflake Support 提单申请)*。

#### 4. 五大防扣费安全锁（The 5 Anti-Burn Safety Locks）
为确保看板开发既流畅又绝对安全，生产实践中必须牢记以下五道防线：
1. **秒级自动休眠**：虚拟仓库强制设置 `AUTO_SUSPEND = 60`（1 分钟无 SQL 查询即刻休眠）；
2. **函数级内存强缓存**：所有读取数仓的函数必须添加 `@st.cache_data(ttl=600)` 10 分钟强缓存，用户在页面上点击切换表名或筛选时，直接从 Python 内存极速返回，**绝不向数仓发起二次 SQL 扫描**；
3. **严格查询限流**：样本数据探查一律增加 `LIMIT 50`，防止全表扫描千万级大表；
4. **配置应用级休眠计时**：在 Stage 根目录 `.streamlit/config.toml` 中配置 `streamlitSleepTimeoutMinutes = 15`，与官方 WebSocket 15 分钟兜底机制紧密联动；
5. **随手关闭标签页与手动休眠**：调试完毕随手关闭网页标签页，必要时执行 `ALTER WAREHOUSE <wh> SUSPEND;` 手动挂起。

---

## 三、核心函数与配置全量字典

在编写 SiS 应用时，必须熟练使用以下核心 API：

> 📖 **官方 API 参考手册**：
> - [get_active_session API Reference (Snowpark Python)](https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/api/snowflake.snowpark.context.get_active_session)
> - [st.cache_data 缓存工作机制与 TTL 规范](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data)
> - [Streamlit Core Widgets & Charts API](https://docs.streamlit.io/develop/api-reference/layout/st.columns)

| 函数 / 语法 | 典型用法 | 生产建议 | 核心作用与底层逻辑 |
| :--- | :--- | :--- | :--- |
| `get_active_session()` | `from snowflake.snowpark.context import get_active_session` | 必须置顶使用 | **免密上下文**：自动捕获当前访问者的 Snowflake RBAC 身份，无需任何密码连接串。 |
| `@st.cache_data` | `@st.cache_data(ttl=600)` | 所有查询必须加缓存 | **防刷锁**：将查询结果缓存指定秒数，用户筛选交互时不再反复扣费查询底表。 |
| `st.metric()` | `st.metric(label="总调用量", value=1240, delta="+12%")` | 适合看板顶部 | **KPI 记分卡**：直观展示关键核心指标及同比/环比浮动。 |
| `st.selectbox()` | `st.selectbox("选择分类", options=['All', 'A', 'B'])` | 用于多维下钻 | **交互下拉菜单**：改变选项后触发应用响应式重新渲染。 |
| `st.line_chart()` | `st.line_chart(df.set_index('DATE')['REVENUE'])` | 必须设置索引列 | **趋势折线图**：原生基于 Altair 渲染的矢量折线图，支持悬浮查看。 |
| `st.dataframe()` | `st.dataframe(df, use_container_width=True)` | 宽屏自适应 | **交互式数据表**：支持列排序、文本搜索、CSV 导出。 |
| `streamlitSleepTimeoutMinutes` | `[snowflake.sleep]` 表配置 | 建议设为 `15`（范围 5~240） | **应用级休眠计时器**：在 `.streamlit/config.toml` 中控制无交互后自动挂起应用的时延，与 WebSocket 15 分钟兜底机制协同防烧钱。 |

---

## 四、双轨制部署实操与逐行命令（DevOps 代码化 vs Web GUI 低代码）

在企业实战中，Streamlit in Snowflake 支持两种完全不同的落地路径，兼顾工程自动化与业务敏捷性：
- **轨道 A（DevOps / CI/CD 代码化工程部署）**：面向数据工程师与平台架构师，通过 Internal Stage + SQL DDL 声明式管理，纳入 Git 与 CI/CD 自动化流水线；
- **轨道 B（Snowsight Web GUI 交互式探索）**：面向业务分析师（BA）与探索性 PoC 场景，直接在 Snowflake Web 界面点选创建，在线调试。

---

### 轨道 A（DevOps / CI/CD 代码化工程部署）：API 监控看板

#### Step 4.A1: 创建业务监控底表与测试数据

在数据库中准备一份纯技术视角的业务监控与 API 调用量模拟表：

```sql
USE DATABASE DEV_DEMO_DB;
USE SCHEMA API_INTEGRATION;

-- 1. 创建技术指标表
CREATE OR REPLACE TABLE test_sales_metrics (
    date DATE,
    category STRING,
    revenue NUMBER(10,2),
    api_call_count INT
);

-- 2. 插入测试数据
INSERT INTO test_sales_metrics VALUES
  ('2026-10-25', 'Electronics', 12500.50, 420),
  ('2026-10-26', 'Clothing', 8400.00, 310),
  ('2026-10-27', 'Groceries', 15200.75, 590),
  ('2026-10-28', 'Home & Kitchen', 6300.20, 180),
  ('2026-10-29', 'Electronics', 14200.00, 480);
```

> **控制台真实回显与底表验证截图**：
> ```text
> Table TEST_SALES_METRICS successfully created.
> number of rows inserted: 5
> ```
>
> 执行 `SELECT * FROM DEV_DEMO_DB.API_INTEGRATION.test_sales_metrics;` 查看准备就绪的 5 条多维度技术指标数据：
>
> ![Snowflake 监控底表数据查询结果](../images/10_step_01_test_sales_metrics_table.png)

---

#### Step 4.A2: 编写完整的 Streamlit 应用源码 (`streamlit_app.py`)

编写应用脚本，实现 KPI 记分卡、动态分类筛选、趋势折线图和实时明细数据表：

```python
# ==============================================================================
# 文件名: streamlit_app.py
# 作用: Streamlit in Snowflake 生产级交互式监控看板 (Route A)
# ==============================================================================
import streamlit as st
from snowflake.snowpark.context import get_active_session

# 1. 页面基础配置 (宽屏沉浸模式)
st.set_page_config(page_title="Snowflake API 监控看板", layout="wide")
st.title("📊 Snowflake API 调用与业务监控实时看板")

# 2. 获取仓内活动会话 (零密码安全鉴权)
session = get_active_session()

# 3. 生产防刷核心：使用 cache_data 对 SQL 查询实施 10 分钟缓存
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

# 4. 侧边栏交互筛选器
st.sidebar.header("🔍 多维数据下钻筛选")
categories = ["全部 (All)"] + sorted(list(raw_df["CATEGORY"].unique()))
selected_category = st.sidebar.selectbox("选择业务分类：", categories)

if selected_category != "全部 (All)":
    df = raw_df[raw_df["CATEGORY"] == selected_category]
else:
    df = raw_df

# 5. 看板顶部核心 KPI 仪表卡片 (Columns 排布)
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

# 6. 图表与明细数据分栏呈现
chart_col, table_col = st.columns([3, 2])

with chart_col:
    st.subheader("📈 每日营收趋势折线图")
    chart_data = df.groupby("DATE")["REVENUE"].sum().reset_index()
    st.line_chart(chart_data.set_index("DATE")["REVENUE"])

with table_col:
    st.subheader("📋 实时底层数据台账")
    st.dataframe(df, use_container_width=True, hide_index=True)

# 7. 手动刷新按钮
if st.button("🔄 清除应用缓存并强制重新拉取"):
    st.cache_data.clear()
    st.rerun()
```

---

#### Step 4.A3: 通过 Stage + SQL 实现自动化 DevOps 部署

通过 **Internal Stage + SQL DDL** 即可将 Streamlit 看板纳入 Git CI/CD 自动化部署流：

> 📖 **官方 DDL 与部署规范**：
> - [CREATE STREAMLIT 语法规范与参数手册](https://docs.snowflake.com/en/sql-reference/sql/create-streamlit)
> - [在 Snowflake 内部 Stage 托管 Streamlit 文件的官方操作指南](https://docs.snowflake.com/en/developer-guide/streamlit/create-streamlit-sql)

```sql
-- 1. 创建内部 Stage (启用目录表索引)
CREATE OR REPLACE STAGE dev_streamlit_stage DIRECTORY = (ENABLE = TRUE);

-- 2. 上传脚本文件 (客户端或终端 PUT 命令)
PUT file:///tmp/streamlit_app.py @DEV_DEMO_DB.API_INTEGRATION.dev_streamlit_stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- 3. 执行 DDL 声明式创建 Streamlit 应用对象
CREATE OR REPLACE STREAMLIT dev_demo_dashboard
  ROOT_LOCATION = '@DEV_DEMO_DB.API_INTEGRATION.dev_streamlit_stage'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = 'COMPUTE_WH'
  COMMENT = '生产级 API 监控与可视化看板 (Route A - DevOps)';
```

> **内部 Stage 文件验证截图**：
>
> 执行 `LIST @DEV_DEMO_DB.API_INTEGRATION.dev_streamlit_stage;` 确认 `streamlit_app.py` 已经成功挂载于数仓暂存区中：
>
> ![Snowflake 内部 Stage 存储的 Streamlit 源码文件](../images/10_step_02_stage_streamlit_file.png)

---

#### Step 4.A4: 验证部署状态与看板运行实景

执行 `SHOW STREAMLITS;` 查询已部署的看板元数据：

```sql
SHOW STREAMLITS LIKE 'DEV_DEMO_DASHBOARD' IN SCHEMA DEV_DEMO_DB.API_INTEGRATION;
```

> **控制台真实查询结果**：
> ```text
> ┌──────────────────────────┬─────────────────────┬───────────────┬─────────────────┬──────────┬────────────┐
> │ created_on               │ name                │ database_name │ schema_name     │ owner    │ warehouse  │
> ├──────────────────────────┼─────────────────────┼───────────────┼─────────────────┼──────────┼────────────┤
> │ 2026-11-02 08:38:52 PST  │ DEV_DEMO_DASHBOARD  │ DEV_DEMO_DB   │ API_INTEGRATION │ SYSADMIN │ COMPUTE_WH │
> └──────────────────────────┴─────────────────────┴───────────────┴─────────────────┴──────────┴────────────┘
> ```

在 Snowflake Snowsight 控制台中，直接点击左侧菜单栏 **`Projects -> Streamlit`**，进入已发布看板列表：

![Snowflake Snowsight Streamlit 应用列表](../images/10_step_03_streamlit_app_list.png)

点击进入看板，即可体验原生内嵌于计算仓库中的实时交互式可视化大屏：

![Streamlit in Snowflake 原生交互式监控看板运行实景](../images/10_step_04_streamlit_dashboard_live.png)

---

### 轨道 B（Snowsight Web GUI 交互式探索）：仓内数据表动态探查器 (Schema Table Inspector)

在很多业务分析或敏捷验证场景中，我们不希望每次都通过终端写命令行或执行 `PUT`。分析师希望**直接在 Snowsight 网页上点选创建应用，并动态扫描数仓内任意 Database / Schema 下的全部数据表，点击表名即可触发数据查询与元数据探查**！

#### Step 4.B1: 基于 Snowsight Web 页面配置创建 Streamlit 应用

1. 登录 Snowsight 网页控制台，点击左侧导航栏 **`Projects -> Streamlit`**；
2. 点击右上角蓝色 **`+ Streamlit App`** 按钮；
3. 在弹出的创建窗口中完成核心参数配置：
   - **App Name**：填写 `SCHEMA_TABLE_INSPECTOR`
   - **App location**：Database 选择 `DEV_DEMO_DB`，Schema 选择 `API_INTEGRATION`
   - **Warehouse**：选择 `COMPUTE_WH`（建议确认已配置 `AUTO_SUSPEND = 60` 秒）
4. 点击右下角 **`Create`** 创建应用对象。

> **Snowsight Web 页面配置与创建弹窗实测截图**：
>
> 弹窗直观展现了应用名称、运行仓库以及应用所属的数据库与模式位置，点击 Create 即在当前数仓内即时初始化 Python 运行环境：
>
> ![Snowsight Web 页面配置创建 Streamlit 弹窗](../images/10_step_04_gui_create_streamlit.png)

---

#### Step 4.B2: 编写仓内数据表动态探查器源码 (`streamlit_schema_inspector.py`)

在 Snowsight 在线编辑器中，将默认模板代码替换为以下经过防刷强化的动态探查器完整源码：

```python
# ==============================================================================
# 应用名称: Snowflake 仓内数据表动态探查器 (Schema Table Inspector)
# 核心特性:
#   1. 动态扫描数据库与 Schema，自动枚举所有数据表
#   2. 交互式点选表名，即时触发元数据 KPI 统计与样本数据预览
#   3. 全量启用 @st.cache_data(ttl=600)，彻底杜绝重复刷新消耗数仓 Credit
#   4. 严格 LIMIT 50 限流保护，防止误扫千万级大表
# ==============================================================================
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# 1. 宽屏沉浸式页面配置
st.set_page_config(
    page_title="Snowflake 仓内数据表动态探查器",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Snowflake 仓内数据表动态探查器 (Schema Table Inspector)")
st.caption("基于 Streamlit in Snowflake 原生运行时 · 零密码免密鉴权 · 10 分钟内存缓存防刷保护")

# 2. 获取仓内活动会话 (零密码安全鉴权)
session = get_active_session()

# 3. 缓存函数：拉取可用数据库列表 (防刷保护)
@st.cache_data(ttl=600)
def get_databases():
    df = session.sql("SHOW DATABASES").to_pandas()
    # 过滤掉 Snowflake 内部只读系统库
    dbs = [row['name'] for _, row in df.iterrows() if not row['name'].startswith('SNOWFLAKE')]
    return sorted(dbs)

# 4. 缓存函数：拉取指定数据库下的 Schema 列表
@st.cache_data(ttl=600)
def get_schemas(db_name):
    df = session.sql(f'SHOW SCHEMAS IN DATABASE "{db_name}"').to_pandas()
    schemas = [row['name'] for _, row in df.iterrows() if row['name'] != 'INFORMATION_SCHEMA']
    return sorted(schemas)

# 5. 缓存函数：动态扫描 Schema 下的所有数据表元数据
@st.cache_data(ttl=600)
def scan_tables_in_schema(db_name, schema_name):
    query = f'SHOW TABLES IN SCHEMA "{db_name}"."{schema_name}"'
    df = session.sql(query).to_pandas()
    if df.empty:
        return pd.DataFrame()
    cols_to_keep = ['name', 'rows', 'bytes', 'owner', 'created_on']
    available_cols = [c for c in cols_to_keep if c in df.columns]
    return df[available_cols]

# 6. 缓存函数：安全预览指定表数据（严格限流 LIMIT 50，防止账单失控）
@st.cache_data(ttl=600)
def preview_table_data(db_name, schema_name, table_name, limit=50):
    query = f'SELECT * FROM "{db_name}"."{schema_name}"."{table_name}" LIMIT {limit}'
    return session.sql(query).to_pandas()

# 7. 侧边栏：多级级联数仓导航
st.sidebar.header("🧭 数仓位置导航")
databases = get_databases()
selected_db = st.sidebar.selectbox("1. 选择数据库 (Database)：", databases, index=0 if 'AIRBNB' not in databases else databases.index('AIRBNB'))

schemas = get_schemas(selected_db)
selected_schema = st.sidebar.selectbox("2. 选择模式 (Schema)：", schemas, index=0 if 'RAW' not in schemas else schemas.index('RAW'))

st.sidebar.divider()

# 8. 动态枚举目标 Schema 下的所有数据表
tables_df = scan_tables_in_schema(selected_db, selected_schema)

if tables_df.empty:
    st.warning(f"在 {selected_db}.{selected_schema} 下未找到任何数据表。")
else:
    table_list = sorted(tables_df['name'].tolist())
    st.sidebar.subheader("📋 扫描到的数据表清单")
    selected_table = st.sidebar.selectbox("3. 选择目标表进行探查：", table_list)

    # 提取当前选中表的元数据指标
    current_meta = tables_df[tables_df['name'] == selected_table].iloc[0]
    row_count = int(current_meta.get('rows', 0)) if pd.notnull(current_meta.get('rows')) else 0
    size_bytes = int(current_meta.get('bytes', 0)) if pd.notnull(current_meta.get('bytes')) else 0
    size_kb = size_bytes / 1024.0
    owner = current_meta.get('owner', 'N/A')

    # 主界面：元数据 KPI 卡片矩阵
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

    # 主界面：安全样本数据实时预览 (前 50 行)
    st.subheader(f"📊 数据表 `{selected_table}` 实时样本数据 (前 50 行预览)")
    with st.spinner("正在加载数据预览..."):
        preview_df = preview_table_data(selected_db, selected_schema, selected_table, limit=50)

    st.dataframe(preview_df, use_container_width=True, hide_index=True)

    # 底部操作栏：数据导出与缓存控制
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
```

---

#### Step 4.B3: 运行实景展示与防刷安全验证

点击右上角 **`Run`** 部署并运行该应用：
- 级联选择数据库 `AIRBNB` 与模式 `RAW`；
- 探查器自动枚举出 `RAW_LISTINGS`、`RAW_HOSTS`、`RAW_REVIEWS` 等全部数据表；
- 点击选择 `RAW_LISTINGS`，主界面毫秒级呈现 4 大 KPI 仪表卡：
  - **总数据行数**：`3,818 行`
  - **存储占用空间**：`671.00 KB`
  - **所有者角色**：`TRANSFORM`
- 下方即时渲染出前 50 行真实房源样本明细（包含 `id`, `listing_url`, `name`, `price`, `minimum_nights` 等真实字段），并提供一键 CSV 导出；
- **成本安全闭环**：得益于 `@st.cache_data(ttl=600)`，用户在不同表之间来回点选时，第二次点击同一张表直接从内存秒级出图，仓库在 60 秒无查询后自动进入挂起（SUSPENDED）状态，零浪费任何额度！

> **Snowflake 仓内数据表动态探查器实景运行大图**：
>
> 页面左侧为级联导航与动态扫描到的表清单，顶部清晰呈现元数据指标卡，中央动态渲染数据样本表格，全流程免密、限流、带缓存：
>
> ![Snowflake 仓内数据表动态探查器运行实景](../images/10_step_05_schema_inspector_running.png)

---

## 五、实战避坑与故障排查（重点）

在实际交付 Streamlit in Snowflake 看板时，以下 3 个暗坑发生频率最高：

---

### `[!WARNING]` 【避坑 1】：每次拖动下拉框整页重跑，数仓 Credit 暴增！

- **真实惨案现场**：
  某工程师搭建了一个销售分析看板，没有配置缓存。当业务部门同事反复点击时间范围、切换下拉筛选项时，每次点击都触发一次庞大的 `SELECT ...` 扫描数千万行底表。当天 Virtual Warehouse 一直保持最大运转，产生了数千美元的账单！
- **根因深度分析**：
  Streamlit 的核心设计哲学是**声明式响应（Reactive Execution）**。页面上的任何交互控件（`selectbox`、`slider`、`button`）一旦被触发，Python 引擎**会从第 1 行到最后 1 行重新完整执行一遍代码**！
- **标准解决方案（防刷铁律）**：
  **凡是涉及 `session.sql()` 的数据加载逻辑，必须抽取为独立函数，并使用 `@st.cache_data(ttl=...)` 修饰！**
  > 📖 **官方缓存最佳实践**：[Streamlit 缓存执行架构与生命周期文档 (Optimize performance with st.cache_data)](https://docs.streamlit.io/develop/concepts/architecture/caching)

  ```python
  # 必须设置合理过期时间 (ttl=300 表示 5 分钟内复用内存缓存)
  @st.cache_data(ttl=300)
  def query_heavy_data():
      return session.sql("SELECT ... FROM large_table").to_pandas()
  ```
  这样，无论用户在页面上点击切换筛选器多少次，数据均从应用内存秒级返回，Virtual Warehouse 甚至不会产生任何新的 SQL 扫描，实现**零延迟响应与零额外费用**！

---

### `[!WARNING]` 【避坑 2】：权限穿透与行级安全 (RLS) 陷阱

- **现象**：业务普通用户访问看板时报错 `Object does not exist or not authorized`，或者普通员工通过看板意外看到了全公司所有人员的薪资数据。
- **根因分析**：
  Streamlit in Snowflake 中的 `session = get_active_session()` 并不是以看板创建者（Owner）的身份运行，而是**严格以当前登录用户的会话上下文（Caller's Rights）执行**！
  > 📖 **官方权限治理文档**：[Streamlit in Snowflake 访问控制与权限共享规范 (Managing privileges for Streamlit apps)](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit#privileges-required-for-streamlit-in-snowflake)

- **标准解法**：
  1. 确保将 Streamlit 应用对象授权给目标业务角色：
     ```sql
     GRANT USAGE ON STREAMLIT dev_demo_dashboard TO ROLE ANALYST_ROLE;
     GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE ANALYST_ROLE;
     GRANT SELECT ON TABLE DEV_DEMO_DB.API_INTEGRATION.test_sales_metrics TO ROLE ANALYST_ROLE;
     ```
  2. 如果底表配置了 Snowflake 动态数据脱敏（Masking Policy）或行级安全策略（Row Access Policy），`get_active_session()` 会原生继承策略，实现不同级别员工“看同一个看板、见不同范围数据”的终极安全治理。

---

### `[!WARNING]` 【避坑 3】：缺少第三方 Python 扩展库

- **现象**：在看板中 `import plotly` 或 `import xgboost` 时，页面报错 `ModuleNotFoundError`。
- **根因分析**：SiS 默认仅预装了 Streamlit、Pandas、Altair 等基础常用库。
  > 📖 **官方依赖配置规范**：[在 Streamlit in Snowflake 中使用 environment.yml 安装 Python 包 (Managing Python packages)](https://docs.snowflake.com/en/developer-guide/streamlit/environment-dependencies)

- **标准解法**：
  在 Stage 根目录下提供一个标准 Conda 环境文件 `environment.yml`：
  ```yaml
  name: sis_env
  channels:
    - snowflake
  dependencies:
    - plotly=5.18.0
    - scikit-learn=1.3.0
  ```
  将其上传至 Stage 目录后，Snowflake 运行时会自动解析并挂载所需依赖包。

---

### `[!CAUTION]` 【避坑 4】：Streamlit 页面保持连接阻断 Warehouse 休眠，导致额度被持续吞噬！

- **真实惨案现场**：
  很多开发者在 Snowsight 网页中建好 Streamlit 看板后，顺手将浏览器标签页留在后台下班离开。几天后再次登录时，发现账户提示免费额度用光（甚至在付费账号下产生意外巨额账单）。
- **根因深度分析**：
  Streamlit in Snowflake 依托浏览器与仓内 Python 容器之间的 **WebSocket 双向长连接（Live Heartbeat）** 进行页面状态保持。
  只要浏览器标签页处于打开且活跃状态，前端就会不断向 Warehouse 发送探活心跳，可能阻碍虚拟仓库及时触发休眠。
- **官方 15 分钟 WebSocket 超时与三层防刷防线**：
  1. **平台级兜底机制：默认约 15 分钟 WebSocket 自动断开**：
     Snowflake 官方在账户级别默认启用了 **15 分钟不活跃超时（WebSocket Timeout）**。如果连续 15 分钟没有鼠标晃动或操作，连接会自动被服务端切断，Streamlit 应用自动挂起（Suspend）。
     > ⚠️ **注意**：如果用户仍在屏幕前晃动鼠标，该 15 分钟倒计时会被不断重置！
  2. **应用级主动配置：`.streamlit/config.toml` 自定义休眠计时器**：
     开发者可以在 Stage 的应用根目录下创建 `.streamlit/config.toml` 文件，显式约束最大空闲时延（建议设为 15 分钟，支持 5~240 分钟）：
     ```toml
     [snowflake.sleep]
     streamlitSleepTimeoutMinutes = 15
     ```
  3. **测试完毕务必关闭标签页，并手动休眠仓库**：
     完成前端页面调试后，随手关闭 Streamlit 浏览器标签页；在 SQL 中可随时手动挂起仓库：
     ```sql
     ALTER WAREHOUSE COMPUTE_WH SUSPEND;
     ```
  4. **配置账户级资源配额熔断器（Resource Monitor，企业防刷最强底线）**：
     为 Streamlit 专用仓库绑定 Resource Monitor，一旦额度达到阈值自动挂起，杜绝账单失控：
     ```sql
     CREATE OR REPLACE RESOURCE MONITOR STREAMLIT_COST_GUARD
         WITH CREDIT_QUOTA = 5
         FREQUENCY = MONTHLY
         START_TIMESTAMP = IMMEDIATELY
         TRIGGERS 
             ON 80 PERCENT DO NOTIFY
             ON 100 PERCENT DO SUSPEND;

     ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = STREAMLIT_COST_GUARD;
     ```

---

## 本章小结

1. **零密码免密集成**：通过 `get_active_session()` 摆脱传统 BI 工具对数据库账号密码的脆弱依赖，全面纳入 Snowflake RBAC 权限体系；
2. **性能与成本守门员**：牢记 Streamlit 响应式重跑机制，将 `@st.cache_data` 作为每个查询函数的必备铠甲，兼顾极致流畅体验与数仓成本可控；
3. **DevOps 自动化交付**：通过 `Stage + PUT + CREATE STREAMLIT` 实现看板代码即基础设施，无缝融入企业 CI/CD 发布体系。

