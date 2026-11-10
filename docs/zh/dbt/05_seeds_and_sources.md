# 第 05 章：dbt 种子（Seeds）与数据源（Sources）实战 —— 静态字典表版本化、外部源抽象解耦与数据新鲜度监控（Freshness）

> 本章依据 **《尚硅谷技术讲义写作规范 (shangguigu-style)》** 深度编撰：开门见山直击本质、去业务化聚焦纯技术、实操步骤带真实回显、直面暗坑实战避险、环境前置零隐式假设。

---

## 引言：开门见山，极简心智模型

在现代数据仓库架构中，上游数据流入分析平台通常分为两大典型阵营：
1. **外部源数据（Sources）**：由业务交易系统、第三方 SaaS 工具（如 Fivetran、Airbyte、Kafka CDC 等）持续抽取并载入到数仓 RAW 层的庞大表集合。
2. **静态维度与辅助数据（Seeds）**：如行政区划代码表、国家货币对照表、业务枚举字典表、天体历法日期表等体积小（通常在几百行至几万行之间）、极少变动的离线 CSV 文件。

在传统数仓开发中，这两类数据的处理往往漏洞百出：
- **痛点 1（硬编码与架构强耦合）**：分析人员直接在 SQL 视图中硬编码物理表全路径（如 `FROM AIRBNB.RAW.RAW_LISTINGS`）。一旦上游业务库分表改名、数据库迁移或 Schema 重命名，所有下游 SQL 瞬间瘫痪，修改必须地毯式全库检索替换；
- **痛点 2（静态字典表丢失版本控制）**：字典数据往往由 DBA 在数据库客户端临时跑 `INSERT INTO ... VALUES (...)`，脱离了 Git 代码仓库版本治理，没人知道生产表何时被谁篡改过；
- **痛点 3（“静默坏死”的数据断流）**：第三方抽取工具挂掉或外部 API 限制频次时，数仓内的底层表停止刷新。然而下游报表与 BI 仪表盘由于缺乏监控机制，依然照常调度跑出空数据或陈旧数据，直到业务决策人员发现报表数字不对才被动排查！

**dbt 提供了两大优雅解法 —— `Seeds` 与 `Sources`，彻底闭环了上述痛点**：
- **`Seeds`**：将小型 CSV 纳入 Git 仓库实施版本化，执行 `dbt seed` 一键自动在数据库中建表、推断类型并灌入数据；
- **`Sources`**：在 `YAML` 中对原始库表建立逻辑抽象层，模型内使用 `&#123;&#123; source('source_name', 'table_name') &#125;&#125;` 动态解耦；
- **`Source Freshness`**：通过 `dbt source freshness` 动态嗅探数据源最新业务时间戳，设置警戒阈值（`warn_after` / `error_after`），在 CI/CD 或日常调度中第一时间阻断脏旧数据！

### 极简单明对比：Seeds vs Sources 核心心智模型

| 维度对比 | 种子 (Seeds) | 数据源 (Sources) |
| :--- | :--- | :--- |
| **数据源头** | 项目代码库内的静态 `.csv` 文件 | 外部 ETL/ELT 工具写入数仓的现有物理表 |
| **存储位置** | dbt 项目中的 `seeds/` 目录 | Snowflake 远端数据库（如 `AIRBNB.RAW`） |
| **数据体量** | 小型静态数据（强烈建议 < 100MB / < 10万行） | 海量流水事实、业务系统主数据表 |
| **dbt 角色** | **数据生成者与加载者**（负责建表与插入） | **数据消费者与观察者**（仅做元数据声明与治理） |
| **执行命令** | `dbt seed`（建表并 `INSERT` 数据） | `dbt source freshness`（检测数据新鲜度） |
| **引用语法** | `&#123;&#123; ref('seed_name') &#125;&#125;` | `&#123;&#123; source('source_name', 'table_name') &#125;&#125;` |

