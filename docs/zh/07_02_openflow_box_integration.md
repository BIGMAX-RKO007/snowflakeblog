# 第 07-2 讲：基于 Snowflake Openflow 的 Box 云盘同步与知识检索实战

> 💡 **系列导航**：本讲为 Openflow 专题实战篇。建议先阅读 [第 07-1 讲：Snowflake Openflow 核心原理与多模态数据集成架构](./07_01_openflow_architecture_and_concepts.md) 掌握 Openflow 底层 Apache NiFi 引擎底座、SPCS 容器化托管与多源治理基座。
>
> 本章依据 **《尚硅谷技术讲义写作规范 (shangguigu-style)》** 深度重构：开门见山直击本质、去业务化聚焦纯技术、全 SQL 配置项逐行参数字典拆解、全流程真机截图与毫秒级执行指标拒绝 AI 幻觉、直面暗坑实战避险、环境前置零隐式假设。

---

## 引言：开门见山，极简心智模型

在前面的章节中，我们已经掌握了如何把关系型数据库（如 Oracle）中的**结构化表格数据**通过 CSV/gzip 同步到 Snowflake。

但在现代数据仓库中，还有一类非常庞大的资产叫**非结构化文件数据（Unstructured Files）**——比如企业存储在云盘（Box、AWS S3、Google Drive 等）里的 **PDF 说明书、Word 技术方案、TXT 运维清单**。

### 极简单明对比：结构化数据 vs 非结构化文件

```
【结构化数据 (Oracle)】
┌────┬────────┬─────────┐
│ Id │ Name   │ Balance │  ───────> 传统 ETL / COPY INTO ───> Snowflake 表 (行与列)
├────┼────────┼─────────┤                                     数据直接由 SQL 统计分析
│ 1  │ 张三   │ 100.00  │
└────┴────────┴─────────┘

【非结构化文件 (Box 云盘)】
┌─────────────────────────┐
│ 01_安全密码规范.pdf     │
│ 02_架构设计规范.docx    │  ───────> Openflow 文件同步 ───────> Snowflake Stage (物理原件)
│ 03_运维巡检清单.txt     │                                     + 元数据台账表 (大小/哈希)
└─────────────────────────┘                                     + 正文切块表 (段落内容)
```

- **核心疑问**：云盘里的文件怎么自动、增量同步进数据仓库？同步过来后存在哪里？元数据表记了什么？各项 SQL 配置参数的具体机理是什么？最关键的是：**文件的真实内容到底能不能用 SQL 查出来？有没有真实的控制台执行截图证明不是 AI 幻觉？**
- **本章目标**：不讲任何特定行业的复杂业务（不谈银行、不谈证券），只从纯粹的**数据同步、存储分层、逐行参数解析与 SQL 查询验证**视角，提供 100% 真实环境截图与毫秒级执行指标，手把手跑通全流程闭环！

---

## 一、准备工作与环境依赖 (Prerequisites)

为了杜绝读者在实操过程中被卡住，请在开始前确认以下环境与账号准备就绪：

| 依赖组件 | 规格要求 / 权限 | 作用说明 |
| :--- | :--- | :--- |
| **Snowflake 账号** | 拥有 `ACCOUNTADMIN` 或 `SECURITYADMIN` + `SYSADMIN` 权限 | 创建专用的同步角色、计算仓库、内部 Stage 与数据表 |
| **Box 开发者账号** | 企业版或个人开发者试用账号（开启 2FA） | 创建 Custom App 服务账号并生成 JWT 认证私钥 |
| **目标同步文件夹** | Box 网盘中拥有 `Editor` 或 `Owner` 权限的文件夹 | 授权给服务账号并存放待同步的文件 |
| **Python 环境** | Python 3.10+（可选，用于数据准备与对账） | 生成多格式纯技术测试文件，运行同步对账脚本 |

---

## 二、技术架构与数据流向

在动手操作之前，先通过下图理清整个数据同步的四层拓扑结构：

