# 第 04 章：dbt のマテリアライゼーション戦略とモデル依存関係の実践 —— 4つの物化タイプ、ref マクロによる DAG 依存関係、増分ロード（Incremental）および Ephemeral 仮想 CTE

> 本章は **《尚硅谷（Shangguigu）スタイル技術講義執筆規範》** に完全準拠して執筆されています：本質を突く明快な比較、ビジネスロジックを排した純粋な技術的焦点、実機検証ログ付きの3ステップ実践ループ、現場の落とし穴への実戦対策、前提条件の完全明示。

---

## イントロダクション：結論ファーストと明快なメンタルモデル

第 03 章では、Airbnb の Staging（ステージング）層を構築し、純粋な `SELECT` 文のみで Snowflake 内にビュー（View）をコンパイル・作成することに成功しました。しかし、エンタープライズ規模の本格的なビッグデータ分析基盤において、すべてのモデルをビューのまま運用した場合、深刻なパフォーマンス障害とコンピューティングコストの暴走を招きます：
1. **ビュー照会時のコンピューティングコスト爆発**：BI ダッシュボードやアナリストがビューを参照するたびに、Snowflake は基盤の生データテーブル全体をフルスキャン・再計算するため、高額な Virtual Warehouse Credit を浪費します；
2. **物理テーブルの全件再作成によるレイテンシ増大**：すべてのモデルを通常の物理テーブル（Table）にした場合、`dbt run` のたびに `CREATE OR REPLACE TABLE AS SELECT ...` が実行されます。数億〜数十億行におよぶファクトテーブル（ログ、クリックストリーム、注文履歴など）では、再構築に数十分〜数時間を要してしまいます；
3. **ハードコードによる依存地獄と環境ロック**：従来の `FROM database.schema.table` によるハードコードでは、開発環境（DEV）と本番環境（PROD）の自動切り替えが不可能なだけでなく、依存順序が未定義となり、「親テーブルが存在しない状態で子テーブルを実行してエラー」という致命的な障害が発生します。

**dbt はこれらを解決する 2 大コア機能を備えています**：
- **`ref()` マクロエンジン**：モデル間の依存関係（DAG, Directed Acyclic Graph）を自動解決し、最適な実行順序を制御。環境に応じて対象 Database / Schema を動的にマッピング；
- **4 つの標準マテリアライゼーション戦略（Materializations）**：`view`、`table`、`incremental`、`ephemeral` を適切に使い分け、ストレージコストと照会性能の最適バランスを実現！

### 比較表：4 つのマテリアライゼーション戦略のメンタルモデル

| マテリアライゼーション | Snowflake 内の実体 | 再構築メカニズム (`dbt run`) | ストレージコスト | 照会応答速度 | 代表的なユースケース |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`view` (ビュー)** | 論理ビュー (`VIEW`) | `CREATE OR REPLACE VIEW` | **0** (メタデータのみ) | やや低速 (照会時に都度 SQL 実行) | Staging 層 (`src_*`)、軽量な列リネーム・型変換 |
| **`table` (物理テーブル)** | 物理テーブル (`TABLE`) | `CREATE OR REPLACE TABLE AS` (全件洗替) | ディスク容量消費 | **極めて高速** (事前計算・プルーニング有効) | コアディメンション (`dim_*`)、中間テーブル、BI 直接参照用マート |
| **`incremental` (増分テーブル)** | 物理テーブル (`TABLE`) | 初回は全件作成、2回目以降は差分のみ追加/マージ (`INSERT/MERGE`) | ディスク容量消費 | **極めて高速** (物理永続化) | 大規模イベントログ・ファクトテーブル (`fct_*`)、履歴データ |
| **`ephemeral` (仮想 CTE)** | **オブジェクトなし (非永続化)** | コンパイル時に下流モデルの `WITH ... AS (...)` CTE に直接インライン展開 | **0** | 当該照会に依存 | パイプライン内でのみ再利用し、外部へ公開不要な軽量ロジック |