```
【dbt Seeds & Sources 完整血缘流水线架构】

 ┌────────────────────────────────────────┐
 │ 外部输入 A: 静态 CSV 字典 (Git 版本化) │
 │ seeds/seed_full_moon_dates.csv         │
 └───────────────────┬────────────────────┘
                     │ dbt seed
                     ▼
 ┌────────────────────────────────────────┐
 │ Snowflake 物理表 (Seed 表)             │
 │ AIRBNB.DEV.SEED_FULL_MOON_DATES (272行)│
 └───────────────────┬────────────────────┘
                     │ {{ ref('seed_full_moon_dates') }}
                     ▼
 ┌────────────────────────────────────────┐      ┌────────────────────────────────────────┐
 │ Mart 业务集市层模型                    │ <─── │ Core 核心事实层模型                    │
 │ models/mart/mart_fullmoon_reviews.sql  │      │ models/fct/fct_reviews.sql             │
 └────────────────────────────────────────┘      └───────────────────┬────────────────────┘
                                                                     │ {{ ref('src_reviews') }}
                                                                     ▼
                                                 ┌────────────────────────────────────────┐
                                                 │ Staging 暂存层 (逻辑解耦)              │
                                                 │ models/src/src_reviews.sql             │
                                                 └───────────────────┬────────────────────┘
                                                                     │ {{ source('airbnb', 'reviews') }}
                                                                     ▼
                                                 ┌────────────────────────────────────────┐
                                                 │ 抽象数据源定义 (models/sources.yml)    │
                                                 │ • identifier: raw_reviews              │
                                                 │ • loaded_at_field: date                │
                                                 │ • freshness: warn(1h) / error(24h)     │
                                                 └───────────────────┬────────────────────┘
                                                                     │ 物理指向
                                                                     ▼
                                                 ┌────────────────────────────────────────┐
                                                 │ 外部输入 B: 原始库 (Snowflake RAW)     │
                                                 │ AIRBNB.RAW.RAW_REVIEWS (409,697行)     │
                                                 └────────────────────────────────────────┘
```

---

## 第一部分：种子（Seeds）机制与静态数据版本化实战

### 1. 什么是 dbt Seed？
Seed 是指存放在 dbt 工程 `seeds/` 目录下的 `.csv` 文件。通过执行 `dbt seed` 命令：
1. dbt 会自动在目标 Schema（`AIRBNB.DEV`）下执行 `CREATE OR REPLACE TABLE ...`；
2. 依据 CSV 第一行的表头作为字段名，自动推断每列的数据类型（如整型、字符串、日期）；
3. 将 CSV 中的行记录批量加载（`INSERT`）进该物理表中。

> [!WARNING]
> **反模式警示**：不要使用 Seeds 加载原始业务大表或高频变动的交易数据！CSV 不适合做大数据量存储，大文件会导致 Git 仓库臃肿变慢。Seeds 的唯一正统使命是：**小巧、静态的业务对照表**。

### 2. 业务背景：验证“满月对租客情绪影响”假设
在 Airbnb 运营分析中，管理层提出一个假说：“满月前后，租客的睡眠质量与情绪易受影响，进而给出更多负面差评”。为了验证该假说，我们需要将过去 10 年的天文学满月日期表导入数仓，并与评价事实表进行日期对齐。

### 3. 下载满月历法种子文件
在工程根目录下执行 PowerShell 命令，将包含 272 条满月日期的 CSV 下载到 `seeds/` 目录：
```powershell
Invoke-WebRequest -Uri "https://dbt-datasets.s3.us-east-2.amazonaws.com/seed_full_moon_dates.csv" -OutFile "seeds\seed_full_moon_dates.csv"
```

检查文件前 5 行内容：
```csv
full_moon_date
2009-01-11
2009-02-09
2009-03-11
2009-04-09
```

### 4. 运行 `dbt seed` 将数据入库
在终端执行：
```powershell
dbt seed --profiles-dir .
```

