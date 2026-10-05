"""
1_extrair.py
------------
Fase 1 do pipeline: baixa o .zip do Google Drive, extrai os 4 CSVs
e carrega o conteúdo (sem alterações) nas tabelas RAW do PostgreSQL.

Processo idempotente (TRUNCATE antes de carregar) e resiliente (try/except).
"""

import os
import zipfile
import csv

import gdown

from config import (
    PASTA_DADOS,
    DRIVE_FILE_ID,
    ARQUIVOS,
    CSV_SEPARADOR,
    CSV_ENCODING,
    TAMANHO_BLOCO,
)
from banco import conectar, executar, inserir_em_lote


def baixar_zip():
    """Baixa o .zip do Google Drive para a pasta de dados, se ainda não existir."""
    PASTA_DADOS.mkdir(exist_ok=True)  # cria a pasta 'data' se não existir
    caminho_zip = PASTA_DADOS / "dados.zip"

    url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
    print(f"Baixando arquivo do Google Drive...")
    gdown.download(url, str(caminho_zip), quiet=False)

    return caminho_zip


def extrair_zip(caminho_zip):
    """Extrai o conteúdo do .zip dentro da pasta de dados."""
    print("Extraindo arquivos do .zip...")
    with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
        zip_ref.extractall(PASTA_DADOS)
    print("Extração concluída.")


def carregar_csv_em_blocos(conexao, nome_csv, nome_tabela):
    """
    Lê um CSV em blocos (chunks) e insere cada bloco na tabela RAW
    correspondente, sem alterar o conteúdo original.
    """
    caminho_csv = PASTA_DADOS / nome_csv

    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    # Idempotência: limpa a tabela antes de carregar de novo
    print(f"Limpando tabela {nome_tabela} (TRUNCATE)...")
    executar(conexao, f"TRUNCATE TABLE {nome_tabela};")

    with open(caminho_csv, encoding=CSV_ENCODING, newline="") as f:
        leitor = csv.reader(f, delimiter=CSV_SEPARADOR)
        cabecalho = next(leitor)  # pula a primeira linha (nomes das colunas)

        num_colunas = len(cabecalho)
        placeholders = ", ".join(["%s"] * num_colunas)
        sql_insert = f"INSERT INTO {nome_tabela} VALUES ({placeholders})"

        bloco = []
        total_inserido = 0

        for linha in leitor:
            bloco.append(tuple(linha))

            if len(bloco) >= TAMANHO_BLOCO:
                inserir_em_lote(conexao, sql_insert, bloco)
                total_inserido += len(bloco)
                print(f"  {nome_tabela}: {total_inserido} linhas inseridas...")
                bloco = []

        # insere o que sobrou (último bloco, menor que TAMANHO_BLOCO)
        if bloco:
            inserir_em_lote(conexao, sql_insert, bloco)
            total_inserido += len(bloco)

    print(f"Concluído: {nome_tabela} -> {total_inserido} linhas inseridas.\n")


def main():
    conexao = None
    try:
        caminho_zip = baixar_zip()
        extrair_zip(caminho_zip)

        conexao = conectar()
        print("Conexão com o PostgreSQL estabelecida.\n")

        for chave, info in ARQUIVOS.items():
            try:
                carregar_csv_em_blocos(conexao, info["csv"], info["tabela_raw"])
            except Exception as erro:
                print(f"ERRO ao carregar {info['csv']}: {erro}")
                # continua tentando os outros arquivos, mesmo se um falhar

        print("Extração e carga na camada RAW finalizadas.")

    except Exception as erro:
        import traceback
        print("ERRO geral no processo de extração:")
        traceback.print_exc()

    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco encerrada.")


if __name__ == "__main__":
    main()