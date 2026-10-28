# 第 07 章：非结构化文件数据同步实战 —— 基于 Snowflake Openflow 与 Box 云盘集成

在前面的章节中，我们已经掌握了如何将关系型数据库（如 Oracle）中的**结构化表格数据**（用户表、流水表）高效迁移并同步到 Snowflake。

但在现代企业的数据体系中，除了行和列组成的结构化数据之外，还存在着大量的**非结构化文件数据（Unstructured Files）**——例如存储在企业云盘（Box、AWS S3、Google Drive 等）中的 **PDF 规范、Word 技术方案、TXT 运维清单以及 Markdown 开发文档**。

```
【结构化数据】 (Oracle / MySQL 表格)  ───────> 传统 ETL / COPY INTO ───> Snowflake 表 (行与列)
【非结构化数据】(Box / 云盘中的各类文件) ───> Openflow 文件同步 ───────> Snowflake Stage (物理原件) + 结构化元数据与正文切块
```

**本章聚焦技术本质，抛开复杂的行业业务场景，站在纯粹的「数据同步与存储检索」视角**，系统讲解：
1. **数据源端（Source）**：如何将 Box 作为云存储数据源，通过服务端凭证授权给数据仓库。
2. **传输管道（Pipeline）**：如何利用 Snowflake 官方托管的 **Snowflake Openflow**（基于 Apache NiFi 架构引擎），免手写脚本实现文件增量拉取与变更捕获（CDC）。
3. **数据目标端（Destination）**：文件同步到 Snowflake 后到底存在哪里？元数据表记了什么？实际的文件内容又该如何通过 SQL 查出？

---

## 一、非结构化文件同步技术架构

在进行数据同步前，先通过下图理清整个数据流向。整个过程由「源端云存储 $\rightarrow$ 同步管道 $\rightarrow$ 目标端分层存储 $\rightarrow$ 查询与应用」四部分构成：

```mermaid
flowchart TD
    subgraph Source["数据源端 (Data Source)"]
        B1["Box 共享文件夹<br/>(存储 PDF / Word / TXT 等原始文件)"]
        B2["Box 开发者应用 (Custom App)<br/>(JWT 密钥对实现无人工服务端鉴权)"]
        B3["Box 变更事件流<br/>(提供过去14天增量日志 CDC)"]
    end

    subgraph Pipeline["数据传输管道 (Ingestion Pipeline)"]
        O1["Snowflake Openflow Connector for Box"]
        O2["连接器配置参数<br/>(Box Source / SF Destination / Ingestion)"]
        O3["后台轻量运行时<br/>(自动化拉取、断点续传、哈希计算)"]
    end

    subgraph Destination["数据目标端 (Snowflake Destination)"]
        subgraph Physical["1. 物理文件存储层"]
            S1["内部受管 Stage 暂存区<br/>(@BOX_RAW_STAGE/<br/>保存文件真实物理字节流)"]
        end

        subgraph Metadata["2. 元数据台账与对账层"]
            S2["元数据索引表<br/>(BOX_DOCUMENT_METADATA<br/>记录文件名、字节大小、SHA-256 哈希值、同步时间)"]
        end

        subgraph TextLayer["3. 正文切块与结构化层"]
            S3["文本切块表<br/>(BOX_DOC_CHUNKS<br/>将长篇文档切成小段落，关联 ACL 权限)"]
        end
    end

    subgraph QueryLayer["数据查询与消费层"]
        Q1["SQL Stage 直读<br/>(查看纯文本正文)"]
        Q2["SQL 元数据查询<br/>(核对哈希与文件列表)"]
        Q3["SQL 检索正文切片<br/>(全文检索与精准匹配)"]
        Q4["AI / RAG 知识检索服务<br/>(Cortex Search Service)"]
    end

    B1 -->|文件夹授权协同| B2
    B2 -->|JWT 私钥免密接入| O1
    B3 -.->|增量日志驱动| O1
    O1 --> O3
    O3 -->|文件原件落地| S1
    O3 -->|登记大小/哈希/目录| S2
    O3 -->|文本解析与切分| S3
    S1 --> Q1
    S2 --> Q2
    S3 --> Q3
    S3 --> Q4

    style Source fill:#f0f5ff,stroke:#adc6ff
    style Pipeline fill:#f6ffed,stroke:#b7eb8f
    style Destination fill:#fff7e6,stroke:#ffd591
    style QueryLayer fill:#f9f0ff,stroke:#d3adf7
```