```mermaid
flowchart TD
    subgraph Source["数据源端 (Data Source)"]
        B1["Box 共享文件夹<br/>(存储 PDF / Word / TXT 原始文件)"]
        B2["Box 开发者应用 (Custom App)<br/>(JWT 密钥对免交互服务端认证)"]
        B3["Box 审计事件流<br/>(记录过去14天的增量变更 CDC)"]
    end

    subgraph Pipeline["数据传输管道 (Pipeline)"]
        O1["Snowflake Openflow Connector for Box"]
        O2["连接器核心参数配置<br/>(Box Source / SF Target / Ingestion)"]
        O3["后台轻量运行时引擎<br/>(文件流拉取、断点续传、哈希计算)"]
    end

    subgraph Target["数据目标端 (Snowflake Target)"]
        subgraph S_Stage["1. 物理存储层"]
            T1["内部受管 Stage 暂存区<br/>(@BOX_RAW_STAGE/<br/>保存文件的真实物理二进制/文本原件)"]
        end

        subgraph S_Meta["2. 元数据台账层"]
            T2["元数据索引表<br/>(BOX_DOCUMENT_METADATA<br/>记录文件 ID、大小、SHA-256 哈希、同步时间)"]
        end

        subgraph S_Chunk["3. 正文切块层"]
            T3["文本分块表<br/>(BOX_DOC_CHUNKS<br/>将长篇文档切成小段落，关联 ACL 权限)"]
        end
    end

    subgraph QueryLayer["数据查询与消费层"]
        Q1["SQL Stage 直读<br/>(直接查询 TXT 正文)"]
        Q2["SQL 元数据查询<br/>(核对哈希与文件列表)"]
        Q3["SQL 检索正文段落<br/>(检索切分后的技术条款)"]
    end

    B1 -->|文件夹授权协作| B2
    B2 -->|JWT 私钥免密接入| O1
    B3 -.->|增量事件驱动| O1
    O1 --> O3
    O3 -->|1. 原件物理落盘| T1
    O3 -->|2. 登记大小与哈希| T2
    O3 -->|3. 文本段落切分| T3
    T1 --> Q1
    T2 --> Q2
    T3 --> Q3

    style Source fill:#f0f5ff,stroke:#adc6ff
    style Pipeline fill:#f6ffed,stroke:#b7eb8f
    style Target fill:#fff7e6,stroke:#ffd591
    style QueryLayer fill:#f9f0ff,stroke:#d3adf7
```

### 选型对比：Openflow 连接器 vs 自研 Python 脚本

| 维度 | 方案 A：Snowflake Openflow 连接器（本章推荐） | 方案 B：自研 Python 脚本调用 Box REST API |
| :--- | :--- | :--- |
| **开发工作量** | **极低（界面参数装配，半天即可跑通全链路）** | 高（需自写认证刷新、分页遍历、下载重试等代码） |
| **凭证管理** | **Openflow 托管加密存储 JWT `config.json`，免人工维护** | 需自建 Secret 存储，处理 Token 2小时过期刷新机制 |
| **增量同步 (CDC)** | **开箱即用：底层自动拉取 Box 过去 14 天审计事件流** | 需自行维护上次同步水位线或架设 Webhook 接收服务 |
| **一致性对账** | **自动计算 SHA-256 哈希值与字节大小并入库** | 需在本地下载流中自行计算哈希再写 SQL 插入表 |
| **权限继承 (ACL)** | **自动提取文件被授权人邮箱 (`user_emails`)** | 需逐层递归调用 Box 协作接口拼接关系，逻辑极繁琐 |

---

## 三、核心机理深度剖析：Stage 物理原件暂存 vs 表字段结构化清洗切块 (两段式架构) 与多源数据治理方案

在实际构建基于非结构化文档的现代数据湖仓与企业知识库时，许多工程师和架构师往往存在两个最核心的疑问：

### 疑问 1：当前数据流是将原始文件直接存储到 Snowflake？还是做 ETL 清洗后存入表字段中？

答案是：**生产级工业实践绝非“二选一”，而是标准的“两段式混合存储架构（Two-Stage Hybrid Architecture）”！**

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   非结构化文档两段式存储架构 (Two-Stage Hybrid Architecture)             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│                                    【数据源：Box 云盘】                                 │
│                           (PDF 报告 / Word 方案 / TXT 清单)                            │
│                                              │                                         │
│                                              ▼                                         │
│                 ┌────────────────────────────────────────────────────────┐             │
│                 │ 第一阶段：物理原件落地层 (Raw Ingestion Layer)           │             │
│                 │ • 载体：Snowflake 内部受管 Stage (@BOX_RAW_STAGE/)     │             │
│                 │ • 特点：不丢失任何字节，保留原始格式、版面、图片与排版    │             │
│                 │ • 价值：合规归档、时效防篡改、生成安全下载链接 (Scoped URL)│            │
│                 └────────────────────────────────────────────────────────┘             │
│                                              │                                         │
│                      ┌───────────────────────┴───────────────────────┐                 │
│                      ▼                                               ▼                 │
│ ┌──────────────────────────────────────────┐   ┌─────────────────────────────────────┐ │
│ │ 第二阶段 A：元数据台账表 (Metadata Catalog)│   │ 第二阶段 B：正文清洗与分块表 (Chunks)│ │
│ │ • 表名：BOX_DOCUMENT_METADATA            │   │ • 表名：BOX_DOC_CHUNKS              │ │
│ │ • 字段：文件ID、路径、SHA-256 哈希、大小 │   │ • 字段：段落序号、正文内容、向量 Embedding││
│ │ • 价值：数据对账、版本比对、防重复摄取   │   │ • 价值：SQL 模糊搜索、全文检索、大模型 RAG │ │
│ └──────────────────────────────────────────┘   └─────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **第一阶段：Stage 物理原件落地**：
   - 保持文件的二进制/文本原貌，原汁原味暂存至 Snowflake 受管内部 Stage（`@BOX_RAW_STAGE`）。
   - **核心价值**：审计合规要求企业必须保留原始凭证；下游前端应用需要通过 Snowflake 内置的 `BUILD_SCOPED_FILE_URL` 函数生成时效签名 URL，供用户在浏览器中无损预览或下载原始 PDF/Word 文件。
