import os
import json
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas


# ============================================================
# CONFIGURAÇÕES
# ============================================================

def _base_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _config_path():
    return os.path.abspath(
        os.path.join(_base_dir(), "..", "config.json")
    )


def _carregar_config():
    caminho = _config_path()

    config_padrao = {
        "nome": "Lucas Film",
        "subtitulo": "Películas residencial e automotivas",
        "endereco": "Avenida Theonas Martins Gomes, 369, Mangueirinha, Rio Bonito",
        "telefone": "(21) 9 9495-9893",
        "instagram": "@lucas.filmss"
    }

    try:
        if not os.path.isfile(caminho):
            return config_padrao.copy()

        with open(caminho, "r", encoding="utf-8") as f:
            config = json.load(f)

        for chave, valor in config_padrao.items():
            if chave not in config:
                config[chave] = valor

        return config

    except Exception:
        return config_padrao.copy()


def _logo_path():
    """
    Procura:
    projeto/
        assets/
            logo.png
        pdf_template/
            template.py
    """

    caminho = os.path.abspath(
        os.path.join(
            _base_dir(),
            "..",
            "assets",
            "logo.png"
        )
    )

    if os.path.isfile(caminho):
        return caminho

    return None


def _format_money(valor):
    """
    Formata valores no padrão brasileiro.
    Exemplo:
    1592.50 -> R$ 1.592,50
    """

    valor = float(valor)

    texto = f"{valor:,.2f}"

    texto = (
        texto
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

    return f"R$ {texto}"


# ============================================================
# FUNÇÃO PARA DESENHAR O CABEÇALHO
# ============================================================

def _draw_header(c, largura, altura):

    config = _carregar_config()

    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    logo = _logo_path()

    if logo:

        c.drawImage(
            logo,
            2 * cm,
            altura - 5 * cm,
            width=4 * cm,
            height=4 * cm,
            preserveAspectRatio=True,
            mask="auto"
        )

    # --------------------------------------------------------
    # Nome da empresa
    # --------------------------------------------------------

    c.setFillColor(colors.black)

    c.setFont(
        "Helvetica-Bold",
        22
    )

    c.drawString(
        7 * cm,
        altura - 2.4 * cm,
        config.get("nome", "Lucas Film")
    )

    # --------------------------------------------------------
    # Subtítulo
    # --------------------------------------------------------

    c.setFont(
        "Helvetica",
        13
    )

    c.drawString(
        7 * cm,
        altura - 3.2 * cm,
        config.get(
            "subtitulo",
            "Películas residencial e automotivas"
        )
    )

    # --------------------------------------------------------
    # Endereço
    # --------------------------------------------------------

    c.setFont(
        "Helvetica",
        10
    )

    c.drawString(
        7 * cm,
        altura - 3.9 * cm,
        config.get("endereco", "")
    )

    # --------------------------------------------------------
    # Telefone
    # --------------------------------------------------------

    c.drawString(
        7 * cm,
        altura - 4.5 * cm,
        f"Telefone: {config.get('telefone', '')}"
    )

    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    c.setFont(
        "Helvetica-Oblique",
        9
    )

    c.drawRightString(
        largura - 2 * cm,
        altura - 2.4 * cm,
        datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )
    )

    # --------------------------------------------------------
    # Linha separadora
    # --------------------------------------------------------

    c.setStrokeColor(colors.black)

    c.setLineWidth(1)

    c.line(
        2 * cm,
        altura - 5.8 * cm,
        largura - 2 * cm,
        altura - 5.8 * cm
    )


# ============================================================
# FUNÇÃO PARA INICIAR NOVA PÁGINA
# ============================================================

def _nova_pagina(c, largura, altura):

    c.showPage()

    # Fundo
    c.setFillColorRGB(
        0.97,
        0.97,
        0.97
    )

    c.rect(
        0,
        0,
        largura,
        altura,
        fill=1,
        stroke=0
    )

    # Cabeçalho
    _draw_header(
        c,
        largura,
        altura
    )


# ============================================================
# CABEÇALHO DA TABELA DE MEDIDAS
# ============================================================

def _draw_table_header_medidas(c, y):

    # Fundo
    c.setFillColor(
        colors.HexColor("#333333")
    )

    c.rect(
        2 * cm,
        y - 0.35 * cm,
        17 * cm,
        0.85 * cm,
        fill=True,
        stroke=False
    )

    # Texto
    c.setFillColor(colors.white)

    c.setFont(
        "Helvetica-Bold",
        11
    )

    c.drawString(
        2.2 * cm,
        y,
        "Medida"
    )

    c.drawRightString(
        8 * cm,
        y,
        "Qtd"
    )

    c.drawRightString(
        12 * cm,
        y,
        "Preço/m²"
    )

    c.drawRightString(
        16 * cm,
        y,
        "Área Total"
    )

    c.drawRightString(
        19 * cm,
        y,
        "Total (R$)"
    )


