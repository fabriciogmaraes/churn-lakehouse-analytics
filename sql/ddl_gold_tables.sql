-- DDL Gold Layer — Star Schema
-- Projeto: churn-lakehouse-analytics
-- Camada: Gold
-- Descrição: criação das tabelas dimensão e fato do star schema de churn

-- ============================================================
-- DIM_CUSTOMER
-- ============================================================
CREATE TABLE IF NOT EXISTS churn_lakehouse.gold.dim_customer (
    customer_key    BIGINT      NOT NULL,
    customer_id     STRING      NOT NULL,
    gender          STRING,
    senior_citizen  BOOLEAN,
    partner         BOOLEAN,
    dependents      BOOLEAN
)
USING DELTA;

-- ============================================================
-- DIM_CONTRACT
-- ============================================================
CREATE TABLE IF NOT EXISTS churn_lakehouse.gold.dim_contract (
    contract_key        BIGINT  NOT NULL,
    contract_type       STRING,
    paperless_billing   BOOLEAN
)
USING DELTA;

-- ============================================================
-- DIM_PAYMENT
-- ============================================================
CREATE TABLE IF NOT EXISTS churn_lakehouse.gold.dim_payment (
    payment_key     BIGINT  NOT NULL,
    payment_method  STRING
)
USING DELTA;

-- ============================================================
-- DIM_SERVICES
-- ============================================================
CREATE TABLE IF NOT EXISTS churn_lakehouse.gold.dim_services (
    services_key        BIGINT  NOT NULL,
    phone_service       BOOLEAN,
    multiple_lines      STRING,
    internet_service    STRING,
    online_security     STRING,
    online_backup       STRING,
    device_protection   STRING,
    tech_support        STRING,
    streaming_tv        STRING,
    streaming_movies    STRING
)
USING DELTA;

-- ============================================================
-- FACT_CHURN
-- ============================================================
CREATE TABLE IF NOT EXISTS churn_lakehouse.gold.fact_churn (
    customer_key        BIGINT  NOT NULL,
    contract_key        BIGINT  NOT NULL,
    payment_key         BIGINT  NOT NULL,
    services_key        BIGINT  NOT NULL,
    tenure_months       INT,
    monthly_charges     DOUBLE,
    total_charges       DOUBLE,
    churn_flag          BOOLEAN
)
USING DELTA;