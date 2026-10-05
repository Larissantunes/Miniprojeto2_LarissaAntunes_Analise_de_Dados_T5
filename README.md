# Pipeline de Dados — Viagens a Serviço do Governo Federal

## Descrição do problema

Este projeto constrói um pipeline de dados (ETL) para transformar os
dados brutos de Viagens a Serviço, publicados pelo Portal da Transparência do Governo Federal, em informação para tomada de decisão. O pipeline segue a Arquitetura Medallion, em três camadas, conforme orientações repassadas para seguir o trabalho:

- **Raw**: cópia fiel dos dados originais, sem nenhuma alteração.
- **Silver**: dados limpos, com tipos corretos (datas, valores monetários) e
  integridade referencial entre as tabelas.
- **Gold**: métricas agregadas de negócio, respondendo a perguntas específicas sobre
  custos, destinos e padrões de viagem.

## O que foi utilizado:

- **Python** — extração e transformação dos dados
- **PostgreSQL** (via pgAdmin4) — armazenamento e modelagem do banco
- **psycopg** — conexão entre Python e PostgreSQL
- **gdown** — download automatizado do arquivo de dados hospedado no Google Drive
- **pandas** — leitura de dados e manipulação em tabelas
- **matplotlib** — geração dos gráficos
- **Jupyter Notebook** — camada Gold: consultas, tabelas e visualizações

## Arquitetura do pipeline (isso aqui eu pedi para o claude desenhar para mim)

Google Drive (.zip)
│
▼
1_extrair.py ──────────▶ Camada RAW (4 tabelas, dados crus em TEXT)
│
▼
2_transformar.py ──────▶ Camada SILVER (4 tabelas, tipos corretos, PK/FK, constraints)
│
▼
3_analise.ipynb ───────▶ Camada GOLD (tabelas + views agregadas, perguntas de negócio)


## Como executar

### Pré-requisitos
- Python 3.x instalado
- PostgreSQL instalado e rodando
- pgAdmin 

### Passo a passo

1. Clonei o repositório
2. Copiei '.env.example' para .env e preenchi com as credenciais do PostgreSQL
4. Criei o banco de dados no PostgreSQL (projeto_viagens)
5. Execute o script de criação das tabelas:
   - Abri `0_criar_banco.sql` no pgAdmin (Query Tool) 
6. Executei a extração da camada Raw:
```bash
   python 1_extrair.py
```
7. Executei a transformação para a camada Silver:
```bash
   python 2_transformar.py
```
8. Abri e executei `3_analise.ipynb` no VS Code para ver as perguntas de negócio respondidas com tabelas e gráficos.

## Conclusões e insights

1. **Concentração de custos**: o Fundo Nacional de Segurança Pública é o órgão com
   maior custo total em viagens (R$ 278,5 milhões), seguido por um órgão identificado
   apenas como "Sigiloso".

2. **Diárias dominam o custo médio**: entre os tipos de pagamento, "DIÁRIAS" tem o
   maior valor médio (R$ 2.078,28), à frente de passagens, sugerindo que viagens mais
   longas (mais dias) pesam proporcionalmente mais no orçamento do que o deslocamento
   em si.

3. **Transporte oficial predomina**: "Veículo Oficial" é o meio de transporte mais
   usado nos trechos (386 mil ocorrências), à frente de deslocamentos aéreos.

4. **Destinos mais longes custam mais por viagem**: os três destinos com maior custo médio
   por viagem são estados do Norte (Roraima, Rondônia, Acre), reflexo direto da
   distância.

5. **São Paulo e Brasília concentram o fluxo**: São Paulo e o Distrito Federal são os
   destinos mais frequentes nos trechos registrados.

## Problemas 

- Existe uma categoria de meio de transporte chamada "Inválido" (26.659 ocorrências), que provavelmente indica falha de preenchimento na fonte original.
- O órgão "Sigiloso" aparece como segunda maior fonte de custo.
- Os valores de "custo total" e "custo médio" assumem que `valor_total` é calculado
  como `diárias + passagens + outros gastos − devolução`; essa fórmula é uma
  interpretação dos dados disponíveis, mas pode divergir de uma definição
  oficial.

## Observações
- Tive diversos problemas durante a execução, desde o início, com a leitura de arquivos e carregamento, então pedi diversas vezes ajuda para o claude me orientar em como prosseguir. Tive muita dificuldade também de seguir o fluxo do processo, recorrendo diversas vezes ao claude para me orientar em como prosseguir. A parte que menos tive dificuldade foi depois de pronto para aplicar as análises pedidas. Ainda assim, não me lembrava exatamente de todos os comandos e códigos, e também pedi ao claude ajuda para correção dos códigos. 

## Autor
Larissa Antunes — Análise de Dados com Python [T5]