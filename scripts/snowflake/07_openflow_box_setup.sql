-- ============================================================================
-- Script: 07_openflow_box_setup.sql
-- Description: Snowflake Openflow Connector for Box & Cortex Search Integration
-- Compatible with Snowflake Openflow & Box Enterprise Platform (JWT Authentication)
-- ============================================================================

-- ============================================================================
-- Phase 1: Security & RBAC Infrastructure (Executed by ACCOUNTADMIN / SECURITYADMIN)
-- ============================================================================
USE ROLE SECURITYADMIN;

-- 1. Create Dedicated Role for Openflow Connector Runtime
CREATE ROLE IF NOT EXISTS OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Dedicated role for Snowflake Openflow Box connector execution';

-- 2. Create Read-Only Role for Downstream Applications (Cortex Search & Agent)
CREATE ROLE IF NOT EXISTS CORTEX_SEARCH_READ_ROLE
    COMMENT = 'Read-only role for Cortex Agent, CoWork, and enterprise RAG applications';

-- 3. Create Dedicated Service User for Openflow Runtime (Key-Pair Authentication)
CREATE USER IF NOT EXISTS OPENFLOW_BOX_SVC_USER
    TYPE = SERVICE
    DEFAULT_ROLE = OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Automated service user for Openflow Box Ingestion pipeline';

GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO USER OPENFLOW_BOX_SVC_USER;

-- Role Hierarchy: Grant to SYSADMIN for governance
GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO ROLE SYSADMIN;
GRANT ROLE CORTEX_SEARCH_READ_ROLE TO ROLE SYSADMIN;


-- ============================================================================
-- Phase 2: Compute & Storage Infrastructure (Executed by SYSADMIN)
-- ============================================================================
USE ROLE SYSADMIN;

-- 1. Create Ingestion Warehouse
CREATE WAREHOUSE IF NOT EXISTS OPENFLOW_INGEST_WH
    WITH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 120
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Dedicated compute warehouse for Openflow Box ingestion and Cortex chunking';

-- 2. Create Integration Database and Schemas
CREATE DATABASE IF NOT EXISTS BOX_INTEGRATION_DB
    COMMENT = 'Enterprise repository for Box unstructured data and Cortex knowledge base';

-- Landing schema for raw files, stages, and CDC hashes
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.BOX_LANDING_DATA
    COMMENT = 'Landing zone for raw ingested Box files and streaming audit log CDC';

-- Cortex schema for parsed chunks and search service
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.CORTEX
    COMMENT = 'Processed document chunks, embeddings, and Cortex Search Services';

-- 3. Grant Privileges to Openflow Role
GRANT USAGE, OPERATE ON WAREHOUSE OPENFLOW_INGEST_WH TO ROLE OPENFLOW_CONNECTOR_ROLE;
GRANT USAGE ON DATABASE BOX_INTEGRATION_DB TO ROLE OPENFLOW_CONNECTOR_ROLE;
GRANT USAGE ON SCHEMA BOX_INTEGRATION_DB.BOX_LANDING_DATA TO ROLE OPENFLOW_CONNECTOR_ROLE;
GRANT USAGE ON SCHEMA BOX_INTEGRATION_DB.CORTEX TO ROLE OPENFLOW_CONNECTOR_ROLE;

-- Necessary privileges for Openflow to manage landing tables, stages, and dynamic tables
GRANT CREATE TABLE, CREATE DYNAMIC TABLE, CREATE STAGE, CREATE SEQUENCE 
    ON SCHEMA BOX_INTEGRATION_DB.BOX_LANDING_DATA TO ROLE OPENFLOW_CONNECTOR_ROLE;

GRANT CREATE TABLE, CREATE DYNAMIC TABLE, CREATE CORTEX SEARCH SERVICE 
    ON SCHEMA BOX_INTEGRATION_DB.CORTEX TO ROLE OPENFLOW_CONNECTOR_ROLE;

-- Privileges for Cortex Read Role
GRANT USAGE ON WAREHOUSE OPENFLOW_INGEST_WH TO ROLE CORTEX_SEARCH_READ_ROLE;
GRANT USAGE ON DATABASE BOX_INTEGRATION_DB TO ROLE CORTEX_SEARCH_READ_ROLE;
GRANT USAGE ON SCHEMA BOX_INTEGRATION_DB.CORTEX TO ROLE CORTEX_SEARCH_READ_ROLE;


