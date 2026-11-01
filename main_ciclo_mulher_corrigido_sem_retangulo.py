import flet as ft
import sqlite3
import calendar
import csv
import os
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

# ============================================================
# CICLO DA MULHER — interface redesenhada
# O banco ciclo.db e as tabelas existentes são preservados.
# ============================================================

PASTA_APP = Path(__file__).resolve().parent

# No Android/desktop empacotado, o diretório do código pode ser somente leitura.
# O Flet fornece FLET_APP_STORAGE_DATA para guardar dados persistentes.
ARQUIVO_BANCO_ANTIGO = PASTA_APP / "ciclo.db"
DIRETORIO_DADOS_FLET = os.environ.get("FLET_APP_STORAGE_DATA")
if DIRETORIO_DADOS_FLET:
    DIRETORIO_DADOS_FLET = Path(DIRETORIO_DADOS_FLET).expanduser().resolve()
    # Em desenvolvimento, mantém o banco já existente ao lado do projeto.
    if ".flet" in DIRETORIO_DADOS_FLET.parts and ARQUIVO_BANCO_ANTIGO.exists():
        CAMINHO_BANCO = ARQUIVO_BANCO_ANTIGO
    else:
        CAMINHO_BANCO = DIRETORIO_DADOS_FLET / "ciclo.db"
        # Migra uma cópia inicial do banco antigo, sem apagar o original.
        if ARQUIVO_BANCO_ANTIGO.exists() and not CAMINHO_BANCO.exists():
            CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ARQUIVO_BANCO_ANTIGO, CAMINHO_BANCO)
else:
    CAMINHO_BANCO = ARQUIVO_BANCO_ANTIGO

PASTA_EXPORTACOES = CAMINHO_BANCO.parent / "exportacoes"
MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

ROXO = "#7952B3"              # roxo principal
ROXO_ESCURO = "#35234F"       # ameixa para títulos
LILAS = "#A98BD4"
LILAS_CLARO = "#F0E9FA"
LILAS_MUITO_CLARO = "#FAF7FF"
FUNDO = "#FBF9FF"
BRANCO = "#FFFFFF"
TEXTO = "#71677F"
BORDA = "#E7DFF2"
ROSA = "#A98BD4"
ROSA_CLARO = "#F5F0FC"

# Ilustração original de lírio em PNG transparente, embutida para funcionar no APK.
LIRIO_BASE64 = "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"

def imagem_lirio(tamanho=58):
    return ft.Image(
        src="data:image/png;base64," + LIRIO_BASE64,
        width=tamanho, height=tamanho,
        tooltip="Lírio decorativo",
    )

VERDE = "#4E9C83"
VERDE_CLARO = "#E8F6F0"
LARANJA = "#D99454"
LARANJA_CLARO = "#FFF2E4"


# ---------------------- BANCO DE DADOS ----------------------

