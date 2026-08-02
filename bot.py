import json
import os
import random
from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pdf_template.template import criar_pdf_dados



with open("config.json") as f:
    TOKEN = json.load(f)["token"]

CONFIG_FILE = "config.json"


CONFIG_PADRAO = {
    "nome": "Lucas Film",
    "subtitulo": "Películas residencial e automotivas",
    "endereco": "Avenida Theonas Martins Gomes, 369, Mangueirinha, Rio Bonito",
    "telefone": "(21) 9 9495-9893",
    "instagram": "@lucas.filmss"
}


def carregar_config():
    if not os.path.exists(CONFIG_FILE):
        salvar_config(CONFIG_PADRAO)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Garante que novas configurações sejam adicionadas
        for chave, valor in CONFIG_PADRAO.items():
            if chave not in config:
                config[chave] = valor

        return config

    except Exception:
        return CONFIG_PADRAO.copy()


def salvar_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def _to_float(br_number: str) -> float:
    """Aceita '0.30', '0,30' etc."""
    return float(br_number.replace(",", ".").strip())

def _parse_line(line: str):
    # Ex.: "0.30x0.50, 4, 120"
    partes = [p.strip() for p in line.split(",")]
    total_geral=0
    if len(partes) != 3:
        raise ValueError("Formato inválido. Use: ALTURAxLARGURA, QUANTIDADE, PREÇO_M2")

    medida = partes[0].lower().replace(" ", "")
    if "x" not in medida:
        raise ValueError("Medida deve conter 'x', ex.: 0.30x0.50")

    alt_str, larg_str = medida.split("x", 1)
    altura = _to_float(alt_str)
    largura = _to_float(larg_str)

    quantidade = int(partes[1])
    preco_m2 = _to_float(partes[2])

    area_unit = altura * largura
    area_total = area_unit * quantidade
    total_item = area_unit * quantidade * preco_m2
    total_geral += total_item

    return {
        "medida": f"{altura:.2f}x{largura:.2f}",
        "quantidade": quantidade,
        "preco_m2": preco_m2,
        "area": area_total,
        "total": total_item
    }
def _parse_produto(line: str):
    # Ex.: "Película fumê, 120, 6"
    partes = [p.strip() for p in line.split(",")]

    if len(partes) != 3:
        raise ValueError("Formato inválido. Use: PRODUTO, VALOR_UNITÁRIO, QUANTIDADE")

    nome = partes[0]
    valor_unit = _to_float(partes[1])
    quantidade = int(partes[2])

    total = valor_unit * quantidade

    return {
        "produto": nome,
        "quantidade": quantidade,
        "valor_unit": valor_unit,
        "total": total
    }
def calcular_totais(itens):
    """
    Recebe a lista de itens e retorna:
    - total_itens: soma das quantidades
    - total_m2: soma das áreas (altura * largura * quantidade)
    - total_geral: soma dos valores totais
    """
    total_itens = sum(item["quantidade"] for item in itens)
    total_m2 = sum(item["area"] for item in itens)
    total_geral = sum(item["total"] for item in itens)
    return total_itens, total_m2, total_geral


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Envie uma ou mais linhas no formato:\n"
        "ALTURAxLARGURA, QUANTIDADE, PREÇO_M2\n\n"
        "Exemplo:\n"
        "0.30x0.50, 4, 120\n"
        "1,00x2,00, 2, 150"
    )

async def processar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        linhas = [l for l in update.message.text.splitlines() if l.strip()]
        itens_medida = []
        itens_produto = []
        erros = []

        for ln in linhas:
            try:
                if "x" in ln.lower():
                    itens_medida.append(_parse_line(ln))
                else:
                    itens_produto.append(_parse_produto(ln))
            except Exception as e:
                erros.append(f"Erro na linha '{ln}': {e}")

        if not itens_medida and not itens_produto:
            raise ValueError("Nenhuma linha válida para processar.")

        dados = {
            "data": datetime.now().strftime("%d/%m/%Y"),
            "itens_medida": itens_medida,
            "itens_produto": itens_produto
        }

        caminho_pdf = "orcamento.pdf"
        criar_pdf_dados(dados, caminho_pdf)

        total_geral = 0

        if itens_medida:
            _, _, total_medidas = calcular_totais(itens_medida)
            total_geral += total_medidas

        if itens_produto:
            total_produtos = sum(i["total"] for i in itens_produto)
            total_geral += total_produtos

        with open(caminho_pdf, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename="orcamento.pdf")
            )

        await update.message.reply_text(
            f"💰 Valor total do orçamento: R$ {total_geral:.2f}"
        )

        if erros:
            await update.message.reply_text("❗Erros encontrados:\n" + "\n".join(erros))

    except Exception as e:
        await update.message.reply_text(f"❗ Erro: {e}")


