# Coletor de artigos sobre PINNs

Script em Python que consulta a [API pública do arXiv](https://info.arxiv.org/help/api/index.html), reúne metadados de artigos sobre *physics-informed neural networks* (PINNs) e exporta o resultado para um arquivo CSV.

## Como funciona

1. Busca a frase exata "physics informed neural network" em todos os campos, do artigo mais recente ao mais antigo.
2. Percorre os resultados em páginas de 50 artigos, com pausa de 3 segundos entre as requisições, como o arXiv recomenda.
3. Extrai os dados do XML retornado e descarta duplicatas com base no link.
4. Salva tudo em `artigos_pinn_arxiv.csv`.

## Requisitos

- Python 3.11 ou superior
- Acesso à internet

## Instalação

```bash
git clone https://github.com/<seu-usuario>/<repositorio>.git
cd <repositorio>

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux ou macOS

pip install -r requirements.txt
```

## Uso

```bash
python coletor_artigos_pinn.py
```

A coleta leva alguns segundos. Ao final, o script informa quantos artigos foram salvos, avisa se o total ficou abaixo de 50 e mostra as primeiras linhas no terminal.

Cada execução substitui o CSV existente. Como a busca começa pelos artigos mais recentes, o resultado muda com o tempo.

## Resultado

O arquivo `artigos_pinn_arxiv.csv` incluído no repositório é uma coleta de exemplo com 100 artigos. Ele tem as seguintes colunas:

| Coluna | Descrição | Exemplo |
| --- | --- | --- |
| `titulo` | Título do artigo | `Fractional physics-informed neural networks to model social media virality` |
| `autores` | Autores separados por `; ` | `Alex Koong; George Em Karniadakis` |
| `data_publicacao` | Data da primeira versão (AAAA-MM-DD) | `2026-11-04` |
| `link` | Página do artigo no arXiv | `http://arxiv.org/abs/2611.07215v1` |

O arquivo usa a codificação UTF-8 com BOM para que os acentos apareçam corretamente no Excel.

## Configuração

Para mudar a busca, edite as constantes no início de [`coletor_artigos_pinn.py`](coletor_artigos_pinn.py):

| Constante | Padrão | Função |
| --- | --- | --- |
| `TERMO_BUSCA` | `"physics-informed neural network"` | Frase pesquisada |
| `TOTAL_DESEJADO` | `100` | Limite de artigos a coletar |
| `POR_PAGINA` | `50` | Artigos por requisição |
| `PAUSA_SEGUNDOS` | `3` | Intervalo entre requisições |
| `ARQUIVO_CSV` | `"artigos_pinn_arxiv.csv"` | Arquivo de saída |

## Estrutura

```text
.
├── coletor_artigos_pinn.py  # Script de coleta
├── artigos_pinn_arxiv.csv   # Exemplo de resultado
├── requirements.txt         # Dependências
├── README.md
└── LICENSE
```

## Dados

Os metadados vêm do arXiv. Consulte os [termos de uso da API](https://info.arxiv.org/help/api/tou.html) antes de ampliar a coleta.

## Agradecimentos

Thank you to arXiv for use of its open access interoperability.

*Agradecemos ao arXiv pelo uso de sua interoperabilidade de acesso aberto.*

## Licença

Distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE).
