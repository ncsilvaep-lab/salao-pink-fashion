import base64
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random
import smtplib
import pandas as pd
import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="Salão Pink Fashion",
    page_icon=":material/content_cut:",
    layout="wide",
)


# ----------------------------------------
# FUNÇÃO PARA CARREGAR A LOGO EM BASE64
# ----------------------------------------
def obter_logo_base64():
  caminhos_possiveis = [
      "logo.png",
      "logo.jpg",
      "logo.jpeg",
      "logo.webp",
      "LOGO.PNG",
      "LOGO.JPG",
  ]
  for caminho in caminhos_possiveis:
    if os.path.exists(caminho):
      with open(caminho, "rb") as f:
        ext = caminho.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"
        encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{encoded}"
  return None


# ----------------------------------------
# DESIGN SYSTEM & CSS PERSONALIZADO
# ----------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Poppins:wght@300;400;500;600&display=swap');

    /* Fundo Geral da Aplicação */
    .stApp {
        background-color: #FAF6F8;
        font-family: 'Poppins', sans-serif;
        color: #3A132C;
    }

    /* Títulos Principais */
    h1 {
        font-family: 'Playfair Display', serif !important;
        color: #4A154B !important;
        font-weight: 700 !important;
        font-size: 40px !important;
        letter-spacing: -0.5px;
    }

    /* Subtítulos de Seções e Cabeçalhos */
    h2 {
        font-family: 'Playfair Display', serif !important;
        color: #4A154B !important;
        font-weight: 700 !important;
        font-size: 32px !important;
        letter-spacing: -0.5px;
    }

    h3 {
        font-family: 'Playfair Display', serif !important;
        color: #4A154B !important;
        font-weight: 600 !important;
        font-size: 24px !important;
    }

    /* Subtítulos Descritivos das Páginas */
    .subtitulo-pagina {
        color: #77506A !important;
        font-size: 18px !important;
        font-weight: 400 !important;
        margin-bottom: 22px !important;
    }

    /* Menu Lateral (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #F3E2EC !important;
    }

    section[data-testid="stSidebar"] h2 {
        font-size: 28px !important;
    }

    section[data-testid="stSidebar"] p {
        font-size: 16px !important;
    }

    div[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 18px !important;
        font-weight: 500 !important;
        color: #4A154B !important;
    }

    /* Cards e Containers */
    div[data-testid="stForm"], 
    div[data-testid="stMetric"],
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 22px !important;
        box-shadow: 0 4px 20px rgba(224, 82, 151, 0.06) !important;
        border: 1px solid #F5E3EE !important;
    }

    /* Estilização das Métricas */
    div[data-testid="stMetricValue"] {
        color: #E05297 !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
        font-size: 32px !important;
    }

    /* Botões Modernos e Arredondados */
    .stButton > button {
        border-radius: 12px !important;
        background: linear-gradient(135deg, #E05297 0%, #C2185B 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        padding: 0.6rem 1.3rem !important;
        box-shadow: 0 4px 14px rgba(224, 82, 151, 0.25) !important;
        transition: all 0.3s ease-in-out !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(224, 82, 151, 0.38) !important;
        opacity: 0.96;
    }

    /* Inputs e Seletores */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border-color: #EAD0E1 !important;
        font-size: 15px !important;
    }

    /* Abas Navegáveis (Tabs) */
    button[data-baseweb="tab"] {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        font-size: 16px !important;
        color: #88607A !important;
    }

    button[aria-selected="true"] {
        color: #E05297 !important;
        border-bottom-color: #E05297 !important;
    }

    /* Estilização Avançada das Tabelas */
    div[data-testid="stDataFrame"] {
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid #F0DCE8 !important;
        box-shadow: 0 4px 16px rgba(74, 21, 75, 0.04) !important;
        background-color: #FFFFFF !important;
    }

    </style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------
# CONFIGURAÇÃO DE E-MAIL (REMETENTE)
# ----------------------------------------
EMAIL_REMETENTE = "salaopinkfashioncop@gmail.com"
SENHA_APP = "pjvwgiziggrzglra"


