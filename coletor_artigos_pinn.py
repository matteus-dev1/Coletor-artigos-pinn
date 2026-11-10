"""
Coleta de metadados de artigos científicos por meio da API do arXiv.

Consulta artigos sobre "physics-informed neural network", extrai título,
autores, data de publicação e link, e exporta o resultado para um arquivo CSV.

Uso:
    python coletor_artigos_pinn.py
"""

import time
import xml.etree.ElementTree as ET

import pandas as pd
import requests

# =============================================================================
# Configuração
# =============================================================================
TERMO_BUSCA = "physics-informed neural network"
API_URL = "https://export.arxiv.org/api/query"
TOTAL_DESEJADO = 2000       # Limite superior; volume suficiente para cobrir vários meses
POR_PAGINA = 50             # Quantidade de artigos solicitada por requisição
PAUSA_SEGUNDOS = 3          # Intervalo entre requisições recomendado pelo arXiv
ARQUIVO_CSV = "artigos_pinn_arxiv.csv"

# Namespace do formato Atom, utilizado nas respostas XML da API.
NS = {"atom": "http://www.w3.org/2005/Atom"}


# =============================================================================
# Requisição
# =============================================================================
def buscar_pagina(inicio):
    """Consulta uma página de resultados da API do arXiv.

    Args:
        inicio: Índice do primeiro resultado da página (deslocamento).

    Returns:
        Conteúdo XML da resposta, em formato de texto.

    Raises:
        requests.HTTPError: Se a API retornar um status HTTP de erro.
    """
    parametros = {
        # As aspas restringem a busca à frase exata e o prefixo "all:" abrange
        # todos os campos. Os hifens são substituídos por espaços para evitar
        # que interfiram na interpretação da consulta pela API.
        "search_query": f'all:"{TERMO_BUSCA.replace("-", " ")}"',
        "start": inicio,
        "max_results": POR_PAGINA,
        "sortBy": "submittedDate",   # Ordena do mais recente ao mais antigo
        "sortOrder": "descending",
    }
    resposta = requests.get(API_URL, params=parametros, timeout=30)
    resposta.raise_for_status()
    return resposta.text


# =============================================================================
# Extração
# =============================================================================
def extrair_artigos(xml_texto):
    """Converte uma resposta XML da API em uma lista de artigos.

    Args:
        xml_texto: Conteúdo XML retornado pela API, no formato Atom.

    Returns:
        Lista de dicionários, um por artigo, com as chaves "titulo", "autores",
        "data_publicacao" e "link".
    """
    raiz = ET.fromstring(xml_texto)
    artigos = []

    for entry in raiz.findall("atom:entry", NS):
        # Normaliza as quebras de linha e os espaços repetidos do título.
        titulo = " ".join(entry.findtext("atom:title", "", NS).split())

        autores = [
            autor.findtext("atom:name", "", NS).strip()
            for autor in entry.findall("atom:author", NS)
        ]

        # Mantém apenas a data (AAAA-MM-DD) do carimbo de data e hora ISO 8601.
        data = entry.findtext("atom:published", "", NS)[:10]

        # A tag <id> contém a URL da página do artigo no arXiv.
        link = entry.findtext("atom:id", "", NS).strip()

        artigos.append({
            "titulo": titulo,
            "autores": "; ".join(autores),  # Nomes podem conter vírgulas
            "data_publicacao": data,
            "link": link,
        })

    return artigos


# =============================================================================
# Coleta
# =============================================================================
def rodar_coleta():
    """Percorre as páginas de resultados e reúne os artigos encontrados.

    A coleta termina ao atingir TOTAL_DESEJADO ou quando a API não retorna
    mais resultados. Artigos duplicados são descartados com base no link.

    Returns:
        Lista de dicionários de artigos, sem duplicatas.
    """
    todos = []
    links_vistos = set()

    for inicio in range(0, TOTAL_DESEJADO, POR_PAGINA):
        print(f"Buscando artigos {inicio} a {inicio + POR_PAGINA - 1}...")
        artigos = extrair_artigos(buscar_pagina(inicio))

        if not artigos:
            print("Sem mais resultados.")
            break

        for artigo in artigos:
            if artigo["link"] not in links_vistos:
                links_vistos.add(artigo["link"])
                todos.append(artigo)

        time.sleep(PAUSA_SEGUNDOS)

    return todos


# =============================================================================
# Exportação
# =============================================================================
def salvar_csv(artigos):
    """Exporta os artigos para o arquivo definido em ARQUIVO_CSV.

    Args:
        artigos: Lista de dicionários de artigos.

    Returns:
        DataFrame com os artigos exportados.
    """
    df = pd.DataFrame(artigos)
    # A codificação utf-8-sig garante a exibição correta dos acentos no Excel.
    df.to_csv(ARQUIVO_CSV, index=False, encoding="utf-8-sig")
    return df


if __name__ == "__main__":
    artigos = rodar_coleta()
    df = salvar_csv(artigos)

    print(f"\nColeta concluída: {len(df)} artigos salvos em '{ARQUIVO_CSV}'.")
    if len(df) >= 50:
        print("Quantidade mínima de 50 artigos atingida.")
    else:
        print("Aviso: quantidade inferior ao mínimo de 50 artigos. Revise o termo de busca.")
    print(df.head())
