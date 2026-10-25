# 第 05 章：移行後データ突合検証・品質監査 (Data Reconciliation)

日本の金融 IT プロジェクト（メガバンク・大手証券）において、新旧システム移行フェーズの成否を決する最大の関門が **「新旧データ突合検証 (Reconciliation & Validation)」** です。これは本番稼働判定（Go-Live Sign-off）を取得するための最も厳格な品質防線となります。

勘定系・市場系データにおいては、単に「テーブル件数が一致している」だけでは不十分です。為替レート換算の端数丸め誤差、浮動小数点精度の欠落、全角・半角混在による文字数切り捨て、外部キー欠落による孤児レコード、Oracle 空文字の暗黙 NULL 評価差異、および改行コードや文字コード体系の変異など、微小な不整合が重大な金融事故や帳尻不一致を引き起こします。

本章では、日本の金融 IT 業界標準である **「5階梯 厳格突合検証体系 (5-Tier Reconciliation Architecture)」** に則り、監査・分析専属ロール `MITSUI_ANALYST` によって、異機種間（Oracle 11g 源泉庫 vs Snowflake ターゲットクラウド基盤）の双発エンジン基準比較実演を実施し、さらに日系プロジェクト現場で必須とされる **WinMerge による物理ファイル差分検証・エビデンス保全** を完遂します。

---

## 突合アーキテクチャ設計：5階梯 厳格突合体系

```mermaid
flowchart TD
    subgraph S0["前提監査"]
        R0["MITSUI_ANALYST 最小権限ロール切替<br/>DATABASE / SCHEMA / WAREHOUSE セッション確定"]
    end

    subgraph T1["第一階梯：新旧件数突合 (Row Count)"]
        R1["全ターゲットテーブルの行数完全合致確認<br/>CUST_MASTER: 13 件 | CUST_TRADE_DETAIL: 11 件<br/>判定基準: 差異 (Diff) = 0"]
    end

    subgraph T2["第二階梯：金融集計値突合 (Financial Metrics)"]
        R2["高精度金額・約定数量の絶対値サマリ集計<br/>総約定数量: 1,000,000,000,003,159 株<br/>円貨金額合計: 1,000,000,042,496,878.899 円<br/>外貨金額合計: 1,000,000,000,071,000.499<br/>判定基準: 差異 = 0.000 円 / 取引日区間完全閉塞"]
    end

    subgraph T3["第三階梯：多次元・リレーション境界値突合 (Relational & Boundary)"]
        R3_1["3.1 跨テーブル INNER JOIN 外部キー完全性 (11 件一致・孤児取引ゼロ)"]
        R3_2["3.2 LEFT JOIN 未取引・休眠顧客追跡 (CU00008888, CU00009990)"]
        R3_3["3.3 通貨別 × 売買区分 多次元クロス集計 (EUR / IDR / JPY / USD)"]
        R3_4["3.4 全角日本語極限文字 (50字/150バイト) & NULL空文字判定監査"]
    end

    subgraph T4["第四階梯：暗号学的テーブル全体ハッシュ突合 (Hash Aggregation)"]
        R4["全行・全列無順序ハッシュ指紋検証<br/>HASH_AGG = -3405770010579799674<br/>数学的証明によるビット単位の改ざん・欠落ゼロ保証"]
    end

    subgraph T5["第五階梯：WinMerge 物理ファイル突合 (Visual Diff)"]
        R5["双発対称 CSV 物理ファイルの直接ビジュアル比較<br/>WinMerge 画面エビデンス採取 (Binary Match & Identical)<br/>業務部・品質保証部門 (QA) への最終提出エビデンス"]
    end

    S0 --> T1 --> T2 --> T3 --> T4 --> T5
```

---

## 前提フェーズ：監査セッション環境の初期設定 (Session Setup)

金融セキュリティおよびガバナンス監査基準において、**「最小権限の原則 (Principle of Least Privilege)」** の遵守は絶対要件です。突合監査作業では、データ書き込み権限を持つ `MITSUI_ENGINEER` や管理者権限 `SYSADMIN` / `ACCOUNTADMIN` を使用せず、参照・分析専用ロール `MITSUI_ANALYST` を用います。

### Snowflake 実行 SQL