### 两种技术实现路径的客观对比

| 考量维度 | 方案 A：使用 Snowflake Openflow 连接器（本章方案） | 方案 B：自研 Python 脚本调用 Box REST API |
| :--- | :--- | :--- |
| **开发工作量** | **极低（界面配置，数小时内跑通链路）** | 高（需手写 OAuth 刷新、递归拉取、断点续传等） |
| **凭证管理** | **Openflow 原生加密托管 JWT 私钥配置** | 需自行架设秘钥存储、处理 Token 过期与刷新 |
| **增量同步 (CDC)** | **开箱即用：基于 Box 审计事件流自动增量捕获** | 需维护水位线时间戳，或自行开发 Webhook 接收服务 |
| **元数据与一致性** | **自动计算 SHA-256 哈希与字节大小并登记入库** | 需自己在本地计算哈希并编写 SQL 插入元数据表 |
| **权限继承 (ACL)** | **自动提取文件夹/文件的被授权人邮箱 (`user_emails`)** | 需递归调用 Box 协作接口拼接关系表，逻辑繁琐 |

---

## 二、阶段一：Box 数据源端准备工作

为了让数据同步引擎能够安全拉取 Box 上的文件，需要在 Box 开发者控制台创建专属的 API 服务账号（Service Account），并将需要同步的文件夹授权给该账号。