def preparar_banco():
    """Cria apenas tabelas ausentes; nunca apaga os dados existentes."""
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                intensidade TEXT NOT NULL,
                sintomas TEXT
            )
        """)
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS menstruacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inicio TEXT NOT NULL,
                fim TEXT
            )
        """)
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT
            )
        """)


def buscar_registros():
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        return conexao.execute("""
            SELECT id, data, intensidade, sintomas
            FROM registros
            ORDER BY data DESC, id DESC
        """).fetchall()


def buscar_menstruacoes():
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        return conexao.execute("""
            SELECT id, inicio, fim
            FROM menstruacoes
            ORDER BY inicio DESC, id DESC
        """).fetchall()


def salvar_config(chave, valor):
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        conexao.execute("""
            INSERT INTO configuracoes (chave, valor)
            VALUES (?, ?)
            ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor
        """, (chave, valor))


def buscar_config(chave, padrao=""):
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        resultado = conexao.execute(
            "SELECT valor FROM configuracoes WHERE chave = ?", (chave,)
        ).fetchone()
    return resultado[0] if resultado else padrao


def prever_proxima_menstruacao():
    """Estima uma data a partir dos inícios registrados; não é previsão médica."""
    datas = sorted({
        date.fromisoformat(inicio)
        for _, inicio, _ in buscar_menstruacoes()
        if inicio
    })
    if len(datas) < 2:
        return None, None

    intervalos = [
        (datas[i] - datas[i - 1]).days
        for i in range(1, len(datas))
    ]
    intervalos = [dias for dias in intervalos if 15 <= dias <= 60]
    if not intervalos:
        return None, None

    media = round(sum(intervalos) / len(intervalos))
    return datas[-1] + timedelta(days=media), media


def registrar_inicio(data_inicio):
    valido, _ = validar_periodo_novo(data_inicio)
    if not valido:
        return False
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        conexao.execute(
            "INSERT INTO menstruacoes (inicio, fim) VALUES (?, NULL)",
            (data_inicio.isoformat(),)
        )
    return True


def registrar_fim(data_fim):
    if data_fim > date.today():
        return False
    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        registro = conexao.execute("""
            SELECT id, inicio FROM menstruacoes
            WHERE fim IS NULL ORDER BY id DESC LIMIT 1
        """).fetchone()
        if registro is None:
            return False
        id_registro, inicio = registro
        if data_fim.isoformat() < inicio:
            return False
        conexao.execute(
            "UPDATE menstruacoes SET fim = ? WHERE id = ?",
            (data_fim.isoformat(), id_registro)
        )
    return True



def exportar_dados_csv():
    """Exporta os registros em CSV UTF-8 sem alterar o banco original."""
    PASTA_EXPORTACOES.mkdir(parents=True, exist_ok=True)
    nome = f"ciclo_exportacao_{datetime.now():%Y%m%d_%H%M%S}.csv"
    destino = PASTA_EXPORTACOES / nome
    with sqlite3.connect(CAMINHO_BANCO) as conexao, destino.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["tipo", "data_inicio_ou_registro", "data_fim", "intensidade", "sintomas_ou_observacoes"])
        for _, data_reg, intensidade, sintomas in conexao.execute(
            "SELECT id, data, intensidade, sintomas FROM registros ORDER BY data DESC"
        ):
            escritor.writerow(["Sintoma", data_reg, "", intensidade, sintomas or ""])
        for _, inicio, fim in conexao.execute(
            "SELECT id, inicio, fim FROM menstruacoes ORDER BY inicio DESC"
        ):
            escritor.writerow(["Menstruação", inicio, fim or "Em andamento", "", ""])
    return destino


def criar_backup_banco():
    """Cria uma cópia datada do banco, mantendo o arquivo principal intacto."""
    if not CAMINHO_BANCO.exists():
        preparar_banco()
    PASTA_EXPORTACOES.mkdir(parents=True, exist_ok=True)
    destino = PASTA_EXPORTACOES / f"ciclo_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
    with sqlite3.connect(CAMINHO_BANCO) as origem, sqlite3.connect(destino) as copia:
        origem.backup(copia)
    return destino


def validar_periodo_novo(data_inicio):
    """Impede datas futuras e períodos duplicados ou fora de ordem."""
    if data_inicio > date.today():
        return False, "Não é possível registrar uma data futura como início real."
    periodos = buscar_menstruacoes()
    if any(fim is None for _, _, fim in periodos):
        return False, "Já existe um período em andamento. Registre o fim primeiro."
    datas = [date.fromisoformat(inicio) for _, inicio, _ in periodos if inicio]
    if datas and data_inicio <= max(datas):
        return False, "Esse início precisa ser posterior ao último período registrado."
    return True, ""


def formatar_data(texto):
    try:
        return date.fromisoformat(texto).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return texto or "—"


def validar_data(texto):
    try:
        return date.fromisoformat((texto or "").strip())
    except (ValueError, AttributeError, TypeError):
        return None


# ---------------------- INTERFACE ----------------------

def main(page: ft.Page):
    preparar_banco()
    page.title = "Ciclo da Mulher 💗"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = FUNDO
    page.padding = 0
    page.spacing = 0
    page.window_min_width = 360
    page.window_min_height = 600
    try:
        page.theme = ft.Theme(color_scheme_seed="#7952B3", use_material3=True)
        page.bgcolor = FUNDO
    except (AttributeError, TypeError):
        pass

    def em_tela_pequena():
        largura = getattr(page, "width", None)
        if not largura:
            janela = getattr(page, "window", None)
            largura = getattr(janela, "width", None) if janela else None
        return bool(largura and largura < 720)

    tela_atual = {"nome": "inicio"}
    data_calendario = {"ano": date.today().year, "mes": date.today().month}
    data_selecionada = {"data": date.today()}
    botoes_nav = {}
    # Lista rolável própria para evitar que o conteúdo expanda e vire um bloco vazio.
    area_conteudo = ft.ListView(spacing=14, expand=True, padding=0)
    titulo_pagina = ft.Text("Visão geral", size=24, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO)
    subtitulo_pagina = ft.Text("Seu cantinho de cuidado 💗", size=12, color=TEXTO)
    aviso = ft.Container(visible=False, padding=12, border_radius=12, bgcolor=LILAS_CLARO)

    def mostrar_aviso(mensagem, cor=LILAS_CLARO, texto_cor=ROXO_ESCURO):
        aviso.content = ft.Row([
            ft.Icon(ft.Icons.INFO_OUTLINE, color=texto_cor, size=20),
            ft.Text(mensagem, color=texto_cor, size=13, expand=True),
        ], spacing=10)
        aviso.bgcolor = cor
        aviso.visible = True
        page.update()

    def esconder_aviso():
        aviso.visible = False

    def borda_campo():
        return {
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=12, side=ft.BorderSide(color=BORDA)
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=12, side=ft.BorderSide(color=ROXO, width=1.5)
            ),
        }

    def cartao(conteudo, padding=20, expand=False):
        return ft.Container(
            content=conteudo,
            bgcolor=BRANCO,
            border=ft.Border.all(1, BORDA),
            border_radius=20,
            padding=padding,
            expand=expand,
            animate=ft.Animation(220, ft.AnimationCurve.EASE_OUT),
        )

    def texto_secao(texto, complemento=None):
        itens = [ft.Text(texto, size=19, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO)]
        if complemento:
            itens.append(ft.Text(complemento, size=12, color=TEXTO))
        return ft.Column(itens, spacing=4)

    def botao_primario(texto, icone, acao):
        return ft.Button(
            texto,
            icon=icone,
            on_click=acao,
            bgcolor=ROXO,
            color=BRANCO,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(16, 13, 16, 13),
            ),
        )

    def botao_secundario(texto, icone, acao):
        return ft.OutlinedButton(
            texto,
            icon=icone,
            on_click=acao,
            style=ft.ButtonStyle(
                color=ROXO,
                side=ft.BorderSide(1, BORDA),
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(14, 12, 14, 12),
            ),
        )

    def icone_quadrado(icone, cor_fundo=LILAS_CLARO, cor_icone=ROXO):
        return ft.Container(
            content=ft.Icon(icone, color=cor_icone, size=22),
            bgcolor=cor_fundo,
            border_radius=13,
            padding=12,
        )

    def estatistica(titulo, valor, legenda, icone, cor_fundo, cor_icone, expand=True):
        return cartao(ft.Row([
            icone_quadrado(icone, cor_fundo, cor_icone),
            ft.Column([
                ft.Text(titulo, size=12, color=TEXTO),
                ft.Text(str(valor), size=27, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text(legenda, size=11, color=TEXTO),
            ], spacing=3, expand=True),
        ], spacing=13), padding=16, expand=expand)

    def grafico_ciclo():
        menstruacoes = buscar_menstruacoes()
        datas = sorted({
            date.fromisoformat(inicio)
            for _, inicio, _ in menstruacoes
            if inicio
        })
        intervalos = []
        for i in range(1, len(datas)):
            dias = (datas[i] - datas[i - 1]).days
            if 15 <= dias <= 60:
                intervalos.append((datas[i].strftime("%d/%m"), dias))
        intervalos = intervalos[-5:]

        elementos = [
            ft.Row([
                ft.Column([
                    ft.Text("Regularidade do ciclo", size=18, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                    ft.Text("Intervalos entre inícios registrados", size=12, color=TEXTO),
                ], spacing=4, expand=True),
                icone_quadrado(ft.Icons.INSERT_CHART_OUTLINED),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]
        if not intervalos:
            elementos.append(ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INSIGHTS_OUTLINED, color=LILAS, size=32),
                    ft.Text("Seu gráfico vai aparecer aqui", size=15, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                    ft.Text("Registre dois inícios menstruais ou mais para comparar os intervalos.", size=12, color=TEXTO, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                bgcolor=LILAS_MUITO_CLARO, border_radius=16, padding=22,
            ))
        else:
            maximo = max(35, max(dias for _, dias in intervalos))
            for rotulo, dias in intervalos:
                largura = max(12, int(250 * dias / maximo))
                elementos.append(ft.Column([
                    ft.Row([
                        ft.Text(rotulo, size=12, color=TEXTO, width=48),
                        ft.Container(
                            content=ft.Container(
                                width=largura,
                                height=10,
                                bgcolor=LILAS if dias <= 35 else ROSA,
                                border_radius=8,
                                animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
                            ),
                            bgcolor="#F1EFF8",
                            border_radius=8,
                            padding=2,
                            expand=True,
                        ),
                        ft.Text(f"{dias} dias", size=12, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO, width=62, text_align=ft.TextAlign.RIGHT),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ], spacing=3))
            elementos.append(ft.Text("Os intervalos são informativos e não substituem orientação de saúde.", size=11, color=TEXTO))
        return cartao(ft.Column(elementos, spacing=14), padding=20)

    def ir_para(nome):
        tela_atual["nome"] = nome
        esconder_aviso()
        nomes = {
            "inicio": ("Visão geral", "Resumo do seu ciclo em um só lugar."),
            "calendario": ("Calendário menstrual", "Consulte datas e registre o início ou fim."),
            "registrar": ("Novo registro", "Anote sintomas e como você está se sentindo."),
            "historico": ("Seu histórico", "Consulte, edite ou remova registros salvos."),
            "lembretes": ("Lembretes", "Pequenos lembretes para cuidar de você."),
            "configuracoes": ("Configurações", "Privacidade, backup e seus dados."),
            "cuidados": ("Cuidados e sinais de alerta", "Orientações gerais para cuidar de você."),
            "mais": ("Mais opções", "Outros recursos do seu cantinho."),
        }
        titulo, subtitulo = nomes.get(nome, ("Visão geral", "Acompanhe seu ciclo."))
        titulo_pagina.value = titulo
        subtitulo_pagina.value = subtitulo
        for chave, botao in botoes_nav.items():
            selecionado = chave == nome or (nome in ("lembretes", "configuracoes", "cuidados") and chave == "mais")
            botao.bgcolor = LILAS_CLARO if selecionado else None
            for controle in botao.content.controls:
                if isinstance(controle, ft.Icon):
                    controle.color = ROXO if selecionado else TEXTO
                elif isinstance(controle, ft.Text):
                    controle.color = ROXO_ESCURO if selecionado else TEXTO

        area_conteudo.controls.clear()

        if nome == "inicio":
            construir_inicio()
        elif nome == "calendario":
            construir_calendario()
        elif nome == "registrar":
            construir_registro()
        elif nome == "historico":
            construir_historico()
        elif nome == "lembretes":
            construir_lembretes()
        elif nome == "configuracoes":
            construir_configuracoes()
        elif nome == "cuidados":
            construir_cuidados()
        elif nome == "mais":
            construir_mais()

        # Mantém o item certo marcado na barra inferior do celular.
        barra = getattr(page, "navigation_bar", None)
        if barra is not None:
            indice_por_tela = {
                "inicio": 0, "calendario": 1, "registrar": 2,
                "historico": 3, "mais": 4, "lembretes": 4, "configuracoes": 4, "cuidados": 4,
            }
            barra.selected_index = indice_por_tela.get(nome, 0)

        page.update()

    def construir_inicio():
        hoje = date.today()
        previsao, media = prever_proxima_menstruacao()
        registros = buscar_registros()
        menstruacoes = buscar_menstruacoes()
        inicios = sorted(date.fromisoformat(inicio) for _, inicio, _ in menstruacoes if inicio)
        dia_ciclo = (hoje - inicios[-1]).days + 1 if inicios and inicios[-1] <= hoje else None
        periodo_aberto = next((date.fromisoformat(inicio) for _, inicio, fim in menstruacoes if fim is None), None)
        dias_texto = "Ainda sem previsão"
        data_texto = "Registre dois inícios menstruais para calcular uma estimativa."
        if previsao:
            faltam = (previsao - hoje).days
            data_texto = f"{previsao.day} de {MESES_PT[previsao.month - 1]} de {previsao.year}"
            if faltam > 1:
                dias_texto = f"Faltam aproximadamente {faltam} dias"
            elif faltam == 1:
                dias_texto = "A estimativa é para amanhã"
            elif faltam == 0:
                dias_texto = "A estimativa é para hoje"
            else:
                dias_texto = f"A data estimada passou há {abs(faltam)} dias"

        saudacao = ft.Row([
            ft.Container(
                content=imagem_lirio(62),
                bgcolor=LILAS_CLARO,
                border_radius=20,
                padding=5,
                width=72, height=72,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Column([
                ft.Text("Olá, seja bem-vinda!", size=22, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text("Um espaço delicado para cuidar de você.  ✿", size=13, color=TEXTO),
            ], spacing=4, expand=True),
        ], spacing=14)

        itens_hero = [
            ft.Column([
                ft.Container(
                    content=ft.Text("PREVISÃO DO PRÓXIMO CICLO", size=10, weight=ft.FontWeight.BOLD, color=ROXO),
                    bgcolor=BRANCO, border_radius=20, padding=ft.Padding(10, 7, 10, 7),
                ),
                ft.Text(data_texto, size=21 if em_tela_pequena() else 25, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text(dias_texto, size=13, color=TEXTO),
                ft.Text(
                    f"Média dos intervalos registrados: {media} dias" if media else
                    "A previsão fica mais útil com mais registros.",
                    size=12, color=TEXTO,
                ),
                botao_primario("Ver calendário", ft.Icons.CALENDAR_MONTH_OUTLINED,
                               lambda e: ir_para("calendario")),
            ], spacing=10, expand=True)
        ]
        itens_hero.append(ft.Container(
            content=imagem_lirio(104 if not em_tela_pequena() else 72),
            bgcolor="#F8F2FF",
            border_radius=24,
            padding=6,
            alignment=ft.Alignment.CENTER,
        ))
        hero = ft.Container(
            content=ft.Row(itens_hero, spacing=12, wrap=True, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=LILAS_CLARO, border_radius=22, padding=18 if em_tela_pequena() else 24,
            animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )

        lembrete_data = validar_data(buscar_config("lembrete_data"))
        lembrete_texto = buscar_config("lembrete_texto", "Lembrete do ciclo")
        if lembrete_data:
            aviso.content = ft.Row([
                ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, color=ROXO, size=20),
                ft.Text(
                    f"Lembrete: {lembrete_texto} — {lembrete_data.strftime('%d/%m/%Y')}",
                    color=ROXO_ESCURO, size=13, expand=True,
                ),
            ], spacing=10)
            aviso.bgcolor = LILAS_CLARO
            aviso.visible = True

        cards_stats = [
            estatistica("Sintomas", len(registros), "anotações", ft.Icons.FAVORITE_BORDER, ROSA_CLARO, ROSA, expand=not em_tela_pequena()),
            estatistica("Ciclos", len(menstruacoes), "períodos", ft.Icons.CALENDAR_MONTH_OUTLINED, LILAS_CLARO, ROXO, expand=not em_tela_pequena()),
            estatistica("Dia do ciclo", f"{dia_ciclo}º" if dia_ciclo else "—",
                        "desde o último início" if dia_ciclo else "registre um início",
                        ft.Icons.AUTO_AWESOME_OUTLINED, VERDE_CLARO, VERDE, expand=not em_tela_pequena()),
        ]
        estatisticas = ft.Column(cards_stats, spacing=10) if em_tela_pequena() else ft.Row(cards_stats, spacing=12, wrap=True)

        # Painel independente e recolhível: fechado não reserva altura para os dados.
        resumo_estado = {"aberto": False}
        resumo_conteudo = ft.Container(
            content=estatisticas,
            visible=False,
            bgcolor=BRANCO,
            padding=ft.Padding(0, 14, 0, 0),
        )
        resumo_seta = ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED, color=ROXO, size=24)

        def alternar_resumo(e):
            resumo_estado["aberto"] = not resumo_estado["aberto"]
            resumo_conteudo.visible = resumo_estado["aberto"]
            resumo_seta.name = (
                ft.Icons.KEYBOARD_ARROW_UP_ROUNDED if resumo_estado["aberto"]
                else ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED
            )
            page.update()

        cabecalho_resumo = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=imagem_lirio(42),
                    bgcolor=LILAS_CLARO, border_radius=13, padding=3,
                    width=48, height=48, alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text("Seu resumo", size=17, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                    ft.Text("Estatísticas do seu ciclo", size=12, color=TEXTO),
                ], spacing=3, expand=True),
                resumo_seta,
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=alternar_resumo,
            ink=True,
            bgcolor=LILAS_MUITO_CLARO,
            border_radius=14,
            padding=12,
        )
        cartao_resumo = ft.Container(
            content=ft.Column([cabecalho_resumo, resumo_conteudo], spacing=0, tight=True),
            bgcolor=BRANCO,
            border=ft.Border.all(1, BORDA),
            border_radius=18,
            padding=10,
        )

        cartao_registro = cartao(ft.Row([
            icone_quadrado(ft.Icons.EDIT_NOTE, ROSA_CLARO, ROXO),
            ft.Column([
                ft.Text("Registrar sintomas", size=14, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text("Cólicas, humor e observações.", size=12, color=TEXTO),
                ft.TextButton("Fazer registro  →", on_click=lambda e: ir_para("registrar")),
            ], spacing=5, expand=True),
        ], spacing=12), padding=15)
        cartao_lembretes = cartao(ft.Row([
            icone_quadrado(ft.Icons.NOTIFICATIONS_OUTLINED, VERDE_CLARO, VERDE),
            ft.Column([
                ft.Text("Lembretes", size=14, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text("Organize um aviso pessoal.", size=12, color=TEXTO),
                ft.TextButton("Configurar  →", on_click=lambda e: ir_para("lembretes")),
            ], spacing=5, expand=True),
        ], spacing=12), padding=15)
        acessos = ft.Column([cartao_registro, cartao_lembretes], spacing=10) if em_tela_pequena() else ft.Row([cartao_registro, cartao_lembretes], spacing=14)

        # Sem nenhum dado salvo, não renderiza cartões de previsão/estatísticas
        # nem o gráfico vazio, que antes ocupavam a tela como um retângulo largo.
        tem_dados = bool(registros or menstruacoes)
        componentes_inicio = [
            cartao(saudacao, padding=16 if em_tela_pequena() else 20),
        ]
        if tem_dados:
            componentes_inicio.extend([
                hero,
                cartao_resumo,
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=VERDE if periodo_aberto else ROXO, size=20),
                        ft.Text(
                            f"Período em andamento desde {formatar_data(periodo_aberto.isoformat())}." if periodo_aberto
                            else "Nenhum período marcado como em andamento.",
                            size=12, color=ROXO_ESCURO, expand=True
                        ),
                    ], spacing=10),
                    bgcolor=VERDE_CLARO if periodo_aberto else LILAS_MUITO_CLARO, border_radius=14, padding=13,
                ),
                grafico_ciclo(),
                ft.Text("Previsões são estimativas e não devem ser usadas como método contraceptivo.", size=11, color=TEXTO),
            ])
        else:
            componentes_inicio.append(
                cartao(ft.Column([
                    ft.Icon(ft.Icons.SPA_OUTLINED, size=34, color=ROXO),
                    ft.Text("Seu espaço está pronto", size=17, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                    ft.Text("Registre seu primeiro ciclo ou um sintoma para começar.", size=13, color=TEXTO, text_align=ft.TextAlign.CENTER),
                    botao_primario("Fazer primeiro registro", ft.Icons.ADD_CIRCLE_OUTLINE,
                                   lambda e: ir_para("registrar")),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12), padding=22)
            )
        componentes_inicio.extend([
            texto_secao("Acesso rápido", "O que você quer registrar hoje?"),
            acessos,
        ])
        area_conteudo.controls.extend(componentes_inicio)

    def construir_registro():
        campo_data = ft.TextField(
            label="Data do registro (AAAA-MM-DD)",
            value=date.today().isoformat(),
            border=borda_campo(),
        )
        campo_intensidade = ft.Dropdown(
            label="Escala de dor (0 a 10)",
            options=[
                ft.dropdown.Option("0 — Sem dor"),
                ft.dropdown.Option("1 — Muito leve"),
                ft.dropdown.Option("2 — Leve"),
                ft.dropdown.Option("3 — Leve a moderada"),
                ft.dropdown.Option("4 — Moderada"),
                ft.dropdown.Option("5 — Moderada"),
                ft.dropdown.Option("6 — Moderada a forte"),
                ft.dropdown.Option("7 — Forte"),
                ft.dropdown.Option("8 — Muito forte"),
                ft.dropdown.Option("9 — Intensa"),
                ft.dropdown.Option("10 — Pior dor imaginável"),
            ],
            border=borda_campo(),
        )
        campo_sintomas = ft.TextField(
            label="Sintomas e observações",
            hint_text="Ex.: cólica, cansaço, dor nas costas, humor...",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border=borda_campo(),
        )
        mensagem = ft.Text(color=ROXO, size=13)

        def salvar(e):
            data_valida = validar_data(campo_data.value)
            if not data_valida:
                mensagem.value = "Confira a data. Use o formato AAAA-MM-DD."
            elif not campo_intensidade.value:
                mensagem.value = "Selecione a intensidade da cólica."
            else:
                with sqlite3.connect(CAMINHO_BANCO) as conexao:
                    conexao.execute(
                        "INSERT INTO registros (data, intensidade, sintomas) VALUES (?, ?, ?)",
                        (data_valida.isoformat(), campo_intensidade.value, campo_sintomas.value or ""),
                    )
                mensagem.value = "Registro salvo com sucesso."
                campo_sintomas.value = ""
                campo_intensidade.value = None
            page.update()

        area_conteudo.controls.extend([
            cartao(ft.Column([
                ft.Row([
                    icone_quadrado(ft.Icons.FAVORITE_BORDER, ROSA_CLARO, ROSA),
                    ft.Column([
                        ft.Text("Como você está hoje?", size=19, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                        ft.Text("Seus registros ficam salvos localmente neste dispositivo.", size=12, color=TEXTO),
                    ], spacing=4, expand=True),
                ], spacing=12),
                ft.Divider(color=BORDA),
                campo_data,
                campo_intensidade,
                campo_sintomas,
                botao_primario("Salvar registro", ft.Icons.CHECK_CIRCLE_OUTLINE, salvar),
                mensagem,
            ], spacing=16), padding=24),
        ])

    def mostrar_dialogo(dialogo):
        # Mantém compatibilidade com a API de diálogo usada no projeto anterior.
        page.show_dialog(dialogo)

    def fechar_dialogo():
        page.pop_dialog()

    def construir_historico():
        sintomas = buscar_registros()
        menstruacoes = buscar_menstruacoes()
        area_conteudo.controls.append(texto_secao("Registros de sintomas", "Edite ou exclua uma anotação quando precisar."))

        if not sintomas:
            area_conteudo.controls.append(cartao(ft.Column([
                ft.Icon(ft.Icons.NOTES_OUTLINED, color=LILAS, size=30),
                ft.Text("Nenhum sintoma registrado ainda.", color=ROXO_ESCURO, weight=ft.FontWeight.BOLD),
                ft.Text("Se quiser, use a opção Novo registro para começar.", color=TEXTO, size=12),
            ], spacing=8), padding=20))
        for id_reg, data_reg, intensidade, descricao in sintomas:
            def editar_sintoma(id_atual=id_reg, data_atual=data_reg, nivel_atual=intensidade, desc_atual=descricao):
                campo_data = ft.TextField(label="Data (AAAA-MM-DD)", value=data_atual)
                campo_nivel = ft.Dropdown(
                    label="Intensidade",
                    value=nivel_atual,
                    options=[ft.dropdown.Option("Leve"), ft.dropdown.Option("Moderada"), ft.dropdown.Option("Forte")],
                )
                campo_desc = ft.TextField(label="Sintomas e observações", value=desc_atual or "", multiline=True, min_lines=2)
                msg = ft.Text(color=ROXO)

                def salvar_edicao(e):
                    data_nova = validar_data(campo_data.value)
                    if not data_nova or not campo_nivel.value:
                        msg.value = "Confira a data e a intensidade."
                        page.update()
                        return
                    with sqlite3.connect(CAMINHO_BANCO) as conexao:
                        conexao.execute(
                            "UPDATE registros SET data=?, intensidade=?, sintomas=? WHERE id=?",
                            (data_nova.isoformat(), campo_nivel.value, campo_desc.value or "", id_atual),
                        )
                    fechar_dialogo()
                    ir_para("historico")

                mostrar_dialogo(ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Editar sintoma"),
                    content=ft.Column([campo_data, campo_nivel, campo_desc, msg], tight=True, width=380),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo()),
                        ft.TextButton("Salvar alterações", on_click=salvar_edicao),
                    ],
                ))

            def excluir_sintoma(id_atual=id_reg):
                def confirmar(e):
                    with sqlite3.connect(CAMINHO_BANCO) as conexao:
                        conexao.execute("DELETE FROM registros WHERE id=?", (id_atual,))
                    fechar_dialogo()
                    ir_para("historico")
                mostrar_dialogo(ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Excluir registro?"),
                    content=ft.Text("Esta anotação será removida do histórico."),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo()),
                        ft.TextButton("Excluir", on_click=confirmar),
                    ],
                ))

            area_conteudo.controls.append(cartao(ft.Column([
                ft.Row([
                    icone_quadrado(ft.Icons.FAVORITE_BORDER, ROSA_CLARO, ROSA),
                    ft.Column([
                        ft.Text(formatar_data(data_reg), size=14, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                        ft.Text(f"Intensidade: {intensidade}", size=12, color=TEXTO),
                    ], spacing=4, expand=True),
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, tooltip="Editar", icon_color=ROXO, on_click=lambda e, fn=editar_sintoma: fn()),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip="Excluir", icon_color="#C05B79", on_click=lambda e, fn=excluir_sintoma: fn()),
                ], spacing=8),
                ft.Text(descricao or "Sem observações adicionais.", size=13, color=TEXTO),
            ], spacing=10), padding=16))

        area_conteudo.controls.append(texto_secao("Menstruações registradas", "Os períodos registrados no calendário também aparecem aqui."))
        if not menstruacoes:
            area_conteudo.controls.append(cartao(ft.Text("Nenhuma menstruação registrada ainda.", color=TEXTO), padding=18))

        for id_men, inicio, fim in menstruacoes:
            def editar_menstruacao(id_atual=id_men, inicio_atual=inicio, fim_atual=fim):
                campo_inicio = ft.TextField(label="Início (AAAA-MM-DD)", value=inicio_atual)
                campo_fim = ft.TextField(label="Fim (AAAA-MM-DD; opcional)", value=fim_atual or "")
                msg = ft.Text(color=ROXO)

                def salvar_edicao(e):
                    inicio_novo = validar_data(campo_inicio.value)
                    fim_novo = validar_data(campo_fim.value) if (campo_fim.value or "").strip() else None
                    if not inicio_novo:
                        msg.value = "Informe uma data de início válida."
                        page.update()
                        return
                    if (campo_fim.value or "").strip() and not fim_novo:
                        msg.value = "Confira a data de fim."
                        page.update()
                        return
                    if fim_novo and fim_novo < inicio_novo:
                        msg.value = "O fim não pode ser anterior ao início."
                        page.update()
                        return
                    with sqlite3.connect(CAMINHO_BANCO) as conexao:
                        conexao.execute(
                            "UPDATE menstruacoes SET inicio=?, fim=? WHERE id=?",
                            (inicio_novo.isoformat(), fim_novo.isoformat() if fim_novo else None, id_atual),
                        )
                    fechar_dialogo()
                    ir_para("historico")

                mostrar_dialogo(ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Editar menstruação"),
                    content=ft.Column([campo_inicio, campo_fim, msg], tight=True, width=360),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo()),
                        ft.TextButton("Salvar alterações", on_click=salvar_edicao),
                    ],
                ))

            def excluir_menstruacao(id_atual=id_men):
                def confirmar(e):
                    with sqlite3.connect(CAMINHO_BANCO) as conexao:
                        conexao.execute("DELETE FROM menstruacoes WHERE id=?", (id_atual,))
                    fechar_dialogo()
                    ir_para("historico")
                mostrar_dialogo(ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Excluir período?"),
                    content=ft.Text("Este período será removido do histórico e poderá alterar a estimativa."),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: fechar_dialogo()),
                        ft.TextButton("Excluir", on_click=confirmar),
                    ],
                ))

            fim_texto = formatar_data(fim) if fim else "Em andamento"
            area_conteudo.controls.append(cartao(ft.Row([
                icone_quadrado(ft.Icons.CALENDAR_MONTH_OUTLINED, LILAS_CLARO, ROXO),
                ft.Column([
                    ft.Text(formatar_data(inicio), size=14, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                    ft.Text(f"Fim: {fim_texto}", size=12, color=TEXTO),
                ], spacing=4, expand=True),
                ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, tooltip="Editar", icon_color=ROXO, on_click=lambda e, fn=editar_menstruacao: fn()),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, tooltip="Excluir", icon_color="#C05B79", on_click=lambda e, fn=excluir_menstruacao: fn()),
            ], spacing=8), padding=16))

    def construir_calendario():
        hoje = date.today()
        titulo_mes = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO)
        grade = ft.Column(spacing=5)
        texto_selecionado = ft.Text(f"Data selecionada: {hoje.strftime('%d/%m/%Y')}", size=13, color=TEXTO)
        mensagem = ft.Text(size=13, color=ROXO)
        selecao = {"data": data_selecionada["data"]}

        def desenhar():
            ano, mes = data_calendario["ano"], data_calendario["mes"]
            titulo_mes.value = f"{MESES_PT[mes - 1].capitalize()} {ano}"
            grade.controls.clear()
            grade.controls.append(ft.Row([
                ft.Container(
                    content=ft.Text(letra, size=12, weight=ft.FontWeight.BOLD, color=TEXTO, text_align=ft.TextAlign.CENTER),
                    alignment=ft.Alignment.CENTER, expand=True, padding=5 if em_tela_pequena() else 7,
                )
                for letra in ["D", "S", "T", "Q", "Q", "S", "S"]
            ], spacing=3))

            periodos = buscar_menstruacoes()
            previsao, media = prever_proxima_menstruacao()
            matriz = calendar.Calendar(firstweekday=6).monthdayscalendar(ano, mes)
            for semana in matriz:
                celulas = []
                for numero in semana:
                    if numero == 0:
                        celulas.append(ft.Container(expand=True, padding=9))
                        continue
                    dia = date(ano, mes, numero)
                    menstruando = False
                    for _, inicio_txt, fim_txt in periodos:
                        inicio = date.fromisoformat(inicio_txt)
                        fim = date.fromisoformat(fim_txt) if fim_txt else hoje
                        if inicio <= dia <= fim:
                            menstruando = True
                            break
                    previsto = bool(previsao and previsao <= dia < previsao + timedelta(days=5))
                    selecionado = dia == selecao["data"]
                    if selecionado:
                        fundo, cor = ROXO, BRANCO
                    elif menstruando:
                        fundo, cor = ROSA_CLARO, "#B64D7B"
                    elif previsto:
                        fundo, cor = LILAS_CLARO, ROXO
                    else:
                        fundo, cor = BRANCO, ROXO_ESCURO
                    celulas.append(ft.Container(
                        content=ft.Text(str(numero), size=12, color=cor, text_align=ft.TextAlign.CENTER),
                        bgcolor=fundo,
                        border=ft.Border.all(1, ROXO if selecionado else BORDA),
                        border_radius=12,
                        padding=5 if em_tela_pequena() else 9,
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        on_click=lambda e, d=dia: selecionar(d),
                        animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
                    ))
                grade.controls.append(ft.Row(celulas, spacing=3))
            page.update()

        def selecionar(dia):
            selecao["data"] = dia
            data_selecionada["data"] = dia
            texto_selecionado.value = f"Data selecionada: {dia.strftime('%d/%m/%Y')}"
            mensagem.value = ""
            desenhar()

        def mudar_mes(delta):
            mes = data_calendario["mes"] + delta
            ano = data_calendario["ano"]
            if mes < 1:
                mes, ano = 12, ano - 1
            elif mes > 12:
                mes, ano = 1, ano + 1
            data_calendario.update({"ano": ano, "mes": mes})
            desenhar()

        def salvar_inicio(e):
            valido, motivo = validar_periodo_novo(selecao["data"])
            if valido and registrar_inicio(selecao["data"]):
                mensagem.value = "Início da menstruação registrado."
                mensagem.color = VERDE
            else:
                mensagem.value = motivo or "Não foi possível registrar esse início. Confira o histórico."
                mensagem.color = LARANJA
            desenhar()

        def salvar_fim(e):
            if registrar_fim(selecao["data"]):
                mensagem.value = "Fim da menstruação registrado."
                mensagem.color = VERDE
            else:
                mensagem.value = "Não há período em andamento ou a data é anterior ao início."
                mensagem.color = LARANJA
            desenhar()

        previsao, _ = prever_proxima_menstruacao()
        area_conteudo.controls.extend([
            cartao(ft.Column([
                ft.Row([
                    ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=lambda e: mudar_mes(-1)),
                    ft.Container(content=titulo_mes, alignment=ft.Alignment.CENTER, expand=True),
                    ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=lambda e: mudar_mes(1)),
                ]),
                grade,
                ft.Row([
                    ft.Row([ft.Container(width=10, height=10, bgcolor=ROSA, border_radius=4), ft.Text("Registrado", size=11, color=TEXTO)], spacing=6),
                    ft.Row([ft.Container(width=10, height=10, bgcolor=LILAS, border_radius=4), ft.Text("Previsto", size=11, color=TEXTO)], spacing=6),
                ], spacing=18, wrap=True),
            ], spacing=14), padding=20),
            cartao(ft.Column([
                texto_secao("Registrar período", "Selecione uma data no calendário e escolha uma ação."),
                texto_selecionado,
                ft.Row([
                    botao_primario("Registrar início", ft.Icons.PLAY_CIRCLE_OUTLINE, salvar_inicio),
                    botao_secundario("Registrar fim", ft.Icons.CHECK_CIRCLE_OUTLINE, salvar_fim),
                ], wrap=True, spacing=10),
                mensagem,
                ft.Text("As datas previstas são estimativas. O calendário não substitui orientação de saúde.", size=11, color=TEXTO),
            ], spacing=12), padding=20),
        ])
        desenhar()

    def construir_lembretes():
        campo_data = ft.TextField(
            label="Data do lembrete (AAAA-MM-DD)",
            value=buscar_config("lembrete_data"),
            hint_text="2026-10-20",
            border=borda_campo(),
        )
        campo_texto = ft.TextField(
            label="Mensagem",
            value=buscar_config("lembrete_texto", "Lembrete do ciclo"),
            hint_text="Ex.: observar sintomas ou preparar itens pessoais",
            border=borda_campo(),
        )
        mensagem = ft.Text(color=ROXO, size=13)

        def salvar(e):
            data_lembrete = validar_data(campo_data.value)
            if not data_lembrete:
                mensagem.value = "Informe uma data válida no formato AAAA-MM-DD."
            elif not (campo_texto.value or "").strip():
                mensagem.value = "Escreva uma mensagem para o lembrete."
            else:
                salvar_config("lembrete_data", data_lembrete.isoformat())
                salvar_config("lembrete_texto", campo_texto.value.strip())
                mensagem.value = "Lembrete salvo."
            page.update()

        def remover(e):
            salvar_config("lembrete_data", "")
            salvar_config("lembrete_texto", "")
            campo_data.value = ""
            campo_texto.value = ""
            mensagem.value = "Lembrete removido."
            page.update()

        area_conteudo.controls.append(cartao(ft.Column([
            ft.Row([
                icone_quadrado(ft.Icons.NOTIFICATIONS_OUTLINED, VERDE_CLARO, VERDE),
                ft.Column([
                    ft.Text("Seu lembrete pessoal", size=19, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                    ft.Text("Defina uma data e uma mensagem para ver no aplicativo.", size=12, color=TEXTO),
                ], spacing=4, expand=True),
            ], spacing=12),
            ft.Divider(color=BORDA),
            campo_data,
            campo_texto,
            ft.Row([
                botao_primario("Salvar lembrete", ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, salvar),
                botao_secundario("Remover", ft.Icons.DELETE_OUTLINE, remover),
            ], wrap=True, spacing=10),
            mensagem,
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=LARANJA, size=20),
                    ft.Text("Este lembrete aparece dentro do app. Esta versão não envia notificações se o programa estiver fechado.", size=12, color=TEXTO, expand=True),
                ], spacing=10),
                bgcolor=LARANJA_CLARO,
                border_radius=12,
                padding=12,
            ),
        ], spacing=15), padding=22))

    def construir_configuracoes():
        mensagem_dados = ft.Text(size=12, color=VERDE, selectable=True)

        def fazer_backup(e):
            try:
                destino = criar_backup_banco()
                mensagem_dados.value = f"Backup criado: {destino}"
                mensagem_dados.color = VERDE
            except (OSError, sqlite3.Error) as erro:
                mensagem_dados.value = f"Não foi possível criar o backup: {erro}"
                mensagem_dados.color = "#B42345"
            page.update()

        def exportar_csv(e):
            try:
                destino = exportar_dados_csv()
                mensagem_dados.value = f"Exportação concluída: {destino}"
                mensagem_dados.color = VERDE
            except (OSError, sqlite3.Error) as erro:
                mensagem_dados.value = f"Não foi possível exportar: {erro}"
                mensagem_dados.color = "#B42345"
            page.update()

        area_conteudo.controls.extend([
            cartao(ft.Column([
                ft.Row([
                    icone_quadrado(ft.Icons.SHIELD_OUTLINED, VERDE_CLARO, VERDE),
                    ft.Column([
                        ft.Text("Privacidade dos seus dados", size=18, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                        ft.Text("Os registros ficam guardados localmente neste dispositivo.", size=12, color=TEXTO),
                    ], spacing=4, expand=True),
                ], spacing=12),
                ft.Divider(color=BORDA),
                ft.Text(f"Arquivo do banco de dados: {CAMINHO_BANCO}", size=12, color=TEXTO),
                ft.Text("Não apague nem mova o arquivo ciclo.db se quiser preservar seu histórico.", size=13, color=ROXO_ESCURO),
            ], spacing=12), padding=22),
            cartao(ft.Column([
                ft.Text("Sobre as estimativas", size=17, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text("A previsão é calculada usando a média dos intervalos entre os inícios menstruais registrados. Ciclos podem variar, e essa estimativa não deve ser usada como método contraceptivo nem como diagnóstico.", size=13, color=TEXTO),
            ], spacing=8), padding=22),
            cartao(ft.Column([
                ft.Row([
                    icone_quadrado(ft.Icons.BACKUP_OUTLINED, VERDE_CLARO, VERDE),
                    ft.Column([
                        ft.Text("Backup e exportação", size=18, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                        ft.Text("Faça uma cópia de segurança ou exporte os dados para abrir em uma planilha.", size=12, color=TEXTO),
                    ], spacing=4, expand=True),
                ], spacing=12),
                ft.Row([
                    botao_primario("Criar backup", ft.Icons.BACKUP_OUTLINED, fazer_backup),
                    botao_secundario("Exportar CSV", ft.Icons.TABLE_VIEW_OUTLINED, exportar_csv),
                ], wrap=True, spacing=10),
                mensagem_dados,
                ft.Text("Os arquivos são salvos na pasta 'exportacoes' ao lado do aplicativo. Guarde-os em local seguro, pois podem conter informações íntimas.", size=11, color=TEXTO),
            ], spacing=14), padding=22),
        ])

    def construir_cuidados():
        def bloco(titulo, texto, icone, cor_fundo=LILAS_MUITO_CLARO, cor_icone=ROXO):
            return cartao(ft.Row([
                icone_quadrado(icone, cor_fundo, cor_icone),
                ft.Column([
                    ft.Text(titulo, size=15, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                    ft.Text(texto, size=13, color=TEXTO),
                ], spacing=6, expand=True),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START), padding=16)

        area_conteudo.controls.extend([
            cartao(ft.Column([
                ft.Text("Ideias para aliviar a cólica", size=19, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text("Medidas simples podem ajudar algumas pessoas. Escolha o que for confortável para você.", size=13, color=TEXTO),
                ft.Divider(color=BORDA),
                bloco("Calor suave", "Use uma bolsa térmica morna sobre o abdômen, protegendo a pele e evitando calor excessivo.", ft.Icons.THERMOSTAT, ROSA_CLARO, ROSA),
                bloco("Movimento leve", "Alongamentos tranquilos ou uma caminhada leve podem ajudar se você se sentir bem. Não force se piorar a dor.", ft.Icons.DIRECTIONS_WALK_OUTLINED, VERDE_CLARO, VERDE),
                bloco("Descanso e hidratação", "Tente descansar, beber água e manter refeições regulares. Observe o que costuma trazer conforto para você.", ft.Icons.FAVORITE_BORDER),
                bloco("Acompanhe os sintomas", "Registre intensidade, duração e sintomas associados para perceber padrões e conversar com um profissional de saúde.", ft.Icons.EDIT_NOTE, LILAS_CLARO),
            ], spacing=12), padding=18),
            cartao(ft.Column([
                ft.Text("Sinais de alerta", size=19, weight=ft.FontWeight.BOLD, color="#9B2C45"),
                ft.Text("Procure atendimento médico com urgência se houver dor súbita ou muito intensa, desmaio, febre alta, dificuldade para respirar ou sangramento muito intenso (por exemplo, encharcar absorventes repetidamente em pouco tempo). Também vale buscar avaliação se a dor impede atividades, está piorando, aparece fora do período menstrual ou é diferente do habitual.", size=13, color=TEXTO),
                ft.Text("Este app oferece informações gerais e não faz diagnóstico. Em caso de dúvida ou preocupação, converse com um profissional de saúde ou um adulto de confiança.", size=12, color="#9B2C45", weight=ft.FontWeight.W_500),
            ], spacing=10), padding=18),
            cartao(ft.Column([
                ft.Text("Como entender a escala de dor", size=17, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text("0 = sem dor; 1–3 = leve; 4–6 = moderada; 7–8 = forte; 9–10 = muito intensa. A escala é subjetiva: descreva também como a dor afeta seu dia.", size=13, color=TEXTO),
                botao_secundario("Registrar como estou", ft.Icons.ADD_CIRCLE_OUTLINE, lambda e: ir_para("registrar")),
            ], spacing=10), padding=18),
        ])

    def construir_mais():
        area_conteudo.controls.extend([
            cartao(ft.Column([
                icone_quadrado(ft.Icons.FAVORITE_BORDER, ROSA_CLARO, ROXO),
                ft.Text("Alívio da cólica e sinais de alerta", size=17, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text("Dicas de conforto, escala de dor e quando procurar ajuda.", size=12, color=TEXTO),
                botao_primario("Ver guia de cuidados", ft.Icons.SHIELD_OUTLINED, lambda e: ir_para("cuidados")),
            ], spacing=10), padding=18),
            cartao(ft.Column([
                icone_quadrado(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, ROSA_CLARO, ROXO),
                ft.Text("Lembretes", size=17, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text("Crie uma data e uma mensagem para lembrar de você mesma.", size=12, color=TEXTO),
                botao_primario("Abrir lembretes", ft.Icons.ARROW_FORWARD, lambda e: ir_para("lembretes")),
            ], spacing=10), padding=18),
            cartao(ft.Column([
                icone_quadrado(ft.Icons.SHIELD_OUTLINED, VERDE_CLARO, VERDE),
                ft.Text("Privacidade e backup", size=17, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ft.Text("Confira onde seus dados ficam salvos, crie uma cópia de segurança ou exporte para planilha.", size=12, color=TEXTO),
                botao_primario("Configurações", ft.Icons.SETTINGS_OUTLINED, lambda e: ir_para("configuracoes")),
            ], spacing=10), padding=18),
            ft.Text("Seus registros são íntimos: guarde os backups em local seguro.", size=11, color=TEXTO),
        ])

    def item_menu(nome, rotulo, icone):
        botao = ft.Container(
            content=ft.Row([
                ft.Icon(icone, size=20, color=TEXTO),
                ft.Text(rotulo, size=13, color=TEXTO, weight=ft.FontWeight.W_500),
            ], spacing=12),
            padding=ft.Padding(14, 12, 14, 12),
            border_radius=12,
            on_click=lambda e, n=nome: ir_para(n),
            ink=True,
        )
        botoes_nav[nome] = botao
        return botao

    sidebar = ft.Container(
        width=220,
        bgcolor=BRANCO,
        padding=ft.Padding(16, 22, 16, 18),
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.LOCAL_FLORIST_OUTLINED, color=BRANCO, size=24),
                    bgcolor=ROXO,
                    border_radius=14,
                    padding=11,
                ),
                ft.Column([
                    ft.Text("Ciclo da", size=13, color=TEXTO),
                    ft.Text("Mulher", size=20, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                ], spacing=0),
            ], spacing=10),
            ft.Container(height=20),
            ft.Text("MENU PRINCIPAL", size=10, weight=ft.FontWeight.BOLD, color="#A19BB4"),
            item_menu("inicio", "Visão geral", ft.Icons.GRID_VIEW_OUTLINED),
            item_menu("calendario", "Calendário", ft.Icons.CALENDAR_MONTH_OUTLINED),
            item_menu("registrar", "Novo registro", ft.Icons.ADD_CIRCLE_OUTLINE),
            item_menu("historico", "Histórico", ft.Icons.HISTORY_OUTLINED),
            item_menu("cuidados", "Guia de cuidados", ft.Icons.SHIELD_OUTLINED),
            ft.Container(height=8),
            ft.Text("PREFERÊNCIAS", size=10, weight=ft.FontWeight.BOLD, color="#A19BB4"),
            item_menu("lembretes", "Lembretes", ft.Icons.NOTIFICATIONS_OUTLINED),
            item_menu("configuracoes", "Configurações", ft.Icons.SETTINGS_OUTLINED),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.FAVORITE_ROUNDED, color=ROXO, size=22),
                    ft.Text("Cuide de você", size=13, weight=ft.FontWeight.BOLD, color=ROXO_ESCURO),
                    ft.Text("Um dia de cada vez.", size=11, color=TEXTO),
                ], spacing=7, horizontal_alignment=ft.CrossAxisAlignment.START),
                bgcolor=LILAS_MUITO_CLARO,
                border_radius=16,
                padding=14,
            ),
        ], spacing=5, expand=True),
    )

    chip_data = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, color=ROXO, size=17),
            ft.Text(date.today().strftime("%d/%m/%Y"), size=11, color=ROXO_ESCURO, weight=ft.FontWeight.BOLD),
        ], spacing=7),
        bgcolor=BRANCO, border=ft.Border.all(1, BORDA), border_radius=12, padding=10,
    )

    cabecalho = ft.Container(
        content=ft.Row([
            ft.Column([titulo_pagina, subtitulo_pagina], spacing=3, expand=True),
            chip_data,
        ], spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding(18, 20, 18, 14),
    )

    padding_conteudo = ft.Container(
        content=ft.Column([aviso, area_conteudo], spacing=10, expand=True),
        bgcolor=FUNDO,
        padding=ft.Padding(16, 0, 16, 18),
        expand=True,
    )

    painel = ft.Column([cabecalho, padding_conteudo], spacing=0, expand=True)
    divisor_lateral = ft.VerticalDivider(width=1, color=BORDA)
    estrutura_principal = ft.Row([sidebar, divisor_lateral, painel], spacing=0, expand=True)

    destinos_mobile = ["inicio", "calendario", "registrar", "historico", "mais"]

    def criar_barra_mobile():
        return ft.NavigationBar(
            selected_index=destinos_mobile.index(
                tela_atual["nome"] if tela_atual["nome"] in destinos_mobile else "mais"
            ),
            bgcolor=BRANCO,
            indicator_color=ROSA_CLARO,
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
            on_change=lambda e: ir_para(destinos_mobile[e.control.selected_index]),
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME_ROUNDED, label="Início"),
                ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH_OUTLINED, selected_icon=ft.Icons.CALENDAR_MONTH, label="Ciclo"),
                ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE_OUTLINE, selected_icon=ft.Icons.ADD_CIRCLE, label="Registrar"),
                ft.NavigationBarDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="Histórico"),
                ft.NavigationBarDestination(icon=ft.Icons.MORE_HORIZ, selected_icon=ft.Icons.MORE_HORIZ, label="Mais"),
            ],
        )

    def ajustar_layout(e=None):
        pequeno = em_tela_pequena()
        sidebar.visible = not pequeno
        divisor_lateral.visible = not pequeno
        chip_data.visible = not pequeno
        titulo_pagina.size = 22 if pequeno else 26
        subtitulo_pagina.size = 11 if pequeno else 13
        cabecalho.padding = ft.Padding(16, 16, 16, 12) if pequeno else ft.Padding(28, 24, 28, 18)
        padding_conteudo.padding = ft.Padding(13, 0, 13, 14) if pequeno else ft.Padding(28, 0, 28, 28)
        if pequeno:
            page.navigation_bar = criar_barra_mobile()
        else:
            page.navigation_bar = None
        page.update()

    page.add(estrutura_principal)
    page.on_resize = ajustar_layout
    ajustar_layout()
    ir_para("inicio")


ft.run(main)
