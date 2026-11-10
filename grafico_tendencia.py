"""
Análise da tendência temporal de publicações sobre PINNs no arXiv.

Lê o CSV gerado por coletor_artigos_pinn.py, conta os artigos publicados em
cada mês, exibe a contagem no terminal e salva um gráfico de barras em PNG.

Uso:
    python grafico_tendencia.py
"""

import matplotlib

# Backend não interativo: gera o arquivo de imagem sem abrir janela, o que
# permite executar o script em terminais e servidores sem interface gráfica.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

# =============================================================================
# Configuração
# =============================================================================
ARQUIVO_CSV = "artigos_pinn_arxiv.csv"
ARQUIVO_GRAFICO = "tendencia_artigos_por_mes.png"

# Paleta do gráfico: uma única série dispensa legenda e usa um só matiz.
COR_BARRA = "#2a78d6"
COR_TEXTO = "#3d3c39"
COR_EIXOS = "#898781"
COR_GRADE = "#e4e3df"
COR_FUNDO = "#fcfcfb"

# Quantidade máxima de rótulos no eixo X; acima disso, os rótulos são
# espaçados para evitar sobreposição.
MAX_ROTULOS_X = 24


# =============================================================================
# Leitura e agregação
# =============================================================================
def carregar_artigos(caminho):
    """Lê o CSV de artigos e converte a coluna de datas.

    Args:
        caminho: Caminho do arquivo CSV gerado pelo coletor.

    Returns:
        DataFrame com a coluna "data_publicacao" no tipo datetime.
    """
    # utf-8-sig remove o BOM gravado pelo coletor para compatibilidade com Excel.
    df = pd.read_csv(caminho, encoding="utf-8-sig")
    # Datas inválidas viram NaT e são descartadas, em vez de interromper a análise.
    df["data_publicacao"] = pd.to_datetime(df["data_publicacao"], errors="coerce")
    return df.dropna(subset=["data_publicacao"])


def contar_por_mes(df):
    """Conta os artigos publicados em cada mês.

    Args:
        df: DataFrame com a coluna "data_publicacao" no tipo datetime.

    Returns:
        Series indexada pelo primeiro dia de cada mês ("MS" = month start),
        com a quantidade de artigos. Meses sem publicações aparecem com 0.
    """
    return df.set_index("data_publicacao").resample("MS").size()


# =============================================================================
# Visualização
# =============================================================================
def plotar_tendencia(contagem, caminho_saida):
    """Gera o gráfico de barras da contagem mensal e o salva em PNG.

    Args:
        contagem: Series com a quantidade de artigos por mês.
        caminho_saida: Caminho do arquivo de imagem a ser gerado.
    """
    rotulos = contagem.index.strftime("%Y-%m")
    posicoes = range(len(contagem))

    # A largura da figura acompanha o número de meses, dentro de limites razoáveis.
    largura = min(max(8, len(contagem) * 0.35), 20)
    fig, ax = plt.subplots(figsize=(largura, 5), facecolor=COR_FUNDO)
    ax.set_facecolor(COR_FUNDO)

    ax.bar(posicoes, contagem.values, width=0.8, color=COR_BARRA, zorder=2)

    # Rótulos do eixo X: exibe no máximo MAX_ROTULOS_X, mantendo o último mês.
    passo = max(1, -(-len(contagem) // MAX_ROTULOS_X))  # Divisão com arredondamento para cima
    indices = list(range(0, len(contagem), passo))
    ultimo = len(contagem) - 1
    if indices[-1] != ultimo:
        # Substitui o rótulo anterior pelo último mês quando estão próximos
        # demais, evitando que os dois textos se sobreponham.
        if len(indices) > 1 and ultimo - indices[-1] < passo:
            indices[-1] = ultimo
        else:
            indices.append(ultimo)
    ax.set_xticks(indices)
    ax.set_xticklabels([rotulos[i] for i in indices], rotation=45, ha="right")

    # Título e eixos nomeados.
    periodo = f"{rotulos[0]} a {rotulos[-1]}"
    ax.set_title(
        f"Artigos sobre physics-informed neural networks no arXiv por mês ({periodo})",
        color=COR_TEXTO, fontsize=12, loc="left", pad=12,
    )
    ax.set_xlabel("Mês de publicação (AAAA-MM)", color=COR_TEXTO)
    ax.set_ylabel("Quantidade de artigos", color=COR_TEXTO)

    # Grade e eixos discretos, para que o destaque fique com os dados.
    ax.yaxis.grid(True, color=COR_GRADE, linewidth=0.8, zorder=0)
    ax.yaxis.get_major_locator().set_params(integer=True)  # Contagens são inteiras
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(COR_EIXOS)
    ax.tick_params(colors=COR_EIXOS, labelcolor=COR_TEXTO, length=0)
    ax.margins(x=0.01)

    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=150)
    plt.close(fig)


# =============================================================================
# Saída no terminal
# =============================================================================
def imprimir_contagem(contagem):
    """Exibe a contagem mensal de artigos em formato de tabela.

    Args:
        contagem: Series com a quantidade de artigos por mês.
    """
    print("Artigos por mês:")
    print(f"{'Mês':<8} {'Artigos':>7}")
    for mes, quantidade in contagem.items():
        print(f"{mes:%Y-%m}  {quantidade:>7}")
    print(f"{'Total':<8} {contagem.sum():>7}")


if __name__ == "__main__":
    artigos = carregar_artigos(ARQUIVO_CSV)

    if artigos.empty:
        raise SystemExit(f"Nenhum artigo com data válida encontrado em '{ARQUIVO_CSV}'.")

    contagem = contar_por_mes(artigos)
    imprimir_contagem(contagem)
    plotar_tendencia(contagem, ARQUIVO_GRAFICO)

    print(f"\nGráfico salvo em '{ARQUIVO_GRAFICO}'.")
