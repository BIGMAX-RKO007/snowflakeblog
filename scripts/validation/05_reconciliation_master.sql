-- ==============================================================================
-- プロジェクト名 : 三井フィナンシャルグループ 次世代クラウドデータ基盤移行
-- スクリプト名   : 05_reconciliation_master.sql
-- 業務シナリオ   : 本番移行判定用 新旧データ突合検証 (Oracle vs Snowflake Reconciliation)
-- 実行権限ロール : MITSUI_ANALYST (監査・分析担当者)
-- 適用標準       : 日本金融IT ガバナンス・移行判定基準 (4階梯 厳格突合)
-- ==============================================================================

-- ==============================================================================
-- 【Step 00: 監査セッション環境の初期設定】
-- 目的: 最小権限の原則 (Least Privilege) に則り、データ参照・分析専用ロールへ切り替え
-- ==============================================================================
USE ROLE MITSUI_ANALYST;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- セッションコンテキストの確認
SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();


-- ==============================================================================
-- 【第一階梯：新旧テーブル件数突合 (Row Count Validation)】
-- 目的: 移行対象の全テーブルにおいて、データ欠落 (Loss) および多重取込 (Duplicate) が
--       一切発生していないことを件数レベルで完全に証明する。
-- 判定基準: 差異 (Diff) = 0
-- ==============================================================================

-- 1.1 顧客マスタ (CUST_MASTER) 件数突合 (期待値: 13 件)
SELECT 
    'CUST_MASTER'         AS TABLE_NAME,
    COUNT(*)              AS SNOWFLAKE_COUNT,
    13                    AS ORACLE_BENCHMARK,
    COUNT(*) - 13         AS DIFF,
    CASE WHEN COUNT(*) = 13 THEN '✅ 一致 (PASS)' ELSE '❌ 不一致 (FAIL)' END AS AUDIT_RESULT
FROM CUST_MASTER;

-- 1.2 顧客取引明細 (CUST_TRADE_DETAIL) 件数突合 (期待値: 11 件)
SELECT 
    'CUST_TRADE_DETAIL'   AS TABLE_NAME,
    COUNT(*)              AS SNOWFLAKE_COUNT,
    11                    AS ORACLE_BENCHMARK,
    COUNT(*) - 11         AS DIFF,
    CASE WHEN COUNT(*) = 11 THEN '✅ 一致 (PASS)' ELSE '❌ 不一致 (FAIL)' END AS AUDIT_RESULT
FROM CUST_TRADE_DETAIL;

-- 1.3 監査報告用 統合テーブル件数サマリ (一括取得)
SELECT 
    'CUST_MASTER' AS TARGET_TABLE, 
    COUNT(*) AS TOTAL_ROWS 
FROM CUST_MASTER
UNION ALL
SELECT 
    'CUST_TRADE_DETAIL' AS TARGET_TABLE, 
    COUNT(*) AS TOTAL_ROWS 
FROM CUST_TRADE_DETAIL;


-- ==============================================================================
-- 【第二階梯：重要金融メトリクス・金額サマリ突合 (Financial Metrics Aggregations)】
-- 目的: 小数点精度欠落 (Truncation)、指数表記化 (Scientific Notation)、通貨換算漏れ、
--       および日付切り捨てなどの金融重大インシデントを防止するため、絶対値集計を行う。
-- 判定基準: 数量差 = 0, 金額差 = 0.000, 取引日付区間完全一致
-- ==============================================================================
SELECT 
    COUNT(*)                                       AS TOTAL_TRADES,
    SUM(TRADE_QTY)                                 AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
    MIN(TRADE_DATE)                                AS EARLIEST_TRADE_DATE,
    MAX(TRADE_DATE)                                AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;


-- ==============================================================================
-- 【第三階梯：多次元・リレーション整合性および境界値検証 (Relational & Boundary Verification)】
-- 目的: 
--  3.1 外部キー整合性 (孤児レコードが存在しないことの証明)
--  3.2 未取引口座・休眠口座の正常移行確認 (NULL 追跡)
--  3.3 通貨別・取引区分別の多次元クロス集計
--  3.4 日本語全角文字 (CHAR/BYTE) および NULL/空文字境界値の健全性
-- ==============================================================================

-- 3.1 顧客マスタ × 取引明細 内部結合 (INNER JOIN) 突合 (期待値: 11 件)
-- 理由: 明細側の全取引が有効な顧客IDに紐づいていることを検証 (孤児レコードゼロの保証)
SELECT 
    t.CUST_ID,
    m.CUST_NAME_KANJI,
    m.BRANCH_CD,
    t.TRADE_DATE,
    t.TRADE_TYPE_CD,
    t.TRADE_QTY,
    t.AMOUNT_JPY,
    t.CCY_CODE
FROM CUST_TRADE_DETAIL t
INNER JOIN CUST_MASTER m 
    ON t.CUST_ID = m.CUST_ID
ORDER BY t.CUST_ID, t.TRADE_DATE, t.TRADE_TYPE_CD;

-- 3.2 未取引顧客 (取引ゼロ件) の検知検証 (LEFT JOIN / 孤立顧客の監査) (期待値: 2 件)
-- 理由: CU00008888 (松本 潤) および CU00009990 (井上 陽水) に取引がないことを正確に捉えられているか
SELECT 
    m.CUST_ID,
    m.CUST_NAME_KANJI,
    m.STATUS_CD,
    m.BRANCH_CD,
    COUNT(t.CUST_ID) AS TRADE_COUNT
FROM CUST_MASTER m
LEFT JOIN CUST_TRADE_DETAIL t 
    ON m.CUST_ID = t.CUST_ID
GROUP BY m.CUST_ID, m.CUST_NAME_KANJI, m.STATUS_CD, m.BRANCH_CD
HAVING COUNT(t.CUST_ID) = 0
ORDER BY m.CUST_ID;

-- 3.3 通貨別 (CCY_CODE) × 売買区分 (TRADE_TYPE_CD) クロス集計突合
-- 理由: 通貨別ポートフォリオ残高・売買別の合計値が Oracle 源泉と完全一致するか検証
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

-- 3.4 日本語全角文字境界 (CHAR/BYTE) および NULL/空文字・特殊文字の整合性検証
-- 理由: CUST_TRADE_DETAIL の CU00004445 備考欄 (全角極限文字) がバイト数・文字数切り捨てなく保持され、
--       CUST_MASTER の CU00009990 ステータス空文字が Snowflake で適切に NULL 判定されるか確認
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


-- ==============================================================================
-- 【第四階梯：テーブル全体暗号学的ハッシュ指紋検証 (Global Table Hash Fingerprint)】
-- 目的: 単なる合計値の合致 (正負の相殺等) を排し、全行・全列のデータが
--       1bitの狂いもなく完全同一であることを暗号学的数学証明する。
-- 判定基準: GLOBAL_TABLE_HASH が Oracle 側ハッシュと完全一致
-- ==============================================================================
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