### Step 1.1: 创建后端服务应用（Custom App）
1. 登录 [Box Developer Console (开发者控制台)](https://app.box.com/developers/console)。

![Box Developer Console 控制台首页](../images/07_step_01_box_console_home.png)

2. 点击右上角 **「Create Platform App」**。
3. 应用类型选择 **「Custom App」**（自定义后端服务应用）。

![Custom App 应用类型选择](../images/07_step_02_box_app_type_custom.png)

4. 填写基础信息：
   - **App Name**：`Snowflake_Openflow_Box`
   - **Purpose**：选择 `Integration`（数据集成）
5. 认证方式（Authentication Method）选择 **「Server Authentication (with JWT)」**（基于公私钥对的免人工服务端认证）。

![选择 Server Authentication JWT 认证](../images/07_step_02_box_jwt_auth_selection.png)

### Step 1.2: 配置最小权限作用域（Application Scopes）
在应用的 **「Configuration」** 标签页中，按数据同步需求配置读取权限：

1. **App Access Level**：选择 **「App + Enterprise Access」**。
2. **Content Scopes**：
   - `Read all files and folders stored in Box`：**勾选**（拉取文件夹内的文件列表与二进制流）。
   - `Write all files and folders stored in Box`：**勾选**（Box 平台生成底层文件下载令牌必须的权限，数据管道不会修改云盘原文件）。

![配置 Box 文档读写权限范围](../images/07_step_03_box_content_scopes.png)

3. **Administrative Actions**：
   - `Manage users` 与 `Manage groups`：勾选（用于提取文件的访问权限列表 `user_emails`）。
   - `Manage enterprise properties`：勾选（用于拉取过去 14 天的审计事件流实现增量 CDC 同步）。

![配置 Box 用户及管理类权限范围](../images/07_step_04_box_admin_scopes.png)

### Step 1.3: 生成并下载公私钥对配置文件（`config.json`）
1. 在配置页下方找到 **「Add and Manage Public Keys」**。

![公私钥对与签名密钥管理区](../images/07_step_05_box_keypair_section.png)

2. 点击 **「Generate a Public/Private Keypair」**：
   > [!NOTE] **安全校验提示**  
   > Box 平台要求生成私钥的账号必须启用两步验证（2FA）。如弹出提示，需在个人安全设置中绑定认证器或手机号后重新点击生成。
   > 
   > ![Box 两步验证安全提示](../images/07_step_06_box_2fa_prompt.png)

3. 生成成功后，浏览器会自动下载一个完整的 JSON 凭证文件（例如 `2717878_xxxx_config.json`）。该文件内含 `clientID`、`enterpriseID` 及 RSA 私钥，是后续配置 Openflow 连接器时的核心认证参数。

### Step 1.4: 管理员授权与获取服务账号邮箱
1. 切换到应用的 **「Authorization」**（授权）标签页，点击 **「Review and Submit」** 提交应用。
2. 企业管理员在 [Box 管理控制台](https://app.box.com/master) 的「自定义应用管理器」中点击 **「批准 (Authorize)」**。
3. 在应用的 **「General Settings」** 页面中，复制生成的专属服务账号邮箱：
   - 格式示例：`AutomationUser_2717878_XevDdBO55B@boxdevedition.com`

### Step 1.5: 文件夹协同授权并记录 Folder ID
1. 在 Box 个人/企业网盘中，新建一个专门用于数据同步的文件夹（如 `社内規程マニュアル`）。
2. 点击 **「共享」** $\rightarrow$ **「邀请协作者」**，粘贴上述服务账号邮箱，角色指定为 **「查看者 (Viewer)」**。

![Box 目标文件夹协同邀请服务账号](../images/07_step_07_box_folder_collaborator.png)

3. **记录 Folder ID**：从浏览器地址栏复制文件夹末尾的纯数字 ID（例如 `https://app.box.com/folder/431546000913` 中的 **`431546000913`**）。填 `0` 则代表根目录。

### Step 1.6: 准备测试文件并验证上传
为了完整验证不同文件格式的同步，我们在测试目录准备了 3 份涵盖主流格式的测试文件：
- `01_情報セキュリティ基本規程_2026.pdf`（PDF 文档，大小 781 字节）
- `02_クラウド移行プロジェクト_機密設計書.docx`（Word 文档，大小 1,825 字节）
- `03_コンプライアンス遵守チェックリスト_2026.txt`（纯文本文件，大小 1,429 字节）

在 Box 网页端将这 3 个文件上传至该目标文件夹，确认文件列表就绪：

![Box 目标文件夹真实测试文件上传成功](../images/07_step_08_box_files_uploaded.png)

---

## 三、阶段二：Snowflake 目标端基盘搭建与 RBAC

在 Snowflake 侧，我们需要为数据同步管道创建专用的角色、服务用户、计算仓库（Warehouse）、受管暂存区（Stage）以及用于记录元数据与文本切块的表。

运行工程内置的配置脚本 [`07_openflow_box_setup.sql`](file:///c:/Users/FX/Projects/SnowflakeBlog/scripts/snowflake/07_openflow_box_setup.sql)：

```sql
-- 1. 安全管理与角色规划 (SECURITYADMIN)
USE ROLE SECURITYADMIN;

-- 创建数据同步专属角色
CREATE ROLE IF NOT EXISTS OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Snowflake Openflow Box 连接器专属运行角色';

-- 创建下游只读查询角色
CREATE ROLE IF NOT EXISTS CORTEX_SEARCH_READ_ROLE
    COMMENT = '供下游检索应用调用的只读角色';

-- 创建数据管道自动化服务账号 (支持密钥对免密认证)
CREATE USER IF NOT EXISTS OPENFLOW_BOX_SVC_USER
    TYPE = SERVICE
    DEFAULT_ROLE = OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Openflow 数据管道专用服务账号';

GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO USER OPENFLOW_BOX_SVC_USER;
GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO ROLE SYSADMIN;
GRANT ROLE CORTEX_SEARCH_READ_ROLE TO ROLE SYSADMIN;

-- 2. 算力与存储对象构建 (SYSADMIN)
USE ROLE SYSADMIN;

-- 创建数据同步专用轻量计算仓库
CREATE WAREHOUSE IF NOT EXISTS OPENFLOW_INGEST_WH
    WITH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 120
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = '专用于 Box 文件同步与文本切块的计算资源';

-- 创建数据库与分层模式 (Schema)
CREATE DATABASE IF NOT EXISTS BOX_INTEGRATION_DB;

-- 落地层：用于存放原始文件 Stage 与元数据表
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.BOX_LANDING_DATA;

-- 处理层：用于存放文本切片与检索服务
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.CORTEX;

-- 赋权给连接器专属角色
GRANT USAGE, OPERATE ON WAREHOUSE OPENFLOW_INGEST_WH TO ROLE OPENFLOW_CONNECTOR_ROLE;
GRANT USAGE ON DATABASE BOX_INTEGRATION_DB TO ROLE OPENFLOW_CONNECTOR_ROLE;
GRANT USAGE, CREATE TABLE, CREATE STAGE ON SCHEMA BOX_INTEGRATION_DB.BOX_LANDING_DATA TO ROLE OPENFLOW_CONNECTOR_ROLE;
GRANT USAGE, CREATE TABLE ON SCHEMA BOX_INTEGRATION_DB.CORTEX TO ROLE OPENFLOW_CONNECTOR_ROLE;

-- 3. 存储与表结构初始化 (OPENFLOW_CONNECTOR_ROLE)
USE ROLE OPENFLOW_CONNECTOR_ROLE;
USE WAREHOUSE OPENFLOW_INGEST_WH;
USE DATABASE BOX_INTEGRATION_DB;
USE SCHEMA BOX_LANDING_DATA;

-- ① 创建受管内部 Stage (存储物理原始文件)
CREATE OR REPLACE STAGE BOX_RAW_STAGE
    DIRECTORY = (ENABLE = TRUE)
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
    COMMENT = '存放从 Box 同步下来的非结构化文件原件';

-- ② 创建文件元数据与对账表 (记录文件索引台账)
CREATE OR REPLACE TABLE BOX_DOCUMENT_METADATA (
    FILE_ID             VARCHAR(64) PRIMARY KEY,
    FILE_NAME           VARCHAR(512) NOT NULL,
    FOLDER_ID           VARCHAR(64) NOT NULL,
    FOLDER_PATH         VARCHAR(1024),
    SHA256_HASH         VARCHAR(128) NOT NULL,
    SIZE_BYTES          NUMBER(38, 0),
    BOX_CREATED_AT      TIMESTAMP_NTZ,
    BOX_MODIFIED_AT     TIMESTAMP_NTZ,
    INGESTED_AT         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    USER_EMAILS         ARRAY COMMENT '该文件在 Box 侧具备访问权限的用户邮箱列表 (用于 ACL 安全过滤)'
)
COMMENT = 'Box 文件的元数据主索引与版本状态对账表';

-- ③ 创建文本分块表 (存放切分后的段落文本，供检索使用)
USE SCHEMA BOX_INTEGRATION_DB.CORTEX;

CREATE OR REPLACE TABLE BOX_DOC_CHUNKS (
    CHUNK_ID            VARCHAR(128) PRIMARY KEY,
    FILE_ID             VARCHAR(64) NOT NULL,
    FILE_NAME           VARCHAR(512) NOT NULL,
    FOLDER_ID           VARCHAR(64) NOT NULL,
    CHUNK_INDEX         NUMBER(10, 0),
    CHUNK_TEXT          VARCHAR(16777216) NOT NULL,
    USER_EMAILS         ARRAY NOT NULL,
    UPDATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = '长文本拆分后的细粒度段落块';
```

---

## 四、阶段三：Openflow 连接器配置全量参数字典

在 Snowflake Openflow 中安装并配置 **Openflow Connector for Box** 时，系统会引导填写三大类参数。以下是官方标准参数的完整技术对照字典：

### 1. 数据源端参数（Boxソースパラメーター / Box Source Parameters）

| 参数项（日文 / 英文） | 中文标准释义 | 生产建议配置值 | 详细技术说明 |
| :--- | :--- | :--- | :--- |
| **Box App 構成 JSON**<br/>*(Box App Configuration JSON)* | Box 凭证 JSON 文本 | `{ "boxAppSettings": { ... } }` | 直接将阶段一生成的 `config.json` 完整文本内容粘贴至该文本框。 |
| **Box App構成ファイル**<br/>*(Box App Configuration File)* | Box 凭证文件上传路径 | `/path/to/box_config.json` | 若通过 CLI 或配置卷装载，可直接指定凭证文件物理存储路径（与上述 JSON 二选一）。 |

### 2. 目标端参数（Box宛先パラメーター / Box Destination Parameters）

| 参数项（日文 / 英文） | 中文标准释义 | 生产建议配置值 | 详细技术说明 |
| :--- | :--- | :--- | :--- |
| **宛先データベース**<br/>*(Destination Database)* | 目标数据库 | `BOX_INTEGRATION_DB` | 存储落地 Stage 和元数据表的 Snowflake 目标数据库。 |
| **宛先スキーマ**<br/>*(Destination Schema)* | 目标模式 | `BOX_LANDING_DATA` | 存放文件落地对象的目标 Schema。 |
| **Snowflake認証ストラテジー**<br/>*(Snowflake Authentication Strategy)* | 认证策略 | `Keypair`（推荐）或 `Snowflake Credentials` | 推荐使用非对称密钥对（Keypair），完全免除人工密码过期的维护成本。 |
| **Snowflakeアカウント識別子**<br/>*(Snowflake Account Identifier)* | 账户标识符 | `aakjsrd-oq04293` | Snowflake 组织与账户 ID（格式为 `<org>-<account>`）。 |
| **Snowflake秘密キー**<br/>*(Snowflake Private Key)* | 服务账号私钥内容 | `-----BEGIN ENCRYPTED PRIVATE KEY-----...` | 管道服务账号（`OPENFLOW_BOX_SVC_USER`）对应的私钥内容。 |
| **Snowflake秘密キーファイル**<br/>*(Snowflake Private Key File)* | 服务账号私钥路径 | `/secrets/rsa_key.p8` | 运行节点上私钥文件的物理装载路径（与私钥内容二选一）。 |
| **Snowflake秘密キーパスワード**<br/>*(Snowflake Private Key Password)* | 私钥保护密码 | `********` | 生成私钥时设定的对称加密密码（若私钥无密则留空）。 |
| **Snowflakeロール**<br/>*(Snowflake Role)* | 连接器执行角色 | `OPENFLOW_CONNECTOR_ROLE` | 必须具备目标 Schema 的读写和 Stage 写入特权。 |
| **Snowflakeのユーザー名**<br/>*(Snowflake Username)* | 连接器服务用户名 | `OPENFLOW_BOX_SVC_USER` | 专门用于数据管道的专用服务账号。 |
| **オーバーサイズ値戦略**<br/>*(Oversized Value Strategy)* | 超大字段处理策略 | `Truncate` 或 `Fail` | 当 Box 扩展元数据超出 Snowflake 单列限制时的截断或报错策略。 |
| **Snowflakeウェアハウス**<br/>*(Snowflake Warehouse)* | 计算仓库 | `OPENFLOW_INGEST_WH` | 驱动 Stage 目录刷新及写入元数据表所消耗的计算算力。 |

### 3. 数据拉取参数（Box取り込みパラメーター / Box Ingestion Parameters）

| 参数项（日文 / 英文） | 中文标准释义 | 生产建议配置值 | 详细技术说明 |
| :--- | :--- | :--- | :--- |
| **Boxフォルダー ID**<br/>*(Box Folder ID)* | 目标文件夹 ID | `431546000913`（或 `0`） | 待同步的目标 Box 目录 ID。填 `0` 则递归扫描服务账号有权访问的全部文件夹。 |
| **取り込むファイルの拡張子**<br/>*(Extensions of Files to Ingest)* | 同步文件扩展名白名单 | `pdf,docx,txt,md` | 允许拉取的文件扩展名白名单（逗号分隔，不带点号）。 |
| **Snowflakeファイルのハッシュテーブル名**<br/>*(Snowflake File Hash Table Name)* | 文件版本与哈希表名 | `BOX_DOCUMENT_METADATA` | 用于记录文件版本、SHA-256 哈希值、大小及 CDC 状态的去重台账表。 |

---

## 五、阶段四：数据同步全流程闭环验证与 SQL 真实查询

启动数据同步流程后，文件由 Box 传输进入 Snowflake。为了从技术视角彻底搞懂数据同步的结果，我们分为三步进行实测验证：

### 验证 1：文件元数据与数据一致性对账（Metadata Reconciliation）

文件同步落入 Snowflake 后，元数据表 `BOX_DOCUMENT_METADATA` 会记录下每个文件的属性信息。在 Snowflake 工作区中执行以下 SQL 检查同步台账：

```sql
SELECT 
    FILE_ID,
    FILE_NAME,
    SIZE_BYTES,
    LEFT(SHA256_HASH, 16) || '...' AS HASH_PREFIX,
    FOLDER_ID,
    FOLDER_PATH,
    TO_VARCHAR(INGESTED_AT, 'YYYY-MM-DD HH24:MI:SS') AS SYNC_TIME
FROM BOX_INTEGRATION_DB.BOX_LANDING_DATA.BOX_DOCUMENT_METADATA
ORDER BY FILE_ID;
```

- **真实执行截图与对账结果**：
查询返回 3 条记录，耗时仅 540ms。每个文件的 `SIZE_BYTES` 与 SHA-256 哈希值与本地原始文件 100% 吻合，证明数据传输过程中**零字节损坏、零数据丢失**：

![Snowflake 工作区真实查询执行与元数据对账验证](../images/07_step_09_snowflake_stage_files.png)

---

### 验证 2：直接通过 SQL 查询 Stage 中文件的真实正文数据

> [!QUESTION] **新手常见疑问**  
> 上面的 SQL 查出的是文件名和哈希值（即**元数据 / Metadata**），那**实际的文件数据内容**到底能不能查到？怎么查？

**答案是：完全可以！** 实际的物理文件完整保存在 `@BOX_RAW_STAGE` 中。

对于纯文本格式文件（如 `.txt`、`.csv`、`.md`、`.json`），我们可以直接利用 Snowflake 的 Stage 查询语法读取正文内容。

> [!WARNING] **排错实战：日文字符与特殊路径语法**  
> 如果在 SQL 中直接书写含中文/日文字符的未加引号路径（如 `@BOX_RAW_STAGE/compliance/03_コンプライアンス...`），Snowflake 的词法解析器无法识别非 ASCII 字符，会抛出语法错误：`SQL compilation error: syntax error ... unexpected 'コン'`。  
> **正确解法**：预先定义一个单列文本格式，并通过带单引号的路径或 `PATTERN` 正则表达式安全匹配：

```sql
USE DATABASE BOX_INTEGRATION_DB;
USE SCHEMA BOX_LANDING_DATA;

-- 1. 创建单列纯文本解析格式 (逐行读取，不按逗号拆分)
CREATE OR REPLACE FILE FORMAT BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT 
    TYPE = 'CSV' 
    FIELD_DELIMITER = NONE 
    RECORD_DELIMITER = '\n';

-- 2. 直接查询 Stage 中 03_コンプライアンス遵守チェックリスト_2026.txt 的真实正文内容
SELECT $1 AS FILE_CONTENT 
FROM '@BOX_INTEGRATION_DB.BOX_LANDING_DATA.BOX_RAW_STAGE/compliance/' 
(FILE_FORMAT => 'BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT', PATTERN => '.*03.*txt');
```

- **浏览器端真实执行截图与结果**：
执行仅耗时 **145ms**，查询结果区完整输出了该文本文件的全部 **20 行真实正文条目**（包括标题、章节、日常点检要求等）：

![Snowflake Stage 文件真实正文直接查询执行结果](../images/07_step_10_stage_file_content_query.png)

---

### 验证 3：查询已切块入库的 PDF 与 Word 文档正文内容

对于 PDF 和 Word（`.docx`）等复杂二进制格式，在文件同步流水线中，通常会在落入 Stage 后由文本解析工具切分成便于检索的段落块（Text Chunks），并写入 `BOX_DOC_CHUNKS` 表中。

此时，我们可以直接像查询普通数据库表一样，用 SQL 检索 PDF 与 Word 中的具体条款：

```sql
-- 查询已切片解析入库的 PDF 与 Word 真实文档段落内容
SELECT 
    FILE_NAME,
    CHUNK_INDEX,
    CHUNK_TEXT
FROM BOX_INTEGRATION_DB.CORTEX.BOX_DOC_CHUNKS
ORDER BY FILE_ID, CHUNK_INDEX;
```

- **浏览器端真实执行截图与结果**：
执行耗时 **143ms**，清晰展示了 `01_情報セキュリティ基本規程_2026.pdf` 的密码安全策略以及 `02_クラウド移行プロジェクト_機密設計書.docx` 的云上迁移专线架构设计正文：

![Snowflake Cortex 文档切片真实正文查询执行结果](../images/07_step_11_doc_chunks_content_query.png)

---

### 验证 4：生成浏览器直接查看/下载文件的安全链接（Scoped URL）

如果需要在业务系统、报表或浏览器中直接打开原版的 PDF 或 DOCX 文件，可以使用 Snowflake 内置的 `BUILD_SCOPED_FILE_URL` 函数：

```sql
SELECT 
    RELATIVE_PATH,
    SIZE,
    -- 生成带有时效鉴权的安全下载/预览 URL
    BUILD_SCOPED_FILE_URL(@BOX_RAW_STAGE, RELATIVE_PATH) AS DIRECT_DOWNLOAD_URL
FROM DIRECTORY(@BOX_RAW_STAGE);
```
执行后在结果集中点击生成的 URL，即可在浏览器中原生预览或下载对应的原版文件。

---

## 六、技术进阶：关于 Snowflake 试用版与生产版的功能说明

在进行非结构化文档处理时，新手容易在各种文档解析函数上遇到报错。这里总结真实环境下的技术要点：

1. **新旧函数前缀升级**：
   - Snowflake 较新的版本中，旧版函数 `SNOWFLAKE.CORTEX.PARSE_DOCUMENT` 与 `SNOWFLAKE.CORTEX.SUMMARIZE` 已升级为顶层 SQL 函数：`AI_PARSE_DOCUMENT` 与 `AI_SUMMARIZE`。
2. **试用账户（Trial Account）的 GPU 配额保护**：
   - 官方多模态文档布局与 OCR 解析函数（`AI_PARSE_DOCUMENT`）会消耗较大的 GPU 算力，Snowflake 官方在 **30 天 Free Trial（免费试用）个人账户中全局限制了该函数**（系统会提示 `AI function _AI_PARSE_DOCUMENT is not available for trial accounts`）。
   - **生产环境与替代方案**：
     - 在企业正式订阅账户中，该函数可直接调用，一键提取 PDF 中的排版和文字。
     - 在试用或学习环境中，如本章所示，使用 **Stage 文本格式直读（`TXT_FORMAT`）**、**Snowpark Python 二进制流读取（`SnowflakeFile.open`）** 以及 **`BOX_DOC_CHUNKS` 结构化表**，即可完美跑通端到端的数据同步与检索验证。

---

## 本章小结

本章从纯粹的**数据同步与工程落地**视角，系统走通了非结构化文件从云盘到 Snowflake 的完整技术链路：
1. **源端解耦**：利用 Box JWT 服务账号免密接入，最小权限只读文件夹协同。
2. **传输管道**：依托 Openflow 免代码引擎，自动化处理文件搬运与 CDC 增量捕获。
3. **目标端分层清晰**：
   - **Stage** 负责保障原版文件的完整落地；
   - **元数据表** 负责基于 SHA-256 哈希保障数据一致性对账；
   - **切块表与 Stage SQL** 负责支持文件真实内容的直接检索与业务消费。
