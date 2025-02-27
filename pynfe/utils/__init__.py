# *-* encoding: utf-8 *-*

import codecs
import os
from unicodedata import normalize
from signxml import XMLSigner

try:
    from lxml import etree  # noqa: F401
except ImportError:
    raise Exception("Falhou ao importar lxml/ElementTree")

try:
    from . import flags
except ImportError:
    raise Exception("Falhou ao importar flags")


# @memoize
def so_numeros(texto) -> str:
    """
    Retorna o texto informado mas somente os numeros

    :param texto: String ou Inteiro a ser analisada
    :return: String somente com números
    """
    return "".join(filter(str.isdigit, str(texto)))


# @memoize
def obter_pais_por_codigo(codigo):
    # TODO
    if codigo == "1058":
        return "Brasil"


CAMINHO_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
CAMINHO_MUNICIPIOS = os.path.join(CAMINHO_DATA, "MunIBGE")
CARACTERS_ACENTUADOS = {
    ord("á"): "a",
    ord("â"): "a",
    ord("à"): "a",
    ord("ã"): "a",
    ord("ä"): "a",
    ord("é"): "e",
    ord("ê"): "e",
    ord("ë"): "e",
    ord("í"): "i",
    ord("ï"): "i",
    ord("ó"): "o",
    ord("õ"): "o",
    ord("ô"): "o",
    ord("ö"): "o",
    ord("ú"): "u",
    ord("ü"): "u",
    ord("ç"): "c",
    ord("'"): "",
}


# @memoize
def normalizar_municipio(municipio):
    if not isinstance(municipio, str):
        municipio = municipio.decode("utf-8")

    return municipio.lower().translate(CARACTERS_ACENTUADOS).upper()


# @memoize
def carregar_arquivo_municipios(uf, reverso=False):
    if isinstance(uf, str):
        try:
            uf = int(uf)
        except ValueError:
            uf = flags.CODIGOS_ESTADOS[uf.upper()]

    caminho_arquivo = os.path.join(CAMINHO_MUNICIPIOS, "MunIBGE-UF%s.txt" % uf)

    # Carrega o conteudo do arquivo
    fp = codecs.open(caminho_arquivo, "r", "utf-8-sig")
    linhas = list(fp.readlines())
    fp.close()

    municipios_dict = {}

    for linha in linhas:
        codigo, municipio = linha.split("\t")
        codigo = codigo.strip()
        municipio = municipio.strip()

        if not reverso:
            municipios_dict[codigo] = municipio
        else:
            municipios_dict[normalizar_municipio(municipio)] = codigo

    return municipios_dict


# @memoize
def obter_codigo_por_municipio(municipio, uf):
    # TODO: fazer UF ser opcional
    municipios = carregar_arquivo_municipios(uf, True)
    municipio_normalizado = normalizar_municipio(municipio)
    if municipio_normalizado not in municipios:
        raise ValueError("Município inválido %s" % municipio)
    return municipios[municipio_normalizado]


# @memoize
def obter_municipio_por_codigo(codigo, uf, normalizado=False):
    # TODO: fazer UF ser opcional
    municipios = carregar_arquivo_municipios(uf)
    municipio = municipios.get(codigo)
    if municipio is None:
        raise ValueError
    if normalizado:
        return normalizar_municipio(municipio)
    return municipio


# @memoize
def obter_municipio_e_codigo(dados, uf):
    """Retorna código e município
    municipio_ou_codigo - espera receber um dicionário no formato:
        {codigo: 121212, municipio: u'municipio'}
    """

    cod = dados.get("codigo", "")
    mun = normalizar_municipio(dados.get("municipio", ""))
    try:
        cod = int(cod)
    except ValueError:
        cod = obter_codigo_por_municipio(mun, uf)
    # TODO: se ainda com este teste apresentar erros de nessa seção
    # desenvolver um retorno que informe ao cliente quais nfes estão com erro
    # e não explodir esse a geração das outras nfes
    municipio = obter_municipio_por_codigo(cod, uf, normalizado=True)
    return cod, municipio


# @memoize
def extrair_tag(root):
    return root.tag.split("}")[-1]


def formatar_decimal(dec):
    if dec * 100 - int(dec * 100):
        return str(dec)
    else:
        return "%.2f" % dec


def obter_uf_por_codigo(codigo_uf):
    if isinstance(codigo_uf, str) and codigo_uf.isalpha():
        return codigo_uf

    estados = {v: k for k, v in flags.CODIGOS_ESTADOS.items()}
    return estados[codigo_uf]


def remover_acentos(txt):
    return normalize("NFKD", txt).encode("ASCII", "ignore").decode("ASCII")


class CustomXMLSigner(XMLSigner):
    def __init__(self, method, signature_algorithm, digest_algorithm, c14n_algorithm):
        super().__init__(method, signature_algorithm, digest_algorithm, c14n_algorithm)

    def check_deprecated_methods(self):
        pass
