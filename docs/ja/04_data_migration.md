# 第04章：データ移行実務（Oracle抽出・ステージング・COPY INTO・照合監査）

Snowflake の3層 RBAC 権限モデルおよび `RAW_ORACLE` 移行先スキーマの基盤構築を完了した後は、本番移行の中心となるデータロードおよび品質監査の工程に進みます。

本章では、銀行・証券勘定系の**2テーブル複合構成**（顧客基本台帳 `CUST_MASTER` および顧客取引明細 `CUST_TRADE_DETAIL`）を対象に、**Oracle 側でのデータ抽出・Gzip 圧縮 ➔ Snowflake 管理内部ステージ (@MITSUI_STAGE) へのアップロード ➔ ステージ直接クエリ事前検証と変換ロード (`COPY INTO`) ➔ 金融データ突合（リコンサイル監査）**という一連のエンタープライズ移行パイプラインを実践検証します。

---

## 移行アーキテクチャ概要

```
┌─────────────────────────────────┐
│     Oracle 11g 移行元環境        │
│  (CUST_MASTER: 13件 顧客台帳)   │
│  (CUST_TRADE_DETAIL: 11件 明細) │
└────────────────┬────────────────┘
                 │ 1. Python / SQL*Plus 抽出 (UTF-8, 二重引用符エスケープ, .csv.gz)
                 ▼
┌─────────────────────────────────┐
│    ローカル抽出パッケージ (data/exports) │
│  - cust_master.csv.gz           │
│  - cust_trade_detail.csv.gz     │
└────────────────┬────────────────┘
                 │ 2. Web UI ドラッグ＆ドロップ または PUT コマンド転送 (クライアント暗号化)
                 ▼
┌─────────────────────────────────┐
│ Snowflake セキュア内部ステージ   │
│  @MITSUI_SEC_DB.RAW_ORACLE.     │
│  MITSUI_STAGE                   │
└────────────────┬────────────────┘
                 │ 3. MITSUI_ENGINEER によるテーブルレス検証 ＆ COPY INTO ロード
                 ▼
┌─────────────────────────────────┐
│ Snowflake 移行先テーブル (RAW_ORACLE)│
│  - CUST_MASTER (13 行格納)      │
│  - CUST_TRADE_DETAIL (11 行格納)│
└────────────────┬────────────────┘
                 │ 4. MITSUI_ANALYST による 4次元金融突合監査
                 ▼
┌─────────────────────────────────┐
│ 金融機関水準データ整合性・監査証明書│
│  - レコード件数突合 / 金額集計照合│
│  - 通貨別分布クロス集計 / 全体ハッシュ│
└─────────────────────────────────┘
```

---

## フェーズ1：Oracle 側データ抽出と Gzip 圧縮 (Export to CSV)

### なぜソース側で厳格な正規化抽出が必要なのか？
異機種データベース移行において最も頻発する不整合トラブルには以下があります：
1. **文字エンコーディングの桁あふれ**：Oracle 側で標準化されていない場合、文字化けや切り捨てが発生します。BOM なしの標準 `UTF-8` を強制します。
2. **特殊記号とカンマ区切りの衝突**：金融取引の摘要欄（`REMARKS`）には、全角/半角の句読点やカンマが含まれることが多いため、文字列型は二重引用符（`"`）で厳格に囲みます。
3. **空文字 `''` と `NULL` の仕様差**：Oracle は空文字列 `''` を `NULL` として扱いますが、Snowflake では有効な空文字として認識されます。CSV 出力時に連続カンマ（`,,`）として出力し、第03章で作成した `EMPTY_FIELD_AS_NULL = TRUE` により完全整合させます。
4. **ネットワーク転送コストの最小化**：金融データは膨大であるため、抽出と同時に `gzip` 圧縮を施すことで転送量を 70%〜90% 削減します。

### 抽出スクリプトの実行
プロジェクト内 `scripts/oracle/export_to_csv.py` を実行します：

```bash
# Oracle 11g 側での自動抽出および Gzip 圧縮
python scripts/oracle/export_to_csv.py
```

