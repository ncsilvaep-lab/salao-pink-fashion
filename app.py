import streamlit as st
import pandas as pd
from datetime import datetime
import os
import smtplib
import random
from email.mime.text import MIMEText
import base64

# 1. Configuração da Página
st.set_page_config(
    page_title="Salão Pink Fashion", 
    page_icon=":material/content_cut:", 
    layout="wide"
)

# ----------------------------------------
# FUNÇÃO PARA CARREGAR A LOGO EM BASE64 (PREVINE IMAGEM QUEBRADA)
# ----------------------------------------
def obter_logo_base64():
    # Procura a imagem pelos nomes/extensões mais comuns
    caminhos_possiveis = ["logo.png", "logo.jpg", "logo.jpeg", "logo.webp", "LOGO.PNG", "LOGO.JPG"]
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            with open(caminho, "rb") as f:
                ext = caminho.split('.')[-1].lower()
                mime = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"
                encoded = base64.b64encode(f.read()).decode('utf-8')
                return f"data:{mime};base64,{encoded}"
    return None

# ----------------------------------------
# DESIGN SYSTEM & CSS PERSONALIZADO (MODERNO & FEMININO)
# ----------------------------------------
st.markdown("""
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

    /* Subtítulos de Seções e Cabeçalhos (AUMENTADOS) */
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

    /* Subtítulos Descritivos das Páginas (AUMENTADOS) */
    .subtitulo-pagina {
        color: #77506A !important;
        font-size: 18px !important;
        font-weight: 400 !important;
        margin-bottom: 22px !important;
    }

    /* Menu Lateral (Sidebar) - AUMENTO DE FONTE */
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

    /* Opções do Radio Button na Sidebar (AUMENTADO) */
    div[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 6px 0px !important;
    }

    div[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 18px !important;
        font-weight: 500 !important;
        color: #4A154B !important;
    }

    /* Cards, Métricas e Containers */
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

    /* Tabelas e Dataframes */
    div[data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid #F0DCE8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------
# CONFIGURAÇÃO DE E-MAIL (REMETENTE)
# ----------------------------------------
EMAIL_REMETENTE = "natanaelcampossilva2006@gmail.com"
SENHA_APP = "bwpagsnxwcsxhlsm"

def enviar_codigo_email(email_destino, codigo):
    try:
        msg = MIMEText(f"Olá! Seu código de verificação para o sistema Salão Pink Fashion é: {codigo}")
        msg['Subject'] = 'Código de Verificação - Salão Pink Fashion'
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = email_destino

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_REMETENTE, SENHA_APP)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# ----------------------------------------
# CONFIGURAÇÃO DE ARQUIVOS LOCAIS
# ----------------------------------------
PASTA_DRIVE = "dados_sistema"
os.makedirs(PASTA_DRIVE, exist_ok=True)

ARQ_ESTOQUE = f"{PASTA_DRIVE}/estoque.csv"
ARQ_VENDAS = f"{PASTA_DRIVE}/vendas.csv"
ARQ_FINANCEIRO = f"{PASTA_DRIVE}/financeiro.csv"
ARQ_USUARIOS = f"{PASTA_DRIVE}/usuarios.csv"

def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo).to_dict('records')
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
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = ""
if 'estoque' not in st.session_state:
    st.session_state.estoque = carregar_dados(ARQ_ESTOQUE)
if 'vendas' not in st.session_state:
    st.session_state.vendas = carregar_dados(ARQ_VENDAS)
if 'financeiro' not in st.session_state:
    st.session_state.financeiro = carregar_dados(ARQ_FINANCEIRO)
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = carregar_dados(ARQ_USUARIOS)
    if len(st.session_state.usuarios) == 0:
        st.session_state.usuarios.append({'email': 'admin@salaopinkfashion.com', 'usuario': 'admin', 'senha': '12347'})
        salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)

if 'etapa_cadastro' not in st.session_state:
    st.session_state.etapa_cadastro = 1
if 'codigo_gerado' not in st.session_state:
    st.session_state.codigo_gerado = ""
if 'email_temp' not in st.session_state:
    st.session_state.email_temp = ""

# 3. Tela de Login e Cadastro
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        # Tenta obter a imagem da logo codificada
        logo_b64 = obter_logo_base64()
        
        # Exibição da Logo em HTML (se encontrada)
        if logo_b64:
            st.markdown(f"""
                <div style='text-align: center; margin-top: 10px; margin-bottom: 10px;'>
                    <img src='{logo_b64}' style='max-width: 130px; width: 100%; height: auto; border-radius: 12px;'>
                </div>
            """, unsafe_allow_html=True)

        # Título do Salão Pink Fashion
        st.markdown("""
            <div style='text-align: center; margin-bottom: 20px;'>
                <h1 style='font-size: 38px; margin-bottom: 0px;'>Salão Pink Fashion</h1>
                <p style='color: #88607A; font-size: 17px; font-weight: 400; margin-top: 5px;'>Sistema Integrado de Gestão Beauty</p>
            </div>
        """, unsafe_allow_html=True)

        aba_login, aba_cadastro = st.tabs([
            ":material/login: Entrar", 
            ":material/person_add: Cadastrar Novo Usuário"
        ])

        with aba_login:
            st.write("")
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")

            if st.button("Acessar Painel", type="primary", use_container_width=True, icon=":material/login:"):
                login_sucesso = False
                for usr in st.session_state.usuarios:
                    if str(usr['usuario']) == usuario and str(usr['senha']) == senha:
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
                
                if st.button("Enviar Código de Verificação", type="primary", use_container_width=True, icon=":material/send:"):
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
                            st.warning(f"Erro ao enviar e-mail. Para testes, seu código é: {codigo}")
                            st.session_state.etapa_cadastro = 2 
                    else:
                        st.error("Por favor, digite um e-mail válido.")

            elif st.session_state.etapa_cadastro == 2:
                st.info(f"Código enviado para: **{st.session_state.email_temp}**")
                codigo_digitado = st.text_input("Digite o Código de 6 Dígitos", max_chars=6)
                
                col_voltar, col_avancar = st.columns(2)
                if col_voltar.button("Voltar", icon=":material/arrow_back:"):
                    st.session_state.etapa_cadastro = 1
                    st.rerun()
                    
                if col_avancar.button("Validar Código", type="primary", icon=":material/check_circle:"):
                    if codigo_digitado == st.session_state.codigo_gerado:
                        st.success("Código Validado com sucesso!")
                        st.session_state.etapa_cadastro = 3
                        st.rerun()
                    else:
                        st.error("Código incorreto.")

            elif st.session_state.etapa_cadastro == 3:
                novo_usuario = st.text_input("Defina seu Nome de Usuário")
                nova_senha = st.text_input("Defina sua Senha", type="password")
                
                if st.button("Finalizar Cadastro", type="primary", use_container_width=True, icon=":material/save:"):
                    if novo_usuario and nova_senha:
                        st.session_state.usuarios.append({
                            'email': st.session_state.email_temp, 
                            'usuario': novo_usuario, 
                            'senha': nova_senha
                        })
                        salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)
                        st.success("Cadastro concluído! Acesse a aba 'Entrar'.")
                        st.session_state.etapa_cadastro = 1 
                    else:
                        st.error("Preencha todos os campos.")

        # Rodapé com destaque para a Optimus Engenharia jr
        st.markdown("""
            <div style='text-align: center; margin-top: 45px;'>
                <p style='font-size: 14px; color: #5A204B; font-weight: 500; letter-spacing: 0.5px; margin: 0;'>
                    Desenvolvido por <strong style='color: #C2185B; font-weight: 700;'>Optimus Engenharia jr</strong>
                </p>
            </div>
        """, unsafe_allow_html=True)

# 4. Sistema Principal
else:
    # Cabeçalho da Sidebar (Fontes Aumentadas)
    st.sidebar.markdown("<h2 style='font-size: 28px; margin-bottom: 5px;'>Pink Fashion</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size: 16px; color: #88607A; margin-bottom: 20px;'>Navegação do Sistema</p>", unsafe_allow_html=True)
    
    menu_opcoes = {
        ":material/inventory_2: Gestão de Estoque": "Estoque",
        ":material/point_of_sale: Vendas & Pedidos": "Vendas / Pedidos",
        ":material/payments: Painel Financeiro": "Financeiro"
    }
    
    escolha_formatada = st.sidebar.radio("", list(menu_opcoes.keys()))
    escolha = menu_opcoes[escolha_formatada]

    st.sidebar.divider()
    st.sidebar.markdown(f"<p style='font-size: 16px;'>Sessão ativa: <br><strong style='font-size: 18px; color: #C2185B;'>{st.session_state.usuario_logado.capitalize()}</strong></p>", unsafe_allow_html=True)
    st.write("")
    if st.sidebar.button("Encerrar Sessão", use_container_width=True, icon=":material/logout:"):
        st.session_state.logado = False
        st.rerun()

    # ----------------------------------------
    # MÓDULO 1: ESTOQUE
    # ----------------------------------------
    if escolha == "Estoque":
        st.header("Gestão de Estoque")
        st.markdown("<p class='subtitulo-pagina'>Controle de produtos e materiais em tempo real</p>", unsafe_allow_html=True)
        
        aba1, aba2 = st.tabs([
            ":material/add_box: Cadastrar Item", 
            ":material/inventory: Estoque Atual"
        ])

        with aba1:
            categoria = st.radio("Selecione a Categoria:", ["Peça Pronta", "Material"], horizontal=True)
            st.write("")

            if categoria == "Peça Pronta":
                with st.form("form_peca", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    produto = col1.text_input("Nome da Peça / Produto")
                    tamanho = col2.text_input("Tamanho (Ex: P, M, Único)")

                    col3, col4 = st.columns(2)
                    valor = col3.number_input("Valor de Venda (R$)", min_value=0.0, step=0.5, format="%.2f")
                    disponibilidade = col4.number_input("Quantidade em Estoque", min_value=0, step=1)

                    submit_peca = st.form_submit_button("Cadastrar Produto", type="primary", icon=":material/add:")

                    if submit_peca and produto:
                        st.session_state.estoque.append({
                            'Categoria': 'Peça Pronta', 'Produto': produto,
                            'Tamanho': tamanho, 'Valor (R$)': valor, 'Quantidade': disponibilidade,
                            'Cor': '-', 'Metragem': '-', 'Foto': '-'
                        })
                        salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)
                        st.success(f"Item '{produto}' registrado com sucesso.")

            elif categoria == "Material":
                with st.form("form_material", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    produto = col1.text_input("Nome do Material / Insumo")
                    cor = col2.text_input("Cor")

                    col3, col4, col5 = st.columns(3)
                    metragem = col3.number_input("Metragem/Qtd", min_value=0.0, step=0.1)
                    valor_material = col4.number_input("Custo Total (R$)", min_value=0.0, step=0.5, format="%.2f")
                    foto = col5.file_uploader("Foto do Material", type=["png", "jpg", "jpeg"])

                    submit_material = st.form_submit_button("Cadastrar Material", type="primary", icon=":material/add:")

                    if submit_material and produto:
                        nome_foto = foto.name if foto is not None else "Sem foto"
                        st.session_state.estoque.append({
                            'Categoria': 'Material', 'Produto': produto,
                            'Tamanho': '-', 'Valor (R$)': valor_material, 'Quantidade': '-',
                            'Cor': cor, 'Metragem': metragem, 'Foto': nome_foto
                        })
                        salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)
                        st.success(f"Material '{produto}' registrado com sucesso.")

        with aba2:
            if st.session_state.estoque:
                df_estoque = pd.DataFrame(st.session_state.estoque)
                
                st.subheader("Produtos Prontos")
                df_pecas = df_estoque[df_estoque['Categoria'] == 'Peça Pronta']
                if not df_pecas.empty:
                    st.dataframe(df_pecas, use_container_width=True)
                else:
                    st.info("Nenhum produto cadastrado.")
                
                st.divider()

                st.subheader("Materiais & Insumos")
                df_materiais = df_estoque[df_estoque['Categoria'] == 'Material']
                if not df_materiais.empty:
                    st.dataframe(df_materiais, use_container_width=True)
                else:
                    st.info("Nenhum material cadastrado.")
            else:
                st.info("Seu estoque está vazio.")

    # ----------------------------------------
    # MÓDULO 2: VENDAS E PEDIDOS
    # ----------------------------------------
    elif escolha == "Vendas / Pedidos":
        st.header("Vendas & Agendamentos")
        st.markdown("<p class='subtitulo-pagina'>Registro de serviços prestados e vendas de balcão</p>", unsafe_allow_html=True)

        aba1, aba2 = st.tabs([
            ":material/add_shopping_cart: Novo Registro", 
            ":material/history: Histórico"
        ])

        with aba1:
            tipo_registro = st.radio("Tipo de Operação:", ["Venda de Estoque (Pronta Entrega)", "Novo Pedido (Agendamento / Serviço)"], horizontal=True)
            st.write("")

            if tipo_registro == "Venda de Estoque (Pronta Entrega)":
                pecas_disponiveis = [item for item in st.session_state.estoque if item['Categoria'] == 'Peça Pronta' and str(item['Quantidade']).isdigit() and int(item['Quantidade']) > 0]
                
                if not pecas_disponiveis:
                    st.warning("Não há produtos com estoque disponível no momento.")
                else:
                    with st.form("form_venda_estoque", clear_on_submit=True):
                        col_a, col_b = st.columns(2)
                        nome_cliente = col_a.text_input("Nome do Cliente")
                        data_venda = col_b.date_input("Data da Venda")
                        
                        opcoes_select = {f"{p['Produto']} (Tam: {p['Tamanho']}) - R$ {p['Valor (R$)']} | Disp: {p['Quantidade']} un": p for p in pecas_disponiveis}
                        
                        peca_selecionada = st.selectbox("Selecione o Produto", list(opcoes_select.keys()))
                        
                        col_c, col_d = st.columns(2)
                        qtd_vendida = col_c.number_input("Quantidade", min_value=1, step=1)
                        desconto = col_d.number_input("Desconto Aplicado (R$)", min_value=0.0, step=0.5, format="%.2f")

                        submit_venda = st.form_submit_button("Finalizar Venda", type="primary", icon=":material/shopping_cart_checkout:")

                        if submit_venda and nome_cliente:
                            peca_ref = opcoes_select[peca_selecionada]
                            
                            if qtd_vendida > int(peca_ref['Quantidade']):
                                st.error(f"Estoque insuficiente! Disponível apenas {peca_ref['Quantidade']} unidades.")
                            else:
                                valor_total = (float(peca_ref['Valor (R$)']) * qtd_vendida) - desconto
                                data_str = data_venda.strftime("%d/%m/%Y")
                                
                                for p in st.session_state.estoque:
                                    if p == peca_ref:
                                        p['Quantidade'] = int(p['Quantidade']) - qtd_vendida
                                        break
                                
                                st.session_state.vendas.append({
                                    'Tipo': 'Venda', 'Data': data_str, 'Cliente': nome_cliente,
                                    'Produto': peca_ref['Produto'], 'Qtd': qtd_vendida,
                                    'Total (R$)': valor_total, 'Entrega': 'Pronta Entrega'
                                })
                                salvar_dados(st.session_state.vendas, ARQ_VENDAS)
                                salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)

                                st.session_state.financeiro.append({
                                    'Data': data_str, 'Tipo': 'Entrada',
                                    'Descrição': f"Venda Estoque: {peca_ref['Produto']} ({nome_cliente})", 'Valor (R$)': valor_total
                                })
                                salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)

                                st.success(f"Venda concluída com sucesso (R$ {valor_total:.2f})!")
                                st.rerun()

            elif tipo_registro == "Novo Pedido (Agendamento / Serviço)":
                with st.form("form_pedidos", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    nome_cliente = col_a.text_input("Nome do Cliente")
                    data_entrega = col_b.date_input("Data do Agendamento / Serviço")

                    produto_vendido = st.text_input("Serviço Solicitado (ex: Escova, Coloração, Pacote)")

                    col_c, col_d = st.columns(2)
                    qtd_vendida = col_c.number_input("Quantidade de Sessões/Itens", min_value=1, step=1)
                    valor_total = col_d.number_input("Valor Combinado (R$)", min_value=0.0, step=0.5, format="%.2f")

                    submit_pedido = st.form_submit_button("Confirmar Agendamento", type="primary", icon=":material/event_available:")

                    if submit_pedido and nome_cliente and produto_vendido:
                        data_registro = datetime.now().strftime("%d/%m/%Y")

                        st.session_state.vendas.append({
                            'Tipo': 'Pedido', 'Data': data_registro, 'Cliente': nome_cliente,
                            'Produto': produto_vendido, 'Qtd': qtd_vendida,
                            'Total (R$)': valor_total, 'Entrega': data_entrega.strftime("%d/%m/%Y")
                        })
                        salvar_dados(st.session_state.vendas, ARQ_VENDAS)

                        st.session_state.financeiro.append({
                            'Data': data_registro, 'Tipo': 'Entrada',
                            'Descrição': f"Serviço: {produto_vendido} ({nome_cliente})", 'Valor (R$)': valor_total
                        })
                        salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)

                        st.success(f"Agendamento confirmado (R$ {valor_total:.2f})!")

        with aba2:
            if st.session_state.vendas:
                df_vendas = pd.DataFrame(st.session_state.vendas)
                if 'Tipo' not in df_vendas.columns:
                    df_vendas['Tipo'] = 'Pedido'

                st.subheader("Vendas Concluídas")
                df_vendas_prontas = df_vendas[df_vendas['Tipo'] == 'Venda'].drop(columns=['Tipo'], errors='ignore')
                if not df_vendas_prontas.empty:
                    st.dataframe(df_vendas_prontas, use_container_width=True)
                else:
                    st.info("Nenhuma venda realizada.")
                
                st.divider()

                st.subheader("Agendamentos & Serviços Solicitados")
                df_pedidos_encomendas = df_vendas[df_vendas['Tipo'] == 'Pedido'].drop(columns=['Tipo'], errors='ignore')
                if not df_pedidos_encomendas.empty:
                    st.dataframe(df_pedidos_encomendas, use_container_width=True)
                else:
                    st.info("Nenhum agendamento pendente.")
            else:
                st.info("Nenhuma movimentação registrada.")

    # ----------------------------------------
    # MÓDULO 3: FINANCEIRO
    # ----------------------------------------
    elif escolha == "Financeiro":
        st.header("Painel Financeiro")
        st.markdown("<p class='subtitulo-pagina'>Visão geral das métricas e saúde financeira do salão</p>", unsafe_allow_html=True)

        receitas = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.financeiro if i['Tipo'] == 'Entrada')
        saidas = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.financeiro if i['Tipo'] == 'Saída')
        custos_fixos = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.financeiro if i.get('Tipo') == 'Custo Fixo')
        
        saldo_livre = receitas - saidas - custos_fixos
        valor_estoque = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.estoque if i['Categoria'] == 'Material')

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Receitas Totais", f"R$ {receitas:.2f}")
        col2.metric("Insumos & Saídas", f"R$ {saidas:.2f}")
        col3.metric("Custos Fixos", f"R$ {custos_fixos:.2f}")
        col4.metric("Saldo Líquido", f"R$ {saldo_livre:.2f}")
        
        st.write("")
        st.info(f"Capital imobilizado em estoque (Insumos): **R$ {valor_estoque:.2f}**")

        st.divider()
        aba1, aba2 = st.tabs([
            ":material/add_card: Lançamento Financeiro", 
            ":material/receipt_long: Extrato Detalhado"
        ])

        with aba1:
            with st.form("form_financeiro", clear_on_submit=True):
                tipo_movimento = st.radio(
                    "Tipo de Lançamento:", 
                    ["Saída (Produtos / Insumos)", "Custo Fixo (Aluguel, Luz, Internet)", "Entrada Extra"], 
                    horizontal=True
                )
                
                desc_despesa = st.text_input("Descrição do Lançamento")
                valor_despesa = st.number_input("Valor (R$)", min_value=0.01, step=0.5, format="%.2f")
                submit_financeiro = st.form_submit_button("Salvar Registro", type="primary", icon=":material/check:")

                if submit_financeiro and desc_despesa:
                    tipo_final = "Saída"
                    if "Fixo" in tipo_movimento:
                        tipo_final = "Custo Fixo"
                    elif "Entrada" in tipo_movimento:
                        tipo_final = "Entrada"

                    st.session_state.financeiro.append({
                        'Data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                        'Tipo': tipo_final, 'Descrição': desc_despesa, 'Valor (R$)': valor_despesa
                    })
                    salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)
                    st.success("Movimentação registrada com sucesso!")
                    st.rerun()

        with aba2:
            if st.session_state.financeiro:
                df_financeiro = pd.DataFrame(st.session_state.financeiro)
                
                filtro = st.selectbox("Filtrar Registros:", ["Todos", "Entrada", "Saída", "Custo Fixo"])
                
                if filtro != "Todos":
                    df_exibir = df_financeiro[df_financeiro['Tipo'] == filtro]
                else:
                    df_exibir = df_financeiro
                
                if not df_exibir.empty:
                    st.dataframe(df_exibir, use_container_width=True)
                else:
                    st.info(f"Nenhum registro encontrado para '{filtro}'.")
            else:
                st.info("Sem movimentações no momento.")
