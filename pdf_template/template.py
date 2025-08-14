import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# --- util ---

def _base_dir():
    return os.path.dirname(os.path.abspath(__file__))

def _logo_path():
    # assets está um nível acima de pdf_template
    p = os.path.abspath(os.path.join(_base_dir(), "..", "assets", "logo.png"))
    return p if os.path.isfile(p) else None

def _draw_header(c, largura, altura):
    # Logo (4x4 cm) no topo esquerdo
    lp = _logo_path()
    if lp:
        c.drawImage(lp, 2*cm, altura - 5*cm, width=4*cm, height=4*cm,
                    preserveAspectRatio=True, mask='auto')

    # Título e subtítulo
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(7*cm, altura - 2.4*cm, "Lucas Film")

    c.setFont("Helvetica", 13)
    c.drawString(7*cm, altura - 3.2*cm, "Películas residencial e automotivas")

    # Endereço e telefone
    c.setFont("Helvetica", 10)
    c.drawString(7*cm, altura - 3.9*cm, "Avenida Theonas Martins Gomes, 369, Mangueirinha, Rio Bonito")
    c.drawString(7*cm, altura - 4.5*cm, "Telefone: (21) 9 9495-9893")

    # Data
    c.setFont("Helvetica-Oblique", 9)
    c.drawRightString(largura - 2*cm, altura - 2.4*cm, datetime.now().strftime("%d/%m/%Y %H:%M"))

    # Linha separadora
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(2*cm, altura - 5.8*cm, largura - 2*cm, altura - 5.8*cm)

def _draw_table_header(c, y):
    # Barra de fundo do cabeçalho da tabela
    c.setFillColor(colors.HexColor("#333333"))
    c.rect(2*cm, y - 0.35*cm, 17*cm, 0.85*cm, fill=True, stroke=False)

    # Títulos
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2.2*cm, y, "Medida")
    c.drawRightString(8*cm, y, "Qtd")
    c.drawRightString(12*cm, y, "Preço/m²")
    c.drawRightString(16*cm, y, "Área Total")
    c.drawRightString(19*cm, y, "Total (R$)")

def _format_money(v):
    return f"R$ {v:.2f}"

# --- API principal ---

def criar_pdf_dados(dados, caminho_arquivo):
    """
    dados: {
      'itens': [
        {'medida': '0.30x0.50', 'quantidade': 4, 'preco_m2': 120.0, 'area': 0.60, 'total': 72.0},
        ...
      ]
    }
    """
    c = canvas.Canvas(caminho_arquivo, pagesize=A4)
    largura, altura = A4

    # Fundo claro
    c.setFillColorRGB(0.97, 0.97, 0.97)
    c.rect(0, 0, largura, altura, fill=1, stroke=0)

    # Cabeçalho
    _draw_header(c, largura, altura)

    # Tabela
    y = altura - 7.2*cm
    _draw_table_header(c, y)
    y -= 0.9*cm

    total_geral = 0.0
    c.setFont("Helvetica", 11)

    for i, item in enumerate(dados.get("itens", [])):
        # quebra de página
        if y < 3.5*cm:
            c.showPage()
            c.setFillColorRGB(0.97, 0.97, 0.97)
            c.rect(0, 0, largura, altura, fill=1, stroke=0)
            _draw_header(c, largura, altura)
            y = altura - 7.2*cm
            _draw_table_header(c, y)
            y -= 0.9*cm
            c.setFont("Helvetica", 11)

        # linha zebrada
        if i % 2 == 0:
            c.setFillColor(colors.HexColor("#F2F2F2"))
            c.rect(2*cm, y - 0.32*cm, 17*cm, 0.64*cm, fill=True, stroke=False)

        c.setFillColor(colors.black)
        c.drawString(2.2*cm, y, item["medida"])
        c.drawRightString(8*cm, y, str(item["quantidade"]))
        c.drawRightString(12*cm, y, f"{item['preco_m2']:.2f}")
        c.drawRightString(16*cm, y, f"{item['area']:.2f}")
        c.drawRightString(19*cm, y, f"{item['total']:.2f}")

        total_geral += float(item["total"])
        y -= 0.65*cm

    # ------------------ TOTAL GERAL ------------------
    if y < 4*cm:
        c.showPage()
        c.setFillColorRGB(0.97, 0.97, 0.97)
        c.rect(0, 0, largura, altura, fill=1, stroke=0)
        _draw_header(c, largura, altura)
        y = altura - 7.2*cm

    y -= 0.6*cm
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#FF5733"))
    c.drawRightString(19*cm, y, f"TOTAL GERAL: {_format_money(total_geral)}")

    # ------------------ FORMAS DE PAGAMENTO ------------------
    y -= 1*cm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(2*cm, y, "Formas de pagamento: Dinheiro, Cartão de crédito/débito e Pix")

    # ------------------ RODAPÉ COM REDES SOCIAIS ------------------
    rodape_altura = 2 * cm
    c.setFillColorRGB(0.15, 0.15, 0.15)  # fundo escuro
    c.rect(0, 0, largura, rodape_altura, stroke=0, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, 0.7 * cm, "Instagram: @lucas.filmss")
    c.drawString(7 * cm, 0.7 * cm, "WhatsApp: 21 9 9495 9893")
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(2 * cm, 0.3 * cm, "Siga no Instagram para conhecer melhor nosso trabalho")

    c.save()
