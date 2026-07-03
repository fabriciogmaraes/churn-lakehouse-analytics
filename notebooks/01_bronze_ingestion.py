# Databricks notebook source
# MAGIC %md
# # 01 — Bronze Ingestion
# Lê o CSV bruto do Telco Customer Churn do Volume e grava como Delta Table.
# 
# **Fonte:** `/Volumes/churn_lakehouse/bronze/raw_files/WA_Fn-UseC_-Telco-Customer-Churn.csv`  
# **Destino:** `churn_lakehouse.bronze.telco_raw`  
# **Transformações:** nenhuma — dado entra exatamente como veio da fonte.

# COMMAND ----------

SOURCE_PATH = "/Volumes/churn_lakehouse/bronze/raw_files/WA_Fn-UseC_-Telco-Customer-Churn.csv"
TARGET_TABLE = "churn_lakehouse.bronze.telco_raw"

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

schema = StructType([
    StructField("customerID",       StringType(),  nullable=False),
    StructField("gender",           StringType(),  nullable=True),
    StructField("SeniorCitizen",    IntegerType(), nullable=True),
    StructField("Partner",          StringType(),  nullable=True),
    StructField("Dependents",       StringType(),  nullable=True),
    StructField("tenure",           IntegerType(), nullable=True),
    StructField("PhoneService",     StringType(),  nullable=True),
    StructField("MultipleLines",    StringType(),  nullable=True),
    StructField("InternetService",  StringType(),  nullable=True),
    StructField("OnlineSecurity",   StringType(),  nullable=True),
    StructField("OnlineBackup",     StringType(),  nullable=True),
    StructField("DeviceProtection", StringType(),  nullable=True),
    StructField("TechSupport",      StringType(),  nullable=True),
    StructField("StreamingTV",      StringType(),  nullable=True),
    StructField("StreamingMovies",  StringType(),  nullable=True),
    StructField("Contract",         StringType(),  nullable=True),
    StructField("PaperlessBilling", StringType(),  nullable=True),
    StructField("PaymentMethod",    StringType(),  nullable=True),
    StructField("MonthlyCharges",   DoubleType(),  nullable=True),
    StructField("TotalCharges",     StringType(),  nullable=True),
    StructField("Churn",            StringType(),  nullable=True),
])

# COMMAND ----------

df_raw = (
    spark.read
    .option("header", True)
    .schema(schema)
    .csv(SOURCE_PATH)
)

print(f"Linhas lidas: {df_raw.count()}")
display(df_raw.limit(10))

# COMMAND ----------

from pyspark.sql import functions as F
from datetime import datetime, timezone

df_bronze = (
    df_raw
    .withColumn("_ingested_at", F.lit(datetime.now(timezone.utc)).cast("timestamp"))
    .withColumn("_source_file", F.lit(SOURCE_PATH))
)

display(df_bronze.limit(5))

# COMMAND ----------

(
    df_bronze.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(TARGET_TABLE)
)

print(f"Tabela '{TARGET_TABLE}' gravada com sucesso.")