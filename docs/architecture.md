# Arquitetura

## Visão geral

Pipeline de dados em arquitetura medalhão (bronze/silver/gold), padrão lakehouse, executado inteiramente no **Databricks Free Edition** (serverless — sem gerenciar cluster).

A fonte de dados é o dataset público *Telco Customer Churn* (IBM), ingerido como CSV e transformado camada a camada até chegar num star schema consumido pelo Power BI via conector nativo do Databricks SQL Warehouse.

## Diagrama

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Telco CSV   │ →   │    BRONZE    │ →   │    SILVER    │ →   │     GOLD     │ →   │   Power BI   │
│  (fonte pub) │     │  Delta raw   │     │ Delta limpo  │     │ star schema  │     │  dashboard   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                       │
                                                                       ▼
                                                               ┌──────────────┐
                                                               │    MLflow    │
                                                               │ propensão a  │
                                                               │    churn     │
                                                               └──────────────┘
                                                               (opcional)
```


## Camadas

### Bronze — Ingestão raw

- Lê o CSV original com schema explícito (sem `inferSchema=True`)
- Não aplica nenhuma transformação de negócio — o dado entra exatamente como veio da fonte
- Adiciona duas colunas técnicas de rastreabilidade:
  - `_ingested_at`: timestamp do momento da ingestão
  - `_source_file`: caminho do arquivo de origem
- Gravado como Delta Table no Unity Catalog (`churn_lakehouse.bronze.telco_raw`)
- Modo de escrita: `append` — simula ingestão incremental mesmo com fonte estática

**Por que schema explícito?** Se o CSV mudar silenciosamente (ex.: coluna nova, tipo diferente), o pipeline quebra com erro claro em vez de propagar dado errado pras camadas seguintes sem aviso.

### Silver — Limpeza e padronização

- Lê a Bronze (`churn_lakehouse.bronze.telco_raw`)
- Aplica as seguintes transformações, nesta ordem:

  1. **Correção de `TotalCharges`**: vem como string e tem valores em branco para clientes com `tenure = 0` (cliente novo, ainda sem fechar o primeiro ciclo de cobrança). Decisão: preencher com `0.0` — esses clientes são mantidos na base porque `tenure = 0` é, em si, um sinal relevante de risco de churn.

  2. **Padronização de `SeniorCitizen`**: vem como inteiro (`0`/`1`) enquanto as demais flags vêm como string (`Yes`/`No`). Convertido para boolean para consistência.

  3. **Conversão Yes/No → boolean**: colunas `Partner`, `Dependents`, `PhoneService`, `PaperlessBilling` e `Churn`.

  4. **Deduplicação por `customerID`**: mantém o registro mais recente por `_ingested_at` em caso de duplicata.

- Gravado como Delta Table (`churn_lakehouse.silver.telco_clean`)
- Modo de escrita: `overwrite` — a Silver sempre reflete o estado mais atual da Bronze processada

**Nota sobre colunas de serviço**: colunas como `MultipleLines`, `OnlineSecurity`, etc. possuem uma terceira categoria (`No phone service` / `No internet service`) que significa "não se aplica". Essas categorias são mantidas como estão — colapsá-las para `No` perderia informação relevante para a modelagem.

### Gold — Modelagem dimensional (Star Schema)

- Lê a Silver (`churn_lakehouse.silver.telco_clean`)
- Modela em star schema: uma tabela fato central rodeada de dimensões
- Grão da fato: **1 linha por cliente**

**Dimensões:**

| Tabela | Colunas principais |
|---|---|
| `dim_customer` | `customer_key`, `customerID`, `gender`, `senior_citizen`, `partner`, `dependents` |
| `dim_contract` | `contract_key`, `contract_type`, `paperless_billing` |
| `dim_payment` | `payment_key`, `payment_method` |
| `dim_services` | `services_key`, `phone_service`, `multiple_lines`, `internet_service`, `online_security`, `online_backup`, `device_protection`, `tech_support`, `streaming_tv`, `streaming_movies` |

**Fato:**

| Tabela | Colunas principais |
|---|---|
| `fact_churn` | `customer_key`, `contract_key`, `payment_key`, `services_key`, `tenure_months`, `monthly_charges`, `total_charges`, `churn_flag` |

- Surrogate keys geradas via `monotonically_increasing_id()` do PySpark
- DDL completo em `sql/ddl_gold_tables.sql`
- Gravado como Delta Table (`churn_lakehouse.gold.*`)

### ML — Propensão a churn (opcional)

- Construída sobre a Gold (`fact_churn` + dimensões)
- Feature engineering: ex. quantidade de serviços contratados, razão `total_charges`/`tenure_months`
- Modelo baseline (ex.: regressão logística) treinado e rastreado via **MLflow**
- Output: tabela `churn_lakehouse.gold.churn_propensity_scores` com score de propensão por cliente
- Conecta diretamente com a hipótese da tese: identificar faixas de `tenure` com maior risco de churn como "janela de intervenção"

### Consumo — Power BI

- Conexão direta ao **Databricks SQL Warehouse** via Partner Connect (sem exportar arquivo intermediário)
- Views específicas para BI em `sql/views_powerbi.sql` — lógica de negócio centralizada no SQL, não no DAX
- Dashboard principal: curva de retenção, churn por tenure, por tipo de contrato, por serviços contratados

## Decisões de design

| Decisão | Alternativa descartada | Motivo da escolha |
|---|---|---|
| Schema explícito na Bronze | `inferSchema=True` | Mudança silenciosa no CSV quebra com erro claro, não propaga dado errado |
| Manter `tenure=0` na Silver | Descartar registros | `tenure=0` é sinal de risco em si — removê-lo enviesaria o modelo |
| Manter categorias "No x service" | Colapsar para `No` | Perda de informação relevante para modelagem de serviços |
| Overwrite na Silver | Append | Silver sempre reflete o estado atual da Bronze — append acumularia versões inconsistentes |
| Views dedicadas para Power BI | Lógica no DAX | Centraliza regra de negócio no SQL, facilita manutenção e reutilização |
| Surrogate keys na Gold | Usar `customerID` como chave | Padrão dimensional correto — desacopla chave de negócio da chave técnica |
| Delta Lake em todas as camadas | Parquet puro | Versionamento (time travel), ACID, schema enforcement nativos |