def enviar_codigo_email(email_destino, codigo):
  try:
    # Criar mensagem multipart contendo HTML e imagens (CID)
    msg = MIMEMultipart("related")
    msg["Subject"] = (
        f"✨ Código de Verificação: {codigo} - Salão Pink Fashion"
    )
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = email_destino

    # Parte alternativa para Plain Text + HTML
    msg_alternative = MIMEMultipart("alternative")
    msg.attach(msg_alternative)

    # Fallback de texto simples
    text_plain = (
        f"Olá! Seu código de verificação para o sistema Salão Pink Fashion é:"
        f" {codigo}\n\nSe você não solicitou este código, ignore esta mensagem."
    )
    msg_alternative.attach(MIMEText(text_plain, "plain", "utf-8"))

    # Template HTML Elegante com Paleta Pink & Plum
    html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Código de Verificação - Salão Pink Fashion</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #FAF6F8; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FAF6F8; padding: 40px 10px;">
                <tr>
                    <td align="center">
                        <!-- Card Principal -->
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #FFFFFF; border-radius: 20px; overflow: hidden; box-shadow: 0 8px 30px rgba(74, 21, 75, 0.08); border: 1px solid #F3E2EC;">
                            
                            <!-- Cabeçalho com Gradiente e Logo -->
                            <tr>
                                <td align="center" style="background: linear-gradient(135deg, #4A154B 0%, #881B58 100%); padding: 35px 20px; text-align: center;">
                                    <img src="cid:logo_cid" alt="Salão Pink Fashion" style="max-width: 120px; height: auto; border-radius: 12px; margin-bottom: 12px; display: block;" onerror="this.style.display='none';">
                                    <h1 style="color: #FFFFFF; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: 0.5px; font-family: Georgia, serif;">Salão Pink Fashion</h1>
                                    <p style="color: #F5CEE6; margin: 6px 0 0 0; font-size: 13px; font-weight: 300; letter-spacing: 1px;">SISTEMA INTEGRADO DE GESTÃO BEAUTY</p>
                                </td>
                            </tr>

                            <!-- Conteúdo da Mensagem -->
                            <tr>
                                <td style="padding: 35px 30px; text-align: center;">
                                    <h2 style="color: #3A132C; font-size: 20px; margin: 0 0 12px 0; font-weight: 600;">Olá! Seja bem-vinda(o) 💕</h2>
                                    <p style="color: #6B4962; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                                        Recebemos uma solicitação de criação de conta no sistema do <strong>Salão Pink Fashion</strong>. Utilize o código de segurança abaixo para confirmar seu e-mail:
                                    </p>

                                    <!-- Box do Código em Destaque -->
                                    <div style="background-color: #FDF2F7; border: 2px dashed #E05297; border-radius: 16px; padding: 22px; margin: 20px 0; text-align: center;">
                                        <span style="font-size: 12px; text-transform: uppercase; letter-spacing: 2px; color: #88607A; font-weight: 600; display: block; margin-bottom: 8px;">Seu Código de Confirmação</span>
                                        <span style="font-size: 38px; font-weight: 800; color: #C2185B; letter-spacing: 10px; font-family: 'Courier New', Courier, monospace;">{codigo}</span>
                                    </div>

                                    <p style="color: #9A738E; font-size: 13px; line-height: 1.5; margin: 25px 0 0 0;">
                                        ⚠️ Se você não solicitou este cadastro, por favor desconsidere este mensagem. Seu código é pessoal e intransferível.
                                    </p>
                                </td>
                            </tr>

                            <!-- Rodapé do E-mail -->
                            <tr>
                                <td style="background-color: #FAF4F8; padding: 20px; text-align: center; border-top: 1px solid #F3E2EC;">
                                    <p style="color: #77506A; font-size: 12px; margin: 0; font-weight: 500;">
                                        Desenvolvido por <strong style="color: #C2185B;">Optimus Engenharia Jr</strong>
                                    </p>
                                    <p style="color: #A38298; font-size: 11px; margin: 4px 0 0 0;">
                                        Salão Pink Fashion &copy; Todos os direitos reservados.
                                    </p>
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
    msg_alternative.attach(MIMEText(html_content, "html", "utf-8"))

    # Tentativa de Anexar Imagem Local como CID (Embedded Image)
    caminhos_possiveis = [
        "logo.png",
        "logo.jpg",
        "logo.jpeg",
        "logo.webp",
        "LOGO.PNG",
        "LOGO.JPG",
    ]
    for caminho in caminhos_possiveis:
      if os.path.exists(caminho):
        with open(caminho, "rb") as f:
          ext = caminho.split(".")[-1].lower()
          subtype = "jpeg" if ext in ["jpg", "jpeg"] else ext
          image = MIMEImage(f.read(), _subtype=subtype)
          image.add_header("Content-ID", "<logo_cid>")
          image.add_header(
              "Content-Disposition",
              "inline",
              filename=os.path.basename(caminho),
          )
          msg.attach(image)
          break

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_REMETENTE, SENHA_APP)
    server.send_message(msg)
    server.quit()
    return True
  except Exception as e:
    print("Erro ao enviar e-mail:", e)
    return False


# ----------------------------------------
# CLASSIFICAÇÃO DE ESTOQUE
# ----------------------------------------
def classificar_status_estoque(qtd):
  try:
    q = int(qtd)
    if q <= 2:
      return "🔴 Crítico"
    elif q <= 5:
      return "🟡 Baixo"
    else:
      return "🟢 Normal"
  except:
    return "⚪ Indefinido"


