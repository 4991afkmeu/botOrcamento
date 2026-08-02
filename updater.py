import json
import os
import sys
import urllib.request
import subprocess
import time


# ============================================================
# CONFIGURAÇÃO
# ============================================================

GITHUB_USER = "4991afkmeu"
GITHUB_REPO = "botOrcamento"
GITHUB_BRANCH = "main"

VERSION_FILE = "version.json"

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

VERSION_PATH = os.path.join(
    BASE_DIR,
    VERSION_FILE
)

URL_VERSION = (
    f"https://raw.githubusercontent.com/"
    f"{GITHUB_USER}/{GITHUB_REPO}/"
    f"{GITHUB_BRANCH}/{VERSION_FILE}"
)


# ============================================================
# VERSÃO LOCAL
# ============================================================

def carregar_versao_local():

    try:

        with open(
            VERSION_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            dados = json.load(f)

        return dados.get(
            "version",
            "0.0.0"
        )

    except Exception as e:

        print(
            f"⚠️ Erro ao ler versão local: {e}"
        )

        return "0.0.0"


# ============================================================
# VERSÃO DO GITHUB
# ============================================================

def carregar_versao_github():

    try:

        # Evita cache do GitHub
        url = (
            URL_VERSION
            + "?t="
            + str(time.time())
        )

        with urllib.request.urlopen(
            url,
            timeout=10
        ) as resposta:

            dados = json.loads(
                resposta.read().decode("utf-8")
            )

        return dados.get(
            "version",
            "0.0.0"
        )

    except Exception as e:

        print(
            "⚠️ Não foi possível verificar "
            f"a versão do GitHub: {e}"
        )

        return None


# ============================================================
# CONVERTER VERSÃO
# ============================================================

def converter_versao(versao):

    try:

        partes = versao.split(".")

        return tuple(
            int(x)
            for x in partes
        )

    except Exception:

        return (0, 0, 0)


# ============================================================
# VERIFICAR ATUALIZAÇÃO
# ============================================================

def existe_atualizacao(
    versao_local,
    versao_remota
):

    if not versao_remota:
        return False

    return (
        converter_versao(versao_remota)
        >
        converter_versao(versao_local)
    )


# ============================================================
# ATUALIZAR PELO GIT
# ============================================================

def atualizar():

    print()
    print("🔄 Baixando atualização...")
    print()

    resultado = subprocess.run(
        [
            "git",
            "pull",
            "origin",
            GITHUB_BRANCH
        ],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    if resultado.stdout:

        print(
            resultado.stdout
        )

    if resultado.returncode != 0:

        print(
            "❌ Erro ao executar git pull:"
        )

        if resultado.stderr:

            print(
                resultado.stderr
            )

        return False

    print(
        "✅ Git pull concluído."
    )

    return True


# ============================================================
# VERIFICAR VERSÃO APÓS ATUALIZAÇÃO
# ============================================================

def verificar_atualizacao():

    versao_nova = carregar_versao_local()

    print(
        f"📦 Versão instalada agora: "
        f"{versao_nova}"
    )

    return versao_nova


# ============================================================
# INICIAR BOT
# ============================================================

def iniciar_bot():

    bot_path = os.path.join(
        BASE_DIR,
        "bot.py"
    )

    if not os.path.exists(bot_path):

        print(
            "❌ bot.py não encontrado!"
        )

        return

    print()
    print(
        "🤖 Iniciando bot..."
    )

    subprocess.Popen(
        [
            sys.executable,
            bot_path
        ],
        cwd=BASE_DIR
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 55)
    print(
        "       LUCAS FILM - ATUALIZADOR"
    )
    print("=" * 55)
    print()

    # --------------------------------------------------------
    # Versão instalada
    # --------------------------------------------------------

    versao_local = carregar_versao_local()

    print(
        f"📌 Versão instalada: "
        f"{versao_local}"
    )

    # --------------------------------------------------------
    # Versão GitHub
    # --------------------------------------------------------

    versao_remota = carregar_versao_github()

    if versao_remota:

        print(
            f"🌐 Versão no GitHub: "
            f"{versao_remota}"
        )

    else:

        print(
            "⚠️ Não foi possível obter "
            "a versão do GitHub."
        )

    # --------------------------------------------------------
    # Comparação
    # --------------------------------------------------------

    if existe_atualizacao(
        versao_local,
        versao_remota
    ):

        print()
        print(
            "🆕 NOVA VERSÃO ENCONTRADA!"
        )

        print(
            f"   {versao_local} "
            f"→ "
            f"{versao_remota}"
        )

        # ----------------------------------------------------
        # Atualizar
        # ----------------------------------------------------

        sucesso = atualizar()

        if sucesso:

            print()
            print(
                "🔍 Verificando versão instalada..."
            )

            versao_depois = (
                verificar_atualizacao()
            )

            # ------------------------------------------------
            # Confirmação
            # ------------------------------------------------

            if (
                versao_remota
                and
                versao_depois == versao_remota
            ):

                print(
                    "✅ Atualização confirmada!"
                )

            else:

                print(
                    "⚠️ ATENÇÃO:"
                )

                print(
                    "O Git informou que a atualização "
                    "foi concluída, mas a versão local "
                    "não corresponde à versão do GitHub."
                )

                print(
                    f"Esperada: {versao_remota}"
                )

                print(
                    f"Encontrada: {versao_depois}"
                )

    else:

        print()
        print(
            "✅ Programa já está atualizado."
        )

    # --------------------------------------------------------
    # Pequena pausa
    # --------------------------------------------------------

    time.sleep(1)

    # --------------------------------------------------------
    # Iniciar bot
    # --------------------------------------------------------

    iniciar_bot()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    main()