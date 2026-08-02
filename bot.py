#version 1.0.0
import json
import os
import random
from datetime import datetime

from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from pdf_template.template import criar_pdf_dados


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CONFIG_FILE = "config.json"


def carregar_config():
    config_padrao = {
        "token": "",
        "nome": "Lucas Film",
        "subtitulo": "Película Residencial e Automotiva",
        "endereco": "Rua Doutor Matos, 543, Centro, Rio Bonito - RJ",
        "telefone": "(21) 9 9495-9893",
        "instagram": "@lucas.filmss"
    }

    if not os.path.exists(CONFIG_FILE):
        salvar_config(config_padrao)
        return config_padrao.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Garante que configurações novas sejam adicionadas
        for chave, valor in config_padrao.items():
            if chave not in config:
                config[chave] = valor

        return config

    except Exception:
        return config_padrao.copy()


def salvar_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            config,
            f,
            ensure_ascii=False,
            indent=4
        )


# Carrega o token
CONFIG = carregar_config()
TOKEN = CONFIG.get("token", "").strip()

if not TOKEN:
    raise ValueError(
        "❌ Token do Telegram não encontrado no config.json."
    )


# ============================================================
# FUNÇÕES DE CONVERSÃO E CÁLCULO
# ============================================================

def _to_float(valor):
    """
    Aceita:
    120
    120.50
    120,50
    """
    return float(
        str(valor)
        .replace(",", ".")
        .strip()
    )


def _parse_line(line):
    """
    Processa itens com medida.

    Formato:
    ALTURAxLARGURA, QUANTIDADE, PREÇO_M2

    Exemplo:
    0.80x1.20, 2, 120
    """

    partes = [
        p.strip()
        for p in line.split(",")
    ]

    if len(partes) != 3:
        raise ValueError(
            "Formato inválido.\n"
            "Use: ALTURAxLARGURA, QUANTIDADE, PREÇO_M2\n"
            "Exemplo: 0.80x1.20, 2, 120"
        )

    medida = (
        partes[0]
        .lower()
        .replace(" ", "")
    )

    if "x" not in medida:
        raise ValueError(
            "A medida deve conter 'x'.\n"
            "Exemplo: 0.80x1.20"
        )

    altura_str, largura_str = medida.split("x", 1)

    altura = _to_float(altura_str)
    largura = _to_float(largura_str)

    quantidade = int(partes[1])

    preco_m2 = _to_float(partes[2])

    if altura <= 0:
        raise ValueError("A altura deve ser maior que zero.")

    if largura <= 0:
        raise ValueError("A largura deve ser maior que zero.")

    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    if preco_m2 < 0:
        raise ValueError("O preço não pode ser negativo.")

    area_unitaria = altura * largura

    area_total = area_unitaria * quantidade

    total_item = area_total * preco_m2

    return {
        "medida": f"{altura:.2f}x{largura:.2f}",
        "quantidade": quantidade,
        "preco_m2": preco_m2,
        "area": area_total,
        "total": total_item
    }


def _parse_produto(line):
    """
    Processa produtos sem medida.

    Formato:
    PRODUTO, VALOR_UNITÁRIO, QUANTIDADE

    Exemplo:
    Película G5, 80, 4
    """

    partes = [
        p.strip()
        for p in line.split(",")
    ]

    if len(partes) != 3:
        raise ValueError(
            "Formato inválido.\n"
            "Use: PRODUTO, VALOR_UNITÁRIO, QUANTIDADE\n"
            "Exemplo: Película G5, 80, 4"
        )

    nome = partes[0]

    if not nome:
        raise ValueError(
            "O nome do produto não pode estar vazio."
        )

    valor_unit = _to_float(partes[1])
    quantidade = int(partes[2])

    if valor_unit < 0:
        raise ValueError(
            "O valor unitário não pode ser negativo."
        )

    if quantidade <= 0:
        raise ValueError(
            "A quantidade deve ser maior que zero."
        )

    total = valor_unit * quantidade

    return {
        "produto": nome,
        "quantidade": quantidade,
        "valor_unit": valor_unit,
        "total": total
    }


def calcular_totais_medidas(itens):
    total_itens = sum(i["quantidade"] for i in itens)
    total_m2 = sum(i["area"] for i in itens)
    total = sum(i["total"] for i in itens)
    return total_itens, total_m2, total


def calcular_totais_produtos(itens):
    total_itens = sum(i["quantidade"] for i in itens)
    total = sum(i["total"] for i in itens)
    return total_itens, total


