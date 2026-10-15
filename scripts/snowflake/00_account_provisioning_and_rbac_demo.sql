-- ==============================================================================
-- 脚本名称: 00_account_provisioning_and_rbac_demo.sql
-- 业务场景: 金融级 Snowflake 账号开通、多规格算力、多表隔离与单角色/多角色用户实战验证
-- 适用平台: Snowflake Snowsight Worksheet / SnowSQL
-- 包含内容:
--   1. 阶段 A (SYSADMIN): 创建多规格 Warehouse、数据库及高低安全级两张业务表
--   2. 阶段 B (USERADMIN): 创建三层业务角色体系并挂载继承树
--   3. 阶段 C (SYSADMIN): Warehouse 规格赋权与多表细粒度权限隔离
--   4. 阶段 D (USERADMIN): 开通单角色用户与多角色用户（含 MFA 与改密策略）
--   5. 阶段 E (USERADMIN): 绑定角色至用户
--   6. 阶段 F (验证阶段): 模拟两类用户登录，执行权限隔离与越权拦截验证
-- ==============================================================================


-- ==============================================================================
-- 【阶段 A】：计算与存储资源定义 (使用 SYSADMIN 角色)
-- ==============================================================================
USE ROLE SYSADMIN;

-- 1. 创建多规格计算仓库 (Warehouse)
-- 规格 ①：轻量日常分析用（X-Small，自动挂起 60 秒，自动拉起）
CREATE WAREHOUSE IF NOT EXISTS MITSUI_ANALYST_WH
    WITH WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = '用于日常分析师轻量即席查询与突合验证 (X-Small)';

-- 规格 ②：高吞吐 ETL / 批量数据迁移用（Medium，自动挂起 120 秒）
CREATE WAREHOUSE IF NOT EXISTS MITSUI_ETL_WH
    WITH WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 120
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = '用于夜间批处理、大量数据迁移与高性能计算 (Medium)';

-- 2. 创建数据库与 Schema
CREATE DATABASE IF NOT EXISTS MITSUI_SEC_DB
    COMMENT = '三井证券核心数据仓库';

CREATE SCHEMA IF NOT EXISTS MITSUI_SEC_DB.RAW_ORACLE
    COMMENT = '从 Oracle 11g 迁移的原始数据层';

-- 3. 创建不同安全级别的两张业务表（测试细粒度表权限隔离）
-- 表 ①：客户交易明细公开流水（普通分析师可读，工程师可读写）
CREATE OR REPLACE TABLE MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL (
    TRADE_ID    VARCHAR(20),
    CUST_ID     VARCHAR(10),
    AMOUNT_JPY  NUMBER(18, 3),
    TRADE_DATE  VARCHAR(8)
);

-- 插入一条初始演示数据
INSERT INTO MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL VALUES 
('TRD_20260001', 'CUST_001', 1250000.000, '20260315');

-- 表 ②：高敏内控费率表（仅允许工程师/主管访问，对普通分析师完全不可见）
CREATE OR REPLACE TABLE MITSUI_SEC_DB.RAW_ORACLE.CONFIDENTIAL_FEE_RATES (
    TIER_ID     VARCHAR(10),
    COMMISSION  NUMBER(5, 4),
    UPDATED_BY  VARCHAR(50)
);

-- 插入一条初始机密数据
INSERT INTO MITSUI_SEC_DB.RAW_ORACLE.CONFIDENTIAL_FEE_RATES VALUES 
('TIER_GOLD', 0.0015, 'SYSTEM_ADMIN');


-- ==============================================================================
-- 【阶段 B】：业务角色定义与继承树构建 (使用 USERADMIN 角色)
-- ==============================================================================
USE ROLE USERADMIN;

-- 1. 创建三大职责角色
CREATE ROLE IF NOT EXISTS MITSUI_ADMIN_ROLE    COMMENT = '三井证券项目总管（具备资源运维与审计管理权）';
CREATE ROLE IF NOT EXISTS MITSUI_ENGINEER_ROLE COMMENT = '数据工程师（具备 ETL 读写与高性能计算权）';
CREATE ROLE IF NOT EXISTS MITSUI_ANALYST_ROLE  COMMENT = '数据分析师（仅具备指定表只读与轻量计算权）';

-- 2. 规范角色继承树（挂载至 SYSADMIN，防止资产孤立，避免滥用 ACCOUNTADMIN）
GRANT ROLE MITSUI_ADMIN_ROLE TO ROLE SYSADMIN;
GRANT ROLE MITSUI_ENGINEER_ROLE TO ROLE MITSUI_ADMIN_ROLE;
GRANT ROLE MITSUI_ANALYST_ROLE TO ROLE MITSUI_ENGINEER_ROLE;


-- ==============================================================================
-- 【阶段 C】：多规格算力与多表细粒度赋权 (使用 SYSADMIN 角色)
-- ==============================================================================
USE ROLE SYSADMIN;

-- 1. 基础环境 USAGE 授权（各角色必须拥有 DB 与 Schema 的访问路径）
GRANT USAGE ON DATABASE MITSUI_SEC_DB TO ROLE MITSUI_ANALYST_ROLE;
GRANT USAGE ON SCHEMA MITSUI_SEC_DB.RAW_ORACLE TO ROLE MITSUI_ANALYST_ROLE;

-- 2. 多规格 Warehouse 差异化授权
-- 分析师角色仅能使用轻量级 X-Small 仓库（成本可控，单价 1 信用点/小时）
GRANT USAGE ON WAREHOUSE MITSUI_ANALYST_WH TO ROLE MITSUI_ANALYST_ROLE;

-- 工程师角色具备高性能 Medium 仓库的使用权（高并发吞吐，单价 4 信用点/小时）
GRANT USAGE ON WAREHOUSE MITSUI_ETL_WH TO ROLE MITSUI_ENGINEER_ROLE;