# ============================================================
# CABEÇALHO DA TABELA DE PRODUTOS
# ============================================================

def _draw_table_header_produtos(c, y):

    # Fundo
    c.setFillColor(
        colors.HexColor("#333333")
    )

    c.rect(
        2 * cm,
        y - 0.35 * cm,
        17 * cm,
        0.85 * cm,
        fill=True,
        stroke=False
    )

    # Texto
    c.setFillColor(colors.white)

    c.setFont(
        "Helvetica-Bold",
        11
    )

    c.drawString(
        2.2 * cm,
        y,
        "Produto / Serviço"
    )

    c.drawRightString(
        11 * cm,
        y,
        "Qtd"
    )

    c.drawRightString(
        15 * cm,
        y,
        "Valor Unit."
    )

    c.drawRightString(
        19 * cm,
        y,
        "Total (R$)"
    )


# ============================================================
# DESENHAR LINHA DE MEDIDA
# ============================================================

def _draw_medida(c, y, item, zebra=False):

    if zebra:

        c.setFillColor(
            colors.HexColor("#F2F2F2")
        )

        c.rect(
            2 * cm,
            y - 0.32 * cm,
            17 * cm,
            0.64 * cm,
            fill=True,
            stroke=False
        )

    c.setFillColor(colors.black)

    c.setFont(
        "Helvetica",
        10
    )

    medida = str(
        item.get("medida", "")
    )

    quantidade = item.get(
        "quantidade",
        0
    )

    preco_m2 = float(
        item.get("preco_m2", 0)
    )

    area = float(
        item.get("area", 0)
    )

    total = float(
        item.get("total", 0)
    )

    c.drawString(
        2.2 * cm,
        y,
        medida
    )

    c.drawRightString(
        8 * cm,
        y,
        str(quantidade)
    )

    c.drawRightString(
        12 * cm,
        y,
        f"{preco_m2:.2f}"
    )

    c.drawRightString(
        16 * cm,
        y,
        f"{area:.2f}"
    )

    c.drawRightString(
        19 * cm,
        y,
        f"{total:.2f}"
    )


# ============================================================
# DESENHAR LINHA DE PRODUTO
# ============================================================

def _draw_produto(c, y, item, zebra=False):

    if zebra:

        c.setFillColor(
            colors.HexColor("#F2F2F2")
        )

        c.rect(
            2 * cm,
            y - 0.32 * cm,
            17 * cm,
            0.64 * cm,
            fill=True,
            stroke=False
        )

    c.setFillColor(colors.black)

    c.setFont(
        "Helvetica",
        10
    )

    produto = str(
        item.get("produto", "")
    )

    quantidade = item.get(
        "quantidade",
        0
    )

    valor_unit = float(
        item.get("valor_unit", 0)
    )

    total = float(
        item.get("total", 0)
    )

    c.drawString(
        2.2 * cm,
        y,
        produto
    )

    c.drawRightString(
        11 * cm,
        y,
        str(quantidade)
    )

    c.drawRightString(
        15 * cm,
        y,
        f"{valor_unit:.2f}"
    )

    c.drawRightString(
        19 * cm,
        y,
        f"{total:.2f}"
    )


# ============================================================
# API PRINCIPAL
# ============================================================