-- ============================================================================
-- Phase 3: Stage & Table Schema Setup (Executed by OPENFLOW_CONNECTOR_ROLE)
-- ============================================================================
USE ROLE OPENFLOW_CONNECTOR_ROLE;
USE WAREHOUSE OPENFLOW_INGEST_WH;
USE DATABASE BOX_INTEGRATION_DB;
USE SCHEMA BOX_LANDING_DATA;

-- 1. Internal Stage with Directory Enabled for Ingested Box Files
CREATE OR REPLACE STAGE BOX_RAW_STAGE
    DIRECTORY = (ENABLE = TRUE)
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
    COMMENT = 'Secure internal stage storing raw documents ingested from Box folders';

-- 2. Document Metadata Table (tracks Box file details and ACL permissions)
CREATE OR REPLACE TABLE BOX_DOCUMENT_METADATA (
    FILE_ID             VARCHAR(64) PRIMARY KEY,
    FILE_NAME           VARCHAR(512) NOT NULL,
    FOLDER_ID           VARCHAR(64) NOT NULL,
    FOLDER_PATH         VARCHAR(1024),
    SHA256_HASH         VARCHAR(128) NOT NULL,
    SIZE_BYTES          NUMBER(38, 0),
    BOX_CREATED_AT      TIMESTAMP_NTZ,
    BOX_MODIFIED_AT     TIMESTAMP_NTZ,
    INGESTED_AT         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    USER_EMAILS         ARRAY COMMENT 'List of user emails authorized to access this document in Box (ACL filter)'
)
COMMENT = 'Master index of ingested Box documents with user-level access permissions';

-- 3. Document Content Parsing and Chunking Table in CORTEX schema
USE SCHEMA BOX_INTEGRATION_DB.CORTEX;