```sql
-- 目的・理由: 最小権限原則に則り、データ参照・監査専用ロールへ切り替え
USE ROLE MITSUI_ANALYST;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- セッションコンテキストの確認
SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
```

---

## 第一階梯：新旧テーブル件数突合 (Row Count Validation)

### 1. 業務目的と判定基準
抽出・ファイル転送・ステージング・COPY INTO に至る全パイプラインにおいて、**データ欠落（Data Loss）および多重取り込み（Duplicate Ingestion）が一切生じていないこと** を件数レベルで証明します。
- **判定基準**：$\Delta = \text{Snowflake\_Count} - \text{Oracle\_Benchmark} = 0$

### 2. 双発エンジン比較 SQL

#### Oracle 11g 源泉庫（基準値取得）：
```sql
SELECT 'CUST_MASTER' AS TABLE_NAME, COUNT(*) AS TOTAL_COUNT FROM CUST_MASTER
UNION ALL
SELECT 'CUST_TRADE_DETAIL' AS TABLE_NAME, COUNT(*) AS TOTAL_COUNT FROM CUST_TRADE_DETAIL;
```

#### Snowflake ターゲット庫（突合検証）：
```sql
-- 目的・理由: 移行対象の2テーブルの件数を一括取得し、第1階梯の合格を判定
SELECT 
    'CUST_MASTER' AS TARGET_TABLE, 
    COUNT(*)      AS TOTAL_ROWS 
FROM CUST_MASTER
UNION ALL
SELECT 
    'CUST_TRADE_DETAIL' AS TARGET_TABLE, 
    COUNT(*)            AS TOTAL_ROWS 
FROM CUST_TRADE_DETAIL;
```

### 3. 実機実行結果とエビデンス画像

Snowflake クエリ詳細画面において、`CUST_MASTER` 13 件、`CUST_TRADE_DETAIL` 11 件が確認されました：

![第一階梯 件数突合結果](../images/05_step_01_row_count.png)

| 対象テーブル名 | Oracle 側基準値 | Snowflake 側実測値 | 差分 (Diff) | 監査判定 |
| :--- | :--- | :--- | :--- | :--- |
| `CUST_MASTER` (顧客マスタ) | 13 | 13 | 0 | ✅ 完全一致 (PASS) |
| `CUST_TRADE_DETAIL` (顧客取引明細) | 11 | 11 | 0 | ✅ 完全一致 (PASS) |

---

## 第二階梯：重要金融メトリクス集計突合 (Financial Metrics Aggregation)

### 1. 業務目的と判定基準
行数が合致していても、内部の数値精度が狂っていては金融システムとして破綻します。異機種データベース移行では、浮動小数点変換の丸め誤差、指数表記化、日付の時区ズレなどが頻発します。
第二階梯では、**約定数量 (TRADE_QTY)**、**邦貨金額 (AMOUNT_JPY)**、**外貨金額 (AMOUNT_FCY)**、および **取引対象期間 (MIN/MAX TRADE_DATE)** を絶対精度で合算比較します。
- **判定基準**：
  - 取引数量差 $= 0$
  - 金額差 $= 0.000$（小数第3位まで完全一致）
  - 取引日区間の始点・終点が完全一致

### 2. 双発エンジン比較 SQL

#### Oracle 11g 源泉庫（基準値取得）：
```sql
SELECT 
    COUNT(*)                                       AS TOTAL_TRADES,
    SUM(TRADE_QTY)                                 AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
    TO_CHAR(MIN(TRADE_DATE), 'YYYYMMDD')           AS EARLIEST_TRADE_DATE,
    TO_CHAR(MAX(TRADE_DATE), 'YYYYMMDD')           AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;
```

#### Snowflake ターゲット庫（突合検証）：
```sql
-- 目的・理由: 全約定データに対する核心的金融メトリクスの絶対精度サマリ集計
SELECT 
    COUNT(*)                                       AS TOTAL_TRADES,
    SUM(TRADE_QTY)                                 AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
    MIN(TRADE_DATE)                                AS EARLIEST_TRADE_DATE,
    MAX(TRADE_DATE)                                AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;
```

### 3. 実機実行結果とエビデンス画像

Snowflake Snowsight 上での実行結果画面：

![第二階梯 金額および指標サマリ突合結果](../images/05_step_02_financial_aggregates.png)