```
【dbt DAG モデル依存関係パイプライン図】
                                                        
 ┌───────────────────────┐
 │ AIRBNB.RAW (生データ) │
 └──────────┬────────────┘
            │
            ▼ (SELECT * FROM RAW_...)
 ┌────────────────────────────────────────────────────────┐
 │ Staging 層 [view]                                      │
 │ • models/src/src_listings.sql                          │
 │ • models/src/src_hosts.sql                             │
 │ • models/src/src_reviews.sql                           │
 └──────────┬─────────────────────────────┬───────────────┘
            │ {{ ref('src_listings') }}   │ {{ ref('src_reviews') }}
            │ {{ ref('src_hosts') }}      │
            ▼                             ▼
 ┌───────────────────────────────┐  ┌────────────────────────────────────────────────┐
 │ Core ディメンション層 [table] │  │ Core ファクト層 [incremental]                  │
 │ • dim_listings_cleansed       │  │ • fct_reviews                                  │
 │ • dim_hosts_cleansed          │  │   {% if is_incremental() %}                    │
 └──────────┬────────────────────┘  │     WHERE review_date > (SELECT MAX(...) ...)  │
            │ {{ ref(...) }}        │   {% endif %}                                  │
            ▼                       └────────────────────────────────────────────────┘
 ┌───────────────────────────────┐
 │ Mart データマート層 [table]   │
 │ • dim_listings_w_hosts        │
 └───────────────────────────────┘
```

---

## 第1部：モデル依存関係と `ref` マクロの深層メカニズム

従来の SQL スクリプトにおいて、テーブル B がテーブル A に依存している場合、以下のように記述されがちでした：
```sql
-- 危険なハードコードのアンチパターン！
SELECT * FROM AIRBNB.DEV.src_listings;
```
この記法には 2 つの深刻な課題があります：
1. **環境固定化**：`AIRBNB.PROD` へのデプロイ時に全文置換が必要となり、誤爆や作業漏れのリスクが生じる；
2. **実行順序の喪失**：dbt はテーブル間の前後関係を感知できず、並行ビルド時にテーブル A より先にテーブル B が実行されて失敗する。

dbt では、専用の Jinja マクロ `&#123;&#123; ref('model_name') &#125;&#125;` を使用します：
```sql
-- エンタープライズ標準：動的参照
WITH src_listings AS (
    SELECT * FROM &#123;&#123; ref('src_listings') &#125;&#125;
)
```

### `ref` マクロの利点
1. **DAG 依存関係ツリーの自動構築**：dbt はプロジェクト内のすべての `ref` 宣言を静的解析し、有向非巡回グラフ（DAG）をメモリ内に構築します。`dbt run` 実行時、親モデルを優先実行し、下流の子モデルを安全かつ並行して自動ビルドします。
2. **マルチ環境の動的解決**：ターゲットが `dev` の場合、`&#123;&#123; ref('src_listings') &#125;&#125;` は自動的に `AIRBNB.DEV.SRC_LISTINGS` に展開され、`prod` の場合は `AIRBNB.PROD.SRC_LISTINGS` に展開されます。SQL コードの修正は一切不要です！

---

## 第2部：クレンジング済みディメンション層の実装

次に、`models/dim/` 配下にデータクレンジングを施したディメンションモデルを実装します：
1. `dim_listings_cleansed`：リスティングデータをクレンジング。異常値である `minimum_nights = 0` を `1` に補正し、価格文字列 `$150.00` を高精度な数値型 `NUMBER(10, 2)` に型変換。
2. `dim_hosts_cleansed`：ホストデータをクレンジング。`NVL(host_name, 'Anonymous')` により欠損したホスト名を補完。
3. `dim_listings_w_hosts`：リスティングとホストを結合した、下流で直接活用できるワイドディメンションマート。

### 1. ディレクトリの作成
ターミナルでプロジェクト直下に移動し、`dim` および `fct` フォルダを作成します：
```powershell
New-Item -ItemType Directory -Force -Path "models\dim"
New-Item -ItemType Directory -Force -Path "models\fct"
```

