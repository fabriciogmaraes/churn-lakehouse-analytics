# Databricks notebook source
# MAGIC %md
# # 02 — Silver Transformation
# Lê a tabela Bronze e aplica limpeza, tipagem e deduplicação.
#
# **Fonte:** `churn_lakehouse.bronze.telco_raw`  
# **Destino:** `churn_lakehouse.silver.telco_clean`  
# **Transformações:** correção TotalCharges, padronização SeniorCitizen, conversão Yes/No → boolean, deduplicação por customerID.

# COMMAND ----------

SOURCE_TABLE = "churn_lakehouse.bronze.telco_raw"
TARGET_TABLE = "churn_lakehouse.silver.telco_clean"

# COMMAND ----------

df_bronze = spark.read.table(SOURCE_TABLE)

print(f"Linhas lidas da Bronze: {df_bronze.count()}")
display(df_bronze.limit(5))

# COMMAND ----------

from pyspark.sql import functions as F

df_step1 = df_bronze.withColumn(
    "TotalCharges",
    F.when(F.trim(F.col("TotalCharges")) == "", F.lit(0.0))
     .otherwise(F.col("TotalCharges").cast("double"))
)

# Verifica se ainda tem valores nulos em TotalCharges
nulls = df_step1.filter(F.col("TotalCharges").isNull()).count()
print(f"Nulos em TotalCharges após correção: {nulls}")

# COMMAND ----------

df_step2 = df_step1.withColumn(
    "SeniorCitizen",
    F.col("SeniorCitizen") == 1
)

display(df_step2.select("SeniorCitizen").distinct())

# COMMAND ----------

yes_no_columns = ["Partner", "Dependents", "PhoneService", "PaperlessBilling", "Churn"]

df_step3 = df_step2
for col in yes_no_columns:
    df_step3 = df_step3.withColumn(
        col,
        F.when(F.col(col) == "Yes", True)
         .when(F.col(col) == "No", False)
         .otherwise(None)
    )

display(df_step3.select("Partner", "Dependents", "PhoneService", "PaperlessBilling", "Churn").limit(5))

# COMMAND ----------

from pyspark.sql import Window

window = Window.partitionBy("customerID").orderBy(F.col("_ingested_at").desc())

df_step4 = (
    df_step3
    .withColumn("_row_num", F.row_number().over(window))
    .filter(F.col("_row_num") == 1)
    .drop("_row_num")
)

print(f"Linhas antes da deduplicação: {df_step3.count()}")
print(f"Linhas após deduplicação:     {df_step4.count()}")

# COMMAND ----------

print("=== Checkpoint de qualidade ===")
print(f"Total de linhas: {df_step4.count()}")
print(f"customerID únicos: {df_step4.select('customerID').distinct().count()}")

critical_columns = ["customerID", "tenure", "MonthlyCharges", "TotalCharges", "Churn"]
print("\nNulos por coluna crítica:")
for col in critical_columns:
    nulls = df_step4.filter(F.col(col).isNull()).count()
    print(f"  {col}: {nulls}")

# COMMAND ----------

(
    df_step4.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(TARGET_TABLE)
)

print(f"Tabela '{TARGET_TABLE}' gravada com sucesso.")