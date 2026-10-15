# 第06章：トラブルシューティングと本番運用ベストプラクティス

銀行証券 `CUST_TRADE_DETAIL` の移行検証において直面した実務上の重要課題と解決策をまとめます。

---

## 1. Oracle `BYTE` vs `CHAR` 語義による全角文字桁溢れ

- **事象**：Oracle で `VARCHAR2(100)` と定義すると、UTF-8 環境ではバイト数制限（100バイト）となり、全角日本語（1文字3バイト）は約33文字で `ORA-12899` エラーが発生する。
- **解決策**：Oracle 側で **`VARCHAR2(100 CHAR)`** と明示指定し、Snowflake 側の `VARCHAR(100)`（文字数カウント）と仕様を統一する。

---

## 2. 金額・数量の精度統一ルール（`NUMBER(18,3)`）

- **事象**：Snowflake で単に `NUMBER` と記述すると `NUMBER(38, 0)`（小数なし）と解釈され、外貨金額や手数料の端数が切り捨てられる。
- **解決策**：
  - 金額（円貨・外貨）：`NUMBER(18, 3)` で統一。
  - 取引数量：`NUMBER(15, 0)`。
  - 為替レート：`NUMBER(9, 6)`。

---

## 3. 日付項目の文字列形式統一（YYYYMMDD / YYYYMM）

- **事象**：Oracle の `DATE` 型は内部で時刻を保持しているため、日付比較時に不整合の原因となる。
- **解決策**：`COPY INTO` の変換式で約定日を `VARCHAR(8)`（YYYYMMDD）、決済対象月を `VARCHAR(6)`（YYYYMM）へ標準化する。

---

## 4. タイムゾーン起因の時刻ズレ防止（`TIMESTAMP_NTZ`）

- **事象**：`TIMESTAMP_LTZ` を使用すると、クライアント環境によって JST と UTC の 9 時間差が発生する。
- **解決策**：`TIMESTAMP_NTZ`（壁時計時刻）を採用し、基幹系の時刻をそのまま保持する。

---

## 5. 3 層ロール階層（Role Hierarchy）の徹底

```sql
USE ROLE USERADMIN;
GRANT ROLE MITSUI_ADMIN TO ROLE SYSADMIN;
GRANT ROLE MITSUI_ENGINEER TO ROLE MITSUI_ADMIN;
GRANT ROLE MITSUI_ANALYST TO ROLE MITSUI_ENGINEER;
```
これにより、孤立オブジェクトの発生を防止し、最小特権の原則を満たします。