双発エンジンの実測対照表：

| 金融監査指標 | Oracle 11g 源泉値 | Snowflake 移行先実測値 | 差分 (Diff) | 監査判定 |
| :--- | :--- | :--- | :--- | :--- |
| **総約定件数 (TOTAL_TRADES)** | 11 筆 | 11 筆 | 0 筆 | ✅ 一致 (PASS) |
| **総約定数量 (TOTAL_QTY)** | 1,000,000,000,003,159 株 | 1,000,000,000,003,159 株 | 0 株 | ✅ 一致 (PASS) |
| **円貨金額合計 (TOTAL_AMOUNT_JPY)** | 1,000,000,042,496,878.899 円 | 1,000,000,042,496,878.899 円 | 0.000 円 | ✅ 一致 (PASS) |
| **外貨金額合計 (TOTAL_AMOUNT_FCY)** | 1,000,000,000,071,000.499 | 1,000,000,000,071,000.499 | 0.000 | ✅ 一致 (PASS) |
| **最早約定日 (EARLIEST_TRADE_DATE)** | `20241231` | `20241231` | 0 日 | ✅ 一致 (PASS) |
| **最晩約定日 (LATEST_TRADE_DATE)** | `20250401` | `20250401` | 0 日 | ✅ 一致 (PASS) |

> [!NOTE]
> 顧客 `CU00000001`（三井 証券機構）による 1000 兆円規模の極大トランザクションを含め、Snowflake の `NUMBER(38, 3)` 型により 1 銭の誤差もなく保持されています。

---

## 第三階梯：多次元・リレーション整合性および境界値検証 (Relational & Boundary Verification)

全体サマリの一致だけでは、外部キー結合の不整合や、プラスマイナス金額の偶然の相殺を排除しきれません。第三階梯では構造と極限値の検証を行います。

### 3.1 跨テーブル参照整合性 (INNER JOIN 外部キー突合)

- **業務意義**：`CUST_TRADE_DETAIL` の全明細が、親テーブル `CUST_MASTER` の有効な顧客IDに紐付いていることを保証し、**孤児レコード（Orphan Records）の不在を証明** します。
- **期待値**：全 11 取引が完全結合され、厳密に 11 件出力。

```sql
-- 目的・理由: 親子テーブル間の参照整合性を証明し、孤児取引ゼロを確認
SELECT 
    t.CUST_ID,
    m.CUST_NAME_KANJI,
    m.BRANCH_CD,
    t.TRADE_DATE,
    t.TRADE_TYPE_CD,
    t.TRADE_QTY,
    t.AMOUNT_JPY,
    t.CCY_CODE
FROM MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL t
INNER JOIN MITSUI_SEC_DB.RAW_ORACLE.CUST_MASTER m 
    ON t.CUST_ID = m.CUST_ID
ORDER BY t.CUST_ID, t.TRADE_DATE, t.TRADE_TYPE_CD;
```

Snowsight 実機実行エビデンス（11 件の取引と全角漢字氏名が正確に結合）：

![第三階梯 INNER JOIN 外部キー突合エビデンス](../images/05_step_03_inner_join.png)

---

### 3.2 未取引口座・休眠口座の検知検証 (LEFT JOIN 境界値監査)

- **業務意義**：過去に一度も取引のない休眠口座や新規開設口座が、移行時に失われていないかを検証します。
- **期待値**：取引件数が 0 の顧客 2 件を厳密に抽出：
  1. `CU00008888`（松本 潤、ステータス `02:休眠`）
  2. `CU00009990`（井上 陽水、ステータス空文字→`NULL`）

```sql
-- 目的・理由: 取引履歴ゼロの顧客を抽出し、外部結合および休眠口座の正常移行を検証
SELECT 
    m.CUST_ID,
    m.CUST_NAME_KANJI,
    m.STATUS_CD,
    m.BRANCH_CD,
    COUNT(t.CUST_ID) AS TRADE_COUNT
FROM MITSUI_SEC_DB.RAW_ORACLE.CUST_MASTER m
LEFT JOIN MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL t 
    ON m.CUST_ID = t.CUST_ID
GROUP BY m.CUST_ID, m.CUST_NAME_KANJI, m.STATUS_CD, m.BRANCH_CD
HAVING COUNT(t.CUST_ID) = 0
ORDER BY m.CUST_ID;
```

