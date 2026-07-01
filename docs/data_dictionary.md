# Dicionário de dados — Telco Customer Churn

**Fonte:** IBM Sample Data Set / [Kaggle — Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)  
**Grão:** 1 linha por cliente  
**Volume:** ~7.043 registros, 21 colunas  
**Uso neste projeto:** dataset público utilizado como piloto metodológico — ver `docs/methodology.md`

## Colunas

| Coluna | Tipo (raw) | Descrição | Observação |
|---|---|---|---|
| `customerID` | string | Identificador único do cliente | Chave natural |
| `gender` | string | Gênero (`Male`/`Female`) | |
| `SeniorCitizen` | int | Se o cliente é idoso (`0`/`1`) | Único campo numérico — demais flags vêm como string `Yes`/`No` |
| `Partner` | string | Possui parceiro(a) (`Yes`/`No`) | Converter para boolean na Silver |
| `Dependents` | string | Possui dependentes (`Yes`/`No`) | Converter para boolean na Silver |
| `tenure` | int | Meses como cliente | Métrica central para análise de ciclo de vida |
| `PhoneService` | string | Possui serviço de telefone (`Yes`/`No`) | |
| `MultipleLines` | string | Múltiplas linhas | 3 categorias: `Yes`, `No`, `No phone service` |
| `InternetService` | string | Tipo de internet | `DSL`, `Fiber optic`, `No` |
| `OnlineSecurity` | string | Add-on segurança online | 3 categorias: `Yes`, `No`, `No internet service` |
| `OnlineBackup` | string | Add-on backup online | 3 categorias |
| `DeviceProtection` | string | Add-on proteção de dispositivo | 3 categorias |
| `TechSupport` | string | Add-on suporte técnico | 3 categorias |
| `StreamingTV` | string | Add-on streaming TV | 3 categorias |
| `StreamingMovies` | string | Add-on streaming de filmes | 3 categorias |
| `Contract` | string | Tipo de contrato | `Month-to-month`, `One year`, `Two year` — forte preditor de churn |
| `PaperlessBilling` | string | Fatura sem papel (`Yes`/`No`) | |
| `PaymentMethod` | string | Forma de pagamento | 4 categorias |
| `MonthlyCharges` | double | Cobrança mensal | |
| `TotalCharges` | string ⚠️ | Cobrança total acumulada | **Vem como string com valores em branco** para `tenure=0` — tratar na Silver |
| `Churn` | string | Cliente cancelou (`Yes`/`No`) | Variável target |

## Pontos de atenção conhecidos

### 1. `TotalCharges` com valores em branco
Ocorre em clientes com `tenure = 0` — cliente entrou mas ainda não fechou o primeiro ciclo de cobrança. O campo vem como string no CSV, e os registros com `tenure = 0` têm esse campo em branco (não nulo — em branco), o que impede o cast direto para double.

**Decisão adotada na Silver:** preencher com `0.0`.  
**Alternativa descartada:** descartar esses registros — preferimos manter porque `tenure = 0` é, em si, um sinal relevante de risco de churn.

### 2. Categorias "No x service"
Colunas como `MultipleLines`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV` e `StreamingMovies` possuem uma terceira categoria que significa "não se aplica" — o cliente não tem o serviço base (telefone ou internet) que tornaria o add-on possível.

**Decisão adotada na Silver:** manter as três categorias separadas.  
**Alternativa descartada:** colapsar para `No` — perderia a informação de "não se aplica", que é distinta de "tem o serviço base mas não contratou o add-on".

### 3. `SeniorCitizen` inconsistente em tipo
Vem como inteiro (`0`/`1`) enquanto todas as outras flags booleanas vêm como string (`Yes`/`No`).

**Decisão adotada na Silver:** converter para boolean, alinhando com as demais flags.

## Mapeamento para o star schema (Gold)

| Destino | Colunas de origem |
|---|---|
| `dim_customer` | `customerID`, `gender`, `SeniorCitizen`, `Partner`, `Dependents` |
| `dim_contract` | `Contract`, `PaperlessBilling` |
| `dim_payment` | `PaymentMethod` |
| `dim_services` | `PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies` |
| `fact_churn` | `tenure`, `MonthlyCharges`, `TotalCharges`, `Churn` + chaves das dimensões |