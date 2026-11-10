# 第 05 章：dbt のシード（Seeds）とデータソース（Sources）の実践 —— 静的マスタ表の Git バージョン管理、外部ソースの抽象化・疎結合、およびデータ鮮度監視（Source Freshness）

> 本章は **《尚硅谷（Shangguigu）スタイル技術講義執筆規範》** に完全準拠して執筆されています：本質を突く明快な比較、ビジネスロジックを排した純粋な技術的焦点、実機検証ログ付きの3ステップ実践ループ、現場の落とし穴への実戦対策、前提条件の完全明示。

---

## イントロダクション：結論ファーストと明快なメンタルモデル

モダンデータウェアハウス基盤において、分析プラットフォームへ流入するインプットデータは大きく 2 つのグループに大別されます：
1. **外部データソース（Sources）**：基幹系トランザクション DB や各種 SaaS（Fivetran、Airbyte、Kafka CDC 等）から継続的に抽出され、データウェアハウスの RAW 層に投入される大規模なテーブル群。
2. **静的マスタ・参照データ（Seeds）**：国コード・通貨変換表、業界分類コード、業務区分マスタ、天体歴（満月日付）など、データ量が小さく（通常数百〜数万行以内）、更新頻度が極めて低いオフラインの CSV ファイル群。

従来のデータウェアハウス運用において、これら 2 つのデータに対するアプローチには深刻な課題が存在していました：
- **課題 1（ハードコードによる物理構成との強結合）**：SQL ビュー内で `FROM AIRBNB.RAW.RAW_LISTINGS` のように物理パスを直接ハードコードするため、上流 DB のリネームやスキーマ移行が発生した際、下流のすべての SQL が全滅し、手動置換の地獄に陥る；
- **課題 2（静的マスタ表のバージョン管理不全）**：マスタデータが DBA や担当者の手作業による `INSERT INTO` で投入され、Git リポジトリの管理外となるため、「いつ・誰が・どの値を書き換えたのか」の監査証跡が失われる；
- **課題 3（「サイレント障害」によるデータの鮮度劣化）**：上流の抽出ツールや API が停止して RAW 層の更新が途絶えても、下流の dbt ジョブや BI ダッシュボードは何の警告もなく古いデータを集計し続け、経営陣が異常値に気づくまで障害が放置される！

**dbt は `Seeds` と `Sources` という 2 つの強力な武器によって、これらの課題を根本から解決します**：
- **`Seeds`**：小規模な CSV を Git 管理下に置き、`dbt seed` コマンド一発でテーブル作成・型推論・データ投入を完全自動化；
- **`Sources`**：`YAML` ファイルで元ソースの論理抽象レイヤーを定義し、SQL 内では `&#123;&#123; source('source_name', 'table_name') &#125;&#125;` により完全に疎結合化；
- **`Source Freshness`**：`dbt source freshness` コマンドで最新の業務タイムスタンプを監視し、許容閾値（`warn_after` / `error_after`）を超えた場合に CI/CD や定期ジョブを即座にエラー停止！

### 比較表：Seeds vs Sources のメンタルモデル

| 比較項目 | シード (Seeds) | データソース (Sources) |
| :--- | :--- | :--- |
| **データの出所** | プロジェクト内の静的 `.csv` ファイル | 外部 ETL/ELT ツールが数倉に書き込んだ実体テーブル |
| **保存場所** | dbt プロジェクトの `seeds/` ディレクトリ | Snowflake 上の外部スキーマ（例：`AIRBNB.RAW`） |
| **データ規模** | 小規模な静的マスタ（推奨：< 100MB / < 10万行） | 大規模トランザクション事実、業務トランザクション |
| **dbt の役割** | **生成・投入者**（テーブル作成と INSERT を担当） | **消費者・監視者**（メタデータ宣言と鮮度監査のみ） |
| **実行コマンド** | `dbt seed`（テーブル作成 ＋ データ投入） | `dbt source freshness`（鮮度監査テスト） |
| **参照構文** | `&#123;&#123; ref('seed_name') &#125;&#125;` | `&#123;&#123; source('source_name', 'table_name') &#125;&#125;` |

