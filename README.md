# Churn Lakehouse Analytics 🚧

> Pipeline completo de dados (engenharia → modelagem dimensional → BI) construído sobre **Databricks Free Edition**, usando o dataset público *Telco Customer Churn* como piloto metodológico para detecção do momento ideal de intervenção no ciclo de vida do cliente.

**Status:** 🚧 Em construção

## Por que esse projeto existe

Esse projeto nasceu como um laboratório controlado para testar, em dado público, a metodologia que pretendo aplicar em dado proprietário (predição de churn em uma operadora de internet, tema da minha dissertação de mestrado). A ideia é chegar com prova de conceito documentada, não só com a proposta teórica.

## Arquitetura

Arquitetura em camadas (medalhão), padrão lakehouse:

```
        ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
 CSV →  │   BRONZE    │ →   │   SILVER    │ →   │    GOLD     │ →   │  POWER BI   │
        │ raw ingest  │     │ clean/typed │     │ star schema │     │  dashboard  │
        └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

| Camada | Responsabilidade |
|---|---|
| Bronze | Ingestão raw, sem transformação, formato Delta |
| Silver | Limpeza, tipagem, deduplicação, regras de negócio |
| Gold | Modelagem dimensional (fato + dimensões), pronta pro BI |

## Dataset

[Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) (IBM Sample Data Set) — ~7.000 clientes de uma operadora de telecom, com dados demográficos, serviços contratados, cobrança e flag de churn.

Dicionário completo em [`docs/data_dictionary.md`](docs/data_dictionary.md).

## Stack

- **Databricks Free Edition** (notebooks, SQL Warehouse, Unity Catalog)
- **PySpark** + **Delta Lake**
- **MLflow** (camada de ML, opcional)
- **Power BI** (consumo via conector nativo do Databricks)
- **pytest** (testes automatizados)

## Roadmap

- [x] Setup do repositório e estrutura inicial
- [x] Setup do workspace Databricks Free Edition
- [x] Bronze: ingestão do CSV bruto
- [x] Silver: limpeza e tipagem
- [ ] Gold: star schema (fato + dimensões)
- [ ] Views otimizadas para Power BI
- [ ] Dashboard Power BI (curva de retenção, churn por tenure/plano/contrato)
- [ ] Camada de ML com MLflow (propensão a churn) — opcional
- [ ] Testes automatizados
- [ ] Traduzir README para inglês (README.md) + manter PT-BR (README.pt-br.md)

## Estrutura do repositório

```
churn-lakehouse-analytics/
├── docs/            → arquitetura, dicionário de dados, metodologia
├── notebooks/       → notebooks do Databricks (exportados como .py)
├── src/             → código Python reutilizável (ingestão, transformação, validação)
├── sql/             → DDL das tabelas Gold + views para Power BI
├── powerbi/         → dashboard (.pbix) + medidas DAX documentadas
└── tests/           → testes automatizados (pytest)
```