# ----------------------------------------
# CONFIGURAÇÃO DE ARQUIVOS LOCAIS
# ----------------------------------------
PASTA_DRIVE = "dados_sistema"
os.makedirs(PASTA_DRIVE, exist_ok=True)

ARQ_ESTOQUE = f"{PASTA_DRIVE}/estoque.csv"
ARQ_ATENDIMENTOS = f"{PASTA_DRIVE}/atendimentos.csv"
ARQ_FINANCEIRO = f"{PASTA_DRIVE}/financeiro.csv"
ARQ_USUARIOS = f"{PASTA_DRIVE}/usuarios.csv"


def carregar_dados(arquivo):
  if os.path.exists(arquivo):
    return pd.read_csv(arquivo).to_dict("records")
  return []


def salvar_dados(dados, arquivo):
  df = pd.DataFrame(dados)
  df.to_csv(arquivo, index=False)


def converter_valor(valor):
  try:
    return float(valor)
  except:
    return 0.0


# 2. Inicialização do Banco de Dados
if "logado" not in st.session_state:
  st.session_state.logado = False
if "usuario_logado" not in st.session_state:
  st.session_state.usuario_logado = ""
if "estoque" not in st.session_state:
  st.session_state.estoque = carregar_dados(ARQ_ESTOQUE)
if "atendimentos" not in st.session_state:
  st.session_state.atendimentos = carregar_dados(ARQ_ATENDIMENTOS)
if "financeiro" not in st.session_state:
  st.session_state.financeiro = carregar_dados(ARQ_FINANCEIRO)
if "usuarios" not in st.session_state:
  st.session_state.usuarios = carregar_dados(ARQ_USUARIOS)
  if len(st.session_state.usuarios) == 0:
    st.session_state.usuarios.append({
        "email": "admin@salaopinkfashion.com",
        "usuario": "admin",
        "senha": "12347",
    })
    salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)

if "etapa_cadastro" not in st.session_state:
  st.session_state.etapa_cadastro = 1
if "codigo_gerado" not in st.session_state:
  st.session_state.codigo_gerado = ""
if "email_temp" not in st.session_state:
  st.session_state.email_temp = ""

# 3. Tela de Login e Cadastro
if not st.session_state.logado:
  col1, col2, col3 = st.columns([1, 1.8, 1])
  with col2:
    logo_b64 = obter_logo_base64()

    if logo_b64:
      st.markdown(
          f"""
                <div style='text-align: center; margin-top: 10px; margin-bottom: 10px;'>
                    <img src='{logo_b64}' style='max-width: 130px; width: 100%; height: auto; border-radius: 12px;'>
                </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown(
        """
            <div style='text-align: center; margin-bottom: 20px;'>
                <h1 style='font-size: 38px; margin-bottom: 0px;'>Salão Pink Fashion</h1>
                <p style='color: #88607A; font-size: 17px; font-weight: 400; margin-top: 5px;'>Sistema Integrado de Gestão Beauty</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    aba_login, aba_cadastro = st.tabs(
        [":material/login: Entrar", ":material/person_add: Cadastrar Novo Usuário"]
    )

    with aba_login:
      st.write("")
      usuario = st.text_input("Usuário")
      senha = st.text_input("Senha", type="password")

      if st.button(
          "Acessar Painel",
          type="primary",
          use_container_width=True,
          icon=":material/login:",
      ):
        login_sucesso = False
        for usr in st.session_state.usuarios:
          if str(usr["usuario"]) == usuario and str(usr["senha"]) == senha:
            login_sucesso = True
            break

        if login_sucesso:
          st.session_state.logado = True
          st.session_state.usuario_logado = usuario
          st.rerun()
        else:
          st.error("Usuário ou senha incorretos.")

    with aba_cadastro:
      st.write("")
      if st.session_state.etapa_cadastro == 1:
        email_input = st.text_input("Seu E-mail Profissional")

        if st.button(
            "Enviar Código de Verificação",
            type="primary",
            use_container_width=True,
            icon=":material/send:",
        ):
          if "@" in email_input and "." in email_input:
            codigo = str(random.randint(100000, 999999))
            st.session_state.codigo_gerado = codigo
            st.session_state.email_temp = email_input

            sucesso_email = enviar_codigo_email(email_input, codigo)

            if sucesso_email:
              st.success(f"Código enviado para {email_input}.")
              st.session_state.etapa_cadastro = 2
              st.rerun()
            else:
              st.warning(
                  f"Erro ao enviar e-mail. Para testes, seu código é: {codigo}"
              )
              st.session_state.etapa_cadastro = 2
          else:
            st.error("Por favor, digite um e-mail válido.")

      elif st.session_state.etapa_cadastro == 2:
        st.info(f"Código enviado para: **{st.session_state.email_temp}**")
        codigo_digitado = st.text_input(
            "Digite o Código de 6 Dígitos", max_chars=6
        )

        col_voltar, col_avancar = st.columns(2)
        if col_voltar.button("Voltar", icon=":material/arrow_back:"):
          st.session_state.etapa_cadastro = 1
          st.rerun()

        if col_avancar.button(
            "Validar Código", type="primary", icon=":material/check_circle:"
        ):
          if codigo_digitado == st.session_state.codigo_gerado:
            st.success("Código Validado com sucesso!")
            st.session_state.etapa_cadastro = 3
            st.rerun()
          else:
            st.error("Código incorreto.")

      elif st.session_state.etapa_cadastro == 3:
        novo_usuario = st.text_input("Defina seu Nome de Usuário")
        nova_senha = st.text_input("Defina sua Senha", type="password")

        if st.button(
            "Finalizar Cadastro",
            type="primary",
            use_container_width=True,
            icon=":material/save:",
        ):
          if novo_usuario and nova_senha:
            st.session_state.usuarios.append({
                "email": st.session_state.email_temp,
                "usuario": novo_usuario,
                "senha": nova_senha,
            })
            salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)
            st.success("Cadastro concluído! Acesse a aba 'Entrar'.")
            st.session_state.etapa_cadastro = 1
          else:
            st.error("Preencha todos os campos.")

    st.markdown(
        """
            <div style='text-align: center; margin-top: 45px;'>
                <p style='font-size: 14px; color: #5A204B; font-weight: 500; letter-spacing: 0.5px; margin: 0;'>
                    Desenvolvido por <strong style='color: #C2185B; font-weight: 700;'>Optimus Engenharia jr</strong>
                </p>
            </div>
        """,
        unsafe_allow_html=True,
    )