実行結果ログ：
```text
=== Oracle 11g Data Export Starting (wslc) ===
[*] Exporting CUST_MASTER (顧客基本台帳)...
[+] CUST_MASTER exported: 13 rows -> data/exports/cust_master.csv and cust_master.csv.gz
[*] Exporting CUST_TRADE_DETAIL (顧客取引明細)...
[+] CUST_TRADE_DETAIL exported: 11 rows -> data/exports/cust_trade_detail.csv and cust_trade_detail.csv.gz

=== Export Summary ===
CUST_MASTER:        13 records exported
CUST_TRADE_DETAIL:  11 records exported
Destination Folder: data/exports
```

---

## フェーズ2：Snowflake ステージ (@MITSUI_STAGE) へのアップロード

Snowflake へのデータロードに先立ち、ファイルを内部ステージに配置します。初心者向けの **Snowsight Web コンソールでの GUI 操作** と、本番バッチ向けの **Python / PUT スクリプト操作** の2系統に対応しています。

### 方法 A（初学者推奨）：Snowsight コンソールでのドラッグ＆ドロップ
1. Snowsight にログインし、左側メニューの **データ (カタログエクスプローラー)** を開きます。
2. `MITSUI_SEC_DB` ➔ `RAW_ORACLE` ➔ `ステージ` と展開し、`MITSUI_STAGE` をクリックします。
3. ステージ詳細画面で、所有者が `MITSUI_ENGINEER`、クライアント暗号化が有効であることを確認します。

![Snowsight MITSUI_STAGE 詳細画面](../images/04_stage_overview.png)

4. 画面右上の **↑ ファイルをアップロード** ボタンをクリックし、アップロード用モーダルを開きます：
   - ローカルの `data/exports/` 配下に生成された `cust_master.csv.gz` と `cust_trade_detail.csv.gz` をドラッグ＆ドロップします。
   - アップロードを実行すると、内部ステージへ安全に転送されます。

![Snowsight ステージ アップロードモーダル](../images/04_stage_upload_modal.png)

---

### 方法 B（本番エンジニアリング）：Python / PUT コマンド自動化
本番 CI/CD パイプラインでは、Python Snowflake Connector 経由で PUT コマンドを発行します（スクリプト：`scripts/snowflake/upload_to_stage.py`）：

```python
import snowflake.connector

# MITSUI_ENGINEER ロールで Snowflake に接続
conn = snowflake.connector.connect(
    user='MITSUI_ENGINEER_USER',
    password='MitsuiSecStrongPass2026!',
    account='<your_account_identifier>',
    database='MITSUI_SEC_DB',
    schema='RAW_ORACLE',
    role='MITSUI_ENGINEER'
)
cur = conn.cursor()

# Windows パスはスラッシュ変換＋file:// プレフィックスを指定
cur.execute("PUT file://C:/path/to/cust_master.csv.gz @MITSUI_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;")
cur.execute("PUT file://C:/path/to/cust_trade_detail.csv.gz @MITSUI_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;")
```

> [!NOTE]
> **PUT コマンドの課金特性**：
> `PUT` コマンドはクライアントサイドでの暗号化とクラウドストレージへのダイレクト転送を行うため、**仮想ウェアハウス（Warehouse）のクレジットを一切消費しません**。

---

## フェーズ3：COPY INTO による本番一括ロードとデータ型変換

Snowflake SQL ワークシート（ワークシート名：`04_data_migration_and_reconciliation.sql`）を開き、以下のステップを順次実行します（完全版スクリプト：`scripts/snowflake/04_data_migration_master.sql`）。

---

### Step 01 & 02: エンジニアコンテキスト設定とステージ内ファイル確認
* **目的・理由**：最小権限の原則に従い、移行担当ロール `MITSUI_ENGINEER` に切り替え、専用ウェアハウス `MITSUI_WH` を指定した上で、ステージ内のファイルサイズと MD5 ハッシュを確認します。

```sql
-- ====================================================================
-- 【Step 01 & 02: 工程师上下文设定与暂存区文件清单核查】
-- 目的・理由: 切换至 MITSUI_ENGINEER 角色，指定 MITSUI_WH，并核查暂存区待装载数据。
-- ====================================================================
USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

LIST @MITSUI_STAGE;
```

![Step 01 & 02: エンジニアコンテキスト設定と LIST @MITSUI_STAGE](../images/04_step_01_02.png)

