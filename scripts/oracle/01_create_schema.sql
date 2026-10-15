-- ==============================================================================
-- 脚本名称: 01_create_schema.sql
-- 业务场景: 银行证券 Oracle 11g 源库顾客取引明细表 (CUST_TRADE_DETAIL) DDL
-- 容器环境: gvenzl/oracle-xe:11 (端口 1521, 密码 Mitsui_Sec_2026)
-- ==============================================================================

-- ============================================================
-- 1. 创建核心业务表: CUST_TRADE_DETAIL (顧客取引明細)
-- ============================================================
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

COMMENT ON TABLE CUST_TRADE_DETAIL IS '顧客取引明細（移行前Oracle設計）';
COMMENT ON COLUMN CUST_TRADE_DETAIL.REMARKS IS '摘要・備考：VARCHAR2(100 CHAR)。全角/半角混在時も100文字まで格納可能。Snowflake移行時はVARCHAR(100)へ対応';
COMMENT ON COLUMN CUST_TRADE_DETAIL.TRADE_DATE IS '約定日：DATE型。Snowflake移行時はVarchar(8) YYYYMMDD形式へ変換予定';
COMMENT ON COLUMN CUST_TRADE_DETAIL.SETTLE_MONTH IS '決済対象月：DATE型（月初日で代表）。Snowflake移行時はVarchar(6) YYYYMM形式へ変換予定';
COMMENT ON COLUMN CUST_TRADE_DETAIL.REG_DATETIME IS '登録日時：DATE型（秒まで）。Snowflake移行時はTimestamp_ntz(6)へ変換予定（小数秒は新規付与）';