-- 3. 多表权限差异化隔离授权
-- 表 ① 策略：普通明细表 (CUST_TRADE_DETAIL)
GRANT SELECT ON TABLE MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL TO ROLE MITSUI_ANALYST_ROLE;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL TO ROLE MITSUI_ENGINEER_ROLE;

-- 表 ② 策略：机密费率表 (CONFIDENTIAL_FEE_RATES)
-- 严禁授予 MITSUI_ANALYST_ROLE！仅授予工程师及主管
GRANT SELECT, INSERT, UPDATE ON TABLE MITSUI_SEC_DB.RAW_ORACLE.CONFIDENTIAL_FEE_RATES TO ROLE MITSUI_ENGINEER_ROLE;


-- ==============================================================================
-- 【阶段 D】：用户开通与属性设定 (使用 USERADMIN 角色)
-- ==============================================================================
USE ROLE USERADMIN;

-- 用户 ①：TANAKA_ANALYST（普通分析师，单一角色用户，使用 X-Small 算力）
CREATE USER IF NOT EXISTS TANAKA_ANALYST
    PASSWORD = 'InitPassword123#A'
    MUST_CHANGE_PASSWORD = FALSE           -- 实验演示环境设为 FALSE，生产建议设为 TRUE
    DEFAULT_ROLE = MITSUI_ANALYST_ROLE
    DEFAULT_WAREHOUSE = MITSUI_ANALYST_WH
    EMAIL = 'tanaka@mitsui-sec.co.jp'
    COMMENT = '证券业务分析师，负责数据日常核对（单一角色）';

-- 用户 ②：SATO_TECH_LEAD（技术主管/资深工程师，多角色用户，可调用 Medium 算力）
CREATE USER IF NOT EXISTS SATO_TECH_LEAD
    PASSWORD = 'InitPassword123#B'
    MUST_CHANGE_PASSWORD = FALSE           -- 实验演示环境设为 FALSE，生产建议设为 TRUE
    DEFAULT_ROLE = MITSUI_ENGINEER_ROLE
    DEFAULT_WAREHOUSE = MITSUI_ETL_WH
    EMAIL = 'sato@mitsui-sec.co.jp'
    COMMENT = '技术主管，兼顾迁移工程实施与业务审计（多角色）';


-- ==============================================================================
-- 【阶段 E】：角色绑定 (使用 USERADMIN 角色)
-- ==============================================================================
USE ROLE USERADMIN;

-- 模式 1：单一角色绑定（TANAKA 仅有分析师角色，受严格最小特权管控）
GRANT ROLE MITSUI_ANALYST_ROLE TO USER TANAKA_ANALYST;

-- 模式 2：多角色绑定（SATO 拥有全套业务角色，可按需切换上下文）
GRANT ROLE MITSUI_ENGINEER_ROLE TO USER SATO_TECH_LEAD;
GRANT ROLE MITSUI_ANALYST_ROLE TO USER SATO_TECH_LEAD;
GRANT ROLE MITSUI_ADMIN_ROLE TO USER SATO_TECH_LEAD;


-- ==============================================================================
-- 【阶段 F】：权限隔离与功能验证测试（可在当前 Worksheet 逐步切换验证）
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 场景 1：模拟 TANAKA_ANALYST（数据分析师，受限角色）
-- ------------------------------------------------------------------------------
USE ROLE MITSUI_ANALYST_ROLE;
USE WAREHOUSE MITSUI_ANALYST_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 验证 1.1：查看自身拥有角色（应仅见 MITSUI_ANALYST_ROLE 与 PUBLIC）
SHOW ROLES;

-- 验证 1.2：查询普通明细表（预期：成功读取 1 条数据）
SELECT * FROM CUST_TRADE_DETAIL;

-- 验证 1.3：越权写入测试（预期：失败！报错 SQL compilation error: Access denied）
-- INSERT INTO CUST_TRADE_DETAIL VALUES ('TRD_HACK', 'CUST_999', 999.000, '20260315');

-- 验证 1.4：访问机密高敏费率表（预期：失败！报错 Object 'CONFIDENTIAL_FEE_RATES' does not exist）
-- SELECT * FROM CONFIDENTIAL_FEE_RATES;

-- 验证 1.5：试图越权使用高吞吐仓库（预期：失败！报错 Object 'MITSUI_ETL_WH' does not exist）
-- USE WAREHOUSE MITSUI_ETL_WH;


-- ------------------------------------------------------------------------------
-- 场景 2：模拟 SATO_TECH_LEAD（技术主管，多角色自由切换）
-- ------------------------------------------------------------------------------
-- 切换到工程师角色
USE ROLE MITSUI_ENGINEER_ROLE;
USE WAREHOUSE MITSUI_ETL_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 验证 2.1：执行普通明细表写入（预期：成功插入）
INSERT INTO CUST_TRADE_DETAIL VALUES ('TRD_20260002', 'CUST_002', 8800000.000, '20260316');

-- 验证 2.2：访问机密高敏费率表（预期：成功读取机密费率数据）
SELECT * FROM CONFIDENTIAL_FEE_RATES;

-- 验证 2.3：多角色动态切换验证
-- 主管切换为分析师身份进行低成本即席对账：
USE ROLE MITSUI_ANALYST_ROLE;
USE WAREHOUSE MITSUI_ANALYST_WH;
SELECT COUNT(*), SUM(AMOUNT_JPY) FROM CUST_TRADE_DETAIL;

-- 主管切换回工程师身份进行批处理：
USE ROLE MITSUI_ENGINEER_ROLE;
USE WAREHOUSE MITSUI_ETL_WH;
SELECT 'ETL 权限验证就绪' AS STATUS;