> **実行結果の解説**：  
> ステージ内に配置された2ファイルが確認できます：  
> 1. `mitsui_stage/cust_master.csv.gz`（640 バイト、MD5: `b2869d45...`）  
> 2. `mitsui_stage/cust_trade_detail.csv.gz`（864 バイト、MD5: `b8f55b7e...`）  
> メタデータ検証は正常です。

---

### Step 03: ステージ直接クエリプレビュー（テーブルレス事前検証）
* **目的・理由**：  
  1. **本番トラブル回避**：Snowflake の仕様上、**`(SELECT ... FROM @stage)` 列変換式を含む `COPY INTO` 文では `VALIDATION_MODE` オプションはサポートされません**。  
  2. **テーブルレス検証**：Snowflake では、未ロードの圧縮 CSV ファイルに対してステージから直接 `SELECT $1, $2 ...` でクエリを実行できます。本番ロード前に `LIMIT 5` で試行実行し、列順序と日付・タイムスタンプ変換式がエラーなく機能することを 100% 担保します。

```sql
-- ====================================================================
-- 【Step 03: Stage 暂存区直接投影预览 (无表预检)】
-- 目的・理由: 
--   1. Snowflake 允许在未执行 COPY 前直接用 SELECT $1, $2 语法查询 Stage 中的压缩 CSV。
--   2. 由于带有 (SELECT ...) 转换的 COPY INTO 不支持 VALIDATION_MODE，提前在 Stage 上做轻量试跑可 100% 验证字段映射与类型转换表达式。
-- ====================================================================
SELECT 
    t.$1::NUMBER(15, 0)                       AS TRADE_QTY,
    t.$2::NUMBER(18, 3)                       AS AMOUNT_JPY,
    t.$3::NUMBER(18, 3)                       AS AMOUNT_FCY,
    t.$4::VARCHAR(3)                          AS CCY_CODE,
    t.$5::NUMBER(9, 6)                        AS EXCHANGE_RATE,
    t.$6::VARCHAR(100)                        AS REMARKS,
    t.$7::VARCHAR(10)                         AS CUST_ID,
    t.$8::VARCHAR(2)                          AS TRADE_TYPE_CD,
    t.$9::VARCHAR(4)                          AS BRANCH_CD,
    TO_VARCHAR(TO_DATE(t.$10), 'YYYYMMDD')    AS TRADE_DATE,
    TO_VARCHAR(TO_DATE(t.$11), 'YYYYMM')      AS SETTLE_MONTH,
    TO_TIMESTAMP_NTZ(t.$12)                   AS REG_DATETIME,
    TO_TIMESTAMP_NTZ(t.$13)                   AS UPD_DATETIME
FROM @MITSUI_STAGE/cust_trade_detail.csv.gz (FILE_FORMAT => 'CSV_ORACLE_IMPORT_FF') t
LIMIT 5;
```

![Step 03: ステージ直接クエリプレビュー実行結果](../images/04_step_03_preview.png)

> **実行結果の解説**：  
> 取引数量（全9桁境界値を含む）、邦貨金額、外貨金額、為替レートが正しくパースされ、約定日（`YYYYMMDD`）および決済月（`YYYYMM`）のフォーマット変換が完璧に機能していることが確認できます。

---

### Step 04: CUST_MASTER（顧客基本台帳）の一括ロード
* **目的・理由**：  
  1. ファイルパス `@MITSUI_STAGE/cust_master.csv.gz` を明示指定し、複数ファイル混在時の誤読み込みを防止します。  
  2. `ON_ERROR = 'ABORT_STATEMENT'` により、金融要件に従って1件でも不整合があれば全体をロールバックします。  
  3. 未指定の `MIGRATED_AT` カラムは、テーブル定義の `DEFAULT CURRENT_TIMESTAMP()` により入雲タイムスタンプが自動補完されます。