真实终端输出回显：
```text
12:07:53  Running with dbt=1.12.6
12:07:56  Registered adapter: snowflake=1.12.5
12:07:58  Found 7 models, 1 seed, 563 macros
12:07:58  Concurrency: 4 threads (target='dev')
12:08:00  1 of 1 START seed file DEV.seed_full_moon_dates ................................ [RUN]
12:08:02  1 of 1 OK loaded seed file DEV.seed_full_moon_dates ............................ [INSERT 272 in 2.19s]
12:08:02  
12:08:02  Finished running 1 seed in 0 hours 0 minutes and 4.08 seconds (4.08s).
12:08:02  Completed successfully
12:08:02  Done. PASS=1 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=1
```
Snowflake 仓内已成功创建物理表 `DEV.SEED_FULL_MOON_DATES`，并一次性灌入 272 条精确数据！

---

## 第二部分：数据集市模型构建 —— 关联 Seed 与 Fact 表

在 dbt 中，Seed 生成的表被视作普通模型，**下游可以直接使用标准的 `&#123;&#123; ref('seed_name') &#125;&#125;` 语法进行无缝引用**！

### 1. 编写集市模型 `models/mart/mart_fullmoon_reviews.sql`
创建目录 `models/mart`，并创建文件 `mart_fullmoon_reviews.sql`：
```sql
&#123;&#123;
  config(
    materialized = 'table',
  )
&#125;&#125;

WITH fct_reviews AS (
    SELECT * FROM &#123;&#123; ref('fct_reviews') &#125;&#125;
),
full_moon_dates AS (
    SELECT * FROM &#123;&#123; ref('seed_full_moon_dates') &#125;&#125;
)

SELECT
    r.*,
    CASE
        WHEN fm.full_moon_date IS NULL THEN 'not full moon'
        ELSE 'full moon'
    END AS is_full_moon
FROM fct_reviews r
LEFT JOIN full_moon_dates fm
    ON (TO_DATE(r.review_date) = DATEADD(DAY, 1, fm.full_moon_date))
```

### 关键业务逻辑拆解：
- **`DATEADD(DAY, 1, fm.full_moon_date)`**：满月通常发生在夜间，因此租客在满月受影响后提交评价的时间一般为**满月次日**。
- **`LEFT JOIN` 标记**：若满月次日与评价日期重合，则打上 `'full moon'` 标签，否则标记为 `'not full moon'`。

---

## 第三部分：数据源（Sources）抽象与解耦架构

### 1. 为什么不能直接 `FROM AIRBNB.RAW.RAW_LISTINGS`？
回顾我们在第 03 章编写的 `src_listings.sql`：
```sql
-- 强耦合硬编码反模式
WITH raw_listings AS (
    SELECT * FROM AIRBNB.RAW.RAW_LISTINGS
)
```
这种写法破坏了血缘分析。dbt 无法获知上游有哪些物理源表、属于哪个业务系统，也无法展示源头到模型的完整血缘树。

### 2. 定义源配置文件 `models/sources.yml`
创建 `models/sources.yml`，在 YAML 中声明源命名空间、目标库架构与物理表映射：

```yaml
version: 2

sources:
  - name: airbnb
    schema: raw
    tables:
      - name: listings
        identifier: raw_listings

      - name: hosts
        identifier: raw_hosts

      - name: reviews
        identifier: raw_reviews
        config:
          loaded_at_field: date
          freshness:
            warn_after: {count: 1, period: hour}
            error_after: {count: 24, period: hour}
```

### 核心属性精讲：
- `name: airbnb`：数据源的逻辑命名空间；
- `schema: raw`：指定 Snowflake 中的物理 Schema 名称（即 `AIRBNB.RAW`）；
- `tables.name`：供下游 dbt 模型引用的逻辑表名（如 `listings`）；
- `tables.identifier`：Snowflake 数据库中真实的物理表名（如 `raw_listings`）。若物理表名与逻辑名一致，可省略此项；当两者不同时，通过 `identifier` 实现优雅别名映射！

