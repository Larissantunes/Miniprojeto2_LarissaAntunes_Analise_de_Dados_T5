"""
2_transformar.py
-----------------
**Fase 2 do pipeline: copia os dados da camada RAW para a camada SILVER,
**convertendo tipos (texto -> DATE e DECIMAL) e calculando as colunas
**valor_total e duracao_dias. Processo feito em SQL (INSERT INTO ... SELECT),
**já que Raw e Silver estão no mesmo banco.

**Idempotente: faz TRUNCATE nas tabelas Silver antes de popular de novo.
**Resiliente: cada etapa roda dentro de um try/except.
"""
from banco import conectar, executar

def limpar_tabelas_silver(conexao):
    """Esvazia as 4 tabelas Silver de uma vez (ordem não importa no TRUNCATE em lote)."""
    print("Limpando tabelas Silver (TRUNCATE)...")
    executar(conexao, """
        TRUNCATE TABLE silver_pagamento, silver_passagem, silver_trecho, silver_viagem
        RESTART IDENTITY;
    """)


def transformar_viagem(conexao):
    """Copia raw_viagem -> silver_viagem, convertendo tipos e calculando colunas."""
    print("Transformando silver_viagem...")
    executar(conexao, """
        INSERT INTO silver_viagem (
            id_viagem, num_proposta, situacao, viagem_urgente,
            cod_orgao_superior, nome_orgao_superior, nome_viajante, cargo,
            data_inicio, data_fim, destinos, motivo,
            valor_diarias, valor_passagens, valor_devolucao, valor_outros_gastos,
            valor_total, duracao_dias
        )
        SELECT DISTINCT ON (id_viagem)
            id_viagem,
            num_proposta,
            situacao,
            viagem_urgente,
            cod_orgao_superior,
            nome_orgao_superior,
            nome_viajante,
            cargo,
            TO_DATE(NULLIF(TRIM(data_inicio), ''), 'DD/MM/YYYY'),
            TO_DATE(NULLIF(TRIM(data_fim), ''), 'DD/MM/YYYY'),
            destinos,
            motivo,
            NULLIF(REPLACE(REPLACE(TRIM(valor_diarias), '.', ''), ',', '.'), '')::numeric(10,2),
            NULLIF(REPLACE(REPLACE(TRIM(valor_passagens), '.', ''), ',', '.'), '')::numeric(10,2),
            NULLIF(REPLACE(REPLACE(TRIM(valor_devolucao), '.', ''), ',', '.'), '')::numeric(10,2),
            NULLIF(REPLACE(REPLACE(TRIM(valor_outros_gastos), '.', ''), ',', '.'), '')::numeric(10,2),
            COALESCE(NULLIF(REPLACE(REPLACE(TRIM(valor_diarias), '.', ''), ',', '.'), '')::numeric(10,2), 0)
                + COALESCE(NULLIF(REPLACE(REPLACE(TRIM(valor_passagens), '.', ''), ',', '.'), '')::numeric(10,2), 0)
                + COALESCE(NULLIF(REPLACE(REPLACE(TRIM(valor_outros_gastos), '.', ''), ',', '.'), '')::numeric(10,2), 0)
                - COALESCE(NULLIF(REPLACE(REPLACE(TRIM(valor_devolucao), '.', ''), ',', '.'), '')::numeric(10,2), 0),
            (TO_DATE(NULLIF(TRIM(data_fim), ''), 'DD/MM/YYYY')
                - TO_DATE(NULLIF(TRIM(data_inicio), ''), 'DD/MM/YYYY'))
        FROM raw_viagem
        WHERE id_viagem IS NOT NULL AND TRIM(id_viagem) <> ''
        ORDER BY id_viagem;
    """)


