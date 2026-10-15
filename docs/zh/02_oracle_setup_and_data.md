# 第 02 章：Oracle 迁移源环境搭建与模拟数据准备

银行证券传统架构中，顾客交易明细流水记录在基于本地基础设施的 Oracle 11g 数据库实例中。

为了还原真实业务场景，本章演示如何通过 Docker 极速拉起 Oracle 11g 数据库容器、使用 VSCode Database Client 进行连接测试、创建核心交易表 `CUST_TRADE_DETAIL` 并灌入 11 组高覆盖率的金融测试数据集。

---

## 1. Docker 安装与拉起 Oracle 11g 容器

### 步骤 1：拉取 Oracle 11g XE 镜像
```bash
sudo docker pull gvenzl/oracle-xe:11
```

### 步骤 2：启动容器
配置共享内存 `--shm-size=1g`，映射端口 `1521`，并将数据持久化挂载至本地目录：
```bash
sudo docker run -d \
  --name mitsui_oracle_11g \
  --restart always \
  -e ORACLE_PASSWORD=Mitsui_Sec_2026 \
  -p 1521:1521 \
  --shm-size=1g \
  -v "$PWD/oradata":/opt/oracle/oradata \
  gvenzl/oracle-xe:11
```

---

## 2. VSCode Database Client 连接测试

在 VSCode 中安装 **Database Client** 插件，配置连接参数：
- **Host**: `127.0.0.1` (或 WSL 宿主机 IP)
- **Port**: `1521`
- **Database/SID**: `xe`
- **User**: `system`
- **Password**: `Mitsui_Sec_2026`

![VSCode连接配置](../images/02_img_01.png)

点击连接测试，成功连接至 Oracle 数据库：
![连接成功效果](../images/02_img_02.png)

---

## 3. 核心业务表 DDL：`CUST_TRADE_DETAIL` (顧客取引明細)

以 `system` 登录数据库后，执行建表语句：

```sql
CREATE TABLE CUST_TRADE_DETAIL (
    -- ① 数値情報：初期設定（一般数値）
    -- 対応ルール：Number(15) / 小数なし / 初期値0
    TRADE_QTY          NUMBER(15)        DEFAULT 0        NOT NULL,  -- 取引数量（例：1000株 → 1000）

    -- ② 数値情報：金額（邦貨）
    -- 対応ルール：Number(18,3) 固定（取得元精度に関わらず統一）
    AMOUNT_JPY         NUMBER(18,3)      DEFAULT 0        NOT NULL,  -- 約定金額・円貨（例：12,345,678.900）

    -- ③ 数値情報：金額（外貨）＋通貨区分（ペア定義必須）
    -- 対応ルール：Number(18,3) ＋ 通貨区分をセットで持つ
    AMOUNT_FCY         NUMBER(18,3)      DEFAULT 0,                  -- 約定金額・外貨（例：98,765.500）
    CCY_CODE           VARCHAR2(3),                                  -- 通貨区分（例："USD","EUR"）

    -- ④ 数値情報：レート／率
    -- 対応ルール：Number(9,6)
    EXCHANGE_RATE      NUMBER(9,6),                                  -- 為替レート（例：1.234567）

    -- ⑤ 文字情報：初期設定（一般文字）
    -- 対応ルール：Varchar2(100 CHAR) / 初期値 半角スペース1桁
    -- ★CHAR語義に変更。全角文字混在時の桁あふれを防止し、Snowflake移行後のVARCHAR(100)（文字数カウント）と意味を統一する
    REMARKS            VARCHAR2(100 CHAR) DEFAULT ' ',               -- 摘要・備考

    -- ⑥ 文字情報：参照元項目桁が確定している項目
    -- 対応ルール：顧客管理システム定義=10桁、CHAR語義に統一
    CUST_ID            VARCHAR2(10 CHAR)  NOT NULL,                  -- 顧客ID（参照元：顧客管理システム）

    -- ⑦ 文字情報：ID・区分
    TRADE_TYPE_CD      VARCHAR2(2 CHAR)   NOT NULL,                  -- 取引区分（例："01"=買付,"02"=売付）
    BRANCH_CD          VARCHAR2(4 CHAR)   NOT NULL,                  -- 支店コード

    -- ⑧ 日付情報を保持する項目
    -- Oracle側はDATE型（Snowflake移行後はVarchar(8)/YYYYMMDD または DATEへ変換予定）
    TRADE_DATE         DATE               NOT NULL,                  -- 約定日（基準年月日：日次）
    SETTLE_MONTH       DATE,                                         -- 決済対象月（例：'2025-03-01' で 2025年3月を表現）

    -- ⑨ 時刻情報を保持する項目
    -- Oracle側はDATE型（秒まで保持／Snowflake移行後はTimestamp_ntz(6)へ変換予定）
    REG_DATETIME       DATE               DEFAULT SYSDATE NOT NULL,  -- 登録日時
    UPD_DATETIME       DATE,                                         -- 更新日時

    CONSTRAINT PK_CUST_TRADE_DETAIL PRIMARY KEY (CUST_ID, TRADE_DATE, TRADE_TYPE_CD)
);
```

---

## 4. 模拟测试数据集（覆盖金融极值与全角边界）

执行 [`scripts/oracle/02_seed_trades_data.sql`](file:///home/fx/Develop/SnowflakeBlog/scripts/oracle/02_seed_trades_data.sql)，灌入具有代表性的测试样本：

1. **通常取引・国内株式**（基础标杆）
2. **外国株式・米国口座**（USD 汇率与外币金额）
3. **外国債券・欧州発行**（EUR 汇率）
4. **境界値テスト・最大桁数**（`999999999999999` 最大值极限测试）
5. **最小限必須項目**（仅填主键，校验默认值与 NULL 兼容）
6. **零金额零数量交易**（撤单与月次集计跑批）
7. **全角・半角混在摘要**（中日英符号测试）
8. **全角100字符百字边界**（验证 `CHAR` 语义在全角下的有效性）
9. **訂正取引**（更新时间戳 `UPD_DATETIME` 测试）
10. **低额汇率货币**（印尼盾 `IDR`，多位小数 0.000120 汇率测试）
11. **年末跨年交易**（12月31日 23:58:59 跨年与时间边界）

确认入库统计：
```sql
SELECT COUNT(*) AS TOTAL_ROWS, SUM(AMOUNT_JPY) AS SUM_JPY, SUM(TRADE_QTY) AS SUM_QTY
FROM CUST_TRADE_DETAIL;
```
此基准数据将用于后续的 Snowflake 数据一致性突合验证。
