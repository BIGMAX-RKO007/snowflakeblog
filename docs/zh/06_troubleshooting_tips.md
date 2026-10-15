# 第 06 章：生产避坑指南与金融级解决方案 (Troubleshooting & Best Practices)

在银行证券 `CUST_TRADE_DETAIL` 真实业务建模与迁移中，我们总结了最关键的 5 大生产避坑法则：

---

## ⚠️ 避坑点一：Oracle `BYTE` 与 `CHAR` 语义陷阱（全角日文字符溢出）

### 现象与根因：
- Oracle 默认定义 `VARCHAR2(100)` 时，若数据库使用 UTF-8/AL32UTF8 编码，这里的 `100` 代表 **100 字节（BYTE）**。
- 日文汉字和全角假名在 UTF-8 下每个占用 **3 字节**，因此 100 字节最多只能存储约 **33 个全角日文字符**！
- 当业务端输入如 `RPAD('全角文字百桁境界値検証用摘要欄', 100, '全')` 时，在 Oracle 端会直接抛出 `ORA-12899: value too large for column`。
- 与此相对，Snowflake 的 `VARCHAR(100)` **默认按字符数（Characters）计算**。

### 生产解决方案：
在 Oracle 源端建表时，对于可能包含日文汉字、假名及全角符号的字段，必须**显式指定 `CHAR` 语义**：
```sql
-- 确保全角半角混在时均能容纳 100 个字符
REMARKS VARCHAR2(100 CHAR) DEFAULT ' '
```
在 Snowflake 侧直接对应：
```sql
REMARKS VARCHAR(100) DEFAULT ' '
```

---

## ⚠️ 避坑点二：金额精度统一规范（`NUMBER(18,3)` 统一定义）

### 现象与根因：
金融业务中既有不需要小数的日元（JPY），也有需要 2~3 位小数的美元（USD）、欧元（EUR），甚至汇率（EXCHANGE_RATE）需要 6 位小数。
如果在 Snowflake 中随手定义成 `NUMBER`，默认会被 Snowflake 解释为 `NUMBER(38, 0)`（0位小数），导致所有外币小数位和汇率被暴力截断！

### 生产解决方案：
- 金额字段（邦货/外币）：统一固定为 `NUMBER(18, 3)`。
- 汇率字段：定义为 `NUMBER(9, 6)`。
- 股数数量：定义为 `NUMBER(15, 0)`。

---

## ⚠️ 避坑点三：日期与月份向字符串归一化 (YYYYMMDD / YYYYMM)

### 现象与根因：
Oracle 的 `DATE` 类型包含时分秒，在跨业务系统分析或对外报送时，常因为时间戳格式与时区产生歧义。银行证券业务规范明确要求：
- 约定日（日次）：归一化为 8 位定长纯数字字符串 `VARCHAR(8)`（`YYYYMMDD`）。
- 结算月：归一化为 6 位定长纯数字字符串 `VARCHAR(6)`（`YYYYMM`）。

### 转换解决方案：
在 `COPY INTO` 的 Transform 投影中完成高效清洗转换：
```sql
TO_VARCHAR(TO_DATE(t.$10), 'YYYYMMDD'), -- TRADE_DATE
TO_VARCHAR(TO_DATE(t.$11), 'YYYYMM'),   -- SETTLE_MONTH
```

---

## ⚠️ 避坑点四：时区漂移规避（`TIMESTAMP_NTZ` 壁钟时间）

### 现象与根因：
若将包含时分秒的登入时间存为 `TIMESTAMP_LTZ` 或 `TIMESTAMP_TZ`，当数据工程师在不同的客户端（例如不同时区的本地电脑或服务器）执行查询时，显示的时间会被自动加减时区差（如 JST 与 UTC 之间相差 9 小时）。

### 生产解决方案：
采用 `TIMESTAMP_NTZ`（No Time Zone），确保在 Oracle 数据库里记录的是几点几分几秒，迁移到 Snowflake 中看到的就是几点几分几秒，消除时间审计歧义。

---

## ⚠️ 避坑点五：四层角色继承树（规避孤立对象）

### 治理规范：
严格执行以下角色继承挂载：
```sql
USE ROLE USERADMIN;
GRANT ROLE MITSUI_ADMIN TO ROLE SYSADMIN;
GRANT ROLE MITSUI_ENGINEER TO ROLE MITSUI_ADMIN;
GRANT ROLE MITSUI_ANALYST TO ROLE MITSUI_ENGINEER;
```
这确保了：
1. 运维人员不会滥用最高权限 `ACCOUNTADMIN`；
2. 数据分析师仅具备只读和对账查询权限（最小特权）；
3. 系统管理员 `SYSADMIN` 可以全局透视并管理下属所有业务对象。