def transformar_pagamento(conexao):
    """Copia raw_pagamento -> silver_pagamento (só linhas com id_viagem válido)."""
    print("Transformando silver_pagamento...")
    executar(conexao, """
        INSERT INTO silver_pagamento (
            id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora,
            tipo_pagamento, valor
        )
        SELECT
            r.id_viagem,
            r.num_proposta,
            r.nome_orgao_pagador,
            r.nome_ug_pagadora,
            r.tipo_pagamento,
            NULLIF(REPLACE(REPLACE(TRIM(r.valor), '.', ''), ',', '.'), '')::numeric(10,2)
        FROM raw_pagamento r
        WHERE EXISTS (SELECT 1 FROM silver_viagem v WHERE v.id_viagem = r.id_viagem)
          AND r.tipo_pagamento IS NOT NULL AND TRIM(r.tipo_pagamento) <> '';
    """)


def transformar_passagem(conexao):
    """Copia raw_passagem -> silver_passagem (só linhas com id_viagem válido)."""
    print("Transformando silver_passagem...")
    executar(conexao, """
        INSERT INTO silver_passagem (
            id_viagem, meio_transporte, pais_origem_ida, uf_origem_ida,
            cidade_origem_ida, pais_destino_ida, uf_destino_ida, cidade_destino_ida,
            valor_passagem, taxa_servico, data_emissao
        )
        SELECT
            r.id_viagem,
            r.meio_transporte,
            r.pais_origem_ida,
            r.uf_origem_ida,
            r.cidade_origem_ida,
            r.pais_destino_ida,
            r.uf_destino_ida,
            r.cidade_destino_ida,
            NULLIF(REPLACE(REPLACE(TRIM(r.valor_passagem), '.', ''), ',', '.'), '')::numeric(10,2),
            NULLIF(REPLACE(REPLACE(TRIM(r.taxa_servico), '.', ''), ',', '.'), '')::numeric(10,2),
            TO_DATE(NULLIF(TRIM(r.data_emissao), ''), 'DD/MM/YYYY')
        FROM raw_passagem r
        WHERE EXISTS (SELECT 1 FROM silver_viagem v WHERE v.id_viagem = r.id_viagem);
    """)


def transformar_trecho(conexao):
    """Copia raw_trecho -> silver_trecho (só linhas com id_viagem válido e sequencia numerica)."""
    print("Transformando silver_trecho...")
    executar(conexao, """
        INSERT INTO silver_trecho (
            id_viagem, sequencia_trecho, origem_data, origem_uf, origem_cidade,
            destino_data, destino_uf, destino_cidade, meio_transporte, numero_diarias
        )
        SELECT DISTINCT ON (r.id_viagem, NULLIF(TRIM(r.sequencia_trecho), '')::int)
            r.id_viagem,
            NULLIF(TRIM(r.sequencia_trecho), '')::int,
            TO_DATE(NULLIF(TRIM(r.origem_data), ''), 'DD/MM/YYYY'),
            r.origem_uf,
            r.origem_cidade,
            TO_DATE(NULLIF(TRIM(r.destino_data), ''), 'DD/MM/YYYY'),
            r.destino_uf,
            r.destino_cidade,
            r.meio_transporte,
            NULLIF(REPLACE(REPLACE(TRIM(r.numero_diarias), '.', ''), ',', '.'), '')::numeric(10,2)
        FROM raw_trecho r
        WHERE EXISTS (SELECT 1 FROM silver_viagem v WHERE v.id_viagem = r.id_viagem)
          AND NULLIF(TRIM(r.sequencia_trecho), '') IS NOT NULL;
    """)


def main():
    conexao = None
    try:
        conexao = conectar()
        print("Conexão com o PostgreSQL estabelecida.\n")

        limpar_tabelas_silver(conexao)

        # Ordem importa: silver_viagem primeiro (as outras 3 referenciam ela via FK)
        transformar_viagem(conexao)
        transformar_pagamento(conexao)
        transformar_passagem(conexao)
        transformar_trecho(conexao)

        print("\nTransformação Raw -> Silver finalizada com sucesso.")

    except Exception as erro:
        import traceback
        print("ERRO no processo de transformação:")
        traceback.print_exc()

    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco encerrada.")


if __name__ == "__main__":
    main()