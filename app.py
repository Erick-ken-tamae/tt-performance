import os
from functools import wraps
from io import BytesIO

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    flash,
    session,
    url_for,
    send_file
)

from openpyxl import Workbook

from openpyxl.styles import (
    Font,
    PatternFill,
    Border,
    Side,
    Alignment
)

from openpyxl.chart import (
    BarChart,
    PieChart,
    Reference
)

from openpyxl.chart.label import DataLabelList

from openpyxl.formatting.rule import DataBarRule

from openpyxl.worksheet.table import (
    Table,
    TableStyleInfo
)

from openpyxl.utils import get_column_letter


from models.partida import (
    cadastrar_partida,
    listar_partida,
    buscar_partida,
    finalizar_partida,
    excluir_partida,
    salvar_jogada,
    estatistica_partida,
    listar_sets,
    salvar_set,
    listar_historico_usuario,
    listar_todas_partidas
)

from models.jogada import listar_jogadas

from models.usuario import (
    criar_usuario,
    validar_login,
    email_existe,
    listar_usuarios,
    contar_usuarios,
    excluir_usuario,
    buscar_usuario_por_id
)


# ============================================================
# CONFIGURAÇÃO DO FLASK
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "tt_performance_secret_key"
)


# ============================================================
# DECORATORS
# ============================================================