```
【dbt Seeds & Sources データリネージパイプライン図】

 ┌────────────────────────────────────────┐
 │ 外部入力 A: 静的 CSV マスタ (Git 管理) │
 │ seeds/seed_full_moon_dates.csv         │
 └───────────────────┬────────────────────┘
                     │ dbt seed
                     ▼
 ┌────────────────────────────────────────┐
 │ Snowflake 物理テーブル (Seed 表)       │
 │ AIRBNB.DEV.SEED_FULL_MOON_DATES (272行)│
 └───────────────────┬────────────────────┘
                     │ {{ ref('seed_full_moon_dates') }}
                     ▼
 ┌────────────────────────────────────────┐      ┌────────────────────────────────────────┐
 │ Mart データマート層モデル              │ <─── │ Core ファクト層モデル                  │
 │ models/mart/mart_fullmoon_reviews.sql  │      │ models/fct/fct_reviews.sql             │
 └────────────────────────────────────────┘      └───────────────────┬────────────────────┘
                                                                     │ {{ ref('src_reviews') }}
                                                                     ▼
                                                 ┌────────────────────────────────────────┐
                                                 │ Staging 層 (論理疎結合)                │
                                                 │ models/src/src_reviews.sql             │
                                                 └───────────────────┬────────────────────┘
                                                                     │ {{ source('airbnb', 'reviews') }}
                                                                     ▼
                                                 ┌────────────────────────────────────────┐
                                                 │ 抽象ソース定義 (models/sources.yml)    │
                                                 │ • identifier: raw_reviews              │
                                                 │ • loaded_at_field: date                │
                                                 │ • freshness: warn(1h) / error(24h)     │
                                                 └───────────────────┬────────────────────┘
                                                                     │ 物理参照
                                                                     ▼
                                                 ┌────────────────────────────────────────┐
                                                 │ 外部入力 B: RAW スキーマ (生データ)    │
                                                 │ AIRBNB.RAW.RAW_REVIEWS (409,697行)     │
                                                 └────────────────────────────────────────┘
```

---

## 第1部：シード（Seeds）機能と静的マスタのバージョン管理

### 1. dbt Seed とは何か？
Seed は、dbt プロジェクトの `seeds/` 配下に格納された `.csv` ファイルを指します。`dbt seed` コマンドを実行すると：
1. 対象スキーマ（`AIRBNB.DEV`）に `CREATE OR REPLACE TABLE ...` を実行；
2. CSV 1 行目のヘッダーから列名を決定し、値からデータ型（INTEGER, STRING, DATE 等）を自動推論；
3. CSV 内の行を物理テーブルに一括ロード（`INSERT`）します。

> [!WARNING]
> **アンチパターン**：ギガバイト級のトランザクションログを CSV にして `seeds/` に配置してはいけません！CSV は大規模データの格納に適しておらず、Git リポジトリの肥大化とビルド速度の破綻を招きます。Seed の使命は、**軽量かつ静的なビジネス変換マスタ**に限定されます。

### 2. ビジネス背景：「満月が宿泊客のレビュー感情に及ぼす影響」の検証
Airbnb の運用分析において、「満月の夜は睡眠の質が低下し、宿泊客が翌日により批判的なネガティブレビューを投稿しやすいのではないか？」という仮説が立てられました。この仮説を検証するため、過去 10 年間の天文学的な満月日マスタを取り込み、レビュー事実表と結合します。

### 3. 満月日シードファイルのダウンロード
PowerShell から、272 件の満月日を含む CSV を `seeds/` フォルダへダウンロードします：
```powershell
Invoke-WebRequest -Uri "https://dbt-datasets.s3.us-east-2.amazonaws.com/seed_full_moon_dates.csv" -OutFile "seeds\seed_full_moon_dates.csv"
```

CSV の中身を確認します：
```csv
full_moon_date
2009-01-11
2009-02-09
2009-03-11
2009-04-09
```