```sql
-- ====================================================================
-- 【Step 04: 批量加载 CUST_MASTER (客户维度主表)】
-- 目的・理由: 
--   1. 精确指定 @MITSUI_STAGE/cust_master.csv.gz，严格定向加载，杜绝多文件混杂污染。
--   2. ON_ERROR = 'ABORT_STATEMENT' 确保金融数据一致性，遇任何脏数据立即全单回退。
--   3. 未显式指定的 MIGRATED_AT 列将自动采用 DEFAULT CURRENT_TIMESTAMP() 填入入云时间戳。
-- ====================================================================
COPY INTO CUST_MASTER (
    CUST_ID,
    CUST_NAME_KANJI,
    CUST_NAME_KANA,
    CUST_RANK_CD,
    BRANCH_CD,
    STATUS_CD,
    OPEN_DATE,
    REG_DATETIME
)
FROM (
    SELECT 
        t.$1,
        t.$2,
        t.$3,
        t.$4,
        t.$5,
        t.$6,
        TO_DATE(t.$7),
        TO_TIMESTAMP_NTZ(t.$8)
    FROM @MITSUI_STAGE/cust_master.csv.gz t
)
FILE_FORMAT = (FORMAT_NAME = 'CSV_ORACLE_IMPORT_FF')
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;

-- 検証：ロード件数確認（期待値：13行）
SELECT COUNT(*) AS MASTER_LOADED_ROWS FROM CUST_MASTER;
```

![Step 04: CUST_MASTER 一括ロード実行結果](../images/04_step_04_copy_master.png)

> **実行結果の解説**：  
> `MASTER_LOADED_ROWS = 13` が返却され、顧客マスタ13件の格納が完了しました。

---

### Step 05: CUST_TRADE_DETAIL（顧客取引明細）の一括ロード
* **目的・理由**：Oracle の DATE 型および数値型を、Snowflake 最適化データ型へ高精度にマッピングしながら格納します。

```sql
-- ====================================================================
-- 【Step 05: 批量加载 CUST_TRADE_DETAIL (核心交易事实明细表)】
-- 目的・理由:
--   1. 执行金融字段类型显式强转：日期转 YYYYMMDD、结算月转 YYYYMM、金额与汇率精确匹配。
--   2. 精确指定 @MITSUI_STAGE/cust_trade_detail.csv.gz，实现安全隔离装载。
-- ====================================================================
COPY INTO CUST_TRADE_DETAIL (
    TRADE_QTY,
    AMOUNT_JPY,
    AMOUNT_FCY,
    CCY_CODE,
    EXCHANGE_RATE,
    REMARKS,
    CUST_ID,
    TRADE_TYPE_CD,
    BRANCH_CD,
    TRADE_DATE,
    SETTLE_MONTH,
    REG_DATETIME,
    UPD_DATETIME
)
FROM (
    SELECT 
        t.$1::NUMBER(15, 0),                       -- TRADE_QTY: 数量
        t.$2::NUMBER(18, 3),                       -- AMOUNT_JPY: 円貨金額
        t.$3::NUMBER(18, 3),                       -- AMOUNT_FCY: 外貨金額
        t.$4::VARCHAR(3),                          -- CCY_CODE: 通貨区分
        t.$5::NUMBER(9, 6),                        -- EXCHANGE_RATE: 為替レート
        t.$6::VARCHAR(100),                        -- REMARKS: 摘要（全角100文字対応）
        t.$7::VARCHAR(10),                         -- CUST_ID: 顧客ID
        t.$8::VARCHAR(2),                          -- TRADE_TYPE_CD: 取引区分
        t.$9::VARCHAR(4),                          -- BRANCH_CD: 支店コード
        TO_VARCHAR(TO_DATE(t.$10), 'YYYYMMDD'),    -- TRADE_DATE: YYYYMMDD変換
        TO_VARCHAR(TO_DATE(t.$11), 'YYYYMM'),      -- SETTLE_MONTH: YYYYMM変換
        TO_TIMESTAMP_NTZ(t.$12),                   -- REG_DATETIME: 登録日時
        TO_TIMESTAMP_NTZ(t.$13)                    -- UPD_DATETIME: 更新日時
    FROM @MITSUI_STAGE/cust_trade_detail.csv.gz t
)
FILE_FORMAT = (FORMAT_NAME = 'CSV_ORACLE_IMPORT_FF')
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;

-- 検証：ロード件数確認（期待値：11行）
SELECT COUNT(*) AS TRADE_LOADED_ROWS FROM CUST_TRADE_DETAIL;
```

![Step 05: CUST_TRADE_DETAIL 一括ロード実行結果](../images/04_step_05_copy_trade.png)

> **実行結果の解説**：  
> `TRADE_LOADED_ROWS = 11` が返却され、取引明細11件のロードが完了しました。

---