CREATE OR REPLACE TABLE BOX_DOC_CHUNKS (
    CHUNK_ID            VARCHAR(128) PRIMARY KEY,
    FILE_ID             VARCHAR(64) NOT NULL,
    FILE_NAME           VARCHAR(512) NOT NULL,
    FOLDER_ID           VARCHAR(64) NOT NULL,
    CHUNK_INDEX         NUMBER(10, 0),
    CHUNK_TEXT          VARCHAR(16777216) NOT NULL,
    USER_EMAILS         ARRAY NOT NULL,
    UPDATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Granular text chunks generated by SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER with attached ACLs';

-- 4. Cortex Search Service Definition (Continuous indexing with ACL filter)
CREATE OR REPLACE CORTEX SEARCH SERVICE BOX_ENTERPRISE_SEARCH_SERVICE
    ON CHUNK_TEXT
    ATTRIBUTES USER_EMAILS, FILE_NAME, FOLDER_ID
    WAREHOUSE = OPENFLOW_INGEST_WH
    TARGET_LAG = '1 hour'
    AS (
        SELECT 
            CHUNK_ID,
            CHUNK_TEXT,
            FILE_ID,
            FILE_NAME,
            FOLDER_ID,
            USER_EMAILS
        FROM BOX_INTEGRATION_DB.CORTEX.BOX_DOC_CHUNKS
    );

GRANT USAGE ON CORTEX SEARCH SERVICE BOX_ENTERPRISE_SEARCH_SERVICE TO ROLE CORTEX_SEARCH_READ_ROLE;


-- ============================================================================
-- Phase 4: Sample Data Seed & ACL Verification Query
-- ============================================================================

-- Insert sample technical rules and manuals with varying access permissions
INSERT INTO BOX_INTEGRATION_DB.BOX_LANDING_DATA.BOX_DOCUMENT_METADATA 
(FILE_ID, FILE_NAME, FOLDER_ID, FOLDER_PATH, SHA256_HASH, SIZE_BYTES, BOX_CREATED_AT, BOX_MODIFIED_AT, USER_EMAILS)
SELECT 
    '1000101', 
    '01_情報セキュリティ基本規程_2026.pdf', 
    '99001', 
    '/全社規程集/セキュリティ', 
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 
    148290, 
    CURRENT_TIMESTAMP(), 
    CURRENT_TIMESTAMP(), 
    ARRAY_CONSTRUCT('all_employees@company.co.jp', 'yamada.taro@company.co.jp', 'suzuki.ichiro@company.co.jp');

INSERT INTO BOX_INTEGRATION_DB.BOX_LANDING_DATA.BOX_DOCUMENT_METADATA 
(FILE_ID, FILE_NAME, FOLDER_ID, FOLDER_PATH, SHA256_HASH, SIZE_BYTES, BOX_CREATED_AT, BOX_MODIFIED_AT, USER_EMAILS)
SELECT 
    '1000102', 
    '02_クラウド移行プロジェクト_機密設計書.docx', 
    '99002', 
    '/システム統括部/機密プロジェクト', 
    '4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b', 
    892410, 
    CURRENT_TIMESTAMP(), 
    CURRENT_TIMESTAMP(), 
    ARRAY_CONSTRUCT('system_admin@company.co.jp', 'yamada.taro@company.co.jp');

-- Populate chunks table
INSERT INTO BOX_INTEGRATION_DB.CORTEX.BOX_DOC_CHUNKS 
(CHUNK_ID, FILE_ID, FILE_NAME, FOLDER_ID, CHUNK_INDEX, CHUNK_TEXT, USER_EMAILS)
SELECT 
    '1000101_0', 
    '1000101', 
    '01_情報セキュリティ基本規程_2026.pdf', 
    '99001', 
    0, 
    '【第3条 パスワード管理方針】社内情報システムにアクセスする全従業員は、12文字以上の大文字・小文字・数字・記号を組み合わせたパスワードを設定し、90日ごとに更新しなければならない。また、多要素認証（MFA）の導入を必須とする。', 
    ARRAY_CONSTRUCT('all_employees@company.co.jp', 'yamada.taro@company.co.jp', 'suzuki.ichiro@company.co.jp');

INSERT INTO BOX_INTEGRATION_DB.CORTEX.BOX_DOC_CHUNKS 
(CHUNK_ID, FILE_ID, FILE_NAME, FOLDER_ID, CHUNK_INDEX, CHUNK_TEXT, USER_EMAILS)
SELECT 
    '1000102_0', 
    '1000102', 
    '02_クラウド移行プロジェクト_機密設計書.docx', 
    '99002', 
    0, 
    '【極秘：AWS/Snowflakeハイブリッド接続設計】オンプレミスOracleからSnowflakeへのデータ連携には、AWS Direct ConnectおよびPrivateLinkを経由し、パブリックインターネットを経由しないセキュアな閉域網接続を採用する。', 
    ARRAY_CONSTRUCT('system_admin@company.co.jp', 'yamada.taro@company.co.jp');


-- ============================================================================
-- Phase 5: Verification - Cortex Search Query with User ACL Filtering
-- ============================================================================
-- Simulating query by suzuki.ichiro@company.co.jp (Has general access, NO secret access)
-- Note: Replace with SNOWFLAKE.CORTEX.SEARCH_PREVIEW in active session
/*
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'BOX_INTEGRATION_DB.CORTEX.BOX_ENTERPRISE_SEARCH_SERVICE',
    '{
        "query": "パスワードや閉域網の接続方針について教えてください",
        "columns": ["FILE_NAME", "CHUNK_TEXT"],
        "filter": {
            "@contains": {
                "USER_EMAILS": "suzuki.ichiro@company.co.jp"
            }
        },
        "limit": 3
    }'
);
*/

-- Direct SQL Verification showing ACL segregation
SELECT 
    FILE_NAME, 
    CHUNK_TEXT,
    ARRAY_CONTAINS('suzuki.ichiro@company.co.jp'::VARIANT, USER_EMAILS) AS SUZUKI_AUTHORIZED,
    ARRAY_CONTAINS('system_admin@company.co.jp'::VARIANT, USER_EMAILS) AS ADMIN_AUTHORIZED
FROM BOX_INTEGRATION_DB.CORTEX.BOX_DOC_CHUNKS;
