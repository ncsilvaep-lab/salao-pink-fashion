import base64
from datetime import datetime
import hashlib
import hmac
import html
import logging
import os
import re
import time
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ----------------------------------------
# CREDENCIAIS DE ACESSO ÚNICO
# Defina APP_USER e APP_PASSWORD nos Secrets (arquivo .streamlit/secrets.toml
# ou Settings > Secrets no Streamlit Community Cloud).
# Os valores abaixo são só um plano B para o app não ficar fora do ar.
# Depois de configurar os Secrets, apague as duas linhas abaixo.
# ----------------------------------------
_USUARIO_PADRAO = "admin"
_SENHA_PADRAO = "pink123"


SESSAO_MAX_SEGUNDOS = 8 * 3600  # a sessão expira sozinha após 8 horas

_log = logging.getLogger("pink")


def _obter_credenciais():
    """Retorna (usuario, senha_em_texto ou None, hash_da_senha ou None).

    Ordem de preferência: APP_PASSWORD_HASH (recomendado) > APP_PASSWORD >
    senha padrão antiga (plano B, remover depois de configurar os Secrets).
    """
    try:
        usuario = st.secrets.get("APP_USER", _USUARIO_PADRAO)
        senha = st.secrets.get("APP_PASSWORD", None)
        senha_hash = st.secrets.get("APP_PASSWORD_HASH", None)
    except Exception:
        usuario, senha, senha_hash = _USUARIO_PADRAO, None, None
    if not senha and not senha_hash:
        senha = _SENHA_PADRAO
    return (
        str(usuario).strip().lower(),
        str(senha).strip() if senha else None,
        str(senha_hash).strip() if senha_hash else None,
    )


def _verificar_hash_senha(senha, senha_hash):
    """Confere a senha contra 'pbkdf2_sha256$iteracoes$salt_hex$hash_hex'.

    Gere o valor com: python gerar_hash_senha.py
    """
    try:
        algoritmo, iteracoes, salt_hex, hash_hex = senha_hash.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), bytes.fromhex(salt_hex), int(iteracoes)
        )
        return hmac.compare_digest(calculado, bytes.fromhex(hash_hex))
    except Exception:
        return False


def _credenciais_conferem(usuario_in, senha_in):
    """Compara ignorando maiúsculas no usuário e espaços nas pontas.

    Teclado de celular costuma escrever 'Admin' (primeira letra maiúscula) e
    o autocompletar deixa espaço no fim; a comparação exata rejeitava os dois.
    compare_digest evita vazar informação pelo tempo de resposta.
    """
    usuario_ok, senha_ok, senha_hash = _obter_credenciais()
    u = (usuario_in or "").strip().lower()
    s = (senha_in or "").strip()
    u_confere = hmac.compare_digest(u.encode("utf-8"), usuario_ok.encode("utf-8"))
    if senha_hash:
        s_confere = _verificar_hash_senha(s, senha_hash)
    else:
        s_confere = hmac.compare_digest(s.encode("utf-8"), (senha_ok or "").encode("utf-8"))
    return u_confere and s_confere


def _limpar_texto(valor, max_len=120):
    """Tira caracteres de controle e espaços das pontas e limita o tamanho.

    Validação no servidor: o limite do campo no navegador pode ser contornado.
    """
    texto = re.sub(r"[\x00-\x1f\x7f]", " ", str(valor or "")).strip()
    return texto[:max_len]


def _erro_interno(contexto, exc):
    """Detalhe técnico vai só para o log do servidor; o usuário vê mensagem genérica."""
    _log.error("%s: %s", contexto, exc)
    st.error(f"{contexto}. Tente novamente; se continuar, avise o suporte.")


# 1. Configuração da Página
st.set_page_config(
    page_title="Salão Pink Fashion",
    page_icon=":material/content_cut:",
    layout="wide",
)

# ----------------------------------------
# CONEXÃO COM O SUPABASE
# ----------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# A conexão só é aberta quando alguma função de banco é chamada (depois do
# login). Antes, ela rodava no topo do arquivo: se o secret faltasse ou a chave
# fosse inválida, o app caía antes de desenhar a tela de login.