### 2. `dim_listings_cleansed.sql` の実装
`models/dim/dim_listings_cleansed.sql` を新規作成します：
```sql
WITH src_listings AS (
    SELECT
        *
    FROM
        &#123;&#123; ref('src_listings') &#125;&#125;
)
SELECT
    listing_id,
    listing_name,
    room_type,
    CASE
        WHEN minimum_nights = 0 THEN 1
        ELSE minimum_nights
    END AS minimum_nights,
    host_id,
    REPLACE(
        price_str,
        '$'
    ) :: NUMBER(
        10,
        2
    ) AS price,
    created_at,
    updated_at
FROM
    src_listings
```

### 3. `dim_hosts_cleansed.sql` の実装
`models/dim/dim_hosts_cleansed.sql` を新規作成します：
```sql
WITH src_hosts AS (
    SELECT
        *
    FROM
        &#123;&#123; ref('src_hosts') &#125;&#125;
)
SELECT
    host_id,
    NVL(
        host_name,
        'Anonymous'
    ) AS host_name,
    is_superhost,
    created_at,
    updated_at
FROM
    src_hosts
```

---

## 第3部：マテリアライゼーション設定の二重構造 —— プロジェクト全体 vs 個別モデル

dbt では、設定を 2 つのレベルで管理できます：

### 1. プロジェクトレベル設定 (`dbt_project.yml`)
ディレクトリ配下のモデルに一括してルールを適用します。`dbt_project.yml` を開き、`models` ブロックに設定を追加します：

```yaml
# dbt_project.yml
models:
  airbnb:
    # プロジェクト全体のデフォルトをビュー (view) に設定
    +materialized: view
    # dim ディレクトリ配下の全モデルを物理テーブル (table) として物化
    dim:
      +materialized: table
```
> [!TIP]
> `+` プレフィックスは、ディレクトリ名ではなく dbt 組み込みのディレクティブ（設定項目）であることを明示するためのシンタックスです。

### 2. モデルファイルレベル設定 (`config()` Jinja マクロ)
特定のモデルのみ設定を上書きする場合や、増分設定などの固有パラメータを指定する場合、`.sql` の先頭に `config()` を宣言します：

```sql
&#123;&#123;
  config(
    materialized = 'incremental',
    on_schema_change = 'fail'
  )
&#125;&#125;
```
優先順位：**個別モデルファイル内の `config()` が最優先され、`dbt_project.yml` の設定をオーバーライドします！**

---

## 第4部：増分ロード（Incremental）の実践 —— `fct_reviews` の差分更新

増分マテリアライゼーション（`incremental`）は、dbt の最も強力な中核機能の一つです。毎日大量に発生するレビュー履歴などのファクトテーブルにおいて、全件再計算を排除し、処理コストと時間を劇的に短縮します。

### 1. 増分モデルの動作メカニズム
- **初回実行（Initial Run / ターゲット表が存在しない場合）**：
  Snowflake 上にテーブルが存在しないため、dbt は自動的に `CREATE TABLE AS SELECT ...` を実行して初期全件ロードを行います。
- **2回目以降の増分実行（Subsequent Runs）**：
  dbt はクエリ結果を一時テーブル（例：`fct_reviews__dbt_tmp`）にロードし、既存テーブルに対して `INSERT INTO` または `MERGE INTO` を発行して新着差分のみを同期します。

### 2. `models/fct/fct_reviews.sql` の実装
`models/fct/fct_reviews.sql` を新規作成します：
```sql
&#123;&#123;
  config(
    materialized = 'incremental',
    on_schema_change = 'fail'
  )
&#125;&#125;
WITH src_reviews AS (
    SELECT
        *
    FROM
        &#123;&#123; ref('src_reviews') &#125;&#125;
)
SELECT
    *
FROM
    src_reviews
WHERE
    review_text IS NOT NULL
{% if is_incremental() %}
    AND review_date > (SELECT MAX(review_date) FROM &#123;&#123; this &#125;&#125;)
{% endif %}
```

### 主要構文の詳細解説
- `is_incremental()` マクロ：
  以下の 3 条件をすべて満たす場合にのみ `TRUE` を返します：
  1. 当該モデルが `incremental` に設定されていること；
  2. 対象データベースに**既にテーブルが存在している**こと；
  3. `dbt run` 実行時に `--full-refresh` フラグが**指定されていない**こと。
- `&#123;&#123; this &#125;&#125;` マクロ：
  Snowflake 上に**現在存在する実体テーブル**（`AIRBNB.DEV.FCT_REVIEWS`）を指します。`(SELECT MAX(review_date) FROM &#123;&#123; this &#125;&#125;)` によって既存テーブルの最新タイムスタンプを動的に取得し、正確な差分抽出を行います。
- `on_schema_change = 'fail'`：
  スキーマ変更に対する安全ガード。上流テーブルで列の追加や型変更（Schema Drift）が発生した際、データ不整合を防ぐため即座にエラー停止させます。

---

## 第5部：増分戦略と Ephemeral 仮想マテリアライゼーション

### 1. Snowflake における増分戦略（Incremental Strategies）
`config()` の `incremental_strategy` オプションにより、データ反映アルゴリズムを選択できます：
- **`append`（デフォルト追加入力モード）**：
  差分行をそのまま `INSERT INTO` します。最も高速で低コストですが、過去データの更新（Update）には対応できず、重複リスクがあります。
- **`merge`（Snowflake ネイティブ推奨）**：
  Snowflake の `MERGE INTO` 構文を利用します。`unique_key = 'review_id'` と併用することで、同一キーは `UPDATE`、新規キーは `INSERT` する冪等性（Idempotency）を担保します。
- **`delete+insert`**：
  該当パーティションやキーの既存レコードを削除した上で新規挿入します。

### 2. Ephemeral 仮想 CTE
特定の軽量変換ロジックが下流の 1〜2 モデルでのみ使用され、外部 BI への公開が不要な場合、`ephemeral` を指定します：

```sql
&#123;&#123;
  config(
    materialized = 'ephemeral'
  )
&#125;&#125;
```

**内部動作**：
`ephemeral` モデルは、Snowflake 上にテーブルもビューも一切作成しません。コンパイル時、dbt は自動的に下流モデルの `WITH` 句内にインライン CTE としてコードを展開注入します。

---

## 第6部：実機検証の3ステップ —— ターミナル実行ログと Snowflake 監査

### ステップ 1：結合マート `dim_listings_w_hosts.sql` の作成
`models/dim/dim_listings_w_hosts.sql` を新規作成します：
```sql
WITH l AS (
    SELECT
        *
    FROM
        &#123;&#123; ref('dim_listings_cleansed') &#125;&#125;
),
h AS (
    SELECT
        *
    FROM
        &#123;&#123; ref('dim_hosts_cleansed') &#125;&#125;
)
SELECT
    l.listing_id,
    l.listing_name,
    l.room_type,
    l.minimum_nights,
    l.price,
    l.host_id,
    h.host_name,
    h.is_superhost as host_is_superhost,
    l.created_at,
    GREATEST(l.updated_at, h.updated_at) as updated_at
FROM l
LEFT JOIN h ON (h.host_id = l.host_id)
```

### ステップ 2：初回の `dbt run` 実行
ターミナルで実行します：
```powershell
dbt run --profiles-dir .
```

実際のターミナル実行ログ：
```text
12:48:46  Running with dbt=1.12.6
12:48:47  Registered adapter: snowflake=1.12.5
12:48:51  Found 7 models, 563 macros
12:48:51  Concurrency: 4 threads (target='dev')
12:48:52  1 of 7 START sql view model DEV.src_hosts ...................................... [RUN]
12:48:52  2 of 7 START sql view model DEV.src_listings ................................... [RUN]
12:48:52  3 of 7 START sql view model DEV.src_reviews .................................... [RUN]
12:48:53  1 of 7 OK created sql view model DEV.src_hosts ................................. [SUCCESS 1 in 1.13s]
12:48:53  4 of 7 START sql table model DEV.dim_hosts_cleansed ............................ [RUN]
12:48:54  3 of 7 OK created sql view model DEV.src_reviews ............................... [SUCCESS 1 in 1.29s]
12:48:54  5 of 7 START sql incremental model DEV.fct_reviews ............................. [RUN]
12:48:54  2 of 7 OK created sql view model DEV.src_listings .............................. [SUCCESS 1 in 1.42s]
12:48:54  6 of 7 START sql table model DEV.dim_listings_cleansed ......................... [RUN]
12:48:55  4 of 7 OK created sql table model DEV.dim_hosts_cleansed ....................... [SUCCESS 14111 in 1.85s]
12:48:56  5 of 7 OK created sql incremental model DEV.fct_reviews ........................ [SUCCESS 409697 in 2.39s]
12:48:56  6 of 7 OK created sql table model DEV.dim_listings_cleansed .................... [SUCCESS 17499 in 2.49s]
12:48:56  7 of 7 START sql table model DEV.dim_listings_w_hosts .......................... [RUN]
12:48:58  7 of 7 OK created sql table model DEV.dim_listings_w_hosts ..................... [SUCCESS 17499 in 1.74s]
12:48:59  
12:48:59  Finished running 1 incremental model, 3 table models, 3 view models in 0 hours 0 minutes and 8.41 seconds (8.41s).
12:48:59  Completed successfully
12:48:59  Done. PASS=7 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=7
```
> [!NOTE]
> 実行結果の確認：
> - `src_*` 3 モデルは **view** として作成；
> - `dim_*` 3 モデルは **table** として作成；
> - `fct_reviews` は **incremental** モデルとして初回全件の **409,697 行** がロードされました！

### ステップ 3：2回目の実行で増分同期を検証
データを変更せずに直ちにもう一度 `dbt run` を実行します：
```powershell
dbt run --profiles-dir .
```

2回目のターミナル実行ログ：
```text
12:49:09  1 of 7 OK created sql view model DEV.src_hosts ................................. [SUCCESS 1 in 0.56s]
12:49:09  3 of 7 OK created sql view model DEV.src_reviews ............................... [SUCCESS 1 in 0.57s]
12:49:09  2 of 7 OK created sql view model DEV.src_listings .............................. [SUCCESS 1 in 0.68s]
12:49:10  6 of 7 OK created sql table model DEV.dim_listings_cleansed .................... [SUCCESS 17499 in 0.93s]
12:49:11  4 of 7 OK created sql table model DEV.dim_hosts_cleansed ....................... [SUCCESS 14111 in 1.43s]
12:49:12  5 of 7 OK created sql incremental model DEV.fct_reviews ........................ [SUCCESS 0 in 2.28s]
12:49:13  7 of 7 OK created sql table model DEV.dim_listings_w_hosts ..................... [SUCCESS 17499 in 2.06s]
12:49:13  Finished running 1 incremental model, 3 table models, 3 view models in 0 hours 0 minutes and 5.94 seconds (5.94s).
```
> [!IMPORTANT]
> `fct_reviews` の結果に注目してください：**`SUCCESS 0 in 2.28s`**！
> `{% if is_incremental() %}` 判定が働き、新規データが存在しないため 0 件の同期で即座に完了したことが実証されました。

### Snowflake 側の実体確認
Snowflake でオブジェクトと行数を確認します：
```sql
SHOW OBJECTS IN SCHEMA AIRBNB.DEV;
```