### 4. `dbt seed` の実行
ターミナルで実行します：
```powershell
dbt seed --profiles-dir .
```

実際のターミナル実行ログ：
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
Snowflake 上に物理テーブル `DEV.SEED_FULL_MOON_DATES` が自動生成され、272 件が投入されました！

---

## 第2部：データマートモデルの実装 —— Seed と Fact の結合

dbt では、Seed から作成されたテーブルも通常のモデルと同様に扱われます。**下流モデルからは `&#123;&#123; ref('seed_name') &#125;&#125;` により自然に参照可能です**！

### 1. `models/mart/mart_fullmoon_reviews.sql` の作成
`models/mart` ディレクトリを作成し、以下の SQL を記述します：
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

### ロジック解説：
- **`DATEADD(DAY, 1, fm.full_moon_date)`**：満月は夜間に発生するため、影響を受けた宿泊客がレビューを投稿するのは**翌日**となります。
- **`LEFT JOIN` によるタグ付け**：満月の翌日とレビュー投稿日が一致したレコードには `'full moon'`、それ以外には `'not full moon'` を付与します。

---

## 第3部：データソース（Sources）の抽象化と疎結合設計

### 1. なぜ `FROM AIRBNB.RAW.RAW_LISTINGS` の直書きは避けるべきか？
第 03 章の記述を振り返ります：
```sql
-- ハードコードによる密結合アンチパターン
WITH raw_listings AS (
    SELECT * FROM AIRBNB.RAW.RAW_LISTINGS
)
```
この記法では、dbt のリネージグラフが途切れてしまいます。外部の生データソースがどこにあり、どのような依存関係があるのかを可視化・追跡することができません。

### 2. ソース定義ファイル `models/sources.yml`
`models/sources.yml` を作成し、論理名と物理テーブルのマッピングを定義します：

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

### 主要プロパティの解説：
- `name: airbnb`：データソースの論理名前空間；
- `schema: raw`：Snowflake 上の物理スキーマ名（`AIRBNB.RAW`）；
- `tables.name`：SQL 内で参照する論理名（例：`listings`）；
- `tables.identifier`：Snowflake 上の実際の物理テーブル名（例：`raw_listings`）。物理名と論理名が異なる場合でも安全にマッピングできます。

### 3. Staging 層モデルのリファクタリング（`source()` マクロ）
`models/src/` 配下の 3 つのモデルを `&#123;&#123; source('airbnb', '...') &#125;&#125;` に修正します：

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

### 4. コンパイル検証 `dbt compile`
```powershell
dbt compile --profiles-dir .
```
`Found 8 models, 1 seed, 3 sources, 563 macros` と出力され、すべてのリネージが正しくコンパイルされることを確認します。

---

## 第4部：データ鮮度監視（Source Freshness）の実践

### 1. 鮮度監視の仕組み
本番環境で最も恐ろしいのは「上流バッチのサイレント停止」です。dbt はこれを自動検知します：
- **`loaded_at_field`**：最新時刻を判定する基準カラム（`date` 等）；
- **`warn_after`**：指定期間（例：1時間）を超過した場合に警告（WARN）；
- **`error_after`**：重大な遅延（例：24時間）を超過した場合にエラー（ERROR）。

### 2. `dbt source freshness` の実行
ターミナルで実行します：
```powershell
dbt source freshness --profiles-dir .
```

実際のターミナル実行ログ：
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

### 3. CI/CD 連携と終了ステータスコード（Exit Code）
- Windows PowerShell：`$LASTEXITCODE`
- Linux / macOS：`echo $?`

| 判定結果 | 出力ステータス | 終了コード (`Exit Code`) | CI/CD パイプラインの挙動 |
| :--- | :--- | :--- | :--- |
| **PASS** | `PASS` | `0` | 後続のビルド・デプロイを続行 |
| **WARN** | `WARN` | `0` | Slack 通知等で警告しつつ続行 |
| **ERROR** | `ERROR STALE` | **`1` (非ゼロ終了)** | **パイプラインを即座に強制中断！** |

