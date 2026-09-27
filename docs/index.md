---
layout: home

hero:
  name: "三井証券 DX 実戦プロジェクト"
  text: "Oracle 11g から Snowflake への企業級データ移行"
  tagline: "厳格な金融RBAC権限分離・バッチ移行・新旧データ4段階突合検証の完全再現"
  image:
    src: https://www.snowflake.com/wp-content/themes/snowflake/assets/img/snowflake-logo.svg
    alt: Snowflake Architecture
  actions:
    - theme: brand
      text: 🇨🇳 开始中文实战教程
      link: /zh/00_architecture_overview
    - theme: alt
      text: 🇯🇵 日本語マニュアルを見る
      link: /ja/00_architecture_overview
    - theme: alt
      text: GitHub 源码仓库
      link: https://github.com/BIGMAX-RKO007/snowflakeblog

features:
  - icon: 🏛️
    title: 金融機関向け 3 層 RBAC 権限モデル
    details: SYSADMIN 傘下に MITSUI_ADMIN（総括）→ MITSUI_ENGINEER（移行・ETL）→ MITSUI_ANALYST（分析突合）を厳格分離。最小特権の原則を徹底。
  - icon: ⚡
    title: 高速並列データ取込 (COPY INTO)
    details: 内部名前付きステージ @MITSUI_STAGE とコンピュート自動停止機能を活用し、数万件の取引明細を秒速でクラウドへ取り込み。
  - icon: 🔍
    title: 4 段階の新旧データ突合検証 (Reconciliation)
    details: 行数突合、金額・手数料集計突合、全量 HASH_AGG データ指纹検証、差分抽出により 100% のデータ整合性を担保。
  - icon: 🛡️
    title: 実務知見とトラブルシューティング
    details: BYTE/CHAR語義の全角文字化け防止、NUMBER(18,3)精度保護、TIMESTAMP_NTZ時刻ズレ防止など、現場直伝の解決策を凝縮。
---