# 4. Sistema Principal
else:
  # Sidebar
  st.sidebar.markdown(
      "<h2 style='font-size: 28px; margin-bottom: 5px;'>Pink Fashion</h2>",
      unsafe_allow_html=True,
  )
  st.sidebar.markdown(
      "<p style='font-size: 16px; color: #88607A; margin-bottom:"
      " 20px;'>Navegação do Sistema</p>",
      unsafe_allow_html=True,
  )

  menu_opcoes = {
      ":material/dashboard: Menu Principal": "Dashboard",
      ":material/inventory_2: Produtos & Estoque": "Estoque",
      ":material/calendar_month: Atendimentos & Serviços": "Atendimentos",
      ":material/payments: Painel Financeiro": "Financeiro",
  }

  escolha_formatada = st.sidebar.radio("", list(menu_opcoes.keys()))
  escolha = menu_opcoes[escolha_formatada]

  st.sidebar.divider()
  st.sidebar.markdown(
      "<p style='font-size: 16px;'>Sessão ativa: <br><strong style='font-size:"
      " 18px; color:"
      f" #C2185B;'>{st.session_state.usuario_logado.capitalize()}</strong></p>",
      unsafe_allow_html=True,
  )
  st.write("")
  if st.sidebar.button(
      "Encerrar Sessão", use_container_width=True, icon=":material/logout:"
  ):
    st.session_state.logado = False
    st.rerun()

  # ----------------------------------------
  # MÓDULO 0: MENU PRINCIPAL / DASHBOARD
  # ----------------------------------------
  if escolha == "Dashboard":
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    st.header("Menu Principal")
    st.markdown(
        "<p class='subtitulo-pagina'>Visão geral e resumo do salão em"
        f" <strong>{hoje_str}</strong></p>",
        unsafe_allow_html=True,
    )

    # Cálculo de Métricas Financeiras
    receitas_total = sum(
        converter_valor(i["Valor (R$)"])
        for i in st.session_state.financeiro
        if i["Tipo"] == "Entrada"
    )
    saidas_total = sum(
        converter_valor(i["Valor (R$)"])
        for i in st.session_state.financeiro
        if i["Tipo"] == "Saída"
    )
    custos_fixos = sum(
        converter_valor(i["Valor (R$)"])
        for i in st.session_state.financeiro
        if i.get("Tipo") == "Custo Fixo"
    )
    saldo_livre = receitas_total - saidas_total - custos_fixos

    # Faturamento do dia
    receitas_hoje = sum(
        converter_valor(i["Valor (R$)"])
        for i in st.session_state.financeiro
        if i["Tipo"] == "Entrada" and str(i["Data"]).startswith(hoje_str)
    )

    # Filtros de Atendimentos e Vendas de hoje
    servicos_hoje = [
        a
        for a in st.session_state.atendimentos
        if str(a.get("Data", "")) == hoje_str
        and a.get("Tipo", "Serviço") == "Serviço"
    ]

    vendas_hoje = [
        a
        for a in st.session_state.atendimentos
        if str(a.get("Data", "")) == hoje_str and a.get("Tipo") == "Venda Produto"
    ]

    # Métricas do Topo
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Faturamento Hoje", f"R$ {receitas_hoje:.2f}")
    col_m2.metric("Faturamento Total", f"R$ {receitas_total:.2f}")
    col_m3.metric("Saldo Líquido", f"R$ {saldo_livre:.2f}")
    col_m4.metric("Atendimentos Hoje", f"{len(servicos_hoje)}")

    st.divider()

    # Abas de Organização do Menu Principal
    aba_clientes, aba_vendas, aba_alertas = st.tabs([
        ":material/calendar_month: Clientes Agendados Hoje",
        ":material/shopping_bag: Produtos Vendidos Hoje",
        ":material/warning: Alertas de Estoque",
    ])

    with aba_clientes:
      if servicos_hoje:
        df_serv = pd.DataFrame(servicos_hoje)
        colunas_exibir = [
            c
            for c in ["Cliente", "Descrição", "Profissional", "Total (R$)"]
            if c in df_serv.columns
        ]

        st.dataframe(
            df_serv[colunas_exibir],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cliente": st.column_config.TextColumn("👤 Cliente"),
                "Descrição": st.column_config.TextColumn("✂️ Serviço Realizado"),
                "Profissional": st.column_config.TextColumn("💇‍♀️ Profissional"),
                "Total (R$)": st.column_config.NumberColumn(
                    "💵 Valor Total", format="R$ %.2f"
                ),
            },
        )
      else:
        st.info("Nenhum serviço ou atendimento registrado para a data de hoje.")

    with aba_vendas:
      if vendas_hoje:
        df_vendas = pd.DataFrame(vendas_hoje)
        colunas_exibir_v = [
            c
            for c in ["Cliente", "Descrição", "Total (R$)"]
            if c in df_vendas.columns
        ]

        st.dataframe(
            df_vendas[colunas_exibir_v],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cliente": st.column_config.TextColumn(
                    "👤 Cliente / Compradora"
                ),
                "Descrição": st.column_config.TextColumn(
                    "📦 Produto(s) Vendido(s)"
                ),
                "Total (R$)": st.column_config.NumberColumn(
                    "💵 Valor Recebido", format="R$ %.2f"
                ),
            },
        )
      else:
        st.info(
            "Nenhuma venda de produto registrada no balcão para a data de hoje."
        )

    with aba_alertas:
      if st.session_state.estoque:
        df_e = pd.DataFrame(st.session_state.estoque)
        df_e["Qtd_num"] = df_e["Quantidade"].apply(converter_valor)
        df_baixos = df_e[df_e["Qtd_num"] <= 5].copy()

        if not df_baixos.empty:
          df_baixos["Nível Estoque"] = df_baixos["Qtd_num"].apply(
              classificar_status_estoque
          )
          colunas_exibir_e = [
              c
              for c in ["Nível Estoque", "Produto", "Quantidade", "Categoria"]
              if c in df_baixos.columns
          ]

          st.dataframe(
              df_baixos[colunas_exibir_e],
              use_container_width=True,
              hide_index=True,
              column_config={
                  "Nível Estoque": st.column_config.TextColumn("Status"),
                  "Produto": st.column_config.TextColumn("📦 Produto"),
                  "Quantidade": st.column_config.NumberColumn(
                      "Qtd Restante", format="%d un"
                  ),
                  "Categoria": st.column_config.TextColumn("Categoria"),
              },
          )
        else:
          st.success("✅ Todos os produtos estão com estoque em nível normal!")
      else:
        st.info("Nenhum produto cadastrado no estoque.")

  # ----------------------------------------
  # MÓDULO 1: ESTOQUE DE PRODUTOS
  # ----------------------------------------
  elif escolha == "Estoque":
    st.header("Gestão de Produtos & Estoque")
    st.markdown(
        "<p class='subtitulo-pagina'>Controle de cosméticos, insumos e produtos"
        " para revenda</p>",
        unsafe_allow_html=True,
    )

    aba1, aba2 = st.tabs([
        ":material/add_box: Cadastrar / Entrada de Produto",
        ":material/inventory: Estoque Atual",
    ])

    with aba1:
      with st.form("form_produto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome_produto = col1.text_input(
            "Nome do Produto (Ex: Shampoo L'Oréal, Esmalte Risqué)"
        )
        categoria = col2.selectbox(
            "Finalidade / Categoria",
            ["Uso no Salão (Insumo)", "Revenda ao Cliente"],
        )

        col3, col4, col5 = st.columns(3)
        qtd = col3.number_input("Quantidade a Adicionar", min_value=1, step=1)

        custo = col4.number_input(
            "Custo Unitário (R$)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
        )
        preco_venda = col5.number_input(
            "Preço de Venda (R$)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
        )

        submit_produto = st.form_submit_button(
            "Salvar Registro / Adicionar Estoque",
            type="primary",
            icon=":material/add:",
        )

        if submit_produto and nome_produto:
          produto_existente = None
          for p in st.session_state.estoque:
            if (
                str(p["Produto"]).strip().lower() == nome_produto.strip().lower()
                and p["Categoria"] == categoria
            ):
              produto_existente = p
              break

          if produto_existente:
            qtd_antiga = int(produto_existente["Quantidade"])
            produto_existente["Quantidade"] = qtd_antiga + int(qtd)

            if custo > 0:
              produto_existente["Custo (R$)"] = custo
            if preco_venda > 0:
              produto_existente["Preço Venda (R$)"] = preco_venda

            salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)
            st.success(
                f"Estoque do produto **'{produto_existente['Produto']}'**"
                f" atualizado! Adicionadas {qtd} unidade(s). Novo total:"
                f" **{produto_existente['Quantidade']} un**."
            )
            st.rerun()
          else:
            st.session_state.estoque.append({
                "Produto": nome_produto.strip(),
                "Categoria": categoria,
                "Quantidade": qtd,
                "Custo (R$)": custo,
                "Preço Venda (R$)": preco_venda,
            })
            salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)
            st.success(
                f"Novo produto **'{nome_produto.strip()}'** cadastrado com"
                " sucesso!"
            )
            st.rerun()

    with aba2:
      if st.session_state.estoque:
        df_estoque = pd.DataFrame(st.session_state.estoque)

        df_estoque["Nível Estoque"] = df_estoque["Quantidade"].apply(
            classificar_status_estoque
        )
        colunas = [
            "Nível Estoque",
            "Produto",
            "Quantidade",
            "Custo (R$)",
            "Preço Venda (R$)",
            "Categoria",
        ]
        df_estoque = df_estoque[[c for c in colunas if c in df_estoque.columns]]

        itens_baixos = df_estoque[df_estoque["Quantidade"].astype(int) <= 5]
        if not itens_baixos.empty:
          st.warning(
              f"⚠️ **Atenção:** Há **{len(itens_baixos)}** produto(s) com nível"
              " de estoque **Baixo** ou **Crítico**!"
          )

        st.subheader("Produtos para Revenda")
        df_revenda = df_estoque[
            df_estoque["Categoria"] == "Revenda ao Cliente"
        ].drop(columns=["Categoria"], errors="ignore")

        if not df_revenda.empty:
          st.dataframe(
              df_revenda,
              use_container_width=True,
              hide_index=True,
              column_config={
                  "Nível Estoque": st.column_config.TextColumn(
                      "Status",
                      help=(
                          "🔴 Crítico (≤ 2 unid) | 🟡 Baixo (3 a 5 unid) | 🟢"
                          " Normal (> 5 unid)"
                      ),
                  ),
                  "Produto": st.column_config.TextColumn("📦 Produto"),
                  "Quantidade": st.column_config.NumberColumn(
                      "Qtd. Estoque", format="%d un"
                  ),
                  "Custo (R$)": st.column_config.NumberColumn(
                      "Custo Un.", format="R$ %.2f"
                  ),
                  "Preço Venda (R$)": st.column_config.NumberColumn(
                      "Preço Venda", format="R$ %.2f"
                  ),
              },
          )
        else:
          st.info("Nenhum produto cadastrado para revenda.")

        st.divider()

        st.subheader("Insumos & Produtos de Uso do Salão")
        df_insumos = df_estoque[
            df_estoque["Categoria"] == "Uso no Salão (Insumo)"
        ].drop(columns=["Categoria", "Preço Venda (R$)"], errors="ignore")

        if not df_insumos.empty:
          st.dataframe(
              df_insumos,
              use_container_width=True,
              hide_index=True,
              column_config={
                  "Nível Estoque": st.column_config.TextColumn(
                      "Status",
                      help=(
                          "🔴 Crítico (≤ 2 unid) | 🟡 Baixo (3 a 5 unid) | 🟢"
                          " Normal (> 5 unid)"
                      ),
                  ),
                  "Produto": st.column_config.TextColumn(
                      "🧼 Insumo / Material"
                  ),
                  "Quantidade": st.column_config.NumberColumn(
                      "Qtd. Estoque", format="%d un"
                  ),
                  "Custo (R$)": st.column_config.NumberColumn(
                      "Custo Un.", format="R$ %.2f"
                  ),
              },
          )
        else:
          st.info("Nenhum insumo cadastrado.")
      else:
        st.info("Seu estoque está vazio.")

  # ----------------------------------------
  # MÓDULO 2: ATENDIMENTOS E SERVIÇOS
  # ----------------------------------------
  elif escolha == "Atendimentos":
    st.header("Atendimentos & Serviços")
    st.markdown(
        "<p class='subtitulo-pagina'>Registro de serviços prestados e vendas de"
        " produtos</p>",
        unsafe_allow_html=True,
    )

    aba1, aba2 = st.tabs([
        ":material/add_task: Registrar Atendimento / Venda",
        ":material/history: Histórico de Atendimentos",
    ])

    with aba1:
      tipo_op = st.radio(
          "Tipo de Operação:",
          ["Novo Servico / Agendamento", "Venda de Produto do Balcão"],
          horizontal=True,
      )
      st.write("")

      if tipo_op == "Novo Servico / Agendamento":
        with st.form("form_servico", clear_on_submit=True):
          col_a, col_b = st.columns(2)
          cliente = col_a.text_input("Nome da Cliente")
          data_atend = col_b.date_input(
              "Data do Atendimento", format="DD/MM/YYYY"
          )

          col_c, col_d = st.columns(2)
          servico = col_c.text_input(
              "Serviço Realizado (Ex: Corte, Escova, Coloração, Manicure)"
          )
          profissional = col_d.text_input("Profissional Responsável")

          valor_servico = st.number_input(
              "Valor do Serviço (R$)",
              min_value=0.0,
              value=0.0,
              step=1.0,
              format="%.2f",
          )

          submit_servico = st.form_submit_button(
              "Confirmar Atendimento",
              type="primary",
              icon=":material/check_circle:",
          )

          if submit_servico and cliente and servico:
            data_str = data_atend.strftime("%d/%m/%Y")

            st.session_state.atendimentos.append({
                "Tipo": "Serviço",
                "Data": data_str,
                "Cliente": cliente,
                "Descrição": servico,
                "Profissional": profissional,
                "Total (R$)": valor_servico,
            })
            salvar_dados(st.session_state.atendimentos, ARQ_ATENDIMENTOS)

            st.session_state.financeiro.append({
                "Data": data_str,
                "Tipo": "Entrada",
                "Descrição": f"Serviço: {servico} ({cliente})",
                "Valor (R$)": valor_servico,
            })
            salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)

            st.success(
                f"Atendimento registrado com sucesso (R$ {valor_servico:.2f})!"
            )

      elif tipo_op == "Venda de Produto do Balcão":
        prods_revenda = [
            item
            for item in st.session_state.estoque
            if item["Categoria"] == "Revenda ao Cliente"
            and str(item["Quantidade"]).isdigit()
            and int(item["Quantidade"]) > 0
        ]

        if not prods_revenda:
          st.warning(
              "Não há produtos cadastrados para revenda com estoque disponível."
          )
        else:
          with st.form("form_venda_balcao", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            cliente = col_a.text_input("Nome da Cliente")
            data_venda = col_b.date_input("Data da Venda", format="DD/MM/YYYY")

            opcoes_select = {
                f"{p['Produto']} - R$ {p['Preço Venda (R$)']} | Qtd Disp:"
                f" {p['Quantidade']}": p
                for p in prods_revenda
            }
            prod_selecionado = st.selectbox(
                "Selecione o Produto", list(opcoes_select.keys())
            )

            qtd_vendida = st.number_input(
                "Quantidade Vendida", min_value=1, step=1
            )
            submit_venda = st.form_submit_button(
                "Finalizar Venda de Produto",
                type="primary",
                icon=":material/shopping_cart:",
            )

            if submit_venda and cliente:
              prod_ref = opcoes_select[prod_selecionado]

              if qtd_vendida > int(prod_ref["Quantidade"]):
                st.error(
                    "Estoque insuficiente! Disponível apenas"
                    f" {prod_ref['Quantidade']} unidades."
                )
              else:
                valor_total = float(prod_ref["Preço Venda (R$)"]) * qtd_vendida
                data_str = data_venda.strftime("%d/%m/%Y")

                for p in st.session_state.estoque:
                  if p == prod_ref:
                    p["Quantidade"] = int(p["Quantidade"]) - qtd_vendida
                    break

                st.session_state.atendimentos.append({
                    "Tipo": "Venda Produto",
                    "Data": data_str,
                    "Cliente": cliente,
                    "Descrição": f"{qtd_vendida}x {prod_ref['Produto']}",
                    "Profissional": "-",
                    "Total (R$)": valor_total,
                })
                salvar_dados(st.session_state.atendimentos, ARQ_ATENDIMENTOS)
                salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)

                st.session_state.financeiro.append({
                    "Data": data_str,
                    "Tipo": "Entrada",
                    "Descrição": (
                        f"Venda Produto: {prod_ref['Produto']} ({cliente})"
                    ),
                    "Valor (R$)": valor_total,
                })
                salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)

                st.success(
                    f"Venda registrada com sucesso (R$ {valor_total:.2f})!"
                )
                st.rerun()

    with aba2:
      if st.session_state.atendimentos:
        df_atend = pd.DataFrame(st.session_state.atendimentos)
        st.dataframe(
            df_atend,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Tipo": st.column_config.TextColumn("📌 Operação"),
                "Data": st.column_config.TextColumn("📅 Data"),
                "Cliente": st.column_config.TextColumn("👤 Cliente"),
                "Descrição": st.column_config.TextColumn("📝 Detalhes"),
                "Profissional": st.column_config.TextColumn("💇‍♀️ Profissional"),
                "Total (R$)": st.column_config.NumberColumn(
                    "💵 Valor Total", format="R$ %.2f"
                ),
            },
        )
      else:
        st.info("Nenhum atendimento ou venda registrado até o momento.")

  # ----------------------------------------
  # MÓDULO 3: PAINEL FINANCEIRO
  # ----------------------------------------
  elif escolha == "Financeiro":
    st.header("Painel Financeiro")
    st.markdown(
        "<p class='subtitulo-pagina'>Gestão de caixa, receitas, despesas"
        " variáveis e custos fixos</p>",
        unsafe_allow_html=True,
    )

    aba_f1, aba_f2 = st.tabs([
        ":material/add_card: Nova Movimentação / Despesa",
        ":material/receipt_long: Extrato de Transações",
    ])

    with aba_f1:
      with st.form("form_financeiro", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        tipo_mov = col_f1.selectbox(
            "Tipo de Movimentação",
            [
                "Saída (Despesa Variável)",
                "Custo Fixo",
                "Entrada Avulsa / Diversos",
            ],
        )
        data_mov = col_f2.date_input("Data do Registro", format="DD/MM/YYYY")

        desc_mov = st.text_input(
            "Descrição (Ex: Conta de Luz, Compra de Toalhas, Aluguel)"
        )
        valor_mov = st.number_input(
            "Valor da Operação (R$)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.2f",
        )

        submit_mov = st.form_submit_button(
            "Lançar no Caixa", type="primary", icon=":material/save:"
        )

        if submit_mov and desc_mov and valor_mov > 0:
          data_str = data_mov.strftime("%d/%m/%Y")

          if "Entrada" in tipo_mov:
            tipo_salvo = "Entrada"
          elif tipo_mov == "Custo Fixo":
            tipo_salvo = "Custo Fixo"
          else:
            tipo_salvo = "Saída"

          st.session_state.financeiro.append({
              "Data": data_str,
              "Tipo": tipo_salvo,
              "Descrição": desc_mov,
              "Valor (R$)": valor_mov,
          })
          salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)
          st.success(
              f"Movimentação **'{desc_mov}'** de **R$"
              f" {valor_mov:.2f}** registrada com sucesso!"
          )
          st.rerun()

    with aba_f2:
      if st.session_state.financeiro:
        df_fin = pd.DataFrame(st.session_state.financeiro)

        # Cálculo consolidado
        tot_entradas = sum(
            converter_valor(i["Valor (R$)"])
            for i in st.session_state.financeiro
            if i["Tipo"] == "Entrada"
        )
        tot_saidas = sum(
            converter_valor(i["Valor (R$)"])
            for i in st.session_state.financeiro
            if i["Tipo"] == "Saída"
        )
        tot_custos_fixos = sum(
            converter_valor(i["Valor (R$)"])
            for i in st.session_state.financeiro
            if i.get("Tipo") == "Custo Fixo"
        )
        saldo_liquido = tot_entradas - tot_saidas - tot_custos_fixos

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Entradas", f"R$ {tot_entradas:.2f}")
        c2.metric("Despesas Variáveis", f"R$ {tot_saidas:.2f}")
        c3.metric("Custos Fixos", f"R$ {tot_custos_fixos:.2f}")
        c4.metric("Saldo Líquido", f"R$ {saldo_liquido:.2f}")

        st.divider()

        st.dataframe(
            df_fin,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Data": st.column_config.TextColumn("📅 Data"),
                "Tipo": st.column_config.TextColumn("🏷️ Categoria"),
                "Descrição": st.column_config.TextColumn("📝 Descrição"),
                "Valor (R$)": st.column_config.NumberColumn(
                    "💵 Valor", format="R$ %.2f"
                ),
            },
        )
      else:
        st.info("Nenhuma movimentação financeira registrada até o momento.")