> [!TIP]
> 終了コードが非ゼロ（1）になる仕組みにより、GitHub Actions や Airflow などのオーケストレーションツールが異常を即座に検知し、陳腐化したデータの流出を自動で水際阻止できます。

---

## 第5部：実機検証の3ステップ —— 全モデル実行と Snowflake 監査

### ステップ 1：全モデルの `dbt run` 実行
```powershell
dbt run --profiles-dir .
```

実際のターミナル実行ログ：
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

### ステップ 2：Snowflake 倉内オブジェクトの監査
Python から Snowflake のオブジェクト構造を確認します：
```sql
SHOW OBJECTS IN SCHEMA AIRBNB.DEV;
```

実測オブジェクト一覧：
```text
KIND       | NAME                      | ROWS
TABLE      | DIM_HOSTS_CLEANSED        | 14,111
TABLE      | DIM_LISTINGS_CLEANSED     | 17,499
TABLE      | DIM_LISTINGS_W_HOSTS      | 17,499
TABLE      | FCT_REVIEWS               | 409,697
TABLE      | MART_FULLMOON_REVIEWS     | 409,697
TABLE      | SEED_FULL_MOON_DATES      | 272
VIEW       | SRC_HOSTS                 | 0 (ビュー)
VIEW       | SRC_LISTINGS              | 0 (ビュー)
VIEW       | SRC_REVIEWS               | 0 (ビュー)
```

### ステップ 3：満月仮説のサンプルデータ検証
`MART_FULLMOON_REVIEWS` テーブルから集計クエリを実行：
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

実測出力結果：
```text
Date: 2021-10-22 00:00:00 | is_full_moon: not full moon | count: 57
Date: 2021-10-21 00:00:00 | is_full_moon: full moon     | count: 89
Date: 2021-10-20 00:00:00 | is_full_moon: not full moon | count: 130
Date: 2021-10-19 00:00:00 | is_full_moon: not full moon | count: 121
Date: 2021-10-18 00:00:00 | is_full_moon: not full moon | count: 196
```
> [!NOTE]
> 2021-10-20 の満月に対して、翌日（2021-10-21）のレビュー 89 件に正しく `full moon` フラグが付与されていることが確認できました！

---

## 第6部：現場の落とし穴とベストプラクティス

### 1. 落とし穴 1：Seed を ETL 抽出ツールとして誤用する
- **事象**：数百メガバイトのトランザクションログを CSV で `seeds/` に配置し、`dbt seed` で流し込もうとする。
- **原因**：dbt Seed は内部でバッチ INSERT を行うため、大規模データでは極めて低速であり、Git リポジトリも肥大化します。
- **回避策**：Seed は軽量な静的コード表（数千行以内）に限定し、大規模データは専用のデータパイプライン（Airbyte、Snowpipe、Fivetran 等）で RAW スキーマに投入して `sources` で管理します。

### 2. 落とし穴 2：dbt v1.5+ における freshness 設定の非推奨警告
- **事象**：`sources.yml` のトップレベルに `freshness:` を指定すると非推奨警告が出る。
- **回避策**：最新の dbt 構文に準拠し、必ず `config:` ブロック内に `loaded_at_field` と `freshness` を記述します。

---

## 本章のまとめ

本章を通じて、dbt 分析エンジニアリングにおけるインプット層のガバナンスを完全に確立しました：
1. **Seeds と Sources の役割分担**：静的マスタは Git 管理下の Seeds、動的外部データは Sources で抽象化；
2. **`dbt seed` と `source()` による完全な疎結合化**：物理パスのハードコードを撤廃し、環境可搬性を担保；
3. **データ鮮度監視（Source Freshness）の実装**：上流障害を検知し、CI/CD で過時データの拡散を未然に防ぐ防壁を構築；
4. **Airbnb 満月レビューマート（Mart）の完成**：Seed 参照と事実表を結合し、数倉の 4 層モデリングを実証。

続く第 06 章では、マスタの過去履歴を時間軸で管理する **Snapshots（SCD Type-2 履歴管理・スローチェンジングディメンション）** の実践手法を学んでいきます！

