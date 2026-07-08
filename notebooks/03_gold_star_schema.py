# Databricks notebook source
# MAGIC %md
# MAGIC # MAGIC %md
# MAGIC # # 03 — Gold Star Schema
# MAGIC # Povoa as tabelas dimensão e fato a partir da Silver.
# MAGIC #
# MAGIC # **Fonte:** `churn_lakehouse.silver.telco_clean`  
# MAGIC # **Destino:** `churn_lakehouse.gold.*`  
# MAGIC # **Tabelas:** dim_customer, dim_contract, dim_payment, dim_services, fact_churn

# COMMAND ----------

SOURCE_TABLE = "churn_lakehouse.silver.telco_clean"

DIM_CUSTOMER = "churn_lakehouse.gold.dim_customer"
DIM_CONTRACT = "churn_lakehouse.gold.dim_contract"
DIM_PAYMENT  = "churn_lakehouse.gold.dim_payment"
DIM_SERVICES = "churn_lakehouse.gold.dim_services"
FACT_CHURN   = "churn_lakehouse.gold.fact_churn"

# COMMAND ----------

from pyspark.sql import functions as F

df_silver = spark.read.table(SOURCE_TABLE)
print(f"Linhas lidas da Silver: {df_silver.count()}")

# COMMAND ----------

dim_payment = (
    df_silver
    .select("PaymentMethod")
    .distinct()
    .withColumnRenamed("PaymentMethod", "payment_method")
    .withColumn("payment_key", F.monotonically_increasing_id() + 1)
    .select("payment_key", "payment_method")
)

(
    dim_payment.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(DIM_PAYMENT)
)

print(f"dim_payment gravada: {dim_payment.count()} linhas")
display(dim_payment)

# COMMAND ----------

dim_contract = (
    df_silver
    .select("Contract", "PaperlessBilling")
    .distinct()
    .withColumnRenamed("Contract", "contract_type")
    .withColumnRenamed("PaperlessBilling", "paperless_billing")
    .withColumn("contract_key", F.monotonically_increasing_id() + 1)
    .select("contract_key", "contract_type", "paperless_billing")
)

(
    dim_contract.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(DIM_CONTRACT)
)

print(f"dim_contract gravada: {dim_contract.count()} linhas")
display(dim_contract)

# COMMAND ----------

dim_services = (
    df_silver
    .select(
        "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies"
    )
    .distinct()
    .withColumnRenamed("PhoneService",     "phone_service")
    .withColumnRenamed("MultipleLines",    "multiple_lines")
    .withColumnRenamed("InternetService",  "internet_service")
    .withColumnRenamed("OnlineSecurity",   "online_security")
    .withColumnRenamed("OnlineBackup",     "online_backup")
    .withColumnRenamed("DeviceProtection", "device_protection")
    .withColumnRenamed("TechSupport",      "tech_support")
    .withColumnRenamed("StreamingTV",      "streaming_tv")
    .withColumnRenamed("StreamingMovies",  "streaming_movies")
    .withColumn("services_key", F.monotonically_increasing_id() + 1)
    .select(
        "services_key", "phone_service", "multiple_lines", "internet_service",
        "online_security", "online_backup", "device_protection",
        "tech_support", "streaming_tv", "streaming_movies"
    )
)

(
    dim_services.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(DIM_SERVICES)
)

print(f"dim_services gravada: {dim_services.count()} linhas")

# COMMAND ----------

dim_customer = (
    df_silver
    .select("customerID", "gender", "SeniorCitizen", "Partner", "Dependents")
    .distinct()
    .withColumnRenamed("customerID",    "customer_id")
    .withColumnRenamed("SeniorCitizen", "senior_citizen")
    .withColumnRenamed("Partner",       "partner")
    .withColumnRenamed("Dependents",    "dependents")
    .withColumn("customer_key", F.monotonically_increasing_id() + 1)
    .select("customer_key", "customer_id", "gender", "senior_citizen", "partner", "dependents")
)

(
    dim_customer.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(DIM_CUSTOMER)
)

print(f"dim_customer gravada: {dim_customer.count()} linhas")
display(dim_customer.limit(5))

# COMMAND ----------

fact_churn = (
    df_silver
    .join(
        dim_customer.select("customer_key", "customer_id"),
        df_silver["customerID"] == dim_customer["customer_id"],
        "left"
    )
    .join(
        dim_contract.select("contract_key", "contract_type", "paperless_billing"),
        (df_silver["Contract"] == dim_contract["contract_type"]) &
        (df_silver["PaperlessBilling"] == dim_contract["paperless_billing"]),
        "left"
    )
    .join(
        dim_payment.select("payment_key", "payment_method"),
        df_silver["PaymentMethod"] == dim_payment["payment_method"],
        "left"
    )
    .join(
        dim_services.select(
            "services_key", "phone_service", "multiple_lines", "internet_service",
            "online_security", "online_backup", "device_protection",
            "tech_support", "streaming_tv", "streaming_movies"
        ),
        (df_silver["PhoneService"]     == dim_services["phone_service"]) &
        (df_silver["MultipleLines"]    == dim_services["multiple_lines"]) &
        (df_silver["InternetService"]  == dim_services["internet_service"]) &
        (df_silver["OnlineSecurity"]   == dim_services["online_security"]) &
        (df_silver["OnlineBackup"]     == dim_services["online_backup"]) &
        (df_silver["DeviceProtection"] == dim_services["device_protection"]) &
        (df_silver["TechSupport"]      == dim_services["tech_support"]) &
        (df_silver["StreamingTV"]      == dim_services["streaming_tv"]) &
        (df_silver["StreamingMovies"]  == dim_services["streaming_movies"]),
        "left"
    )
    .select(
        "customer_key",
        "contract_key",
        "payment_key",
        "services_key",
        df_silver["tenure"].alias("tenure_months"),
        df_silver["MonthlyCharges"].alias("monthly_charges"),
        df_silver["TotalCharges"].alias("total_charges"),
        df_silver["Churn"].alias("churn_flag")
    )
)

(
    fact_churn.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(FACT_CHURN)
)

print(f"fact_churn gravada: {fact_churn.count()} linhas")
display(fact_churn.limit(5))

# COMMAND ----------

print("=== Checkpoint Gold ===")
print(f"dim_customer : {spark.read.table(DIM_CUSTOMER).count()} linhas")
print(f"dim_contract : {spark.read.table(DIM_CONTRACT).count()} linhas")
print(f"dim_payment  : {spark.read.table(DIM_PAYMENT).count()} linhas")
print(f"dim_services : {spark.read.table(DIM_SERVICES).count()} linhas")
print(f"fact_churn   : {spark.read.table(FACT_CHURN).count()} linhas")

nulls_fato = spark.read.table(FACT_CHURN).filter(
    F.col("customer_key").isNull() |
    F.col("contract_key").isNull() |
    F.col("payment_key").isNull() |
    F.col("services_key").isNull()
).count()
print(f"\nLinhas com chave nula na fato: {nulls_fato}")