### 3. 重构 Staging 层模型（使用 `source()` 宏）
将 `models/src/` 下的 3 个模型重构为使用 `&#123;&#123; source('airbnb', '...') &#125;&#125;`：

#### (1) `models/src/src_listings.sql`
```sql
WITH raw_listings AS (
    SELECT
        *
    FROM
        &#123;&#123; source('airbnb', 'listings') &#125;&#125;
)
SELECT
    id AS listing_id,
    name AS listing_name,
    listing_url,
    room_type,
    minimum_nights,
    host_id,
    price AS price_str,
    created_at,
    updated_at
FROM
    raw_listings
```

#### (2) `models/src/src_hosts.sql`
```sql
WITH raw_hosts AS (
    SELECT
        *
    FROM
        &#123;&#123; source('airbnb', 'hosts') &#125;&#125;
)
SELECT
    id AS host_id,
    name AS host_name,
    is_superhost,
    created_at,
    updated_at
FROM
    raw_hosts
```

#### (3) `models/src/src_reviews.sql`
```sql
WITH raw_reviews AS (
    SELECT
        *
    FROM
        &#123;&#123; source('airbnb', 'reviews') &#125;&#125;
)
SELECT
    listing_id,
    date AS review_date,
    reviewer_name,
    comments AS review_text,
    sentiment AS review_sentiment
FROM
    raw_reviews
```

### 4. 静态编译验证 `dbt compile`
执行 `dbt compile`，验证 dbt 能否正确将 `source()` 解析为 `AIRBNB.RAW.RAW_*`：
```powershell
dbt compile --profiles-dir .
```
终端回显显示：`Found 8 models, 1 seed, 3 sources, 563 macros`，全部拓扑节点编译通过！

---

## 第四部分：数据新鲜度监控（Source Freshness）实战

### 1. 新鲜度监控核心原理
数据管道在生产中最怕“源头断流”。dbt 提供了开箱即用的新鲜度检测：
- **`loaded_at_field`**：指定用于评估最新时间的字段（通常是业务时间戳，如 `date` 或 `created_at`）；
- **`warn_after`**：当数据延迟超过设定周期（如 1 小时）时发出警告（WARNING）；
- **`error_after`**：当数据延迟超过严重容忍周期（如 24 小时）时直接判定为错误（ERROR）。

### 2. 执行 `dbt source freshness`
在终端运行新鲜度检查：
```powershell
dbt source freshness --profiles-dir .
```

真实终端输出回显：
```text
12:09:18  Running with dbt=1.12.6
12:09:19  Registered adapter: snowflake=1.12.5
12:09:20  Found 8 models, 1 seed, 3 sources, 563 macros
12:09:20  Pulling freshness from warehouse metadata tables for 0 sources
12:09:20  1 of 1 START freshness of airbnb.reviews ....................................... [RUN]
12:09:21  1 of 1 ERROR STALE freshness of airbnb.reviews ................................. [ERROR STALE in 0.90s]
12:09:21  Finished running 1 source in 0 hours 0 minutes and 1.83 seconds (1.83s).
12:09:21  [ERROR]: in source reviews (models\sources.yml)
12:09:21    Status: error
12:09:21  Done.
```

### 3. CI/CD 生产退出码机制（Exit Code）
观察执行后的退出码：
- 在 Windows PowerShell 下查看：`$LASTEXITCODE`
- 在 Linux / macOS 下查看：`echo $?`

| 运行结果 | 终端输出状态 | 进程退出码 (`Exit Code`) | CI/CD 流水线行为 |
| :--- | :--- | :--- | :--- |
| **PASS** | `PASS`（数据在容忍期内） | `0` | 继续执行后续构建与发布 |
| **WARN** | `WARN`（超过预警阈值） | `0`（默认放行） | 触发通知告警，但允许继续构建 |
| **ERROR** | `ERROR STALE`（数据严重断流） | **`1`（非零退出码）** | **直接中断流水线，阻断发布！** |