def login_required(f):
    """
    Decorator para proteger rotas que exigem login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "usuario_id" not in session:
            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator para proteger rotas
    que exigem administrador.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "usuario_id" not in session:
            return redirect(
                url_for("login")
            )

        if session.get("usuario_tipo") != "Administrador":

            flash(
                "Acesso restrito a administradores.",
                "error"
            )

            return redirect(
                url_for("inicio")
            )

        return f(*args, **kwargs)

    return decorated_function


def eh_dono_da_partida(partida):
    """
    Verifica se a partida pertence ao usuário logado.

    Administradores possuem acesso a todas as partidas.
    """

    if partida is None:
        return False

    if session.get("usuario_tipo") == "Administrador":
        return True

    return (
        partida.get("usuario_id")
        == session.get("usuario_id")
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = validar_login(
            email,
            senha
        )

        if usuario:

            session["usuario_id"] = usuario["id"]

            session["usuario_nome"] = usuario["nome"]

            session["usuario_tipo"] = usuario["tipo"]

            flash(
                "Login realizado com sucesso!",
                "success"
            )

            # Administrador vai para o painel administrativo
            if usuario["tipo"] == "Administrador":

                return redirect(
                    url_for("admin")
                )

            # Jogadores/Treinadores
            # vão para a página inicial
            return redirect(
                url_for("inicio")
            )

        else:

            flash(
                "Email ou senha incorretos.",
                "error"
            )

            return redirect(
                url_for("login")
            )

    return render_template(
        "login.html"
    )


# ============================================================
# CADASTRO
# ============================================================

@app.route(
    "/cadastro",
    methods=["GET", "POST"]
)
def cadastro():

    if request.method == "POST":

        nome = request.form.get(
            "nome"
        )

        email = request.form.get(
            "email"
        )

        senha = request.form.get(
            "senha"
        )

        confirmar_senha = request.form.get(
            "confirmar_senha"
        )

        tipo = request.form.get(
            "tipo",
            "Jogador"
        )

        # ----------------------------------------------------
        # CONFIRMAR SENHA
        # ----------------------------------------------------

        if senha != confirmar_senha:

            flash(
                "As senhas não coincidem.",
                "error"
            )

            return redirect(
                url_for("cadastro")
            )

        # ----------------------------------------------------
        # VERIFICAR EMAIL
        # ----------------------------------------------------

        if email_existe(email):

            flash(
                "Este email já está cadastrado.",
                "error"
            )

            return redirect(
                url_for("cadastro")
            )

        # ----------------------------------------------------
        # CRIAR USUÁRIO
        # ----------------------------------------------------

        criar_usuario(
            nome,
            email,
            senha,
            tipo
        )

        flash(
            "Conta criada com sucesso! Faça login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "cadastro.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# PÁGINA INICIAL
# ============================================================

@app.route("/")
@login_required
def inicio():

    partidas = listar_partida(
        session["usuario_id"]
    )

    return render_template(
        "partida.html",
        partidas=partidas
    )


# ============================================================
# SALVAR PARTIDA
# ============================================================

@app.route(
    "/salvar_partida",
    methods=["POST"]
)
@login_required
def salvar_partida():

    nome = request.form["nome"]

    clube = request.form["clube"]

    adversario = request.form["adversario"]

    clube_adversario = request.form[
        "clube_adversario"
    ]

    data_partida = request.form[
        "data_partida"
    ]

    quantidade_sets = int(
        request.form["melhor_de"]
    )

    cadastrar_partida(
        session["usuario_id"],
        nome,
        clube,
        adversario,
        clube_adversario,
        data_partida,
        quantidade_sets
    )

    return redirect("/")


# ============================================================
# INICIAR PARTIDA
# ============================================================

@app.route(
    "/iniciar_partida/<id>"
)
@login_required
def iniciar_partida(id):

    partida = buscar_partida(id)

    if not eh_dono_da_partida(partida):

        flash(
            "Você não tem acesso a essa partida.",
            "error"
        )

        return redirect("/")

    if partida["status"] == "FINALIZADA":

        return redirect(
            f"/historico/{id}"
        )

    return render_template(
        "iniciar_partida.html",
        partida=partida
    )


# ============================================================
# FINALIZAR PARTIDA
# ============================================================

@app.route(
    "/finalizar_partida",
    methods=["POST"]
)
@login_required
def finalizar():

    dados = request.get_json()

    partida = buscar_partida(
        dados["partida_id"]
    )

    if not eh_dono_da_partida(partida):

        return jsonify({
            "erro": "Acesso negado"
        }), 403

    finalizar_partida(
        dados["partida_id"],
        dados["vencedor"],
        dados["sets_jogador"],
        dados["sets_adversario"]
    )

    return jsonify({
        "mensagem": "Partida finalizada"
    })


# ============================================================
# EXCLUIR PARTIDA
# ============================================================

@app.route(
    "/excluir_partida/<id>"
)
@login_required
def excluir(id):

    partida = buscar_partida(id)

    if not eh_dono_da_partida(partida):

        flash(
            "Você não tem acesso a essa partida.",
            "error"
        )

        return redirect("/")

    excluir_partida(id)

    flash(
        "Partida excluída com sucesso!",
        "success"
    )

    return redirect("/")


# ============================================================
# HISTÓRICO GERAL
# ============================================================

@app.route("/historico")
@login_required
def historico_lista():

    partidas = listar_historico_usuario(
        session["usuario_id"]
    )

    return render_template(
        "historico_lista.html",
        partidas=partidas
    )


# ============================================================
# HISTÓRICO DE UMA PARTIDA
# ============================================================

@app.route(
    "/historico/<id>"
)
@login_required
def historico(id):

    partida = buscar_partida(id)

    if not eh_dono_da_partida(partida):

        flash(
            "Você não tem acesso a essa partida.",
            "error"
        )

        return redirect("/")

    sets = listar_sets(id)

    print(
        "SETS:",
        sets
    )

    return render_template(
        "historico.html",
        partida=partida,
        sets=sets
    )


# ============================================================
# SALVAR JOGADA
# ============================================================

@app.route(
    "/salvar_jogada",
    methods=["POST"]
)
@login_required
def salvar_jogada_api():

    dados = request.get_json()

    partida = buscar_partida(
        dados["partida_id"]
    )

    if not eh_dono_da_partida(partida):

        return jsonify({
            "erro": "Acesso negado"
        }), 403

    salvar_jogada(
        dados["partida_id"],
        dados["set_numero"],
        dados["jogador"],
        dados["vencedor_ponto"],
        dados["tecnica"],
        dados["resultado"]
    )

    return jsonify({
        "status": "ok"
    })


# ============================================================
# SALVAR SET
# ============================================================

@app.route(
    "/salvar_set",
    methods=["POST"]
)
@login_required
def salvar_set_api():

    dados = request.get_json()

    partida = buscar_partida(
        dados["partida_id"]
    )

    if not eh_dono_da_partida(partida):

        return jsonify({
            "erro": "Acesso negado"
        }), 403

    print(
        "DADOS RECEBIDOS:",
        dados
    )

    salvar_set(
        dados["partida_id"],
        dados["numero_set"],
        dados["pontos_jogador"],
        dados["pontos_adversario"],
        dados["vencedor"]
    )

    return jsonify({
        "status": "ok"
    })


# ============================================================
# ANÁLISE
# ============================================================

@app.route(
    "/analise/<id>"
)
@login_required
def analise(id):

    partida = buscar_partida(id)

    if not eh_dono_da_partida(partida):

        flash(
            "Você não tem acesso a essa partida.",
            "error"
        )

        return redirect("/")

    estatistica = estatistica_partida(id)

    sets = listar_sets(id)

    jogadas = listar_jogadas(id)

    # --------------------------------------------------------
    # ESTATÍSTICAS DO JOGADOR
    # --------------------------------------------------------

    estatistica_jogador = [
        item
        for item in estatistica
        if item["jogador"]
        == partida["nome_jogador"]
    ]

    # --------------------------------------------------------
    # ESTATÍSTICAS DO ADVERSÁRIO
    # --------------------------------------------------------

    estatistica_adversario = [
        item
        for item in estatistica
        if item["jogador"]
        == partida["nome_adversario"]
    ]

    # --------------------------------------------------------
    # CALCULAR RESUMO
    # --------------------------------------------------------

    def calcular_resumo(lista):

        total_acertos = sum(
            item["acertos"]
            for item in lista
        )

        total_erros = sum(
            item["erros"]
            for item in lista
        )

        total_jogadas = (
            total_acertos
            + total_erros
        )

        if total_jogadas > 0:

            aproveitamento = round(
                (
                    total_acertos
                    / total_jogadas
                ) * 100,
                2
            )

        else:

            aproveitamento = 0

        if lista:

            melhor = max(
                lista,
                key=lambda item:
                    item["aproveitamento"]
            )["tecnica"]

            pior = min(
                lista,
                key=lambda item:
                    item["aproveitamento"]
            )["tecnica"]

            mais_utilizada = max(
                lista,
                key=lambda item:
                    item["acertos"]
                    + item["erros"]
            )["tecnica"]

        else:

            melhor = "-"
            pior = "-"
            mais_utilizada = "-"

        return {
            "total_acertos":
                total_acertos,

            "total_erros":
                total_erros,

            "aproveitamento":
                aproveitamento,

            "melhor_tecnica":
                melhor,

            "pior_tecnica":
                pior,

            "tecnica_mais_utilizada":
                mais_utilizada
        }

    resumo_jogador = calcular_resumo(
        estatistica_jogador
    )

    resumo_adversario = calcular_resumo(
        estatistica_adversario
    )

    return render_template(
        "analise.html",

        partida=partida,

        sets=sets,

        jogadas=jogadas,

        estatistica_jogador=
            estatistica_jogador,

        estatistica_adversario=
            estatistica_adversario,

        resumo_jogador=
            resumo_jogador,

        resumo_adversario=
            resumo_adversario
    )


# ============================================================
# ADMINISTRAÇÃO
# ============================================================

@app.route("/admin")
@admin_required
def admin():

    usuarios = listar_usuarios()

    total_usuarios = contar_usuarios()

    return render_template(
        "admin.html",

        usuarios=usuarios,

        total_usuarios=total_usuarios
    )


# ============================================================
# LISTA DE DESEMPENHO
# ============================================================

@app.route(
    "/admin/desempenho"
)
@admin_required
def admin_desempenho():

    partidas = listar_todas_partidas()

    return render_template(
        "admin_desempenho.html",
        partidas=partidas
    )


# ============================================================
# DESEMPENHO DE UMA PARTIDA
# ============================================================

@app.route(
    "/admin/desempenho/<id>"
)
@admin_required
def admin_desempenho_partida(id):

    partida = buscar_partida(id)

    if not partida:

        flash(
            "Partida não encontrada.",
            "error"
        )

        return redirect(
            url_for(
                "admin_desempenho"
            )
        )

    # --------------------------------------------------------
    # BUSCAR DADOS
    # --------------------------------------------------------

    estatistica = estatistica_partida(id)

    sets = listar_sets(id)

    jogadas = listar_jogadas(id)

    # --------------------------------------------------------
    # JOGADOR
    # --------------------------------------------------------

    estatistica_jogador = [
        item
        for item in estatistica
        if item["jogador"]
        == partida["nome_jogador"]
    ]

    # --------------------------------------------------------
    # ADVERSÁRIO
    # --------------------------------------------------------

    estatistica_adversario = [
        item
        for item in estatistica
        if item["jogador"]
        == partida["nome_adversario"]
    ]

    # --------------------------------------------------------
    # CALCULAR RESUMO
    # --------------------------------------------------------

    def calcular_resumo(lista):

        total_acertos = sum(
            item["acertos"]
            for item in lista
        )

        total_erros = sum(
            item["erros"]
            for item in lista
        )

        total_jogadas = (
            total_acertos
            + total_erros
        )

        if total_jogadas > 0:

            aproveitamento = round(
                (
                    total_acertos
                    / total_jogadas
                ) * 100,
                2
            )

        else:

            aproveitamento = 0

        if lista:

            melhor_tecnica = max(
                lista,
                key=lambda item:
                    item["aproveitamento"]
            )["tecnica"]

            pior_tecnica = min(
                lista,
                key=lambda item:
                    item["aproveitamento"]
            )["tecnica"]

            tecnica_mais_utilizada = max(
                lista,
                key=lambda item:
                    item["acertos"]
                    + item["erros"]
            )["tecnica"]

        else:

            melhor_tecnica = "-"
            pior_tecnica = "-"
            tecnica_mais_utilizada = "-"

        return {
            "total_acertos":
                total_acertos,

            "total_erros":
                total_erros,

            "total_jogadas":
                total_jogadas,

            "aproveitamento":
                aproveitamento,

            "melhor_tecnica":
                melhor_tecnica,

            "pior_tecnica":
                pior_tecnica,

            "tecnica_mais_utilizada":
                tecnica_mais_utilizada
        }

    resumo_jogador = calcular_resumo(
        estatistica_jogador
    )

    resumo_adversario = calcular_resumo(
        estatistica_adversario
    )

    return render_template(
        "admin_desempenho_partida.html",

        partida=partida,

        sets=sets,

        jogadas=jogadas,

        estatistica_jogador=
            estatistica_jogador,

        estatistica_adversario=
            estatistica_adversario,

        resumo_jogador=
            resumo_jogador,

        resumo_adversario=
            resumo_adversario
    )


# ============================================================
# EXPORTAR EXCEL
# ============================================================

@app.route(
    "/admin/desempenho/<id>/excel"
)
@admin_required
def exportar_excel_partida(id):

    # ========================================================
    # BUSCAR PARTIDA
    # ========================================================

    partida = buscar_partida(id)

    if not partida:

        flash(
            "Partida não encontrada.",
            "error"
        )

        return redirect(
            url_for(
                "admin_desempenho"
            )
        )

    # ========================================================
    # BUSCAR DADOS
    # ========================================================

    estatistica = estatistica_partida(id)

    sets = listar_sets(id)

    jogadas = listar_jogadas(id)

    # ========================================================
    # NOMES
    # ========================================================

    jogador_nome = partida.get(
        "nome_jogador",
        "Jogador"
    )

    adversario_nome = partida.get(
        "nome_adversario",
        "Adversário"
    )

    # ========================================================
    # SEPARAR ESTATÍSTICAS
    # ========================================================

    estatistica_jogador = [
        item
        for item in estatistica
        if item.get("jogador")
        == jogador_nome
    ]

    estatistica_adversario = [
        item
        for item in estatistica
        if item.get("jogador")
        == adversario_nome
    ]

    # ========================================================
    # RESUMO
    # ========================================================

    def calcular_resumo_excel(lista):

        acertos = sum(
            item.get("acertos", 0)
            for item in lista
        )

        erros = sum(
            item.get("erros", 0)
            for item in lista
        )

        total = (
            acertos
            + erros
        )

        if total > 0:

            aproveitamento = round(
                (acertos / total) * 100,
                2
            )

        else:

            aproveitamento = 0

        return {
            "acertos": acertos,
            "erros": erros,
            "total": total,
            "aproveitamento":
                aproveitamento
        }

    resumo_jogador = calcular_resumo_excel(
        estatistica_jogador
    )

    resumo_adversario = calcular_resumo_excel(
        estatistica_adversario
    )

    # ========================================================
    # CRIAR WORKBOOK
    # ========================================================

    wb = Workbook()

    ws = wb.active

    ws.title = "Dashboard"

    # ========================================================
    # CORES
    # ========================================================

    AZUL = "1565C0"

    AZUL_ESCURO = "0D47A1"

    AZUL_CLARO = "E3F2FD"

    VERDE = "2E7D32"

    VERDE_CLARO = "E8F5E9"

    VERMELHO = "C62828"

    VERMELHO_CLARO = "FFEBEE"

    ROXO = "6A1B9A"

    ROXO_CLARO = "F3E5F5"

    LARANJA = "EF6C00"

    CINZA = "F5F7FA"

    CINZA_ESCURO = "455A64"

    BRANCO = "FFFFFF"

    PRETO = "263238"

    # ========================================================
    # BORDA
    # ========================================================

    BORDA = Side(
        style="thin",
        color="D9E1E8"
    )

    BORDA_LEVE = Border(
        left=BORDA,
        right=BORDA,
        top=BORDA,
        bottom=BORDA
    )

    # ========================================================
    # CONFIGURAÇÃO DASHBOARD
    # ========================================================
    #
    # Layout em COLUNA ÚNICA (6 colunas), com um jogador
    # embaixo do outro. Assim:
    #   - Celular: cabe na tela na vertical, sem rolar de lado.
    #   - Tablet/PC: fica centralizado e legível.
    # Sem painéis congelados (no celular ocupariam a tela toda).
    # ========================================================

    ws.sheet_view.showGridLines = False

    ws.sheet_properties.tabColor = AZUL

    ws.sheet_view.zoomScale = 100

    ws.page_setup.orientation = "portrait"

    ws.page_setup.fitToWidth = 1

    ws.page_setup.fitToHeight = 0

    ws.sheet_properties.pageSetUpPr.fitToPage = True

    ULTIMA_COLUNA = 6  # A:F

    # ========================================================
    # TÍTULO
    # ========================================================

    ws.merge_cells("A1:F2")

    ws["A1"] = "TT PERFORMANCE"

    ws["A1"].font = Font(bold=True, size=22, color=BRANCO)

    ws["A1"].alignment = Alignment(
        horizontal="center",
        vertical="center"
    )

    for row in ws["A1:F2"]:
        for cell in row:
            cell.fill = PatternFill("solid", fgColor=AZUL_ESCURO)

    ws.row_dimensions[1].height = 26
    ws.row_dimensions[2].height = 26

    # ========================================================
    # SUBTÍTULO
    # ========================================================

    ws.merge_cells("A3:F3")

    ws["A3"] = (
        "Relatório de desempenho • "
        f"{jogador_nome} x "
        f"{adversario_nome}"
    )

    ws["A3"].font = Font(size=11, italic=True, color=CINZA_ESCURO)

    ws["A3"].alignment = Alignment(
        horizontal="center",
        vertical="center",
        wrap_text=True
    )

    ws.row_dimensions[3].height = 34

    # ========================================================
    # SEÇÃO (um jogador) – reutilizada para os dois lados
    # ========================================================

    def criar_card(linha, inicio_coluna, titulo, valor, cor):

        fim_coluna = inicio_coluna + 1

        ws.merge_cells(
            start_row=linha,
            start_column=inicio_coluna,
            end_row=linha,
            end_column=fim_coluna
        )

        ws.merge_cells(
            start_row=linha + 1,
            start_column=inicio_coluna,
            end_row=linha + 2,
            end_column=fim_coluna
        )

        titulo_cell = ws.cell(row=linha, column=inicio_coluna)

        valor_cell = ws.cell(row=linha + 1, column=inicio_coluna)

        titulo_cell.value = titulo

        valor_cell.value = valor

        titulo_cell.font = Font(bold=True, size=10, color=BRANCO)

        titulo_cell.fill = PatternFill("solid", fgColor=cor)

        titulo_cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

        valor_cell.font = Font(bold=True, size=22, color=PRETO)

        valor_cell.fill = PatternFill("solid", fgColor=BRANCO)

        valor_cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

        for r in range(linha, linha + 3):
            for c in range(inicio_coluna, fim_coluna + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = BORDA_LEVE
                if r == linha:
                    cell.fill = PatternFill("solid", fgColor=cor)

    def criar_secao(linha, nome, resumo, coluna_dados):
        """
        Monta um bloco completo (nome, cards, aproveitamento,
        gráfico de barras e pizza) começando em 'linha'.
        Retorna a próxima linha livre.

        coluna_dados: coluna inicial (ocultas) dos dados
        auxiliares dos gráficos.
        """

        col_rot = coluna_dados
        col_val = coluna_dados + 1

        # ---- Nome ------------------------------------------
        ws.merge_cells(
            start_row=linha, start_column=1,
            end_row=linha, end_column=ULTIMA_COLUNA
        )

        ws.cell(row=linha, column=1).value = nome

        ws.cell(row=linha, column=1).font = Font(
            bold=True, size=16, color=BRANCO
        )

        ws.cell(row=linha, column=1).alignment = Alignment(
            horizontal="center", vertical="center"
        )

        for c in range(1, ULTIMA_COLUNA + 1):
            ws.cell(row=linha, column=c).fill = PatternFill(
                "solid", fgColor=AZUL
            )

        ws.row_dimensions[linha].height = 30

        # ---- Cards -----------------------------------------
        linha_cards = linha + 2

        ws.row_dimensions[linha_cards].height = 22
        ws.row_dimensions[linha_cards + 1].height = 26
        ws.row_dimensions[linha_cards + 2].height = 26

        criar_card(linha_cards, 1, "ACERTOS", resumo["acertos"], VERDE)
        criar_card(linha_cards, 3, "ERROS", resumo["erros"], VERMELHO)
        criar_card(linha_cards, 5, "JOGADAS", resumo["total"], AZUL)

        # ---- Aproveitamento --------------------------------
        linha_aprov = linha_cards + 4

        ws.merge_cells(
            start_row=linha_aprov, start_column=1,
            end_row=linha_aprov, end_column=3
        )

        ws.merge_cells(
            start_row=linha_aprov, start_column=4,
            end_row=linha_aprov, end_column=6
        )

        ws.cell(row=linha_aprov, column=1).value = "Aproveitamento"

        ws.cell(row=linha_aprov, column=1).font = Font(
            bold=True, size=13, color=ROXO
        )

        ws.cell(row=linha_aprov, column=1).alignment = Alignment(
            horizontal="right", vertical="center"
        )

        ws.cell(row=linha_aprov, column=4).value = (
            resumo["aproveitamento"] / 100
        )

        ws.cell(row=linha_aprov, column=4).number_format = "0.0%"

        ws.cell(row=linha_aprov, column=4).font = Font(
            bold=True, size=16, color=ROXO
        )

        ws.cell(row=linha_aprov, column=4).alignment = Alignment(
            horizontal="left", vertical="center", indent=1
        )

        for c in range(1, ULTIMA_COLUNA + 1):
            ws.cell(row=linha_aprov, column=c).fill = PatternFill(
                "solid", fgColor=ROXO_CLARO
            )

        ws.row_dimensions[linha_aprov].height = 30

        # ---- Dados auxiliares (colunas ocultas) -------------
        ws.cell(row=1, column=col_rot).value = "Indicador"
        ws.cell(row=1, column=col_val).value = nome

        ws.cell(row=2, column=col_rot).value = "Acertos"
        ws.cell(row=2, column=col_val).value = resumo["acertos"]

        ws.cell(row=3, column=col_rot).value = "Erros"
        ws.cell(row=3, column=col_val).value = resumo["erros"]

        ws.cell(row=4, column=col_rot).value = "Jogadas"
        ws.cell(row=4, column=col_val).value = resumo["total"]

        ws.cell(row=7, column=col_rot).value = "Resultado"
        ws.cell(row=7, column=col_val).value = "Quantidade"

        ws.cell(row=8, column=col_rot).value = "Acertos"
        ws.cell(row=8, column=col_val).value = resumo["acertos"]

        ws.cell(row=9, column=col_rot).value = "Erros"
        ws.cell(row=9, column=col_val).value = resumo["erros"]

        # ---- Gráfico de barras -----------------------------
        barras = BarChart()
        barras.type = "col"
        barras.style = 10
        barras.title = f"Desempenho - {nome}"

        # openpyxl >= 3.1 esconde os eixos por padrão
        barras.x_axis.delete = False
        barras.y_axis.delete = False

        # OS DADOS ESTÃO EM COLUNAS OCULTAS: sem isto o Excel
        # deixa o gráfico VAZIO ("Área do Gráfico").
        barras.visible_cells_only = False

        barras.legend = None

        barras.dataLabels = DataLabelList()
        barras.dataLabels.showVal = True
        barras.dataLabels.showSerName = False
        barras.dataLabels.showCatName = False
        barras.dataLabels.showLegendKey = False

        barras.add_data(
            Reference(
                ws, min_col=col_val, max_col=col_val,
                min_row=1, max_row=4
            ),
            titles_from_data=True
        )

        barras.set_categories(
            Reference(
                ws, min_col=col_rot,
                min_row=2, max_row=4
            )
        )

        barras.height = 7.5
        barras.width = 14.6

        linha_barras = linha_aprov + 2

        ws.add_chart(barras, f"A{linha_barras}")

        # ---- Pizza -----------------------------------------
        pizza = PieChart()
        pizza.title = f"Acertos x Erros - {nome}"
        pizza.visible_cells_only = False

        pizza.add_data(
            Reference(
                ws, min_col=col_val,
                min_row=7, max_row=9
            ),
            titles_from_data=True
        )

        pizza.set_categories(
            Reference(
                ws, min_col=col_rot,
                min_row=8, max_row=9
            )
        )

        pizza.dataLabels = DataLabelList()
        pizza.dataLabels.showPercent = True
        pizza.dataLabels.showVal = False
        pizza.dataLabels.showSerName = False
        pizza.dataLabels.showCatName = False
        pizza.dataLabels.showLegendKey = False
        pizza.legend.position = "b"

        pizza.height = 7.5
        pizza.width = 14.6

        linha_pizza = linha_barras + 16

        ws.add_chart(pizza, f"A{linha_pizza}")

        # próxima linha livre (com um respiro)
        return linha_pizza + 17

    # ========================================================
    # MONTAR: JOGADOR e, logo abaixo, ADVERSÁRIO
    # ========================================================

    proxima = criar_secao(
        5,
        jogador_nome,
        resumo_jogador,
        14   # N:O
    )

    criar_secao(
        proxima,
        adversario_nome,
        resumo_adversario,
        17   # Q:R
    )

    # ========================================================
    # ESCONDER DADOS AUXILIARES
    # ========================================================

    for coluna in ["N", "O", "P", "Q", "R", "S"]:
        ws.column_dimensions[coluna].hidden = True


    # ========================================================
    # ABA TÉCNICAS
    # ========================================================

    ws_tecnicas = wb.create_sheet(
        "Técnicas"
    )

    ws_tecnicas.sheet_view.showGridLines = False

    ws_tecnicas.freeze_panes = "A2"

    ws_tecnicas.sheet_properties.tabColor = (
        VERDE
    )

    cabecalho_tecnicas = [
        "Jogador",
        "Técnica",
        "Acertos",
        "Erros",
        "Total",
        "Aproveitamento"
    ]

    for coluna, nome in enumerate(
        cabecalho_tecnicas,
        start=1
    ):

        cell = ws_tecnicas.cell(
            row=1,
            column=coluna
        )

        cell.value = nome

        cell.font = Font(
            bold=True,
            color=BRANCO
        )

        cell.fill = PatternFill(
            "solid",
            fgColor=AZUL_ESCURO
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    # ========================================================
    # INSERIR TÉCNICAS
    # ========================================================

    for item in estatistica:

        acertos = item.get(
            "acertos",
            0
        )

        erros = item.get(
            "erros",
            0
        )

        total = (
            acertos
            + erros
        )

        aproveitamento = (
            acertos / total
            if total > 0
            else 0
        )

        ws_tecnicas.append([
            item.get(
                "jogador",
                ""
            ),

            item.get(
                "tecnica",
                ""
            ),

            acertos,

            erros,

            total,

            aproveitamento
        ])

    # ========================================================
    # FORMATAR TÉCNICAS
    # ========================================================

    for row in range(
        2,
        ws_tecnicas.max_row + 1
    ):

        ws_tecnicas.cell(
            row=row,
            column=6
        ).number_format = "0.00%"

        for coluna in range(
            1,
            7
        ):

            ws_tecnicas.cell(
                row=row,
                column=coluna
            ).border = BORDA_LEVE

    # ========================================================
    # BARRAS DE APROVEITAMENTO
    # ========================================================

    if ws_tecnicas.max_row >= 2:

        ws_tecnicas.conditional_formatting.add(
            f"F2:F{ws_tecnicas.max_row}",

            DataBarRule(
                start_type="num",
                start_value=0,
                end_type="num",
                end_value=1,
                color=AZUL,
                showValue=True
            )
        )

    # ========================================================
    # TABELA TÉCNICAS
    # ========================================================

    if ws_tecnicas.max_row >= 2:

        tabela_tecnicas = Table(
            displayName="TabelaTecnicas",
            ref=(
                "A1:F"
                f"{ws_tecnicas.max_row}"
            )
        )

        estilo_tecnicas = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False
        )

        tabela_tecnicas.tableStyleInfo = (
            estilo_tecnicas
        )

        ws_tecnicas.add_table(
            tabela_tecnicas
        )

    # ========================================================
    # TÉCNICAS JOGADOR
    # ========================================================

    tecnicas_jogador = [
        item
        for item in estatistica
        if item.get("jogador")
        == jogador_nome
    ]

    # ========================================================
    # TÉCNICAS ADVERSÁRIO
    # ========================================================

    tecnicas_adversario = [
        item
        for item in estatistica
        if item.get("jogador")
        == adversario_nome
    ]

    # ========================================================
    # GRÁFICOS DE TÉCNICAS (abaixo da tabela, um sobre o outro)
    # ========================================================
    #
    # Ficam abaixo da tabela (e não ao lado) para não obrigar
    # rolagem horizontal no celular. Os dados auxiliares ficam
    # em colunas ocultas e os gráficos usam
    # visible_cells_only = False para continuarem aparecendo.
    # ========================================================

    fim_tabela_tecnicas = ws_tecnicas.max_row

    linha_grafico = fim_tabela_tecnicas + 3

    def grafico_tecnicas(
        itens,
        nome,
        coluna_base
    ):

        nonlocal linha_grafico

        if not itens:
            return

        ws_tecnicas.cell(
            row=1, column=coluna_base
        ).value = "Técnica"

        ws_tecnicas.cell(
            row=1, column=coluna_base + 1
        ).value = "Acertos"

        ws_tecnicas.cell(
            row=1, column=coluna_base + 2
        ).value = "Erros"

        for indice, item in enumerate(itens, start=2):

            ws_tecnicas.cell(
                row=indice, column=coluna_base
            ).value = item.get("tecnica", "")

            ws_tecnicas.cell(
                row=indice, column=coluna_base + 1
            ).value = item.get("acertos", 0)

            ws_tecnicas.cell(
                row=indice, column=coluna_base + 2
            ).value = item.get("erros", 0)

        ultima = len(itens) + 1

        grafico = BarChart()
        grafico.type = "bar"
        grafico.style = 10
        grafico.title = f"Técnicas - {nome}"
        grafico.x_axis.delete = False
        grafico.y_axis.delete = False
        grafico.visible_cells_only = False
        grafico.legend.position = "b"

        grafico.add_data(
            Reference(
                ws_tecnicas,
                min_col=coluna_base + 1,
                max_col=coluna_base + 2,
                min_row=1,
                max_row=ultima
            ),
            titles_from_data=True
        )

        grafico.set_categories(
            Reference(
                ws_tecnicas,
                min_col=coluna_base,
                min_row=2,
                max_row=ultima
            )
        )

        # altura cresce um pouco com o número de técnicas
        grafico.height = max(8, min(20, 4 + len(itens) * 1.2))
        grafico.width = 16

        ws_tecnicas.add_chart(
            grafico,
            f"A{linha_grafico}"
        )

        # reserva linhas para o próximo gráfico não sobrepor
        linha_grafico += int(grafico.height * 2) + 3

        for k in range(3):
            ws_tecnicas.column_dimensions[
                get_column_letter(coluna_base + k)
            ].hidden = True

    grafico_tecnicas(tecnicas_jogador, jogador_nome, 20)

    grafico_tecnicas(tecnicas_adversario, adversario_nome, 24)


    # ========================================================
    # ABA JOGADAS
    # ========================================================

    ws_jogadas = wb.create_sheet(
        "Jogadas"
    )

    ws_jogadas.sheet_view.showGridLines = False

    ws_jogadas.freeze_panes = "A2"

    ws_jogadas.sheet_properties.tabColor = (
        CINZA_ESCURO
    )

    # ========================================================
    # DESCOBRIR CAMPOS DAS JOGADAS
    # ========================================================

    campos_jogadas = []

    for jogada in jogadas:

        for campo in jogada.keys():

            if (
                campo != "_id"
                and campo not in campos_jogadas
            ):

                campos_jogadas.append(
                    campo
                )

    # ========================================================
    # CABEÇALHO JOGADAS
    # ========================================================

    for coluna, campo in enumerate(
        campos_jogadas,
        start=1
    ):

        cell = ws_jogadas.cell(
            row=1,
            column=coluna
        )

        cell.value = campo

        cell.font = Font(
            bold=True,
            color=BRANCO
        )

        cell.fill = PatternFill(
            "solid",
            fgColor=AZUL_ESCURO
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    # ========================================================
    # DADOS JOGADAS
    # ========================================================

    for linha, jogada in enumerate(
        jogadas,
        start=2
    ):

        for coluna, campo in enumerate(
            campos_jogadas,
            start=1
        ):

            valor = jogada.get(
                campo,
                ""
            )

            ws_jogadas.cell(
                row=linha,
                column=coluna
            ).value = str(valor)

            ws_jogadas.cell(
                row=linha,
                column=coluna
            ).border = BORDA_LEVE

    # ========================================================
    # TABELA JOGADAS
    # ========================================================

    if (
        campos_jogadas
        and ws_jogadas.max_row >= 2
    ):

        ultima_coluna = get_column_letter(
            len(campos_jogadas)
        )

        tabela_jogadas = Table(
            displayName="TabelaJogadas",

            ref=(
                "A1:"
                f"{ultima_coluna}"
                f"{ws_jogadas.max_row}"
            )
        )

        estilo_jogadas = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False
        )

        tabela_jogadas.tableStyleInfo = (
            estilo_jogadas
        )

        ws_jogadas.add_table(
            tabela_jogadas
        )

    # ========================================================
    # ABA SETS
    # ========================================================

    ws_sets = wb.create_sheet(
        "Sets"
    )

    ws_sets.sheet_view.showGridLines = False

    ws_sets.sheet_properties.tabColor = (
        LARANJA
    )

    ws_sets["A1"] = (
        "HISTÓRICO DOS SETS"
    )

    ws_sets["A1"].font = Font(
        bold=True,
        size=18,
        color=BRANCO
    )

    ws_sets["A1"].fill = PatternFill(
        "solid",
        fgColor=AZUL_ESCURO
    )

    # ========================================================
    # CAMPOS DOS SETS
    # ========================================================

    campos_sets = []

    for item in sets:

        for campo in item.keys():

            if (
                campo != "_id"
                and campo not in campos_sets
            ):

                campos_sets.append(
                    campo
                )

    # ========================================================
    # CABEÇALHO SETS
    # ========================================================

    for coluna, campo in enumerate(
        campos_sets,
        start=1
    ):

        cell = ws_sets.cell(
            row=3,
            column=coluna
        )

        cell.value = campo

        cell.font = Font(
            bold=True,
            color=BRANCO
        )

        cell.fill = PatternFill(
            "solid",
            fgColor=AZUL
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    # ========================================================
    # DADOS SETS
    # ========================================================

    for linha, item in enumerate(
        sets,
        start=4
    ):

        for coluna, campo in enumerate(
            campos_sets,
            start=1
        ):

            ws_sets.cell(
                row=linha,
                column=coluna
            ).value = str(
                item.get(
                    campo,
                    ""
                )
            )

            ws_sets.cell(
                row=linha,
                column=coluna
            ).border = BORDA_LEVE

    if not sets:

        ws_sets["A3"] = (
            "Nenhum dado de set registrado."
        )

    # ========================================================
    # AJUSTAR LARGURA DAS COLUNAS
    # ========================================================
    #
    # IMPORTANTE:
    # Não usamos:
    #
    # coluna[0].column_letter
    #
    # porque células mescladas podem ser MergedCell.
    # ========================================================

    for worksheet in wb.worksheets:

        for numero_coluna in range(
            1,
            worksheet.max_column + 1
        ):

            maior = 0

            for numero_linha in range(
                1,
                worksheet.max_row + 1
            ):

                cell = worksheet.cell(
                    row=numero_linha,
                    column=numero_coluna
                )

                # Ignorar células mescladas
                if (
                    cell.__class__.__name__
                    == "MergedCell"
                ):
                    continue

                if cell.value is not None:

                    tamanho = len(
                        str(cell.value)
                    )

                    if tamanho > maior:

                        maior = tamanho

            letra = get_column_letter(
                numero_coluna
            )

            worksheet.column_dimensions[
                letra
            ].width = min(
                max(maior + 3, 12),
                35
            )

    # ========================================================
    # TAMANHO DAS COLUNAS DASHBOARD
    # (layout em coluna única: 6 colunas estreitas, funciona
    #  no celular, no tablet e no PC)
    # ========================================================

    for numero_coluna in range(1, 7):

        ws.column_dimensions[
            get_column_letter(numero_coluna)
        ].width = 13

    # margem lateral pequena para dar respiro no PC/tablet
    ws.sheet_format.defaultRowHeight = 18


    # ========================================================
    # ALINHAMENTO DAS TABELAS
    # ========================================================

    for worksheet in wb.worksheets:

        for row in worksheet.iter_rows():

            for cell in row:

                if cell.value is not None:

                    cell.alignment = Alignment(
                        horizontal=cell.alignment.horizontal,
                        vertical="center",
                        wrap_text=True,
                        indent=cell.alignment.indent
                    )

    # ========================================================
    # SALVAR ARQUIVO NA MEMÓRIA
    # ========================================================

    arquivo = BytesIO()

    wb.save(
        arquivo
    )

    arquivo.seek(0)

    # ========================================================
    # NOME DO ARQUIVO
    # ========================================================

    jogador_arquivo = (
        jogador_nome
        .replace(" ", "_")
        .replace("/", "-")
        .replace("\\", "-")
    )

    adversario_arquivo = (
        adversario_nome
        .replace(" ", "_")
        .replace("/", "-")
        .replace("\\", "-")
    )

    nome_arquivo = (
        "TT_Performance_"
        f"{jogador_arquivo}_vs_"
        f"{adversario_arquivo}.xlsx"
    )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    return send_file(
        arquivo,
        as_attachment=True,
        download_name=nome_arquivo,
        mimetype=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )


# ============================================================
# EXCLUIR USUÁRIO
# ============================================================

@app.route(
    "/admin/excluir_usuario/<id>"
)
@admin_required
def admin_excluir_usuario(id):

    if id == session.get("usuario_id"):

        flash(
            "Você não pode excluir sua própria conta.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    usuario = buscar_usuario_por_id(id)

    if not usuario:

        flash(
            "Usuário não encontrado.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    excluir_usuario(id)

    flash(
        "Usuário excluído com sucesso!",
        "success"
    )

    return redirect(
        url_for("admin")
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )