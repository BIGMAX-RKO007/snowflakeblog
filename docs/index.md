---
layout: home

hero:
  name: "銀行証券 DX 実戦プロジェクト"
  text: "Oracle 11g から Snowflake への企業級データ移行"
  tagline: "厳格な金融RBAC権限分離・高速COPY INTO・新旧データ4段階突合検証の完全再現"
  image:
    src: /snowflake.svg
    alt: Snowflake Architecture
  actions:
    - theme: brand
      text: チュートリアルを始める
      link: /00_architecture_overview
    - theme: alt
      text: 3層RBAC設計を見る
      link: /03_snowflake_rbac_setup

features:
  - icon: 🏛️
    title: 金融機関向け 3 層 RBAC 権限モデル
    details: SYSADMIN 傘下に MITSUI_ADMIN（総括）→ MITSUI_ENGINEER（移行・ETL）→ MITSUI_ANALYST（分析突合）を厳格分離。最小特権の原則を徹底。
  - icon: ⚡
    title: 高速並列データ取込 (COPY INTO)
    details: 内部名前付きステージ @MITSUI_STAGE とコンピュート自動停止機能を活用し、数万件の取引明細を秒速でクラウドへ安全に取り込み。
  - icon: 🔍
    title: 4 段階の新旧データ突合検証 (Reconciliation)
    details: 行数突合、金額・手数料集計突合、全量 HASH_AGG データ指紋検証、差分抽出により 100% のデータ整合性を担保。
  - icon: 🛡️
    title: エンタープライズ耐障害性・セキュリティ
    details: Time Travel (0〜90日)、Fail-safe (7日)、Zero-copy Clone による秒速バックアップ、AES-256 自動キーローテーションを完備。
  - icon: 📐
    title: Oracle → Snowflake 型推計方針（8大設計ルール）
    details: VARCHAR(8) による業務日付統一、TIMESTAMP_NTZ(6) 監査分離、全角文字溢れ防止など、金融実務に即した型定義標準を確立。
  - icon: 💡
    title: 現場直伝の知見とトラブルシューティング
    details: コンピュートコスト最適化（月$508モデル）、タイムゾーン時差防止、ロードエラー即時追跡など、現場の落とし穴と回避策を凝縮。
---

<div class="vp-doc" style="max-width: 960px; margin: 40px auto 0; padding: 0 24px;">

## 🚀 移行工程全体像 (End-to-End Migration Flow)

本プロジェクトでは、証券取引の根幹を成す「顧客取引明細データ（`CUST_TRADE_DETAIL`）」を題材に、本番金融システム水準の厳格な移行工程を網羅しています。

```mermaid
flowchart LR
    classDef srcStyle fill:#f8fafc,stroke:#dc2626,stroke-width:2px,color:#0f172a;
    classDef stageStyle fill:#f8fafc,stroke:#2563eb,stroke-width:2px,color:#0f172a;
    classDef dwhStyle fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#ffffff;
    classDef verifyStyle fill:#16a34a,stroke:#15803d,stroke-width:2px,color:#ffffff;

    subgraph Source ["【オンプレミス / 移行元】"]
        O1["Oracle 11g EE<br/>CUST_TRADE_DETAIL<br/>(11件の極限境界値)"]:::srcStyle
        O2["CSV 抽出・暗号化<br/>UTF-8 / LF / GZIP"]:::srcStyle
        O1 --> O2
    end

    subgraph Staging ["【クラウド連携】"]
        S1["内部ステージ<br/>@MITSUI_STAGE<br/>(暗号化ストレージ)"]:::stageStyle
        O2 -->|SnowSQL PUT| S1
    end

    subgraph Snowflake ["【Snowflake 移行先 DWH】"]
        W1["MITSUI_WH (XS)<br/>自動停止 60秒"]:::dwhStyle
        T1["MITSUI_DB.PUBLIC<br/>CUST_TRADE_DETAIL<br/>(8大型推計標準準拠)"]:::dwhStyle
        S1 -->|COPY INTO<br/>FORCE=TRUE| T1
        W1 -.->|コンピュート提供| T1
    end

    subgraph Audit ["【新旧突合・品質監査】"]
        V1["Step 1: 行数カウント突合"]:::verifyStyle
        V2["Step 2: 金額・手数料集計突合"]:::verifyStyle
        V3["Step 3: HASH_AGG 指紋突合"]:::verifyStyle
        V4["Step 4: MINUS 差分全件抽出"]:::verifyStyle
        T1 --> V1 & V2 & V3 & V4
    end
```

---

## 📊 主要成果指標 (Key Project Metrics)

| 評価指標 | 達成基準 | 実装内容と成果 |
| :--- | :---: | :--- |
| **データ整合性** | **100% 一致** | 4 段階の突合監査（行数・集計値・HASH_AGG データ指紋・全量 MINUS 差分抽出）により差分 0 件を証明。 |
| **セキュリティ・権限分離** | **最小特権達成** | ACCOUNTADMIN/SECURITYADMIN を基盤担当に集約し、SYSADMIN 配下に 3 階層業務ロールを構築。 |
| **データ復元・耐障害性** | **RPO=0 / 秒速復旧** | Time Travel (最大 90 日) と Zero-copy Clone を組み合わせ、ストレージ追加コスト 0 で秒速スナップショット確保。 |
| **文字コード・型互換性** | **溢れ・文字化けゼロ** | Oracle の BYTE 語義から Snowflake の文字数カウント `VARCHAR(100)` への移行標準を策定。 |
| **コスト最適化** | **月額約 $508** | コンピュート自動停止（60秒）、Micro-partition 差分課金、XS ウェアハウス活用による極小化。 |

---

## 🗺️ 実践チュートリアル ナビゲーション

各章の手順に従うことで、ゼロから本番水準の Snowflake 移行環境を構築できます。

1. [**00. プロジェクト背景とアーキテクチャ設計**](/00_architecture_overview)  
   現行課題、オブジェクト体系（19種）、8大データ型推計ルール、パラメータ継承構造、耐障害性。
2. [**01. Snowflake アカウント開設と初期設定**](/01_snowflake_signup)  
   30 日間無料トライアル環境の払い出し、クラウド（AWS/Azure）選定、初期ログイン手順。
3. [**02. Oracle 移行元環境構築と模擬データ投入**](/02_oracle_setup_and_data)  
   Docker による Oracle 11g XE 起動、極限境界値を含む 11 件のテストケース作成、データ抽出。
4. [**03. 3層RBAC権限モデルと環境構築**](/03_snowflake_rbac_setup)  
   MITSUI_ADMIN / ENGINEER / ANALYST の 3 階層ロール設計、Step 4.1〜4.15 の SQL 実行。
5. [**04. データ移行実務（抽出・ステージ・取込）**](/04_data_migration)  
   内部名前付きステージへのアップロード、`COPY INTO` によるバルクインロード、エラー追跡。
6. [**05. 移行後データ突合検証・整合性監査**](/05_data_reconciliation)  
   金融監査に耐えうる 4 段階の突合クエリ実行と、実データによる 100% 整合性証明。
7. [**06. トラブルシューティングとベストプラクティス**](/06_troubleshooting_tips)  
   文字コード桁溢れ、NUMBER 精度、日付文字列化の意義、クエリプロファイル最適化。

</div>