async def teste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = []
    precos_possiveis = [89, 90, 100, 120]
    total_geral = 0

    for _ in range(50):
        altura = round(random.uniform(0.30, 2.00), 2)
        largura = round(random.uniform(0.30, 2.00), 2)
        medida = f"{altura}x{largura}"
        qtd = random.randint(1, 10)
        preco_m2 = random.choice(precos_possiveis)

        total_item = altura * largura * qtd * preco_m2
        total_geral += total_item

        dados.append({
            "medida": medida,
            "quantidade": qtd,
            "preco_m2": preco_m2,
            "area": round(altura*largura*qtd, 2),
            "total": round(total_item, 2)
        })

    caminho_pdf = "teste_aleatorio.pdf"
    criar_pdf_dados({"data": datetime.now().strftime("%d/%m/%Y"), "itens": dados}, caminho_pdf)

async def alterar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text.strip()

        # Remove "!alterar"
        comando = texto[len("!alterar"):].strip()

        if not comando:
            await update.message.reply_text(
                "❗ Use:\n\n"
                "!alterar campo novo_valor\n\n"
                "Campos disponíveis:\n"
                "• nome\n"
                "• subtitulo\n"
                "• endereco\n"
                "• telefone\n"
                "• instagram\n\n"
                "Exemplo:\n"
                "!alterar endereco Rua das Flores, 100, Rio Bonito"
            )
            return

        partes = comando.split(" ", 1)

        campo = partes[0].lower()

        campos_validos = [
            "nome",
            "subtitulo",
            "endereco",
            "telefone",
            "instagram"
        ]

        if campo not in campos_validos:
            await update.message.reply_text(
                f"❌ Campo '{campo}' não existe.\n\n"
                "Campos disponíveis:\n"
                "nome\n"
                "subtitulo\n"
                "endereco\n"
                "telefone\n"
                "instagram"
            )
            return

        # Se o usuário colocou apenas "!alterar endereco",
        # o campo será apagado.
        if len(partes) == 1:
            novo_valor = ""
        else:
            novo_valor = partes[1].strip()

        config = carregar_config()

        valor_anterior = config.get(campo, "")

        config[campo] = novo_valor

        salvar_config(config)

        await update.message.reply_text(
            f"✅ Configuração alterada!\n\n"
            f"Campo: {campo}\n"
            f"Anterior: {valor_anterior or '(vazio)'}\n"
            f"Novo: {novo_valor or '(vazio)'}"
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Erro ao alterar configuração:\n{e}"
        )

async def config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        dados = carregar_config()

        mensagem = (
            "⚙️ CONFIGURAÇÕES ATUAIS\n\n"
            f"Nome: {dados['nome']}\n"
            f"Subtítulo: {dados['subtitulo']}\n"
            f"Endereço: {dados['endereco']}\n"
            f"Telefone: {dados['telefone']}\n"
            f"Instagram: {dados['instagram']}"
        )

        await update.message.reply_text(mensagem)

    except Exception as e:
        await update.message.reply_text(
            f"❌ Erro ao carregar configurações: {e}"
        )
# envia PDF para o usuário
    with open(caminho_pdf, "rb") as f:
        await update.message.reply_document(document=InputFile(f, filename="teste_aleatorio.pdf"))

        # mensagem com total geral
        await update.message.reply_text(f"✅ PDF de teste gerado com 50 itens.\nTotal geral: R$ {total_geral:.2f}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos normais
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("teste", teste))

    # Comandos de configuração
    # DEVEM vir antes do processar()
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^!alterar(?:\s|$)"),
            alterar
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^!config$"),
            config
        )
    )

    # Orçamentos
    # Deve ser o último handler de texto
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            processar
        )
    )

    print("Bot rodando...")
    app.run_polling()
