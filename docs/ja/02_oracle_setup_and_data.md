# 第02章：Oracle 移行元環境構築と模擬証券データ投入

Docker 上に検証用 Oracle 11g コンテナを立ち上げ、VSCode Database Client を用いた疎通確認、および `CUST_TRADE_DETAIL`（顧客取引明細）のテーブル作成と 11 パターンのテストデータ投入を行います。

---

## 1. Docker による Oracle 11g の起動

```bash
# 1. イメージの取得
sudo docker pull gvenzl/oracle-xe:11

# 2. コンテナ起動 (共有メモリ 1GB、ポート 1521、データ永続化)
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

## 2. VSCode Database Client による接続確認

VSCode の Database Client 拡張機能より接続情報を設定します：
- **Host**: `127.0.0.1`
- **Port**: `1521`
- **Database**: `xe`
- **Username**: `system`
- **Password**: `Mitsui_Sec_2026`

![VSCode接続設定](../images/02_img_01.png)

接続テストを実行し、「Connected」となることを確認します：
![接続成功](../images/02_img_02.png)

---

## 3. 顧客取引明細テーブル DDL（`CUST_TRADE_DETAIL`）

```sql
CREATE TABLE CUST_TRADE_DETAIL (
    TRADE_QTY          NUMBER(15)        DEFAULT 0        NOT NULL,  -- 取引数量
    AMOUNT_JPY         NUMBER(18,3)      DEFAULT 0        NOT NULL,  -- 約定金額・円貨
    AMOUNT_FCY         NUMBER(18,3)      DEFAULT 0,                  -- 約定金額・外貨
    CCY_CODE           VARCHAR2(3),                                  -- 通貨区分
    EXCHANGE_RATE      NUMBER(9,6),                                  -- 為替レート
    REMARKS            VARCHAR2(100 CHAR) DEFAULT ' ',               -- 摘要・備考（CHAR語義指定）
    CUST_ID            VARCHAR2(10 CHAR)  NOT NULL,                  -- 顧客ID
    TRADE_TYPE_CD      VARCHAR2(2 CHAR)   NOT NULL,                  -- 取引区分
    BRANCH_CD          VARCHAR2(4 CHAR)   NOT NULL,                  -- 支店コード
    TRADE_DATE         DATE               NOT NULL,                  -- 約定日
    SETTLE_MONTH       DATE,                                         -- 決済対象月
    REG_DATETIME       DATE               DEFAULT SYSDATE NOT NULL,  -- 登録日時
    UPD_DATETIME       DATE,                                         -- 更新日時
    CONSTRAINT PK_CUST_TRADE_DETAIL PRIMARY KEY (CUST_ID, TRADE_DATE, TRADE_TYPE_CD)
);
```

---

## 4. 11 パターンの模擬テストデータ投入

[`scripts/oracle/02_seed_trades_data.sql`](file:///home/fx/Develop/SnowflakeBlog/scripts/oracle/02_seed_trades_data.sql) を実行し、全角文字境界値、外貨・為替レート、極限値（999999999999999）を含むデータを投入します。

```sql
-- 投入後確認クエリ
SELECT COUNT(*) AS TOTAL_ROWS, SUM(AMOUNT_JPY) AS SUM_JPY, SUM(TRADE_QTY) AS SUM_QTY
FROM CUST_TRADE_DETAIL;
```