> [!TIP]
> 这种非零退出码机制是现代数据 DevOps 的核心守门人（Gatekeeper）。它确保了当上游数据提供方发生断流时，自动化调度系统（如 GitHub Actions、Airflow）能够第一时间熔断报错，绝不将过时数据污染到下游报表！

---

## 第五部分：三板斧闭环实操 —— 全链路构建与 Snowflake 仓内验真

现在我们执行全量编译与运行，并在 Snowflake 中验证包含 Seed 与 Mart 的完整数仓架构。

### 第一板斧：执行全量 `dbt run`
```powershell
dbt run --profiles-dir .
```

真实终端输出回显：
```text
12:09:37  Running with dbt=1.12.6
12:09:37  Registered adapter: snowflake=1.12.5
12:09:38  Found 8 models, 1 seed, 3 sources, 563 macros
12:09:38  Concurrency: 4 threads (target='dev')
12:09:39  1 of 8 START sql view model DEV.src_hosts ...................................... [RUN]
12:09:39  2 of 8 START sql view model DEV.src_listings ................................... [RUN]
12:09:39  3 of 8 START sql view model DEV.src_reviews .................................... [RUN]
12:09:40  3 of 8 OK created sql view model DEV.src_reviews ............................... [SUCCESS 1 in 0.49s]
12:09:40  4 of 8 START sql incremental model DEV.fct_reviews ............................. [RUN]
12:09:40  1 of 8 OK created sql view model DEV.src_hosts ................................. [SUCCESS 1 in 0.55s]
12:09:40  5 of 8 START sql table model DEV.dim_hosts_cleansed ............................ [RUN]
12:09:40  2 of 8 OK created sql view model DEV.src_listings .............................. [SUCCESS 1 in 0.60s]
12:09:40  6 of 8 START sql table model DEV.dim_listings_cleansed ......................... [RUN]
12:09:41  6 of 8 OK created sql table model DEV.dim_listings_cleansed .................... [SUCCESS 17499 in 1.30s]
12:09:41  5 of 8 OK created sql table model DEV.dim_hosts_cleansed ....................... [SUCCESS 14111 in 1.45s]
12:09:41  7 of 8 START sql table model DEV.dim_listings_w_hosts .......................... [RUN]
12:09:41  4 of 8 OK created sql incremental model DEV.fct_reviews ........................ [SUCCESS 0 in 1.52s]
12:09:41  8 of 8 START sql table model DEV.mart_fullmoon_reviews ......................... [RUN]
12:09:42  7 of 8 OK created sql table model DEV.dim_listings_w_hosts ..................... [SUCCESS 17499 in 0.96s]
12:09:43  8 of 8 OK created sql table model DEV.mart_fullmoon_reviews .................... [SUCCESS 409697 in 1.84s]
12:09:43  
12:09:43  Finished running 1 incremental model, 4 table models, 3 view models in 0 hours 0 minutes and 5.37 seconds (5.37s).
12:09:43  Completed successfully
12:09:43  Done. PASS=8 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=8
```

### 第二板斧：Snowflake 仓内物理对象审计
通过 Python 连接 Snowflake 执行对象探查：
```sql
SHOW OBJECTS IN SCHEMA AIRBNB.DEV;
```

实测输出清单：
```text
KIND       | NAME                      | ROWS
TABLE      | DIM_HOSTS_CLEANSED        | 14,111
TABLE      | DIM_LISTINGS_CLEANSED     | 17,499
TABLE      | DIM_LISTINGS_W_HOSTS      | 17,499
TABLE      | FCT_REVIEWS               | 409,697
TABLE      | MART_FULLMOON_REVIEWS     | 409,697
TABLE      | SEED_FULL_MOON_DATES      | 272
VIEW       | SRC_HOSTS                 | 0 (视图不占存储)
VIEW       | SRC_LISTINGS              | 0 (视图不占存储)
VIEW       | SRC_REVIEWS               | 0 (视图不占存储)
```

