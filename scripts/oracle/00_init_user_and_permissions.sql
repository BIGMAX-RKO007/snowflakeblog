-- ==============================================================================
-- 脚本名称: 00_init_user_and_permissions.sql
-- 业务场景: 三井证券 Oracle 11g 源库用户、角色、模式 (Schema) 与最小特权初始化
-- 执行身份: SYSTEM (超级管理员)
-- 映射目标: 建立 MITSUI_SRC (数据属主) 与 MITSUI_EXTRACTOR (只读抽取账号)
-- ==============================================================================

SET SQLBLANKLINES ON;
SET DEFINE OFF;

-- ============================================================
-- 1. 创建三井证券业务模式属主 (MITSUI_SRC)
-- 注：在 Oracle 体系中，创建用户 MITSUI_SRC 即等价于创建 Schema MITSUI_SRC
-- ============================================================
-- 若已存在则安全清理（可选）
-- DROP USER MITSUI_SRC CASCADE;

CREATE USER MITSUI_SRC IDENTIFIED BY Mitsui_Sec_2026
    DEFAULT TABLESPACE USERS
    TEMPORARY TABLESPACE TEMP
    QUOTA UNLIMITED ON USERS;

-- 授予基础建表与连接权限
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE TO MITSUI_SRC;


-- ============================================================
-- 2. 创建金融只读抽取角色 (ROLE_MITSUI_READ) 与抽取账号 (MITSUI_EXTRACTOR)
-- 目的: 满足金融安全合规与职责分离 (SoD) 原则，禁止在后续数据迁移中使用超级管理员
-- ============================================================
-- DROP USER MITSUI_EXTRACTOR CASCADE;
-- DROP ROLE ROLE_MITSUI_READ;

CREATE ROLE ROLE_MITSUI_READ;

CREATE USER MITSUI_EXTRACTOR IDENTIFIED BY Mitsui_Sec_2026
    DEFAULT TABLESPACE USERS
    TEMPORARY TABLESPACE TEMP;

GRANT CREATE SESSION TO MITSUI_EXTRACTOR;
GRANT ROLE_MITSUI_READ TO MITSUI_EXTRACTOR;

-- 验证创建结果
SELECT USERNAME, ACCOUNT_STATUS, DEFAULT_TABLESPACE, CREATED 
FROM DBA_USERS 
WHERE USERNAME IN ('MITSUI_SRC', 'MITSUI_EXTRACTOR');


COMMIT;