実際のオブジェクト一覧：
```text
KIND       | NAME                      | ROWS
TABLE      | DIM_HOSTS_CLEANSED        | 14,111
TABLE      | DIM_LISTINGS_CLEANSED     | 17,499
TABLE      | DIM_LISTINGS_W_HOSTS      | 17,499
TABLE      | FCT_REVIEWS               | 409,697
VIEW       | SRC_HOSTS                 | 0 (ビューのためストレージ消費なし)
VIEW       | SRC_LISTINGS              | 0 (ビューのためストレージ消費なし)
VIEW       | SRC_REVIEWS               | 0 (ビューのためストレージ消費なし)
```

---

## 第7部：現場の落とし穴とベストプラクティス

### 1. 落とし穴 1：旧オブジェクトの自動クリーンアップなし（Object Shadowing）
- **事象**：モデルの設定を `table` から `view` や `ephemeral` に変更しても、Snowflake 内に過去のテーブルが残存する。
- **原因**：dbt は定義されたモデルのビルドのみを行い、**過去に作成された同名の異なるオブジェクトを自動検知して削除することはありません**。
- **回避策**：マテリアライゼーション戦略の変更やモデル削除時は、Snowflake 側で `DROP TABLE / VIEW IF EXISTS` を手動実行して不要オブジェクトを掃除します。

### 2. 落とし穴 2：スキーマ変更時の増分データズレ
- **事象**：上流で新しい列が追加された際、増分ロードの `INSERT` で列順序が狂う。
- **原因**：増分モデルのターゲット物理テーブル構造は初回作成時に固定されており、動的追従できないため。
- **回避策**：
  1. `on_schema_change = 'fail'` を指定して予期せぬズレを検知・停止させる；
  2. 正式なスキーマ拡張時は、全件再構築フラグで実行する：
     ```powershell
     dbt run --full-refresh --select fct_reviews
     ```

---

## 第8部：公式認定クイズで理解度チェック (Quiz)

dbt Analytics Engineering 公式認定試験の出題形式に準拠した重要チェック問題です：

### 問題 1 (単一選択)
**問**：絶え間なく流入するイベントデータ（Event Data）を扱い、既存の履歴テーブルに対して新規レコードのみを追加・同期したい場合、どのマテリアライゼーションを選択すべきですか？
- A. `table`
- B. `incremental`
- C. `ephemeral`
- D. `view`

> **正解**：**B**
> **解説**：`table` は毎回全件を再構築するため大規模データでは非効率です。`ephemeral` は CTE にコンパイルされるため永続化されません。`view` は参照時に毎回全件集計します。物理テーブルの高速応答と、差分のみを追加する高効率性を両立できるのは **`incremental`** のみです。

---

### 問題 2 (単一選択)
**問**：SQL の変換ロジックをモジュール化して再利用したいが、データベース内に物理テーブルや論理ビューなどの「実体」を一切作成したくない場合、どのマテリアライゼーションを選択すべきですか？
- A. `table`
- B. `ephemeral`
- C. `view`
- D. `incremental`

> **正解**：**B**
> **解説**：`table` および `incremental` は物理テーブルを作成し、`view` は論理ビューを作成します。**`ephemeral`** のみがデータベース内に実体を作成せず、コンパイル時に下流モデルの CTE として直接インライン展開されます。

---

## 本章のまとめ

本章を通じて、dbt のエンタープライズ向けマテリアライゼーションと依存管理の全容をマスターしました：
1. **4つのマテリアライゼーションの適材適所**：`view`（低コスト）、`table`（高速ディメンション）、`incremental`（大規模ファクト差分更新）、`ephemeral`（軽量 CTE）；
2. **`ref()` マクロと DAG 依存関係の完全な理解**：環境依存を排除し、安全なビルド順序を自動化；
3. **Airbnb のクレンジング層と増分ファクトの実装完了**：Snowflake 上で 7 つのモデルを完全に検証；
4. **差分同期の高速性の確認**：`is_incremental()` と `&#123;&#123; this &#125;&#125;` による秒単位の差分更新を実証。

続く第 05 章では、**Seeds（静的マスタデータの取り込み）** および **Snapshots（SCD Type-2 履歴管理・スローチェンジングディメンション）** の実践的な構築手法を学んでいきます！