# ============================================================
# /START
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bem-vindo ao Bot de Orçamentos da Lucas Film!\n\n"
        "📐 ITENS COM MEDIDA\n"
        "ALTURAxLARGURA, QUANTIDADE, PREÇO_M2\n"
        "Ex: 0.80x1.20, 2, 120\n\n"
        "📦 PRODUTOS\n"
        "PRODUTO, VALOR_UNITÁRIO, QUANTIDADE\n"
        "Ex: Película G5, 80, 4\n\n"
        "Você pode misturar os dois formatos."
    )


# ============================================================
# PROCESSAMENTO
# ============================================================

async def processar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        if not update.message or not update.message.text:
            return

        linhas = [
            l.strip()
            for l in update.message.text.splitlines()
            if l.strip()
        ]

        itens_medida = []
        itens_produto = []
        erros = []

        for linha in linhas:
            try:
                if "x" in linha.lower():
                    itens_medida.append(_parse_line(linha))
                else:
                    itens_produto.append(_parse_produto(linha))
            except Exception as e:
                erros.append(f"❌ {linha}\n{e}")

        if not itens_medida and not itens_produto:
            await update.message.reply_text(
                "❌ Nenhum item válido encontrado."
            )
            return

        dados = {
            "data": datetime.now().strftime("%d/%m/%Y"),
            "itens_medida": itens_medida,
            "itens_produto": itens_produto
        }

        caminho_pdf = "orcamento.pdf"
        criar_pdf_dados(dados, caminho_pdf)

        total_medidas = 0
        total_produtos = 0
        total_m2 = 0

        if itens_medida:
            _, total_m2, total_medidas = calcular_totais_medidas(itens_medida)

        if itens_produto:
            _, total_produtos = calcular_totais_produtos(itens_produto)

        total_geral = total_medidas + total_produtos

        with open(caminho_pdf, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename="orcamento.pdf")
            )

        msg = "✅ ORÇAMENTO GERADO!\n\n"

        if itens_medida:
            msg += (
                f"📐 Medidas: {len(itens_medida)}\n"
                f"📏 {total_m2:.2f} m²\n"
                f"💰 R$ {total_medidas:.2f}\n\n"
            )

        if itens_produto:
            msg += (
                f"📦 Produtos: {len(itens_produto)}\n"
                f"💰 R$ {total_produtos:.2f}\n\n"
            )

        msg += f"💰 TOTAL: R$ {total_geral:.2f}"

        await update.message.reply_text(msg)

        if erros:
            await update.message.reply_text("\n\n".join(erros))

    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {e}")


# ============================================================
# TESTE
# ============================================================

async def teste(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        dados_medidas = []
        total_geral = 0

        for _ in range(50):
            h = round(random.uniform(0.3, 2.0), 2)
            w = round(random.uniform(0.3, 2.0), 2)
            q = random.randint(1, 10)
            preco = random.choice([89, 90, 100, 120])

            area = h * w * q
            total = area * preco
            total_geral += total

            dados_medidas.append({
                "medida": f"{h}x{w}",
                "quantidade": q,
                "preco_m2": preco,
                "area": area,
                "total": total
            })

        dados = {
            "data": datetime.now().strftime("%d/%m/%Y"),
            "itens_medida": dados_medidas,
            "itens_produto": []
        }

        caminho_pdf = "teste.pdf"
        criar_pdf_dados(dados, caminho_pdf)

        with open(caminho_pdf, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename="teste.pdf")
            )

        await update.message.reply_text(
            f"✅ Teste gerado\n💰 R$ {total_geral:.2f}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ============================================================
# ALTERAR CONFIG
# ============================================================

async def alterar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        texto = update.message.text.strip()
        comando = texto[len("!alterar"):].strip()

        if not comando:
            await update.message.reply_text("Use: !alterar campo valor")
            return

        partes = comando.split(" ", 1)
        campo = partes[0].lower()
        valor = partes[1] if len(partes) > 1 else ""

        config = carregar_config()
        config[campo] = valor
        salvar_config(config)

        await update.message.reply_text("✅ Atualizado!")

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ============================================================
# CONFIG
# ============================================================

async def config(update: Update, context: ContextTypes.DEFAULT_TYPE):

    dados = carregar_config()

    await update.message.reply_text(
        f"Nome: {dados.get('nome')}\n"
        f"Sub: {dados.get('subtitulo')}\n"
        f"End: {dados.get('endereco')}\n"
        f"Tel: {dados.get('telefone')}\n"
        f"Insta: {dados.get('instagram')}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("teste", teste))

    app.add_handler(MessageHandler(filters.Regex(r"^!alterar"), alterar))
    app.add_handler(MessageHandler(filters.Regex(r"^!config$"), config))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar))

    print("🤖 Rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()