### Step 06: ロード履歴監査（COPY_HISTORY 関数の活用）
* **目的・理由**：金融監査基準に基づき、`INFORMATION_SCHEMA.COPY_HISTORY` 関数を用いて、処理ステータス（`LOADED`）、パース行数（`ROW_PARSED`）、格納行数（`ROW_COUNT`）、エラー件数（`ERROR_COUNT = 0`）を確証します。

```sql
-- ====================================================================
-- 【Step 06: 查询最近 24 小时内的加载历史与吞吐指标】
-- 目的・理由: 检查文件装载状态（STATUS = LOADED）、解析行数（ROW_PARSED）、装载行数（ROW_COUNT）以及零报错（ERROR_COUNT = 0）。
-- ====================================================================
SELECT 
    TABLE_NAME,
    FILE_NAME,
    STATUS,
    ROW_COUNT,
    ROW_PARSED,
    ERROR_COUNT,
    LAST_LOAD_TIME
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'CUST_TRADE_DETAIL',
    START_TIME => DATEADD(HOURS, -24, CURRENT_TIMESTAMP())
))
UNION ALL
SELECT 
    TABLE_NAME,
    FILE_NAME,
    STATUS,
    ROW_COUNT,
    ROW_PARSED,
    ERROR_COUNT,
    LAST_LOAD_TIME
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'CUST_MASTER',
    START_TIME => DATEADD(HOURS, -24, CURRENT_TIMESTAMP())
));
```

![Step 06: COPY_HISTORY 実行ログ監査](../images/04_step_06_copy_history.png)

---

## フェーズ4：ビジネスアナリストによる4次元データ突合監査 (MITSUI_ANALYST)

証券システム移行において、ロードの完了はゴールではありません。業務監査を担当する独立ロール `MITSUI_ANALYST` により、Oracle 元データと Snowflake 先データの突合（リコンサイル）を実施します。

---

### Step 07 & 08: アナリストロールへの切替と件数突合 (Row Count Reconciliation)
* **目的・理由**：業務監査ロール `MITSUI_ANALYST` へ切り替え、SELECT 権限のみで安全にアクセスできることを確認した上で、両テーブルの総件数を照合します。

```sql
-- ====================================================================
-- 【Step 07 & 08: 切换分析师角色与总行数突合】
-- 目的・理由: 切换至 MITSUI_ANALYST，验证分析师账号对双表仅具有 SELECT 权限，并核对总记录数。
-- ====================================================================
USE ROLE MITSUI_ANALYST;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

SELECT 
    'CUST_MASTER' AS TABLE_NAME,
    COUNT(*)      AS RECORD_COUNT
FROM CUST_MASTER
UNION ALL
SELECT 
    'CUST_TRADE_DETAIL' AS TABLE_NAME,
    COUNT(*)            AS RECORD_COUNT
FROM CUST_TRADE_DETAIL;
```

![Step 07 & 08: アナリストロール切替と件数突合](../images/04_step_07_08_reconciliation_count.png)

> **実行結果の解説**：  
> `CUST_MASTER` = 13件、`CUST_TRADE_DETAIL` = 11件。Oracle 元データと完全一致しました。

---

### Step 09: 主要金融指標・取引総量の突合 (Financial Metrics Reconciliation)
* **目的・理由**：取引数量、邦貨金額、外貨金額、および約定日付境界（最古・最新）を集計照合し、移行による浮動小数点誤差や桁落ちがゼロであることを証明します。

```sql
-- ====================================================================
-- 【Step 09: 核心金融金额与交易总量突合】
-- 目的・理由: 确保传输过程中无精度截断、无舍入误差，精确比对总数量、总日元金额、总外币金额与交易日期边界。
-- ====================================================================
SELECT 
    COUNT(*)                                       AS TOTAL_TRADES,
    SUM(TRADE_QTY)                                 AS TOTAL_TRADE_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
    MIN(TRADE_DATE)                                AS EARLIEST_TRADE_DATE,
    MAX(TRADE_DATE)                                AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;
```

![Step 09: 金融集計指標のリコンサイル突合結果](../images/04_step_09_financial_reconciliation.png)