2. **第二阶段：ETL 清洗、切块与元数据入表**：
   - **元数据入表 (`BOX_DOCUMENT_METADATA`)**：记录文件大小、Box File ID、修改时间与 SHA-256 物理哈希值，提供 100% 精确的对账防重能力；
   - **正文切块入表 (`BOX_DOC_CHUNKS`)**：利用文本解析算子将数万字的长篇文档按照段落、语义滑动窗口（如 500 字/块）拆分为细粒度文本切片，供 SQL 检索或 Cortex 向量搜索引擎使用。

---

### 疑问 2：如果有多个非结构化数据源（Box, S3, SharePoint, Google Drive），如何做统一数据管理方案？

当数据源从单一的 Box 扩展到 AWS S3、Microsoft SharePoint、Google Drive、本地 SFTP 时，如果为每个源头单独开发一套表，会导致数仓资产极度碎片化。

工业级统一治理方案采用 **“多 Stage 物理隔离 + 全局统一 Catalog 表 + 可插拔解析管道 + 统一行级策略”** 的中台架构：

```
【源端 1: Box】        ──> 内部 Stage: @BOX_RAW_STAGE        ──┐
【源端 2: AWS S3】     ──> 外部 Stage: @S3_CORP_STAGE        ──┼──> 【全局统一文档编目表】
【源端 3: SharePoint】 ──> 内部 Stage: @SHAREPOINT_STAGE     ──┤    (UNSTRUCTURED_DOCUMENT_CATALOG)
【源端 4: 本地 SFTP】  ──> 内部 Stage: @SFTP_LANDING_STAGE   ──┘                 │
                                                                                 ▼
                                                                     【统一可插拔解析管道】
                                                                     (PDF/Word/TXT Parser)
                                                                                 │
                                                                                 ▼
                                                                     【统一检索与向量分块库】
                                                                     (CORP_DOC_CHUNKS)
```

```sql
CREATE OR REPLACE TABLE UNSTRUCTURED_DOCUMENT_CATALOG (
    -- 全局唯一文档标识 (SHA-256 或 UUID，跨源去重)
    doc_global_id         VARCHAR(64) PRIMARY KEY,
    
    -- 来源系统与原始标识
    source_system         VARCHAR(32) NOT NULL,   -- 'BOX', 'AWS_S3', 'SHAREPOINT', 'LOCAL_SFTP'
    source_file_id        VARCHAR(256) NOT NULL,  -- 源端原始 ID (如 Box File ID: 123456789)
    
    -- 物理存储映射
    stage_name            VARCHAR(128) NOT NULL,  -- '@BOX_RAW_STAGE', '@S3_CORP_STAGE'
    stage_relative_path   VARCHAR(1024) NOT NULL, -- 暂存区内的相对路径
    file_name             VARCHAR(256) NOT NULL,  -- 文件真实名称
    mime_type             VARCHAR(64) NOT NULL,   -- 'application/pdf', 'application/vnd.openxmlformats...'
    file_size_bytes       NUMBER(38,0) NOT NULL,  -- 文件精确字节大小
    
    -- 数据完整性与幂等去重
    content_sha256        VARCHAR(64) NOT NULL,   -- 文件物理 SHA-256 哈希值
    ingestion_timestamp   TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- 解析处理状态机
    parsing_status        VARCHAR(32) DEFAULT 'PENDING', -- 'PENDING', 'PARSED', 'FAILED', 'SKIPPED'
    parsed_timestamp      TIMESTAMP_LTZ,
    
    -- 动态扩展属性与源端特有元数据 (JSON 半结构化存储)
    source_metadata       VARIANT,                -- 存放 Box 目录层级、S3 Tags、SharePoint Site 等
    
    -- 访问控制权限列表 (继承源端权限体系)
    acl_permissions       ARRAY                   -- 允许访问的用户邮箱或群组列表 ['alice@corp.com', 'group_legal']
);
```

---

## 四、Box 数据源端准备与凭证获取（全流程真实截图）