# ----------------------------------------
# FUNÇÕES DE INTERAÇÃO COM BANCO SUPABASE
# ----------------------------------------
def carregar_dados(tabela):
    try:
        res = init_supabase().table(tabela).select("*").execute()
        return res.data if res.data else []
    except Exception as e:
        _erro_interno(f"Não foi possível carregar {tabela}", e)
        return []

def salvar_registro(tabela, dados_dict):
    try:
        init_supabase().table(tabela).insert(dados_dict).execute()
        return True
    except Exception as e:
        _erro_interno(f"Não foi possível salvar em {tabela}", e)
        return False

def atualizar_quantidade_estoque(id_prod, nova_qtd):
    try:
        init_supabase().table("estoque").update({"quantidade": nova_qtd}).eq("id", id_prod).execute()
        return True
    except Exception as e:
        _erro_interno("Não foi possível atualizar o estoque", e)
        return False

# ----------------------------------------
# FUNÇÃO PARA CARREGAR A LOGO EM BASE64
# ----------------------------------------
def obter_logo_base64():
    caminhos_possiveis = [
        "logo.png", "logo.jpg", "logo.jpeg", "logo.webp", "LOGO.PNG", "LOGO.JPG"
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

    .stApp { background-color: #FAF6F8; font-family: 'Poppins', sans-serif; color: #3A132C; }
    h1 { font-family: 'Playfair Display', serif !important; color: #4A154B !important; font-weight: 700 !important; font-size: 40px !important; letter-spacing: -0.5px; }
    h2 { font-family: 'Playfair Display', serif !important; color: #4A154B !important; font-weight: 700 !important; font-size: 32px !important; letter-spacing: -0.5px; }
    h3 { font-family: 'Playfair Display', serif !important; color: #4A154B !important; font-weight: 600 !important; font-size: 24px !important; }
    .subtitulo-pagina { color: #77506A !important; font-size: 18px !important; font-weight: 400 !important; margin-bottom: 22px !important; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #F3E2EC !important; }
    div[data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 18px !important; font-weight: 500 !important; color: #4A154B !important; }
    div[data-testid="stForm"], div[data-testid="stMetric"], div[data-testid="stExpander"] { background-color: #FFFFFF !important; border-radius: 16px !important; padding: 22px !important; box-shadow: 0 4px 20px rgba(224, 82, 151, 0.06) !important; border: 1px solid #F5E3EE !important; }
    div[data-testid="stMetricValue"] { color: #E05297 !important; font-family: 'Playfair Display', serif !important; font-weight: 700 !important; font-size: 32px !important; }
    .stButton > button { border-radius: 12px !important; background: linear-gradient(135deg, #E05297 0%, #C2185B 100%) !important; color: #FFFFFF !important; border: none !important; font-weight: 500 !important; font-size: 15px !important; padding: 0.6rem 1.3rem !important; box-shadow: 0 4px 14px rgba(224, 82, 151, 0.25) !important; }
    button[data-baseweb="tab"] { font-family: 'Poppins', sans-serif !important; font-weight: 500 !important; font-size: 16px !important; color: #88607A !important; }
    button[aria-selected="true"] { color: #E05297 !important; border-bottom-color: #E05297 !important; }
    div[data-testid="stDataFrame"] { border-radius: 14px !important; overflow: hidden !important; border: 1px solid #F0DCE8 !important; background-color: #FFFFFF !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

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

def converter_valor(valor):
    try:
        return float(valor)
    except:
        return 0.0

# 2. Inicialização do Session State
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = ""

# 3. Tela de Login Exclusiva
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        logo_b64 = obter_logo_base64()
        if logo_b64:
            st.markdown(
                f"<div style='text-align: center;'><img src='{logo_b64}' style='max-width: 130px;'></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 20px;'>
                <h1>Salão Pink Fashion</h1>
                <p style='color: #88607A;'>Sistema Integrado de Gestão Beauty</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        if st.session_state.pop("sessao_expirada", False):
            st.info("Sua sessão expirou por segurança. Entre novamente.")
        # Dentro de um formulário, apertar Enter no campo de senha também envia.
        # Com st.button solto, o Enter só confirmava o campo e nada acontecia.
        with st.form("form_login", clear_on_submit=False):
            usuario_in = st.text_input("Usuário")
            senha_in = st.text_input("Senha", type="password")
            enviar = st.form_submit_button(
                "Acessar Painel", type="primary", use_container_width=True, icon=":material/login:"
            )

        if enviar:
            agora = time.time()
            bloqueado_ate = st.session_state.get("bloqueado_ate", 0)
            if agora < bloqueado_ate:
                st.error(f"Muitas tentativas. Aguarde {int(bloqueado_ate - agora) + 1} segundos.")
            elif _credenciais_conferem(usuario_in, senha_in):
                st.session_state.logado = True
                st.session_state.usuario_logado = (usuario_in or "").strip().lower()
                st.session_state.tentativas_login = 0
                st.session_state.login_em = time.time()
                st.rerun()
            else:
                tentativas = st.session_state.get("tentativas_login", 0) + 1
                st.session_state.tentativas_login = tentativas
                if tentativas >= 5:
                    st.session_state.bloqueado_ate = agora + 60
                    st.session_state.tentativas_login = 0
                    st.error("Muitas tentativas. Aguarde 60 segundos.")
                else:
                    st.error("Usuário ou senha incorretos.")

# 4. Sistema Principal
else:
    # Sessão com prazo: se alguém esquecer o painel aberto num aparelho, ele fecha sozinho.
    if time.time() - st.session_state.get("login_em", 0) > SESSAO_MAX_SEGUNDOS:
        st.session_state.logado = False
        st.session_state.usuario_logado = ""
        st.session_state.sessao_expirada = True
        st.rerun()

    st.sidebar.markdown("<h2 style='font-size: 28px;'>Pink Fashion</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='color: #88607A;'>Navegação do Sistema</p>", unsafe_allow_html=True)

    menu_opcoes = {
        ":material/dashboard: Menu Principal": "Dashboard",
        ":material/inventory_2: Produtos & Estoque": "Estoque",
        ":material/calendar_month: Atendimentos & Serviços": "Atendimentos",
        ":material/payments: Painel Financeiro": "Financeiro",
    }

    escolha_formatada = st.sidebar.radio(
        "Navegação", list(menu_opcoes.keys()), label_visibility="collapsed"
    )
    escolha = menu_opcoes[escolha_formatada]

    st.sidebar.divider()
    st.sidebar.markdown(f"<p>Sessão ativa: <br><strong style='color: #C2185B;'>{html.escape(st.session_state.usuario_logado.capitalize())}</strong></p>", unsafe_allow_html=True)
    
    if st.sidebar.button("Encerrar Sessão", use_container_width=True, icon=":material/logout:"):
        st.session_state.logado = False
        st.session_state.usuario_logado = ""
        st.session_state.login_em = 0
        st.rerun()

    # ----------------------------------------
    # MÓDULO 0: DASHBOARD
    # ----------------------------------------
    if escolha == "Dashboard":
        hoje_str = datetime.now().strftime("%d/%m/%Y")
        st.header("Menu Principal")
        st.markdown(f"<p class='subtitulo-pagina'>Visão geral e resumo do salão em <strong>{hoje_str}</strong></p>", unsafe_allow_html=True)

        fin_dados = carregar_dados("financeiro")
        atend_dados = carregar_dados("atendimentos")
        estoque_dados = carregar_dados("estoque")

        receitas_total = sum(converter_valor(i["valor"]) for i in fin_dados if i["tipo"] == "Entrada")
        saidas_total = sum(converter_valor(i["valor"]) for i in fin_dados if i["tipo"] == "Saída")
        custos_fixos = sum(converter_valor(i["valor"]) for i in fin_dados if i.get("tipo") == "Custo Fixo")
        saldo_livre = receitas_total - saidas_total - custos_fixos

        receitas_hoje = sum(converter_valor(i["valor"]) for i in fin_dados if i["tipo"] == "Entrada" and str(i["data"]).startswith(hoje_str))

        servicos_hoje = [a for a in atend_dados if str(a.get("data", "")) == hoje_str and a.get("tipo", "Serviço") == "Serviço"]
        vendas_hoje = [a for a in atend_dados if str(a.get("data", "")) == hoje_str and a.get("tipo") == "Venda Produto"]

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Faturamento Hoje", f"R$ {receitas_hoje:.2f}")
        col_m2.metric("Faturamento Total", f"R$ {receitas_total:.2f}")
        col_m3.metric("Saldo Líquido", f"R$ {saldo_livre:.2f}")
        col_m4.metric("Atendimentos Hoje", f"{len(servicos_hoje)}")

        st.divider()

        aba_clientes, aba_vendas, aba_alertas = st.tabs([
            ":material/calendar_month: Clientes Agendados Hoje",
            ":material/shopping_bag: Produtos Vendidos Hoje",
            ":material/warning: Alertas de Estoque",
        ])

        with aba_clientes:
            if servicos_hoje:
                df_serv = pd.DataFrame(servicos_hoje)
                st.dataframe(
                    df_serv[["cliente", "descricao", "profissional", "total"]],
                    use_container_width=True, hide_index=True,
                    column_config={
                        "cliente": "👤 Cliente",
                        "descricao": "✂️ Serviço Realizado",
                        "profissional": "💇‍♀️ Profissional",
                        "total": st.column_config.NumberColumn("💵 Valor Total", format="R$ %.2f"),
                    },
                )
            else:
                st.info("Nenhum serviço ou atendimento registrado para a data de hoje.")

        with aba_vendas:
            if vendas_hoje:
                df_vendas = pd.DataFrame(vendas_hoje)
                st.dataframe(
                    df_vendas[["cliente", "descricao", "total"]],
                    use_container_width=True, hide_index=True,
                    column_config={
                        "cliente": "👤 Cliente / Compradora",
                        "descricao": "📦 Produto(s) Vendido(s)",
                        "total": st.column_config.NumberColumn("💵 Valor Recebido", format="R$ %.2f"),
                    },
                )
            else:
                st.info("Nenhuma venda de produto registrada no balcão para a data de hoje.")

        with aba_alertas:
            if estoque_dados:
                df_e = pd.DataFrame(estoque_dados)
                df_e["Qtd_num"] = df_e["quantidade"].apply(converter_valor)
                df_baixos = df_e[df_e["Qtd_num"] <= 5].copy()

                if not df_baixos.empty:
                    df_baixos["Nível Estoque"] = df_baixos["Qtd_num"].apply(classificar_status_estoque)
                    st.dataframe(
                        df_baixos[["Nível Estoque", "produto", "quantidade", "categoria"]],
                        use_container_width=True, hide_index=True,
                        column_config={
                            "Nível Estoque": "Status",
                            "produto": "📦 Produto",
                            "quantidade": st.column_config.NumberColumn("Qtd Restante", format="%d un"),
                            "categoria": "Categoria",
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
        st.markdown("<p class='subtitulo-pagina'>Controle de cosméticos, insumos e produtos para revenda</p>", unsafe_allow_html=True)

        aba1, aba2 = st.tabs([
            ":material/add_box: Cadastrar / Entrada de Produto",
            ":material/inventory: Estoque Atual",
        ])

        with aba1:
            with st.form("form_produto", clear_on_submit=True):
                col1, col2 = st.columns(2)
                nome_produto = col1.text_input("Nome do Produto (Ex: Shampoo L'Oréal, Esmalte Risqué)")
                categoria = col2.selectbox("Finalidade / Categoria", ["Uso no Salão (Insumo)", "Revenda ao Cliente"])

                col3, col4, col5 = st.columns(3)
                qtd = col3.number_input("Quantidade a Adicionar", min_value=1, max_value=100000, step=1)
                custo = col4.number_input("Custo Unitário (R$)", min_value=0.0, max_value=1_000_000.0, value=0.0, step=1.0, format="%.2f")
                preco_venda = col5.number_input("Preço de Venda (R$)", min_value=0.0, max_value=1_000_000.0, value=0.0, step=1.0, format="%.2f")

                if st.form_submit_button("Salvar Registro / Adicionar Estoque", type="primary", icon=":material/add:"):
                    nome_produto = _limpar_texto(nome_produto, 100)
                    if nome_produto:
                        estoque_atual = carregar_dados("estoque")
                        prod_existente = next((p for p in estoque_atual if p["produto"].strip().lower() == nome_produto.strip().lower() and p["categoria"] == categoria), None)

                        if prod_existente:
                            nova_qtd = int(prod_existente["quantidade"]) + int(qtd)
                            atualizar_quantidade_estoque(prod_existente["id"], nova_qtd)
                            st.success(f"Estoque de **'{nome_produto}'** atualizado para **{nova_qtd} un**!")
                        else:
                            salvar_registro("estoque", {
                                "produto": nome_produto.strip(),
                                "categoria": categoria,
                                "quantidade": qtd,
                                "custo": custo,
                                "preco_venda": preco_venda
                            })
                            st.success(f"Novo produto **'{nome_produto}'** cadastrado no Supabase!")
                        st.rerun()

        with aba2:
            estoque_dados = carregar_dados("estoque")
            if estoque_dados:
                df_e = pd.DataFrame(estoque_dados)
                df_e["Nível Estoque"] = df_e["quantidade"].apply(classificar_status_estoque)

                df_revenda = df_e[df_e["categoria"] == "Revenda ao Cliente"]
                df_insumos = df_e[df_e["categoria"] == "Uso no Salão (Insumo)"]

                st.subheader("Produtos para Revenda")
                if not df_revenda.empty:
                    st.dataframe(
                        df_revenda[["Nível Estoque", "produto", "quantidade", "custo", "preco_venda"]],
                        use_container_width=True, hide_index=True,
                        column_config={
                            "Nível Estoque": "Status",
                            "produto": "📦 Produto",
                            "quantidade": st.column_config.NumberColumn("Qtd. Estoque", format="%d un"),
                            "custo": st.column_config.NumberColumn("Custo Un.", format="R$ %.2f"),
                            "preco_venda": st.column_config.NumberColumn("Preço Venda", format="R$ %.2f"),
                        },
                    )

                st.divider()
                st.subheader("Insumos & Produtos de Uso do Salão")
                if not df_insumos.empty:
                    st.dataframe(
                        df_insumos[["Nível Estoque", "produto", "quantidade", "custo"]],
                        use_container_width=True, hide_index=True,
                        column_config={
                            "Nível Estoque": "Status",
                            "produto": "🧼 Insumo / Material",
                            "quantidade": st.column_config.NumberColumn("Qtd. Estoque", format="%d un"),
                            "custo": st.column_config.NumberColumn("Custo Un.", format="R$ %.2f"),
                        },
                    )
            else:
                st.info("Seu estoque está vazio.")

    # ----------------------------------------
    # MÓDULO 2: ATENDIMENTOS E SERVIÇOS
    # ----------------------------------------
    elif escolha == "Atendimentos":
        st.header("Atendimentos & Serviços")
        st.markdown("<p class='subtitulo-pagina'>Registro de serviços prestados e vendas de produtos</p>", unsafe_allow_html=True)

        aba1, aba2 = st.tabs([
            ":material/add_task: Registrar Atendimento / Venda",
            ":material/history: Histórico de Atendimentos",
        ])

        with aba1:
            tipo_op = st.radio("Tipo de Operação:", ["Novo Servico / Agendamento", "Venda de Produto do Balcão"], horizontal=True)

            if tipo_op == "Novo Servico / Agendamento":
                with st.form("form_servico", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    cliente = col_a.text_input("Nome da Cliente")
                    data_atend = col_b.date_input("Data do Atendimento", format="DD/MM/YYYY")

                    col_c, col_d = st.columns(2)
                    servico = col_c.text_input("Serviço Realizado (Ex: Corte, Escova, Coloração, Manicure)")
                    profissional = col_d.text_input("Profissional Responsável")

                    valor_servico = st.number_input("Valor do Serviço (R$)", min_value=0.0, max_value=1_000_000.0, value=0.0, step=1.0, format="%.2f")

                    if st.form_submit_button("Confirmar Atendimento", type="primary", icon=":material/check_circle:"):
                        cliente = _limpar_texto(cliente, 100)
                        servico = _limpar_texto(servico, 150)
                        profissional = _limpar_texto(profissional, 100)
                        if cliente and servico:
                            data_str = data_atend.strftime("%d/%m/%Y")

                            salvar_registro("atendimentos", {
                                "tipo": "Serviço",
                                "data": data_str,
                                "cliente": cliente,
                                "descricao": servico,
                                "profissional": profissional,
                                "total": valor_servico,
                            })

                            salvar_registro("financeiro", {
                                "data": data_str,
                                "tipo": "Entrada",
                                "descricao": f"Serviço: {servico} ({cliente})",
                                "valor": valor_servico,
                            })

                            st.success(f"Atendimento registrado com sucesso (R$ {valor_servico:.2f})!")
                            st.rerun()

            elif tipo_op == "Venda de Produto do Balcão":
                estoque_dados = carregar_dados("estoque")
                prods_revenda = [item for item in estoque_dados if item["categoria"] == "Revenda ao Cliente" and int(item["quantidade"]) > 0]

                if not prods_revenda:
                    st.warning("Não há produtos cadastrados para revenda com estoque disponível.")
                else:
                    with st.form("form_venda_balcao", clear_on_submit=True):
                        col_a, col_b = st.columns(2)
                        cliente = col_a.text_input("Nome da Cliente")
                        data_venda = col_b.date_input("Data da Venda", format="DD/MM/YYYY")

                        opcoes_select = {f"{p['produto']} - R$ {p['preco_venda']} | Qtd Disp: {p['quantidade']}": p for p in prods_revenda}
                        prod_selecionado = st.selectbox("Selecione o Produto", list(opcoes_select.keys()))
                        qtd_vendida = st.number_input("Quantidade Vendida", min_value=1, step=1)

                        if st.form_submit_button("Finalizar Venda de Produto", type="primary", icon=":material/shopping_cart:"):
                            cliente = _limpar_texto(cliente, 100)
                            if cliente:
                                prod_ref = opcoes_select[prod_selecionado]
                                if qtd_vendida > int(prod_ref["quantidade"]):
                                    st.error("Estoque insuficiente!")
                                else:
                                    valor_total = float(prod_ref["preco_venda"]) * qtd_vendida
                                    data_str = data_venda.strftime("%d/%m/%Y")

                                    atualizar_quantidade_estoque(prod_ref["id"], int(prod_ref["quantidade"]) - qtd_vendida)

                                    salvar_registro("atendimentos", {
                                        "tipo": "Venda Produto",
                                        "data": data_str,
                                        "cliente": cliente,
                                        "descricao": f"{qtd_vendida}x {prod_ref['produto']}",
                                        "profissional": "-",
                                        "total": valor_total,
                                    })

                                    salvar_registro("financeiro", {
                                        "data": data_str,
                                        "tipo": "Entrada",
                                        "descricao": f"Venda Produto: {prod_ref['produto']} ({cliente})",
                                        "valor": valor_total,
                                    })

                                    st.success(f"Venda registrada com sucesso (R$ {valor_total:.2f})!")
                                    st.rerun()

        with aba2:
            atend_dados = carregar_dados("atendimentos")
            if atend_dados:
                df_atend = pd.DataFrame(atend_dados)
                st.dataframe(
                    df_atend[["tipo", "data", "cliente", "descricao", "profissional", "total"]],
                    use_container_width=True, hide_index=True,
                    column_config={
                        "tipo": "📌 Operação",
                        "data": "📅 Data",
                        "cliente": "👤 Cliente",
                        "descricao": "📝 Detalhes",
                        "profissional": "💇‍♀️ Profissional",
                        "total": st.column_config.NumberColumn("💵 Valor Total", format="R$ %.2f"),
                    },
                )
            else:
                st.info("Nenhum atendimento ou venda registrado até o momento.")

    # ----------------------------------------
    # MÓDULO 3: PAINEL FINANCEIRO
    # ----------------------------------------
    elif escolha == "Financeiro":
        st.header("Painel Financeiro")
        st.markdown("<p class='subtitulo-pagina'>Gestão de caixa, receitas, despesas variáveis e custos fixos</p>", unsafe_allow_html=True)

        aba_f1, aba_f2 = st.tabs([
            ":material/add_card: Nova Movimentação / Despesa",
            ":material/receipt_long: Extrato de Transações",
        ])

        with aba_f1:
            with st.form("form_financeiro", clear_on_submit=True):
                col_f1, col_f2 = st.columns(2)
                tipo_mov = col_f1.selectbox("Tipo de Movimentação", ["Saída (Despesa Variável)", "Custo Fixo", "Entrada Avulsa / Diversos"])
                data_mov = col_f2.date_input("Data do Registro", format="DD/MM/YYYY")

                desc_mov = st.text_input("Descrição (Ex: Conta de Luz, Compra de Toalhas, Aluguel)")
                valor_mov = st.number_input("Valor da Operação (R$)", min_value=0.0, max_value=1_000_000.0, value=0.0, step=1.0, format="%.2f")

                if st.form_submit_button("Lançar no Caixa", type="primary", icon=":material/save:"):
                    desc_mov = _limpar_texto(desc_mov, 150)
                    if desc_mov and valor_mov > 0:
                        data_str = data_mov.strftime("%d/%m/%Y")
                        tipo_salvo = "Entrada" if "Entrada" in tipo_mov else ("Custo Fixo" if tipo_mov == "Custo Fixo" else "Saída")

                        salvar_registro("financeiro", {
                            "data": data_str,
                            "tipo": tipo_salvo,
                            "descricao": desc_mov,
                            "valor": valor_mov,
                        })
                        st.success(f"Movimentação **'{desc_mov}'** de **R$ {valor_mov:.2f}** salva com sucesso!")
                        st.rerun()

        with aba_f2:
            fin_dados = carregar_dados("financeiro")
            if fin_dados:
                tot_entradas = sum(converter_valor(i["valor"]) for i in fin_dados if i["tipo"] == "Entrada")
                tot_saidas = sum(converter_valor(i["valor"]) for i in fin_dados if i["tipo"] == "Saída")
                tot_custos_fixos = sum(converter_valor(i["valor"]) for i in fin_dados if i.get("tipo") == "Custo Fixo")
                saldo_liquido = tot_entradas - tot_saidas - tot_custos_fixos

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Entradas", f"R$ {tot_entradas:.2f}")
                c2.metric("Despesas Variáveis", f"R$ {tot_saidas:.2f}")
                c3.metric("Custos Fixos", f"R$ {tot_custos_fixos:.2f}")
                c4.metric("Saldo Líquido", f"R$ {saldo_liquido:.2f}")

                st.divider()

                df_fin = pd.DataFrame(fin_dados)
                st.dataframe(
                    df_fin[["data", "tipo", "descricao", "valor"]],
                    use_container_width=True, hide_index=True,
                    column_config={
                        "data": "📅 Data",
                        "tipo": "🏷️ Categoria",
                        "descricao": "📝 Descrição",
                        "valor": st.column_config.NumberColumn("💵 Valor", format="R$ %.2f"),
                    },
                )
            else:
                st.info("Nenhuma movimentação financeira registrada até o momento.")