### 第三板斧：验证满月假说样本数据
查询 `MART_FULLMOON_REVIEWS` 中满月与非满月的关联情况：
```sql
SELECT
    review_date,
    is_full_moon,
    COUNT(*) AS review_count
FROM
    AIRBNB.DEV.MART_FULLMOON_REVIEWS
GROUP BY
    review_date,
    is_full_moon
ORDER BY
    review_date DESC
LIMIT 5;
```

实测输出回显：
```text
Date: 2021-10-22 00:00:00 | is_full_moon: not full moon | count: 57
Date: 2021-10-21 00:00:00 | is_full_moon: full moon     | count: 89
Date: 2021-10-20 00:00:00 | is_full_moon: not full moon | count: 130
Date: 2021-10-19 00:00:00 | is_full_moon: not full moon | count: 121
Date: 2021-10-18 00:00:00 | is_full_moon: not full moon | count: 196
```
> [!NOTE]
> 2021-10-20 为天文满月日，由于模型逻辑按 `DATEADD(DAY, 1, fm.full_moon_date)` 计算，次日（2021-10-21）的 89 条评价被精准标记为 `full moon`！

---

## 第六部分：直面暗坑 —— 工业级避险指南

### 1. 暗坑一：将 Seeds 当作数据抽取加载工具（Data Dumping）
- **现象**：把几个 G 的业务交易日志保存为 CSV 放到 `seeds/` 目录下，试图通过 `dbt seed` 加载进数仓。
- **根因**：dbt Seed 底层采用逐批 `INSERT` 方式，并非针对大数据量设计的流式载入工具（如 Snowflake 的 `COPY INTO` 或 Snowpipe）。大文件会导致编译极度缓慢、Git 仓库膨胀锁死。
- **避险方案**：严格恪守 Seed 仅用于小体积静态映射表（<几千行）；海量数据必须通过专属摄入通道（如 Airbyte、Fivetran、Snowpipe）进入 RAW 层，再用 `sources` 进行抽象管理。

### 2. 暗坑二：dbt v1.5+ 后 freshness 配置废弃警告
- **现象**：在 `sources.yml` 中直接使用顶级 `freshness:` 时出现黄色报警：
  `[WARNING][PropertyMovedToConfigDeprecation]: Found 'freshness' as a top-level property...`
- **根因**：dbt 在高版本中规范了配置继承链，将 `freshness` 与 `loaded_at_field` 统一归入 `config:` 块内。
- **避险方案**：统一将新鲜度配置写在 `config:` 字典下：
  ```yaml
  config:
    loaded_at_field: date
    freshness:
      warn_after: {count: 1, period: hour}
      error_after: {count: 24, period: hour}
  ```

---

## 本章小结

在这一章中，我们全面攻克了 dbt 分析工程的输入层治理规范：
1. **理解了 Seeds 与 Sources 的边界**：Seeds 处理小体积版本化静态表，Sources 抽象外部数据仓库源表；
2. **掌握了 `dbt seed` 与 `source()` 宏解耦机制**：摆脱物理表硬编码，实现灵活的别名映射与环境自适应；
3. **实装了数据新鲜度守护机制（Source Freshness）**：理解了 `loaded_at_field` 与非零退出码在生产 CI/CD 中的卡点作用；
4. **验证了 Airbnb 满月评论集市模型（Mart）**：无缝将种子维度与海量事实表关联分析，完成数仓四层架构闭环。

在接下来的第 06 章中，我们将学习如何为这些模型构建工业级的 **Snapshots（慢变化维 SCD Type-2 历史拉链表）**，让数仓具备时间旅行般的历史状态追踪能力！