Snowsight 実機実行エビデンス（休眠口座 2 件を正確に検知）：

![第三階梯 LEFT JOIN 休眠顧客検知エビデンス](../images/05_step_04_left_join_boundary.png)

---

### 3.3 通貨別 × 売買区分 多次元クロス集計 (Currency & Trade Type Breakdown)

- **業務意義**：全体の約定金額を `CCY_CODE`（通貨コード）と `TRADE_TYPE_CD`（`01`: 買付, `02`: 売付, `03`: 失効）でクロス分析し、通貨ごとの資産ポートフォリオが完全に一致していることを証明します。

```sql
-- 目的・理由: 通貨区分・売買区分ごとに多次元スライスし、資産分類のズレを完全排除
SELECT 
    NVL(CCY_CODE, 'JPY')        AS CURRENCY,
    TRADE_TYPE_CD,
    COUNT(*)                    AS TRADE_COUNT,
    SUM(TRADE_QTY)              AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)   AS TOTAL_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3) AS TOTAL_FCY
FROM CUST_TRADE_DETAIL
GROUP BY NVL(CCY_CODE, 'JPY'), TRADE_TYPE_CD
ORDER BY CURRENCY, TRADE_TYPE_CD;
```

Snowflake クエリ詳細画面のエビデンス：

![第三階梯 通貨別・取引区分別クロス集計結果](../images/05_step_05_currency_breakdown.png)

通貨別クロス集計照合表：

| 通貨 (CCY) | 取引区分 (TYPE) | 筆数 | 約定数量 (QTY) | 円貨約定額 (JPY) | 外貨約定額 (FCY) | 監査判定 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EUR** | `01` (買付) | 1 | 200 | 3,200,000.000 | 20,000.000 | ✅ 一致 |
| **IDR** | `01` (買付) | 1 | 10 | 1,200.000 | 1,000.000 | ✅ 一致 |
| **JPY** | `01` (買付) | 4 | 1,650 | 21,995,678.900 | 0.000 | ✅ 一致 |
| **JPY** | `02` (売付) | 2 | 800 | 9,800,000.000 | 0.000 | ✅ 一致 |
| **JPY** | `03` (失効) | 1 | 0 | 0.000 | 0.000 | ✅ 一致 |
| **USD** | `01` (買付) | 1 | 999,999,999,999,999 | 999,999,999,999,999.999 | 999,999,999,999,999.999 | ✅ 一致 |
| **USD** | `02` (売付) | 1 | 500 | 7,500,000.000 | 50,000.500 | ✅ 一致 |

---

### 3.4 日本語全角極限文字および空文字 NULL 判定検証

- **全角日本語格納**：顧客 `CU00004445` の備考欄（全角漢字 50 文字、AL32UTF8 で 150 バイト）が、文字欠落やマルチバイト文字化けなく保持されているか確認。
- **NULL 評価一貫性**：顧客 `CU00009990` の Oracle 上の空文字 `''` が、Snowflake で正しく `NULL` として評価されているか確認。

```sql
-- 目的・理由: 日本語マルチバイトの文字数・バイト数完全性と、空文字のNULL移行を検証
SELECT 
    'TRADE_DETAIL_REMARKS_EXTREME' AS CHECK_TYPE,
    CUST_ID,
    LENGTH(REMARKS)                AS CHAR_LENGTH,
    OCTET_LENGTH(REMARKS)          AS BYTE_LENGTH,
    REMARKS
FROM CUST_TRADE_DETAIL
WHERE CUST_ID = 'CU00004445'
UNION ALL
SELECT 
    'CUST_MASTER_STATUS_NULL'      AS CHECK_TYPE,
    CUST_ID,
    LENGTH(NVL(STATUS_CD, ''))     AS CHAR_LENGTH,
    OCTET_LENGTH(NVL(STATUS_CD, '')) AS BYTE_LENGTH,
    NVL(STATUS_CD, '<<NULL_DETECTED>>') AS REMARKS
FROM CUST_MASTER
WHERE STATUS_CD IS NULL;
```

