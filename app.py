import streamlit as st
import pandas as pd
from datetime import datetime
import os
import smtplib
import random
from email.mime.text import MIMEText

# ----------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ----------------------------------------
st.set_page_config(
    page_title="Salão Pink Fashion", 
    page_icon="💅", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (MODERNA)
# ----------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Estilização de Botões */
    .stButton > button {
        background: linear-gradient(135deg, #e91e63 0%, #ff4081 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(233, 30, 99, 0.25) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(233, 30, 99, 0.4) !important;
    }

    /* Cards de Métricas no Financeiro */
    div[data-testid="stMetric"] {
        background: rgba(233, 30, 99, 0.03);
        border: 1px solid rgba(233, 30, 99, 0.15);
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
    }
    
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #888888;
    }

    /* Modificação das Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(233, 30, 99, 0.1) !important;
        color: #e91e63 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------
# FUNÇÕES DE ESTILIZAÇÃO DO ESTOQUE
# ----------------------------------------
def colorir_estoque_pecas(row):
    """Aplica cores para Produtos com base na coluna 'Quantidade'"""
    try:
        qtd = float(row['Quantidade'])
    except (ValueError, TypeError):
        return [''] * len(row)
    
    if qtd <= 5:
        # Vermelho (Estoque baixo)
        style = 'background-color: #ffcdd2; color: #801010; font-weight: 600;'
    elif qtd <= 10:
        # Amarelo (Estoque médio)
        style = 'background-color: #fff9c4; color: #7a5c00; font-weight: 600;'
    else:
        # Verde (Estoque alto)
        style = 'background-color: #c8e6c9; color: #1b5e20; font-weight: 600;'
    return [style] * len(row)

def colorir_estoque_materiais(row):
    """Aplica cores para Materiais com base na coluna 'Metragem'"""
    try:
        qtd = float(row['Metragem'])
    except (ValueError, TypeError):
        return [''] * len(row)
    
    if qtd <= 5:
        style = 'background-color: #ffcdd2; color: #801010; font-weight: 600;'
    elif qtd <= 10:
        style = 'background-color: #fff9c4; color: #7a5c00; font-weight: 600;'
    else:
        style = 'background-color: #c8e6c9; color: #1b5e20; font-weight: 600;'
    return [style] * len(row)

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
    except Exception:
        return False

# ----------------------------------------
# CONFIGURAÇÃO DE ARQUIVOS LOCAIS
# ----------------------------------------
PASTA_DRIVE = "dados_sistema_pink_fashion"
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
    except Exception:
        return 0.0

# ----------------------------------------
# 2. INICIALIZAÇÃO DO ESTADO
# ----------------------------------------
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

# ----------------------------------------
# 3. TELA DE LOGIN E CADASTRO
# ----------------------------------------
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        if os.path.exists("logo.jpg"):
            c1, c2, c3 = st.columns([1, 1.2, 1])
            with c2:
                st.image("logo.jpg", use_container_width=True)
        elif os.path.exists("logo.png"):
            c1, c2, c3 = st.columns([1, 1.2, 1])
            with c2:
                st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center; color: #e91e63;'>💖 Salão Pink Fashion</h1>", unsafe_allow_html=True)
            
        st.markdown("<h4 style='text-align: center; color: #888888; font-weight: 400; margin-top: -10px;'>Gestão & Beleza</h4>", unsafe_allow_html=True)
        st.write("")
        
        aba_login, aba_cadastro = st.tabs(["🔐 Entrar", "📝 Cadastrar Novo Usuário"])

        with aba_login:
            st.write("Faça login para acessar a plataforma:")
            usuario = st.text_input("👤 Usuário")
            senha = st.text_input("🔑 Senha", type="password")

            if st.button("Entrar no Sistema", type="primary", use_container_width=True):
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
                    st.error("❌ Usuário ou senha incorretos!")

        with aba_cadastro:
            if st.session_state.etapa_cadastro == 1:
                st.write("Digite seu e-mail para receber o código de validação:")
                email_input = st.text_input("📧 Seu E-mail")
                
                if st.button("Enviar Código", type="primary", use_container_width=True):
                    if "@" in email_input and "." in email_input:
                        codigo = str(random.randint(100000, 999999))
                        st.session_state.codigo_gerado = codigo
                        st.session_state.email_temp = email_input
                        
                        sucesso_email = enviar_codigo_email(email_input, codigo)
                        
                        if sucesso_email:
                            st.success(f"Código enviado para {email_input}!")
                            st.session_state.etapa_cadastro = 2
                            st.rerun()
                        else:
                            st.warning(f"Erro no envio do e-mail. Para testes, o código é: {codigo}")
                            st.session_state.etapa_cadastro = 2 
                    else:
                        st.error("Por favor, digite um e-mail válido.")

            elif st.session_state.etapa_cadastro == 2:
                st.info(f"Um código de 6 dígitos foi enviado para: {st.session_state.email_temp}")
                codigo_digitado = st.text_input("🔢 Digite o Código", max_chars=6)
                
                col_voltar, col_avancar = st.columns(2)
                if col_voltar.button("⬅️ Voltar"):
                    st.session_state.etapa_cadastro = 1
                    st.rerun()
                    
                if col_avancar.button("Validar Código", type="primary"):
                    if codigo_digitado == st.session_state.codigo_gerado:
                        st.success("Código Validado!")
                        st.session_state.etapa_cadastro = 3
                        st.rerun()
                    else:
                        st.error("❌ Código Incorreto!")

            elif st.session_state.etapa_cadastro == 3:
                st.write("Crie as credenciais da sua nova conta:")
                novo_usuario = st.text_input("👤 Defina um Nome de Usuário")
                nova_senha = st.text_input("🔑 Defina uma Senha", type="password")
                
                if st.button("Finalizar Cadastro", type="primary", use_container_width=True):
                    if novo_usuario and nova_senha:
                        st.session_state.usuarios.append({
                            'email': st.session_state.email_temp, 
                            'usuario': novo_usuario, 
                            'senha': nova_senha
                        })
                        salvar_dados(st.session_state.usuarios, ARQ_USUARIOS)
                        st.success("✅ Cadastro concluído! Faça login na aba 'Entrar'.")
                        st.session_state.etapa_cadastro = 1 
                    else:
                        st.error("Preencha todos os campos!")

        st.markdown("""
            <div style='text-align: center; margin-top: 50px;'>
                <p style='font-family: "Courier New", Courier, monospace; font-size: 13px; color: #888888; letter-spacing: 0.5px;'>
                    Desenvolvido por <span style='font-weight: bold; color: #ff4b4b;'>Optimus engenharia jr</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

# ----------------------------------------
# 4. SISTEMA PRINCIPAL
# ----------------------------------------
else:
    st.sidebar.markdown("<h2 style='color: #e91e63;'>💅 Pink Fashion</h2>", unsafe_allow_html=True)
    menu = ["📦 Estoque & Produtos", "🛍️ Atendimentos & Vendas", "📊 Painel Financeiro"]
    escolha = st.sidebar.radio("Navegação principal:", menu)

    st.sidebar.divider()
    st.sidebar.write(f"✨ Usuário conectado: **{st.session_state.usuario_logado.capitalize()}**")
    if st.sidebar.button("🚪 Sair da Conta", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

    # ----------------------------------------
    # MÓDULO 1: ESTOQUE E PRODUTOS
    # ----------------------------------------
    if escolha == "📦 Estoque & Produtos":
        st.header("💅 Gestão de Estoque e Produtos")
        aba1, aba2 = st.tabs(["➕ Novo Cadastro", "📋 Inventário Atual"])

        with aba1:
            categoria = st.radio("Selecione o tipo de item:", ["Produto Pronto (Venda)", "Insumo / Cosmético (Uso do Salão)"], horizontal=True)
            st.divider()

            if categoria == "Produto Pronto (Venda)":
                with st.form("form_peca", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    produto = col1.text_input("Nome do Produto/Cosmético")
                    tamanho = col2.text_input("Tamanho / Volume (Ex: 250ml, Único, Kit)")

                    col3, col4 = st.columns(2)
                    valor = col3.number_input("Valor de Venda (R$)", min_value=0.0, step=0.5, format="%.2f")
                    disponibilidade = col4.number_input("Quantidade em Estoque", min_value=0, step=1)

                    submit_peca = st.form_submit_button("Cadastrar Produto", type="primary")

                    if submit_peca and produto:
                        st.session_state.estoque.append({
                            'Categoria': 'Peça Pronta', 'Produto': produto,
                            'Tamanho': tamanho, 'Valor (R$)': valor, 'Quantidade': disponibilidade,
                            'Cor': '-', 'Metragem': '-', 'Foto': '-'
                        })
                        salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)
                        st.success(f"✅ Produto '{produto}' registrado com sucesso!")

            elif categoria == "Insumo / Cosmético (Uso do Salão)":
                with st.form("form_material", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    produto = col1.text_input("Nome do Material / Insumo")
                    cor = col2.text_input("Cor / Tonalidade (Se houver)")

                    col3, col4, col5 = st.columns(3)
                    metragem = col3.number_input("Qtd / Unidades", min_value=0.0, step=0.1)
                    valor_material = col4.number_input("Custo Total de Compra (R$)", min_value=0.0, step=0.5, format="%.2f")
                    foto = col5.file_uploader("Foto do Produto", type=["png", "jpg", "jpeg"])

                    submit_material = st.form_submit_button("Cadastrar Insumo", type="primary")

                    if submit_material and produto:
                        nome_foto = foto.name if foto is not None else "Sem foto"
                        st.session_state.estoque.append({
                            'Categoria': 'Material', 'Produto': produto,
                            'Tamanho': '-', 'Valor (R$)': valor_material, 'Quantidade': '-',
                            'Cor': cor, 'Metragem': metragem, 'Foto': nome_foto
                        })
                        salvar_dados(st.session_state.estoque, ARQ_ESTOQUE)
                        st.success(f"✅ Insumo '{produto}' salvo!")

        with aba2:
            if st.session_state.estoque:
                # Legenda das Cores
                st.markdown("""
                <div style="background-color: rgba(0,0,0,0.02); padding: 10px 15px; border-radius: 8px; border: 1px solid #eeeeee; margin-bottom: 20px;">
                    <strong>🎨 Legenda de Alerta de Estoque:</strong>&nbsp;&nbsp;&nbsp;&nbsp;
                    <span style="background-color: #ffcdd2; color: #801010; padding: 3px 10px; border-radius: 5px; font-weight: bold;">🔴 1 a 5 un (Baixo)</span>&nbsp;&nbsp;
                    <span style="background-color: #fff9c4; color: #7a5c00; padding: 3px 10px; border-radius: 5px; font-weight: bold;">🟡 5 a 10 un (Médio)</span>&nbsp;&nbsp;
                    <span style="background-color: #c8e6c9; color: #1b5e20; padding: 3px 10px; border-radius: 5px; font-weight: bold;">🟢 Mais de 10 un (Alto)</span>
                </div>
                """, unsafe_allow_html=True)

                df_estoque = pd.DataFrame(st.session_state.estoque)
                
                st.subheader("🛍️ Produtos para Venda")
                df_pecas = df_estoque[df_estoque['Categoria'] == 'Peça Pronta']
                if not df_pecas.empty:
                    df_pecas_styled = df_pecas.style.apply(colorir_estoque_pecas, axis=1)
                    st.dataframe(df_pecas_styled, use_container_width=True)
                else:
                    st.info("Nenhum produto cadastrado para venda.")
                
                st.divider()

                st.subheader("💄 Insumos e Materiais de Uso")
                df_materiais = df_estoque[df_estoque['Categoria'] == 'Material']
                if not df_materiais.empty:
                    df_materiais_styled = df_materiais.style.apply(colorir_estoque_materiais, axis=1)
                    st.dataframe(df_materiais_styled, use_container_width=True)
                else:
                    st.info("Nenhum insumo cadastrado no estoque.")
            else:
                st.info("O estoque está vazio no momento.")

    # ----------------------------------------
    # MÓDULO 2: ATENDIMENTOS E VENDAS
    # ----------------------------------------
    elif escolha == "🛍️ Atendimentos & Vendas":
        st.header("🛍️ Atendimentos, Agendamentos e Vendas")
        aba1, aba2 = st.tabs(["🛒 Novo Registro", "🧾 Histórico de Movimentações"])

        with aba1:
            tipo_registro = st.radio("Selecione o tipo de operação:", ["Venda de Produto (Pronta Entrega)", "Agendamento / Serviço Personalizado"], horizontal=True)
            st.divider()

            if tipo_registro == "Venda de Produto (Pronta Entrega)":
                pecas_disponiveis = [item for item in st.session_state.estoque if item['Categoria'] == 'Peça Pronta' and str(item['Quantidade']).isdigit() and int(item['Quantidade']) > 0]
                
                if not pecas_disponiveis:
                    st.warning("⚠️ Não há produtos com estoque disponível no momento.")
                else:
                    with st.form("form_venda_estoque", clear_on_submit=True):
                        col_a, col_b = st.columns(2)
                        nome_cliente = col_a.text_input("Nome da Cliente")
                        data_venda = col_b.date_input("Data do Atendimento/Venda", format="DD/MM/YYYY")
                        
                        opcoes_select = {f"{p['Produto']} ({p['Tamanho']}) - R$ {p['Valor (R$)']} | Qtd: {p['Quantidade']} un": p for p in pecas_disponiveis}
                        
                        peca_selecionada = st.selectbox("Selecione o Produto", list(opcoes_select.keys()))
                        
                        col_c, col_d = st.columns(2)
                        qtd_vendida = col_c.number_input("Quantidade", min_value=1, step=1)
                        desconto = col_d.number_input("Desconto (R$)", min_value=0.0, step=0.5, format="%.2f")

                        submit_venda = st.form_submit_button("Concluir Venda", type="primary")

                        if submit_venda and nome_cliente:
                            peca_ref = opcoes_select[peca_selecionada]
                            
                            if qtd_vendida > int(peca_ref['Quantidade']):
                                st.error(f"❌ Estoque insuficiente! Apenas {peca_ref['Quantidade']} unidade(s) disponível(is).")
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
                                    'Descrição': f"Venda Produto: {peca_ref['Produto']} ({nome_cliente})", 'Valor (R$)': valor_total
                                })
                                salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)

                                st.success(f"✅ Venda efetuada com sucesso! (R$ {valor_total:.2f})")
                                st.rerun()

            elif tipo_registro == "Agendamento / Serviço Personalizado":
                with st.form("form_pedidos", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    nome_cliente = col_a.text_input("Nome da Cliente")
                    data_entrega = col_b.date_input("Data Agendada para o Serviço", format="DD/MM/YYYY")

                    st.divider()
                    produto_vendido = st.text_input("Serviço Solicitado (Ex: Cabelo, Unhas, Maquiagem)")

                    col_c, col_d = st.columns(2)
                    qtd_vendida = col_c.number_input("Quantidade de Procedimentos", min_value=1, step=1)
                    valor_total = col_d.number_input("Valor Combinado (R$)", min_value=0.0, step=0.5, format="%.2f")

                    submit_pedido = st.form_submit_button("Agendar / Confirmar Serviço", type="primary")

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
                            'Descrição': f"Serviço Agendado: {produto_vendido} ({nome_cliente})", 'Valor (R$)': valor_total
                        })
                        salvar_dados(st.session_state.financeiro, ARQ_FINANCEIRO)

                        st.success(f"✅ Agendamento do serviço gravado! (R$ {valor_total:.2f})")

        with aba2:
            if st.session_state.vendas:
                df_vendas = pd.DataFrame(st.session_state.vendas)
                if 'Tipo' not in df_vendas.columns:
                    df_vendas['Tipo'] = 'Pedido'

                st.subheader("🛍️ Vendas de Produtos Realizadas")
                df_vendas_prontas = df_vendas[df_vendas['Tipo'] == 'Venda'].drop(columns=['Tipo'], errors='ignore')
                if not df_vendas_prontas.empty:
                    st.dataframe(df_vendas_prontas, use_container_width=True)
                else:
                    st.info("Nenhuma venda de produto efetuada até o momento.")
                
                st.divider()

                st.subheader("💇‍♀️ Serviços e Agendamentos Registrados")
                df_pedidos_encomendas = df_vendas[df_vendas['Tipo'] == 'Pedido'].drop(columns=['Tipo'], errors='ignore')
                if not df_pedidos_encomendas.empty:
                    st.dataframe(df_pedidos_encomendas, use_container_width=True)
                else:
                    st.info("Nenhum serviço agendado até o momento.")
            else:
                st.info("Nenhum histórico de registros encontrado.")

    # ----------------------------------------
    # MÓDULO 3: FINANCEIRO
    # ----------------------------------------
    elif escolha == "📊 Painel Financeiro":
        st.header("📊 Gestão Financeira e Métricas")

        receitas = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.financeiro if i['Tipo'] == 'Entrada')
        saidas = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.financeiro if i['Tipo'] == 'Saída')
        custos_fixos = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.financeiro if i.get('Tipo') == 'Custo Fixo')
        
        saldo_livre = receitas - saidas - custos_fixos
        valor_estoque = sum(converter_valor(i['Valor (R$)']) for i in st.session_state.estoque if i['Categoria'] == 'Material')

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Faturamento (Receitas)", f"R$ {receitas:.2f}")
        col2.metric("Despesas Variáveis", f"R$ {saidas:.2f}")
        col3.metric("Custos Fixos", f"R$ {custos_fixos:.2f}")
        col4.metric("Lucro Líquido", f"R$ {saldo_livre:.2f}", delta=f"R$ {saldo_livre:.2f}", delta_color="normal")
        
        st.write("")
        st.info(f"💎 **Patrimônio em Materiais e Cosméticos:** R$ {valor_estoque:.2f}")

        st.divider()
        aba1, aba2 = st.tabs(["💸 Nova Movimentação", "📈 Extrato Detalhado"])

        with aba1:
            with st.form("form_financeiro", clear_on_submit=True):
                tipo_movimento = st.radio(
                    "Tipo de Lançamento:", 
                    ["Saída (Variável - ex: compra de produtos, descartáveis)", "Custo Fixo (ex: aluguel, energia, taxa de sistemas)", "Entrada Extra"], 
                    horizontal=True
                )
                
                desc_despesa = st.text_input("Descrição do Lançamento")
                valor_despesa = st.number_input("Valor (R$)", min_value=0.01, step=0.5, format="%.2f")
                submit_financeiro = st.form_submit_button("Registrar Movimentação", type="primary")

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
                    st.success(f"✅ Lançamento '{tipo_final}' gravado com sucesso!")
                    st.rerun()

        with aba2:
            if st.session_state.financeiro:
                df_financeiro = pd.DataFrame(st.session_state.financeiro)
                
                st.subheader("Relatório Geral de Caixas")
                filtro = st.selectbox("Filtrar lançamentos:", ["Todos", "Entrada", "Saída", "Custo Fixo"])
                
                if filtro != "Todos":
                    df_exibir = df_financeiro[df_financeiro['Tipo'] == filtro]
                else:
                    df_exibir = df_financeiro
                
                if not df_exibir.empty:
                    st.dataframe(df_exibir, use_container_width=True)
                else:
                    st.info(f"Nenhum lançamento do tipo '{filtro}' encontrado.")
            else:
                st.info("Nenhuma movimentação lançada no sistema.")