def criar_pdf_dados(dados, caminho_arquivo):

    c = canvas.Canvas(
        caminho_arquivo,
        pagesize=A4
    )

    largura, altura = A4

    # --------------------------------------------------------
    # Fundo
    # --------------------------------------------------------

    c.setFillColorRGB(
        0.97,
        0.97,
        0.97
    )

    c.rect(
        0,
        0,
        largura,
        altura,
        fill=1,
        stroke=0
    )

    # --------------------------------------------------------
    # Cabeçalho
    # --------------------------------------------------------

    _draw_header(
        c,
        largura,
        altura
    )

    # --------------------------------------------------------
    # Dados recebidos
    # --------------------------------------------------------

    itens_medida = dados.get(
        "itens_medida",
        []
    )

    itens_produto = dados.get(
        "itens_produto",
        []
    )

    # --------------------------------------------------------
    # Compatibilidade com versão antiga
    # --------------------------------------------------------

    if not itens_medida:

        itens_medida = dados.get(
            "itens",
            []
        )

    # --------------------------------------------------------
    # Totais
    # --------------------------------------------------------

    total_medidas = sum(
        float(item.get("total", 0))
        for item in itens_medida
    )

    total_produtos = sum(
        float(item.get("total", 0))
        for item in itens_produto
    )

    total_geral = (
        total_medidas +
        total_produtos
    )

    # --------------------------------------------------------
    # Posição inicial
    # --------------------------------------------------------

    y = altura - 7.2 * cm

    # ========================================================
    # MEDIDAS
    # ========================================================

    if itens_medida:

        c.setFillColor(colors.black)

        c.setFont(
            "Helvetica-Bold",
            14
        )

        c.drawString(
            2 * cm,
            y,
            "Itens por Medida"
        )

        y -= 0.7 * cm

        _draw_table_header_medidas(
            c,
            y
        )

        y -= 0.9 * cm

        for i, item in enumerate(
            itens_medida
        ):

            # Verifica espaço
            if y < 4 * cm:

                _nova_pagina(
                    c,
                    largura,
                    altura
                )

                y = altura - 7.2 * cm

                c.setFont(
                    "Helvetica-Bold",
                    14
                )

                c.drawString(
                    2 * cm,
                    y,
                    "Itens por Medida"
                )

                y -= 0.7 * cm

                _draw_table_header_medidas(
                    c,
                    y
                )

                y -= 0.9 * cm

            _draw_medida(
                c,
                y,
                item,
                zebra=(i % 2 == 0)
            )

            y -= 0.65 * cm

        # Subtotal
        y -= 0.3 * cm

        c.setFillColor(colors.black)

        c.setFont(
            "Helvetica-Bold",
            11
        )

        c.drawRightString(
            19 * cm,
            y,
            f"Subtotal medidas: {_format_money(total_medidas)}"
        )

        y -= 0.9 * cm

    # ========================================================
    # PRODUTOS E SERVIÇOS
    # ========================================================

    if itens_produto:

        # Verifica espaço
        if y < 6 * cm:

            _nova_pagina(
                c,
                largura,
                altura
            )

            y = altura - 7.2 * cm

        c.setFillColor(colors.black)

        c.setFont(
            "Helvetica-Bold",
            14
        )

        c.drawString(
            2 * cm,
            y,
            "Produtos e Serviços"
        )

        y -= 0.7 * cm

        _draw_table_header_produtos(
            c,
            y
        )

        y -= 0.9 * cm

        for i, item in enumerate(
            itens_produto
        ):

            # Verifica espaço
            if y < 4 * cm:

                _nova_pagina(
                    c,
                    largura,
                    altura
                )

                y = altura - 7.2 * cm

                c.setFont(
                    "Helvetica-Bold",
                    14
                )

                c.drawString(
                    2 * cm,
                    y,
                    "Produtos e Serviços"
                )

                y -= 0.7 * cm

                _draw_table_header_produtos(
                    c,
                    y
                )

                y -= 0.9 * cm

            _draw_produto(
                c,
                y,
                item,
                zebra=(i % 2 == 0)
            )

            y -= 0.65 * cm

        # Subtotal
        y -= 0.3 * cm

        c.setFillColor(colors.black)

        c.setFont(
            "Helvetica-Bold",
            11
        )

        c.drawRightString(
            19 * cm,
            y,
            f"Subtotal produtos: {_format_money(total_produtos)}"
        )

        y -= 0.9 * cm

    # ========================================================
    # TOTAL GERAL
    # ========================================================

    if y < 5 * cm:

        _nova_pagina(
            c,
            largura,
            altura
        )

        y = altura - 7.2 * cm

    y -= 0.4 * cm

    c.setFont(
        "Helvetica-Bold",
        16
    )

    c.setFillColor(
        colors.HexColor("#FF5733")
    )

    c.drawRightString(
        19 * cm,
        y,
        f"TOTAL GERAL: {_format_money(total_geral)}"
    )

    # ========================================================
    # FORMAS DE PAGAMENTO
    # ========================================================

    y -= 1 * cm

    c.setFont(
        "Helvetica-Bold",
        11
    )

    c.setFillColor(colors.black)

    c.drawString(
        2 * cm,
        y,
        "Formas de pagamento: Dinheiro, Cartão de crédito/débito e Pix"
    )

    # ========================================================
    # RODAPÉ
    # ========================================================

    rodape_altura = 2 * cm

    c.setFillColorRGB(
        0.15,
        0.15,
        0.15
    )

    c.rect(
        0,
        0,
        largura,
        rodape_altura,
        stroke=0,
        fill=1
    )

    config = _carregar_config()

    c.setFillColor(colors.white)

    c.setFont(
        "Helvetica",
        10
    )

    c.drawString(
        2 * cm,
        0.7 * cm,
        f"Instagram: {config.get('instagram', '')}"
    )

    c.drawString(
        7 * cm,
        0.7 * cm,
        f"WhatsApp: {config.get('telefone', '')}"
    )

    c.setFont(
        "Helvetica-Oblique",
        9
    )

    c.drawString(
        2 * cm,
        0.3 * cm,
        "Siga no Instagram para conhecer melhor nosso trabalho"
    )

    # ========================================================
    # SALVAR PDF
    # ========================================================

    c.save()