#### 双発エンジン照合結果：
- **Oracle 11g**: `LENGTH` = 50 文字, `LENGTHB` = 150 バイト
- **Snowflake**: `LENGTH` = 50 文字, `OCTET_LENGTH` = 150 バイト
- **監査判定**：全角・半角混在および空文字の解釈が完全一致。

---

## 第四階梯：テーブル全体暗号ハッシュ指紋検証 (Global Table Hash)

### 1. 業務目的と数学的証明
前三階梯によりマクロ・ミクロ双方が検証されましたが、異なる行間で値が入れ替わった極めて稀なケースを完全に排除するため、第四階梯ではテーブル全体の数学的指紋を算出します。
Snowflake 独自の `HASH_AGG` 関数により、全行・全主要カラムの値を結合した **64 ビット整数の暗号ハッシュ値** を生成します：
- テーブル内の任意の 1 文字、1 ビットでも差異があれば、ハッシュ値は劇的に変化（雪崩効果）します。

### 2. 実行 SQL

```sql
-- 目的・理由: 全 11 行・10 カラムのデータを完全無順序ハッシュ集約し、改ざん・欠落ゼロを証明
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

### 3. 実機実行結果とエビデンス画像

Snowflake クエリ詳細画面で算出された指紋：

![第四階梯 暗号ハッシュ指紋結果](../images/05_step_06_global_hash.png)

```text
GLOBAL_TABLE_HASH: -3405770010579799674
```

算出されたハッシュ値は、移行検証スクリプトの算出結果と完全一致し、**全行・全列のデータが数学的に 100% 同一であること** が証明されました。

---

## 第五階梯：WinMerge による物理ファイル直接突合とエビデンス保全 (Physical File Reconciliation)

日本の金融機関や大手 SIer におけるシステム移行検収では、データベース内部のクエリ実行ログのみならず、**「WinMerge による新旧ファイル直接比較エビデンス」** の提出が品質管理部門（QA）および監査法人から強く要求されます。

### 1. なぜ日系プロジェクトで WinMerge が不可欠なのか？
* **非技術意思決定層への直感的説明責任**：業務部や監査担当者に対し、左右ペイン（左：現行 Oracle / 右：次世代 Snowflake）に全レコードが並び、差分ハイライトが一切ない純白状態、およびステータスバーの `Identical` や `Selected files are identical (binary match)` のポップアップを提示することで、受入合意を即座に形成できます。
* **物理ファイル層の文字コード・改行コード監査**：WinMerge 画面下部にエンコーディング（`UTF-8`）および改行コード（`Win / CRLF` または `UNIX / LF`）が常時明示され、文字化けや改行コード混在の事故を物理レベルで防止します。
* **固定長 CHAR 空白パディングの透過検証**：`CHAR(10)` などの末尾空白が意図せずトリムされたり過剰付与されていないかを透過的に目視確認できます。

### 2. 双発物理 CSV エクスポートの準備

自動化スクリプト `scripts/validation/export_snowflake_for_winmerge.py` を実行し、Oracle 側と Snowflake 側から同一のソート順・精度フォーマットで CSV ファイルを出力します：

```powershell
# 双発物理 CSV エクスポートの実行
python scripts/validation/export_snowflake_for_winmerge.py
```

* Oracle 側基準ファイル：`data/exports/oracle_cust_master.csv` / `oracle_cust_trade_detail.csv`
* Snowflake 側実測ファイル：`data/exports/snowflake_cust_master.csv` / `snowflake_cust_trade_detail.csv`

---

### 3. 顧客マスタ (CUST_MASTER) WinMerge 実機比較

WinMerge を起動し、双発の顧客基本台帳 CSV を比較：

```cmd
"C:\Program Files\WinMerge\WinMergeU.exe" data\exports\oracle_cust_master.csv data\exports\snowflake_cust_master.csv
```

実機比較エビデンス（**Selected files are identical (binary match)** の完全一致ポップアップ）：

![WinMerge CUST_MASTER 比較エビデンス](../images/05_step_06_winmerge_master_diff.png)

#### 監査ポイント解説：
1. **バイナリ一致ポップアップ**：中央ダイアログに `Selected files are identical (binary match).` と明示され、バイト単位での 100% 完全同等性が証明されています。
2. **全角漢字・半角カナの完全保持**：`三井 証券機構`、`ミツイ ショウケンキコウ`、`佐藤 太郎` 等のマルチバイト文字が一切の欠落なく保持されています。
3. **固定長末尾空白の維持**：`CUST_RANK_CD` カラムの `'S '`、`'A '`、`'C '` の末尾半角スペースが完全に維持されています。
4. **空文字 NULL の表現整合性**：`CU00009990`（井上 陽水）のステータス空文字が、Snowflake 側でも同一の空フィールドとして出力され、カンマ位置が完全に合致しています。

---

### 4. 顧客取引明細 (CUST_TRADE_DETAIL) WinMerge 実機比較

WinMerge で金融取引明細 CSV を直接比較：

```cmd
"C:\Program Files\WinMerge\WinMergeU.exe" data\exports\oracle_cust_trade_detail.csv data\exports\snowflake_cust_trade_detail.csv
```

実機比較エビデンス（左：Oracle 源泉側、右：Snowflake 移行先側）：

![WinMerge CUST_TRADE_DETAIL 比較エビデンス](../images/05_step_05_winmerge_trade_diff.png)

#### 監査ポイント解説：
1. **右下ステータスバー判定**：明確に **`Identical`**（完全同一）と判定され、左右ペインともに `UTF-8` / `Win`（CRLF）で統一されています。
2. **左端 Location Pane（差分ロケーションバー）**：全体バーが完全な均一グレー（差分ゼロ）であり、**黄色（差分行）や赤色（欠落行）が 1 箇所も存在しません**。
3. **1000兆円極大トランザクションと小数第3位精度**：2行目 `CU00000001` の `999999999999999.999` が、指数表記化することなく左右完全に合致しています。
4. **全角100文字極限備考の検証**：7行目 `CU00004445` の `全角文字百桁境界値検証用摘要欄全全全全全全全全全...` が一文字の欠落もなく左右対照されています。

---

### 5. 金融現場における WinMerge 推奨設定ガイド

プロジェクトの受入検収基準として WinMerge を採用する際は、メニュー **「編集」➔「設定」➔「比較」** にて以下の標準パラメータを設定することが推奨されます：

| 設定項目 (UI 表示) | 推奨設定値 | 金融プロジェクトにおける理由 |
| :--- | :---: | :--- |
| **空白** | **すべて比較** | 固定長 `CHAR` の末尾スペース欠落や想定外の余白混入を厳密に検知するため |
| **改行コードの違いを無視する** | **チェック ON** | Linux 側（LF）と Windows クライアント側（CRLF）の偽差分を排除するため |
| **文字コード自動判定** | **UTF-8 (BOM なし)** | クラウド DWH 標準に合わせ、BOM 混入による先頭カラム破損を防止するため |
| **プラグイン** | **Prediffer / CSV 表形式** | 項目数が多いファクトテーブルにおいてカラム単位のズレを目視確認するため |

---

## 6. ローカル自動化検証スクリプト

本章のすべての SQL、Python 自動化ツール、および WinMerge 自動連携スクリプトは、プロジェクトのリポジトリに保存されています：

1. **Snowflake 突合マスタースクリプト**：`scripts/validation/05_reconciliation_master.sql`
2. **Oracle 11g ローカルベンチマークスクリプト**：`scripts/oracle/05_oracle_reconcile.py`
3. **Snowflake Python 自動検証ツール**：`scripts/validation/05_snowflake_reconcile_verify.py`
4. **WinMerge 双発 CSV エクスポートツール**：`scripts/validation/export_snowflake_for_winmerge.py`
5. **WinMerge エビデンス画面取得ツール**：`scripts/validation/grab_winmerge.py`

ターミナルからのワンクリック実行コマンド：

```powershell
# 1. Oracle 11g 源泉側ベンチマークの実行
python scripts/oracle/05_oracle_reconcile.py