### Step 3.1: 创建后端服务应用（Custom App）
1. 登录 [Box 开发者控制台 (Box Developer Console)](https://app.box.com/developers/console)。

![Box Developer Console 控制台首页](../images/07_step_01_box_console_home.png)

2. 点击右上角 **「Create Platform App」**。
3. 应用类型选择 **「Custom App」**。

![Custom App 应用类型选择](../images/07_step_02_box_app_type_custom.png)

4. 填写基础信息：
   - **App Name**：`Snowflake_Openflow_Box`
   - **Purpose**：选择 `Integration`（数据集成）
5. 认证方式选择 **「Server Authentication (with JWT)」**（基于公私钥对的免交互服务端认证）。

![选择 Server Authentication JWT 认证](../images/07_step_02_box_jwt_auth_selection.png)

6. 确认创建 JWT 后端应用：

![创建 JWT 后端应用确认](../images/07_step_03_box_create_app_jwt.png)

---

### Step 3.2: 配置最小权限作用域（Application Scopes）
进入应用的 **「Configuration」** 标签页：

![Box 应用配置主界面](../images/07_step_04_box_configuration_page.png)

1. **App Access Level**：勾选 **「App + Enterprise Access」**。
2. **Content Scopes**：
   - `Read all files and folders stored in Box`：**必须勾选**（读取指定目录下的文件列表与二进制流）。
   - `Write all files and folders stored in Box`：**必须勾选**（用于生成下载令牌，绝不篡改文件）。

![配置 Box 文档读写权限范围](../images/07_step_03_box_content_scopes.png)

3. **Administrative Actions**：
   - `Manage users` 与 `Manage groups`：勾选（提取文件访问权限列表 `user_emails`）。
   - `Manage enterprise properties`：勾选（拉取过去 14 天审计事件流以实现增量 CDC 同步）。

![配置 Box 用户及管理类权限范围](../images/07_step_04_box_admin_scopes.png)

---

### Step 3.3: 生成并下载公私钥对配置文件（`config.json`）
1. 页面向下滚动至 **「Add and Manage Public Keys」**。

![公私钥对与签名密钥管理区](../images/07_step_05_box_keypair_section.png)

2. 点击 **「Generate a Public/Private Keypair」**：

![签名密钥管理面板](../images/07_step_05_manage_signature_keys.png)

> [!WARNING] **【避坑提示：Box 2FA 强制要求】**  
> Box 强制要求开发者账号开启两步验证（2FA），否则生成私钥时会弹出阻断提示。前往账号安全设置绑定短信或 Authenticator 即可：
> 
> ![Box 两步验证安全提示](../images/07_step_06_box_2fa_prompt.png)

3. 两步验证通过后，公私钥对自动配置完毕：

![JWT 公私钥对配置就绪](../images/07_step_06_jwt_configured.png)

4. 点击右上角 **「Save Changes」** 保存应用配置：

![应用配置保存成功](../images/07_step_07_jwt_saved.png)

5. 浏览器自动下载一个完整的 JSON 凭证文件（例如 `2717878_xxxx_config.json`），内含 Client ID、Enterprise ID 以及加密的 RSA 私钥：

![凭证配置文件成功下载至本地](../images/07_step_09_config_downloaded.png)

---

### Step 3.4: 文件夹协同授权并获取 Folder ID
1. 在应用的 **「General Settings」** 页面中复制专属服务账号邮箱（例如 `AutomationUser_2717878_XevDdBO55B@boxdevedition.com`）；
2. 打开日常使用的 Box 网盘，新建一个用于同步的文件夹（如 `社内規程マニュアル`）；
3. 点击 **「共享」** $\rightarrow$ **「邀请协作者」**，粘贴该服务账号邮箱，角色设置为 **「查看者 (Viewer)」**：

![Box 目标文件夹协同邀请服务账号](../images/07_step_07_box_folder_collaborator.png)

4. 协同邀请发送成功，服务账号已获得只读读取权限：

![协同邀请成功展示](../images/07_step_10_folder_collaboration_invited.png)

5. **记录 Folder ID**：从浏览器地址栏复制文件夹 ID（如 `https://app.box.com/folder/431546000913` 末尾的数字 **`431546000913`**）。填 `0` 则代表根目录。

---

### Step 3.5: 上传 3 份纯技术测试文档
为了测试不同文件类型的同步效果，上传 3 份纯技术测试文件到该文件夹中：
1. `01_情報セキュリティ基本規程_2026.pdf`（PDF 文档，大小 **781 字节**）
2. `02_クラウド移行プロジェクト_機密設計書.docx`（Word 文档，大小 **1,825 字节**）
3. `03_コンプライアンス遵守チェックリスト_2026.txt`（纯文本文档，大小 **1,429 字节**）

确认文件在 Box 文件夹中展示正常：

![Box 目标文件夹真实测试文件上传成功](../images/07_step_08_box_files_uploaded.png)

---

## 五、Snowflake 目标端基盘构建（全量 DDL 脚本与逐行参数深度解析）

在 Snowflake 侧，按照最小权限原则创建专用的角色、服务用户、计算仓库（Warehouse）、受管内部 Stage 以及两张核心数据表。

运行工程内置的标准初始化脚本 [`07_openflow_box_setup.sql`](file:///c:/Users/FX/Projects/SnowflakeBlog/scripts/snowflake/07_openflow_box_setup.sql)：

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

### 逐行配置项与参数深度字典（彻底杜绝参数疑惑）

为确保每一项 SQL 配置清晰透彻，以下将上述脚本的所有参数逐行拆解：

#### 1. 服务账号与权限配置项 (`CREATE USER ... TYPE = SERVICE`)

| 配置项 | 参数值 | 为什么这样配？（技术机理与安全规范） |
| :--- | :--- | :--- |
| `TYPE = SERVICE` | `SERVICE` | **专用服务账号类型**。区别于人类交互用户（`PERSON`），服务账号禁止使用交互式密码和 Web 界面登录，专用于自动化管道密钥对（Keypair）免交互认证，不受企业 SSO 密码过期策略阻断。 |
| `DEFAULT_ROLE` | `OPENFLOW_CONNECTOR_ROLE` | **默认激活角色**。当 Openflow 通过 Python/JDBC 建立连接且未显式指定 Role 时，自动降权使用该专属角色，防止越权越位。 |
| `GRANT ROLE ... TO SYSADMIN` | 角色继承 | **Snowflake 最佳安全实践**。所有自定义角色必须自下而上挂载到 `SYSADMIN`，防止出现脱离主管理员监管的“幽灵角色”。 |

#### 2. 计算仓库配置项 (`CREATE WAREHOUSE OPENFLOW_INGEST_WH`)

| 配置项 | 参数值 | 为什么这样配？（技术机理与成本防烧） |
| :--- | :--- | :--- |
| `WAREHOUSE_SIZE` | `'XSMALL'` | **最小算力规格（1 信用点/小时）**。文件元数据入库和 Stage 文本切片主要为 I/O 密集型操作，XSMALL 算力完全足够，可避免高规格机器空转烧钱。 |
| `AUTO_SUSPEND` | `120`（秒） | **空闲 2 分钟自动挂起**。同步任务通常为周期性微批次，执行完几秒钟后等待 2 分钟无新查询即进入休眠，杜绝闲置计费。 |
| `AUTO_RESUME` | `TRUE` | **自动唤醒**。下游一旦有查询或写入请求发起，Warehouse 在 1 秒内自动拉起，对业务完全透明。 |
| `INITIALLY_SUSPENDED` | `TRUE` | **创建时默认休眠**。创建对象瞬间不立即消耗算力，只有首次真正被使用时才开始计费。 |

#### 3. 内部 Stage 配置项 (`CREATE STAGE BOX_RAW_STAGE`)

| 配置项 | 参数值 | 为什么这样配？（技术机理与底层联动） |
| :--- | :--- | :--- |
| `DIRECTORY = (ENABLE = TRUE)` | `ENABLE = TRUE` | **开启 Stage 目录表（Directory Table）**。这是非结构化数据管理的关键特性！开启后 Snowflake 会在 Stage 之上自动维护文件元数据表，使得我们能够直接用 `SELECT * FROM DIRECTORY(@BOX_RAW_STAGE)` 查询文件大小与路径，并支持下游挂载 Stream 变更流。 |
| `ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')` | `'SNOWFLAKE_SSE'` | **Snowflake 服务器端加密**。采用 AES-256 算法，密钥由 Snowflake 强安全体系自动轮转，确保文件原件落盘时的物理静态合规与机密性。 |

#### 4. 元数据台账表配置项 (`BOX_DOCUMENT_METADATA`)

| 字段名称 | 类型约束 | 业务与技术含义 |
| :--- | :--- | :--- |
| `FILE_ID` | `VARCHAR(64) PRIMARY KEY` | **Box 端全局唯一对象 ID**。作为主键保证多次增量同步时幂等 Upsert，防止重复录入。 |
| `FILE_NAME` | `VARCHAR(512) NOT NULL` | **文件完整名称**。包含扩展名（如 `.pdf`、`.docx`），供业务直观检索。 |
| `FOLDER_ID` / `FOLDER_PATH` | `VARCHAR` | **父级目录 ID 与全路径面包屑**。保留文件在源端的目录归属结构。 |
| `SHA256_HASH` | `VARCHAR(128) NOT NULL` | **文件的 SHA-256 加密哈希值**。判断文件内容是否变更的唯一金标准（CDC 判定），杜绝网络传输丢包损坏。 |
| `SIZE_BYTES` | `NUMBER(38, 0)` | **文件精确物理字节大小**。与源端及 Stage 文件大小进行绝对对账。 |
| `BOX_CREATED_AT` / `MODIFIED_AT` | `TIMESTAMP_NTZ` | **源端创建与修改时间戳**。驱动增量抽取的水位线（Watermark）。 |
| `USER_EMAILS` | `ARRAY` | **访问控制权限列表（ACL）**。半结构化数组存储，作为下游行级安全策略（Row Access Policy）的强过滤依据。 |

#### 5. 正文切块表配置项 (`BOX_DOC_CHUNKS`)

| 字段名称 | 类型约束 | 业务与技术含义 |
| :--- | :--- | :--- |
| `CHUNK_ID` | `VARCHAR(128) PRIMARY KEY` | **复合切片主键**。规则为 `<file_id>_<chunk_index>`，保证每个文本切片全局唯一。 |
| `CHUNK_INDEX` | `NUMBER(10, 0)` | **段落顺序索引**。记录该块在原文档中的先后位置，便于上下文还原重组。 |
| `CHUNK_TEXT` | `VARCHAR(16777216) NOT NULL` | **段落真实文字正文**。采用 Snowflake 最大 16MB 文本列，承载切块清洗后的文字。 |
| `USER_EMAILS` | `ARRAY NOT NULL` | **继承权限列表**。查询切块时同样受权限约束，防止越权嗅探正文。 |

---

## 六、Openflow 连接器配置全量参数字典

在配置 **Openflow Connector for Box** 时，连接器会引导填写三大类参数。以下是官方标准参数的完整技术对照字典：

### 1. Box 数据源参数（Boxソースパラメーター / Box Source Parameters）

| 参数项（日文 / 英文） | 中文标准释义 | 生产建议配置值 | 详细技术说明 |
| :--- | :--- | :--- | :--- |
| **Box App 構成 JSON**<br/>*(Box App Configuration JSON)* | Box 凭证 JSON 文本 | `{ "boxAppSettings": { ... } }` | 直接将阶段四生成的 `config.json` 完整文本内容粘贴至该文本框。 |
| **Box App構成ファイル**<br/>*(Box App Configuration File)* | Box 凭证文件上传路径 | `/path/to/box_config.json` | 若通过 CLI 或配置卷装载，可直接指定凭证文件物理存储路径（与上述 JSON 二选一）。 |

### 2. Snowflake 目标端参数（Box宛先パラメーター / Box Destination Parameters）

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
| **オーバーサイズ値戦略**<br/>*(Oversized Value Strategy)* | 超大字段处理策略 | `Truncate`（截断）或 `Fail`（报错） | 当 Box 扩展元数据超出 Snowflake 单列限制时的处理策略。 |
| **Snowflakeウェアハウス**<br/>*(Snowflake Warehouse)* | 计算仓库 | `OPENFLOW_INGEST_WH` | 驱动 Stage 目录刷新及写入元数据表所消耗的计算算力。 |

### 3. 数据拉取参数（Box取り込みパラメーター / Box Ingestion Parameters）

| 参数项（日文 / 英文） | 中文标准释义 | 生产建议配置值 | 详细技术说明 |
| :--- | :--- | :--- | :--- |
| **Boxフォルダー ID**<br/>*(Box Folder ID)* | 目标文件夹 ID | `431546000913`（或 `0`） | 待同步的目标 Box 目录 ID。填 `0` 则递归扫描服务账号有权访问的全部文件夹。 |
| **取り込むファイルの拡張子**<br/>*(Extensions of Files to Ingest)* | 同步文件扩展名白名单 | `pdf,docx,txt,md` | 允许拉取的文件扩展名白名单（逗号分隔，不带点号）。 |
| **Snowflakeファイルのハッシュテーブル名**<br/>*(Snowflake File Hash Table Name)* | 文件版本与哈希表名 | `BOX_DOCUMENT_METADATA` | 用于记录文件版本、SHA-256 哈希值、大小及 CDC 状态的去重台账表。 |

---

## 七、数据同步闭环实操与真机执行验证（拒绝 AI 幻觉）

启动数据同步后，文件由 Box 传输到 Snowflake。下面按照**“痛点引出 $\rightarrow$ 标准 SQL 语法 $\rightarrow$ 真机控制台执行截图与毫秒级指标”**的尚硅谷三板斧模式，对同步结果逐一验证：

### 实测环境真实性指标公示：
- **测试租户**：`aakjsrd-oq04293` (AWS Tokyo)
- **计算仓库**：`OPENFLOW_INGEST_WH` (X-Small)
- **目标数据库**：`BOX_INTEGRATION_DB`
- **执行时间与指标**：全流程包含真实执行毫秒数，截图均取自真实 Snowflake Worksheets 控制台。

---

### 实操 1：元数据台账查询与哈希对账（Metadata Reconciliation）

- **【痛点引出】**：文件搬到 Snowflake 之后，怎么知道传输过程有没有丢字节？版本是不是最新的？
- **【标准语法】**：查询元数据台账表，对比文件大小与 SHA-256 哈希值：

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

- **【真实控制台回显与真机截图】**：
执行耗时 **540ms**，成功返回 3 条文件台账记录。每个文件的 `SIZE_BYTES` 与 SHA-256 哈希值与本地原始文件 100% 吻合（PDF: 781 字节，DOCX: 1,825 字节，TXT: 1,429 字节），证明数据传输过程中**零字节损坏、零数据丢失**：

![Snowflake 工作区真实查询执行与元数据对账验证](../images/07_step_09_snowflake_stage_files.png)

---

### 实操 2：SQL 直接读取 Stage 中文本文件真实正文（Stage Query）

- **【痛点引出】**：元数据表查出来的只是“档案卡”（文件名、大小、哈希），那我能不能直接用 SQL 查出**文件内部的真实文字数据**？
- **【标准语法】**：先定义单列纯文本格式，再用带单引号的 Stage 路径或 `PATTERN` 匹配查询：

```sql
USE DATABASE BOX_INTEGRATION_DB;
USE SCHEMA BOX_LANDING_DATA;

-- 1. 创建单列纯文本读取格式 (逐行读取，不拆分逗号)
CREATE OR REPLACE FILE FORMAT BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT 
    TYPE = 'CSV' 
    FIELD_DELIMITER = NONE 
    RECORD_DELIMITER = '\n';

-- 2. 直接查询 Stage 中 03_コンプライアンス遵守チェックリスト_2026.txt 的真实正文内容
SELECT $1 AS FILE_CONTENT 
FROM '@BOX_INTEGRATION_DB.BOX_LANDING_DATA.BOX_RAW_STAGE/compliance/' 
(FILE_FORMAT => 'BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT', PATTERN => '.*03.*txt');
```

- **【真实控制台回显与真机截图】**：
执行耗时仅 **145ms**，结果集直接返回了该文件的全部 **20 行真实正文内容**（包含章节标题、各项技术点检细则等）：

![Snowflake Stage 文件真实正文直接查询执行结果](../images/07_step_10_stage_file_content_query.png)

---

### 实操 3：SQL 检索已切块的 PDF 与 Word 真实段落内容

- **【痛点引出】**：PDF 和 Word（DOCX）是复杂的二进制格式，业务上怎么精准按段落检索其中的具体条款？
- **【标准语法】**：通过长文本切片流水线入库后，直接查询 `BOX_DOC_CHUNKS` 表：

```sql
SELECT 
    FILE_NAME,
    CHUNK_INDEX,
    CHUNK_TEXT
FROM BOX_INTEGRATION_DB.CORTEX.BOX_DOC_CHUNKS
ORDER BY FILE_ID, CHUNK_INDEX;
```

- **【真实控制台回显与真机截图】**：
执行耗时 **143ms**，清晰展示了 `01_情報セキュリティ基本規程_2026.pdf` 的密码安全策略以及 `02_クラウド移行プロジェクト_機密設計書.docx` 的云上迁移专线架构设计正文：

![Snowflake Cortex 文档切片真实正文查询执行结果](../images/07_step_11_doc_chunks_content_query.png)

---

### 实操 4：生成浏览器安全预览/下载时效链接（Scoped URL）

- **【痛点引出】**：如果业务人员需要下载或在浏览器原生打开 PDF 或 Word 原版文件，怎么安全授权？
- **【标准语法】**：使用 Snowflake 内置的 `BUILD_SCOPED_FILE_URL` 函数生成时效签名 URL：

```sql
SELECT 
    RELATIVE_PATH,
    SIZE,
    -- 生成带有时效鉴权的安全下载/预览 URL
    BUILD_SCOPED_FILE_URL(@BOX_RAW_STAGE, RELATIVE_PATH) AS DIRECT_DOWNLOAD_URL
FROM DIRECTORY(@BOX_RAW_STAGE);
```

点击查询结果中的 URL，浏览器即可直接调用内置 PDF 阅读器进行预览或无损下载。

---

## 八、实战避坑与故障排查（重点暗坑与费用防吞噬指南）

在实际工程落地中，新手最常踩进以下 4 个坑。本节直面问题，给出经过验证的避坑解法：

### 避坑 1：Stage 路径中包含多字节字符报错（`unexpected 'コン'`）

> [!WARNING] **【现象与报错信息】**  
> 在 Snowflake Worksheets 中直接书写如下语句：
> ```sql
> SELECT $1 FROM @BOX_RAW_STAGE/compliance/03_コンプライアンス遵守チェックリスト_2026.txt;
> ```
> 系统抛出编译错误：`SQL compilation error: syntax error line 22 at position 34 unexpected 'コン'.`

- **根因分析**：Snowflake 的 SQL 词法解析器在解析未加单引号的 Stage 路径时，仅支持 ASCII 字符，读到中文或日文字符时会被截断并视为非法标识符。
- **标准避险方案**：
  1. 使用单引号将完整 Stage 路径包裹起来：`FROM '@BOX_RAW_STAGE/compliance/03_...'`；
  2. 或者使用父目录加 `PATTERN` 正则匹配：`FROM '@BOX_RAW_STAGE/compliance/' (PATTERN => '.*03.*txt')`。

---

### 避坑 2：Trial 试用账户调用 `AI_PARSE_DOCUMENT` 报错

> [!WARNING] **【现象与报错信息】**  
> 调用多模态文档解析函数时：
> ```sql
> SELECT SNOWFLAKE.CORTEX.PARSE_DOCUMENT('@BOX_RAW_STAGE', '01_安全密码规范.pdf', {'mode': 'LAYOUT'});
> ```
> 报错提示：`SNOWFLAKE.CORTEX.PARSE_DOCUMENT is not available on this account`，或者：  
> `AI function _AI_PARSE_DOCUMENT is not available for trial accounts.`

- **根因分析**：
  1. **前缀弃用升级**：新版 Snowflake 已全面弃用 `SNOWFLAKE.CORTEX.` 前缀，统一升级为顶层 SQL 函数 `AI_PARSE_DOCUMENT` 与 `AI_SUMMARIZE`；
  2. **Trial 试用账户配额保护**：文档布局解析与 OCR 消耗极高 GPU 算力，Snowflake 官方在 **30 天免费试用（Free Trial）账户中全局禁用了 `AI_PARSE_DOCUMENT`**。
- **标准避险方案**：
  - **企业生产环境**：升级为付费/企业版后即可直接使用 `AI_PARSE_DOCUMENT`；
  - **学习与验证环境**：如本章实测所示，使用 **Stage 文本格式直读（`TXT_FORMAT`）**、**Snowpark Python 二进制流读取（`SnowflakeFile.open`）** 以及 **`BOX_DOC_CHUNKS` 结构化表**，即可完美跑通端到端的数据同步与检索验证。

---

### 避坑 3：生成公私钥对时弹出 2FA 阻断

> [!WARNING] **【现象与报错信息】**  
> 在 Box Developer Console 点击「Generate a Public/Private Keypair」时，页面弹出阻断提示：`2-Step Verification Required`。

- **根因分析**：Box 平台强制要求创建具有企业级访问权限的私钥必须先通过两步验证以防泄密。
- **标准避险方案**：进入 Box 账号「Account Settings」$\rightarrow$「Security」，开启 SMS 短信验证或 Google Authenticator 绑定后，重新点击生成即可顺利下载 `config.json`。

---

### 避坑 4：`CORTEX SEARCH SERVICE` 设置 `TARGET_LAG` 导致 400 美元额度几天内被耗尽！

> [!CAUTION] **【重大暗坑 · 真实惨案现场】**  
> 刚注册 7~8 天的试用账号，满心以为“30 天免费试用还早得很”，结果某天登录时突然被全屏遮罩强行拦截：  
> `Your free trial has ended and all of your virtual warehouses have been suspended.`  
> 控制台要求立即输入信用卡升级为 Pay-As-You-Go，所有虚拟仓库被强制关停，无法执行任何 SQL！

![Snowflake 试用账户算力限制与阻断真实界面](../images/07_step_11_snowflake_trial_expired.png)

- **根因深度分析**：
  1. **官方试用规则真相**：Snowflake 官网对 Free Trial 的官方定义是 **“30 天 或 400 美元计算额度，二者以先到者为准（Whichever comes first）”**。400 美元折算下来仅约 **130 ~ 150 个 Credits**！
  2. **持续调度后台任务偷跑费用**：在配置 Cortex Search Service 时，如果书写了如下生产语句：
     ```sql
     CREATE OR REPLACE CORTEX SEARCH SERVICE BOX_ENTERPRISE_SEARCH_SERVICE
         ON CHUNK_TEXT
         ATTRIBUTES USER_EMAILS, FILE_NAME, FOLDER_ID
         WAREHOUSE = OPENFLOW_INGEST_WH
         TARGET_LAG = '1 hour'   -- ⚠️ 关键元凶：设置了 1 小时自动同步时延！
     ```
     `CORTEX SEARCH` 底层是一个 **Serverless 持续索引守护任务**。设置了 `TARGET_LAG = '1 hour'`，意味着 Snowflake 无论前台有没有人在操作，**每隔 1 小时都会自动唤醒后台引擎，对文本块重新进行向量化与增量构建索引**！
     整整 7 天（168 小时），后台默默调度了 160 多次向量计算，加上多个未设极速休眠的计算仓库，直接把赠送的 400 美元额度烧得一干二净！

- **工业级生产与教学避险三铁律**：
  1. **实验验证完毕后立即销毁后台守护服务（防偷跑第一定律）**：  
     在教学演练或概念验证（PoC）阶段，一旦完成检索验证，**必须在 SQL 中立即执行清理语句**，杜绝后台持续空转：
     ```sql
     -- 验证完毕后，立即删除持续索引服务（数据表仍保留，但停止后台按小时扣费）
     DROP CORTEX SEARCH SERVICE IF EXISTS BOX_INTEGRATION_DB.CORTEX.BOX_ENTERPRISE_SEARCH_SERVICE;
     ```
  2. **强制所有 Warehouse 开启 60 秒极速休眠**：
     ```sql
     ALTER WAREHOUSE OPENFLOW_INGEST_WH SET AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
     ```
  3. **一旦试用额度耗尽的处理方案（切勿盲目输入信用卡）**：  
     如果您只是学习和验证技术，**完全不需要输入个人银行卡**！直接换一个新邮箱在 Snowflake 官网重新开一个 30 天试用租户，瞬间重获全新的 30 天 + 400 美元额度，之前编写的表结构与 SQL 代码一键重新刷入即可。

---

## 本章小结

本章严格按照**尚硅谷技术讲义标准**完成了非结构化文件数据同步实战：
1. **去业务化，聚焦底层**：摆脱特定金融业务干扰，纯粹验证“文件从云盘安全同步至数据仓库”的技术闭环；
2. **全参数透明拆解**：对 `CREATE USER (TYPE = SERVICE)`、`CREATE WAREHOUSE`、`CREATE STAGE (DIRECTORY = TRUE)` 及元数据与切块表全字段配置项进行了逐行深度解析；
3. **分层清晰，职责明确**：
   - **Stage** 保障文件原始字节流的安全落盘；
   - **元数据表** 基于 SHA-256 哈希值实现 100% 数据一致性对账；
   - **切块表与 Stage 直读** 提供高效的 SQL 内容检索能力。
4. **真实回显，拒绝幻觉**：全流程提供取自真实 Snowflake 租户（`aakjsrd-oq04293`）的控制台截图、540ms/145ms/143ms 等精确执行指标以及真实的配额边界避坑方案。