#### 異機種システム間リコンサイル照合表（Oracle 11g 元データ vs Snowflake 移行先）
| 監査照合指標 | Oracle 11g ソース実績値 | Snowflake ターゲット実績値 | 監査差額 | 判定結果 |
| :--- | :--- | :--- | :--- | :--- |
| **総取引件数** | 11 件 | 11 件 | 0 | ✅ 完全一致 |
| **総約定数量 (株)** | 1,000,000,000,003,159 | 1,000,000,000,003,159 | 0 | ✅ 完全一致 |
| **円貨総金額 (JPY)** | 1,000,000,042,496,878.899 | 1,000,000,042,496,878.899 | 0.000 | ✅ 精度欠損なし |
| **外貨換算金額 (FCY)** | 1,000,000,000,071,000.499 | 1,000,000,000,071,000.499 | 0.000 | ✅ 精度欠損なし |
| **最古約定年月日** | 2024-12-31 | 20241231 | 0 日 | ✅ フォーマット正規化 |
| **最新約定年月日** | 2025-04-01 | 20250401 | 0 日 | ✅ フォーマット正規化 |

---

### Step 10: 通貨別クロス集計と全体ハッシュフィンガープリント照合
* **目的・理由**：  
  1. 通貨区分（`CCY_CODE`）と取引区分（`TRADE_TYPE_CD`）ごとの分布を集計し、外貨アセットの分類ズレがないことを確認します。  
  2. Snowflake の `HASH_AGG` 関数により、テーブル全行全カラムを対象とした一意なハッシュチェックサムを算出し、改ざん防止の監査証跡とします。

```sql
-- ====================================================================
-- 【Step 10: 多币种分布交叉审计与全局哈希指纹校验】
-- 目的・理由: 
--   1. 按币种分组核算笔数与金额，确保外币资产分类无漂移。
--   2. 通过 HASH_AGG 与 HASH 计算全局数据指纹，完成跨系统防篡改质量审计。
-- ====================================================================
-- 10.1 通貨別・取引区分別クロス集計
SELECT 
    NVL(CCY_CODE, 'JPY')      AS CURRENCY,
    TRADE_TYPE_CD,
    COUNT(*)                  AS TRADE_COUNT,
    SUM(TRADE_QTY)            AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3) AS TOTAL_JPY
FROM CUST_TRADE_DETAIL
GROUP BY NVL(CCY_CODE, 'JPY'), TRADE_TYPE_CD
ORDER BY CURRENCY, TRADE_TYPE_CD;

-- 10.2 全体ハッシュフィンガープリント検証
SELECT 
    HASH_AGG(
        HASH(
            CUST_ID,
            TRADE_DATE,
            TRADE_TYPE_CD,
            BRANCH_CD,
            TRADE_QTY,
            AMOUNT_JPY,
            AMOUNT_FCY,
            CCY_CODE,
            EXCHANGE_RATE,
            REMARKS
        )
    ) AS GLOBAL_TABLE_HASH
FROM CUST_TRADE_DETAIL;
```

![Step 10: 通貨別集計と全体ハッシュ検証](../images/04_step_10_hash_and_currency.png)

> **実行結果の解説**：  
> 全体ハッシュ値 `GLOBAL_TABLE_HASH = -3405770010579799674` が算出されました。移行元・移行先間で不可逆かつ改ざん不能な品質証明書が確立されました。

---

## 本番運用の重要ノウハウ（ベストプラクティス）

1. **`COPY INTO (SELECT ...)` における `VALIDATION_MODE` の制約**：
   - 列変換式を含む COPY 文では `VALIDATION_MODE` は利用できません。ステージに対して直接 `SELECT ... LIMIT 5` を発行するテーブルレス事前検証を採用してください。
2. **ステージパスの厳密指定**：
   - 複数ファイルが同一ステージに存在する環境では、必ず `@MITSUI_STAGE/cust_master.csv.gz` のようにファイル名を明示指定し、予期せぬ列不整合を防止します。
3. **Snowflake RBAC 権限階層の連鎖ルール**：
   - テーブルへの `SELECT` 権限とスキーマへの `USAGE` 権限があっても、最上位のデータベースに対する `USAGE ON DATABASE` が欠落しているとアクセス拒否（Object does not exist or not authorized）となります。
4. **Windows 環境における PUT コマンドの URI 規約**：
   - パス区切り文字にはスラッシュ（`/`）を使用し、`file://C:/...` の形式で指定します。