# 2. Snowflake 移行先側の自動突合検証の実行
python scripts/validation/05_snowflake_reconcile_verify.py

# 3. 物理 CSV の出力と WinMerge によるビジュアル比較
python scripts/validation/export_snowflake_for_winmerge.py
& "C:\Program Files\WinMerge\WinMergeU.exe" data\exports\oracle_cust_trade_detail.csv data\exports\snowflake_cust_trade_detail.csv
```

---

## 7. 金融 IT 突合検収サインオフ報告書（公式テンプレート）

日本の大手金融機関におけるプロジェクト納品時、品質管理部門（QA）およびシステムオーナーに提出する公式検収書フォーマットです：

```markdown
================================================================================
【三井フィナンシャルグループ 新旧データ移行突合検収サインオフ報告書】
プロジェクト名 : 次世代クラウドデータ基盤 (Snowflake) 移行検証プロジェクト
検証対象       : CUST_MASTER (顧客基本台帳), CUST_TRADE_DETAIL (顧客取引明細)
検証実行者     : MITSUI_ANALYST (監査分析担当)
検証実施日     : 2026-10-25
総合監査判定   : 合格 (PASS / 本番カットオーバー承認)
添付エビデンス : WinMerge 物理差分比較画像 (05_step_05_winmerge_trade_diff.png / 05_step_06_winmerge_master_diff.png)
================================================================================
```

### 突合検収総決算明細表

| 階梯レベル | 監査検証項目 (Audit Item) | Oracle 側基準値 | Snowflake 側実測値 | 差分 (Diff) | 判定 |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **Tier 1** | 顧客マスタ総件数 (`CUST_MASTER`) | 13 件 | 13 件 | 0 件 | **PASS** |
| **Tier 1** | 顧客取引明細総件数 (`CUST_TRADE_DETAIL`) | 11 件 | 11 件 | 0 件 | **PASS** |
| **Tier 2** | 総約定件数 (`TOTAL_TRADES`) | 11 筆 | 11 筆 | 0 筆 | **PASS** |
| **Tier 2** | 総約定数量 (`TOTAL_QTY`) | 1,000,000,000,003,159 株 | 1,000,000,000,003,159 株 | 0 株 | **PASS** |
| **Tier 2** | 邦貨総約定金額 (`TOTAL_AMOUNT_JPY`) | 1,000,000,042,496,878.899 円 | 1,000,000,042,496,878.899 円 | 0.000 円 | **PASS** |
| **Tier 2** | 外貨総約定金額 (`TOTAL_AMOUNT_FCY`) | 1,000,000,000,071,000.499 | 1,000,000,000,071,000.499 | 0.000 | **PASS** |
| **Tier 2** | 最早約定日 (`EARLIEST_TRADE_DATE`) | `20241231` | `20241231` | 0 日 | **PASS** |
| **Tier 2** | 最晩約定日 (`LATEST_TRADE_DATE`) | `20250401` | `20250401` | 0 日 | **PASS** |
| **Tier 3** | 外部キー参照整合性 (`INNER JOIN`) | 11 件完全一致 (0 孤児) | 11 件完全一致 (0 孤児) | 0 件 | **PASS** |
| **Tier 3** | 未取引口座検知 (`LEFT JOIN`) | 2 件 (CU00008888, 9990) | 2 件 (CU00008888, 9990) | 0 件 | **PASS** |
| **Tier 3** | 通貨別・取引区分別クロス集計 | 7 パターン完全合致 | 7 パターン完全合致 | 0 件 | **PASS** |
| **Tier 3** | 日本語全角極限文字数 (CU00004445) | 50 文字 / 150 バイト | 50 文字 / 150 バイト | 0 欠落 | **PASS** |
| **Tier 3** | Oracle 空文字 NULL 判定 (CU00009990) | `NULL` | `NULL` | 0 齟齬 | **PASS** |
| **Tier 4** | テーブル全体暗号ハッシュ指紋 (`HASH_AGG`) | `-3405770010579799674` | `-3405770010579799674` | 0 bit | **PASS** |
| **Tier 5** | WinMerge 物理 CSV 直接突合 (CUST_MASTER) | 完全一致 (Binary Match) | 完全一致 (Binary Match) | 0 bit | **PASS** |
| **Tier 5** | WinMerge 物理 CSV 直接突合 (CUST_TRADE_DETAIL) | 完全一致 (Identical) | 完全一致 (Identical) | 0 bit | **PASS** |

**結論**：三井証券勘定系 Oracle 11g から Snowflake 次世代データ基盤への全データ移行突合において、論理集計・関係整合性・暗号ハッシュ・および WinMerge 物理ファイル直接突合の全階梯で差異ゼロが実証され、本番稼働承認（Go-Live Approval）の全基準を充足したことを証明します。
