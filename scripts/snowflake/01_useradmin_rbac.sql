-- ==============================================================================
-- 脚本名称: 01_useradmin_rbac.sql
-- 业务场景: 银行证券 Snowflake 企业级三层角色体系构建 (Step 4.1 ~ 4.4)
-- 规范依据: 严格对应 Excel [04.snowflake 环境搭建] 角色继承架构
-- 执行角色: USERADMIN
-- ==============================================================================

USE ROLE USERADMIN;

-- ------------------------------------------------------------------------------
-- 4.1：创建银行证券三层业务角色
-- ------------------------------------------------------------------------------

-- 1. 项目总管角色 (管理数仓、全局架构与分配权限)
CREATE ROLE IF NOT EXISTS MITSUI_ADMIN
    COMMENT = '银行证券项目总管角色 (继承至 SYSADMIN)';

-- 2. 数据工程师角色 (负责Stage建立、ETL跑批、表建模与COPY INTO)
CREATE ROLE IF NOT EXISTS MITSUI_ENGINEER
    COMMENT = '银行证券数据工程师角色 (继承至 MITSUI_ADMIN)';

-- 3. 数据分析师角色 (负责数据查询、报表与对账突合)
CREATE ROLE IF NOT EXISTS MITSUI_ANALYST
    COMMENT = '银行证券数据分析师角色 (继承至 MITSUI_ENGINEER)';


-- ------------------------------------------------------------------------------
-- 4.2: 赋予/继承权限 (建立 Role Hierarchy 角色继承树)
-- 架构: SYSADMIN -> MITSUI_ADMIN -> MITSUI_ENGINEER -> MITSUI_ANALYST
-- ------------------------------------------------------------------------------

-- 将 MITSUI_ADMIN 挂载到 SYSADMIN 之下
GRANT ROLE MITSUI_ADMIN TO ROLE SYSADMIN;

-- 将 MITSUI_ENGINEER 继承给 MITSUI_ADMIN
GRANT ROLE MITSUI_ENGINEER TO ROLE MITSUI_ADMIN;

-- 将 MITSUI_ANALYST 继承给 MITSUI_ENGINEER
GRANT ROLE MITSUI_ANALYST TO ROLE MITSUI_ENGINEER;


-- ------------------------------------------------------------------------------
-- 4.3：创建银行证券技术账号 (Users)
-- ------------------------------------------------------------------------------

-- 1. 工程师账号 (用于执行数据迁移与跑批)
CREATE USER IF NOT EXISTS MITSUI_ENGINEER_USER
    PASSWORD = 'MitsuiSecStrongPass2026!'
    DEFAULT_ROLE = MITSUI_ENGINEER
    DEFAULT_WAREHOUSE = MITSUI_WH
    MUST_CHANGE_PASSWORD = FALSE
    COMMENT = '银行证券ETL与迁移工程账号';

-- 2. 分析师账号 (用于突合对账与分析)
CREATE USER IF NOT EXISTS MITSUI_ANALYST_USER
    PASSWORD = 'MitsuiSecStrongPass2026!'
    DEFAULT_ROLE = MITSUI_ANALYST
    DEFAULT_WAREHOUSE = MITSUI_WH
    MUST_CHANGE_PASSWORD = FALSE
    COMMENT = '银行证券分析师业务账号';


-- ------------------------------------------------------------------------------
-- 4.4: 赋予角色给具体用户
-- ------------------------------------------------------------------------------
GRANT ROLE MITSUI_ENGINEER TO USER MITSUI_ENGINEER_USER;
GRANT ROLE MITSUI_ANALYST TO USER MITSUI_ANALYST_USER;

-- 验证角色与用户
SHOW ROLES LIKE 'MITSUI_%';
SHOW USERS LIKE 'MITSUI_%';
