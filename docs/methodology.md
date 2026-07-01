# Metodologia e racional do projeto

## Contexto

Este projeto faz parte da preparação para a dissertação de mestrado (PPgTI/UFRN, Inteligência Computacional), cujo foco é a **predição de churn numa operadora de internet**, com ênfase em identificar o **momento ideal de intervenção** no ciclo de vida do cliente — ou seja, não apenas prever *se* o cliente vai cancelar, mas *quando* uma ação de retenção (oferta, contato, upgrade) tem maior probabilidade de funcionar.

O acesso a dado proprietário envolve aprovação formal e questões de governança. Este projeto constrói a metodologia completa primeiro em dado público (Telco Customer Churn) para:

1. Validar a arquitetura de dados antes do dado real chegar
2. Testar a abordagem analítica num problema estruturalmente parecido (telecom/ISP)
3. Chegar à conversa com o orientador com prova de conceito, não só com proposta teórica

## Hipótese de trabalho

> Clientes em determinadas faixas de `tenure` (tempo como cliente), combinadas com tipo de contrato e quantidade de serviços contratados, apresentam probabilidade de churn significativamente maior — e essas faixas podem ser usadas como gatilho para ação de retenção antes do cancelamento.

No dataset Telco, isso se traduz em analisar a interação entre `tenure`, `Contract` e `Churn`. A mesma lógica de feature engineering será extrapolada para o dado real da `empresa real` quando o acesso for aprovado.

**Por que `tenure` é central?** Um cliente que cancela no mês 2 tem um perfil de risco completamente diferente de um que cancela no mês 24. Tratar os dois da mesma forma numa campanha de retenção é ineficiente — e caro. A janela de intervenção correta depende de saber em qual fase do ciclo de vida o cliente está.

## O que muda na migração para o dado real

| Aspecto | Piloto (Telco público) | Produção (dado real) |
|---|---|---|
| Granularidade temporal | Snapshot único (1 linha por cliente) | Série temporal (eventos por cliente ao longo do tempo) |
| Definição de churn | Binária e já rotulada | Precisa ser definida operacionalmente (ex.: cancelamento formal vs. inadimplência) |
| Volume | ~7k registros | Escala real da base de clientes |
| Infraestrutura | Databricks Free Edition | Ambiente corporativo (a definir) |
| Governança | Nenhuma (dado aberto) | LGPD, anonimização, aprovação formal |

A arquitetura de pipeline (bronze/silver/gold) e a lógica de modelagem dimensional são diretamente reaproveitáveis — esse é o principal ganho do piloto.

## Conexão com o roadmap do projeto

| Etapa do projeto | Relevância metodológica |
|---|---|
| Bronze → Silver | Garante qualidade e rastreabilidade do dado antes de qualquer análise |
| Gold (star schema) | Estrutura o dado no grão correto para análise de ciclo de vida por cliente |
| Power BI (dashboard) | Valida visualmente as hipóteses antes de partir para modelagem estatística |
| MLflow (opcional) | Formaliza o modelo de propensão a churn e rastreia experimentos — base para a tese |

A sequência deliberada (engenharia → modelagem → visualização → ML) reflete o processo científico: entender o dado antes de modelar, e modelar antes de concluir.