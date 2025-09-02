import streamlit as st
import pandas as pd
import io
from datetime import datetime
import random


st.set_page_config(page_title="Startify", layout="wide")


if "users" not in st.session_state:
    st.session_state.users = {}  
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "produtos" not in st.session_state:
    st.session_state.produtos = []


def generate_id():
    return int(datetime.now().timestamp()*1000) + random.randint(0, 999)

def save_image_bytes(uploaded_file):
    if uploaded_file:
        return uploaded_file.getvalue()
    return None

def export_products_csv():
    df = pd.DataFrame(st.session_state.produtos)
    if df.empty:
        return None
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


st.markdown(
    """
    <div style='padding:15px 30px; background-color:#f4f4f4; border-bottom:1px solid #ddd'>
        <h2 style='margin:0'>Startify</h2>
        <p style='margin:0; color:#555'>Plataforma para criação e gerenciamento de produtos digitais</p>
    </div>
    """,
    unsafe_allow_html=True
)


if st.session_state.current_user:
    page = st.sidebar.radio("Menu", ["Dashboard", "Criar Produto", "Meus Produtos", "Sair"])
else:
    page = st.sidebar.radio("Menu", ["Início", "Criar Conta", "Entrar"])


if page == "Início":
    st.header("Bem-vindo ao Startify")
    st.write("""
    Crie, gerencie e acompanhe seus produtos digitais de forma prática.
    Experimente criar uma conta e começar agora!
    """)

elif page == "Criar Conta":
    st.header("Criar Conta - Onboarding")
    st.write("Preencha seu nome e e-mail para começar")

    
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    if st.button("Próximo"):
        if not nome or not email:
            st.error("Preencha todos os campos")
        else:
            st.session_state.onboarding = {"nome": nome, "email": email}
            st.success("Informações registradas. Agora escolha sua senha e avatar.")

    
    if "onboarding" in st.session_state:
        senha = st.text_input("Senha", type="password")
        senha2 = st.text_input("Confirmar senha", type="password")
        if st.button("Finalizar Cadastro"):
            if not senha or senha != senha2:
                st.error("As senhas não conferem")
            else:
                username = email.split("@")[0]
                st.session_state.users[username] = {
                    "name": st.session_state.onboarding["nome"],
                    "email": email,
                    "password": senha,
                    "created_at": datetime.now().isoformat()
                }
                st.session_state.current_user = username
                st.success(f"Conta criada com sucesso! Bem-vindo, {nome}")
                del st.session_state.onboarding

elif page == "Entrar":
    st.header("Entrar na sua conta")
    username = st.text_input("Usuário (parte antes do @ do e-mail)")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = st.session_state.users.get(username)
        if user and user["password"] == password:
            st.session_state.current_user = username
            st.success(f"Login realizado. Bem-vindo, {user['name']}")
        else:
            st.error("Usuário ou senha incorretos")


def require_login(func):
    def wrapper(*args, **kwargs):
        if st.session_state.current_user is None:
            st.warning("É necessário entrar para acessar esta página.")
            return
        return func(*args, **kwargs)
    return wrapper

@require_login
def dashboard():
    st.header("Dashboard")
    st.write(f"Olá, {st.session_state.users[st.session_state.current_user]['name']}")
    meus_produtos = [p for p in st.session_state.produtos if p["owner"]==st.session_state.current_user]
    st.metric("Produtos criados", len(meus_produtos))
    st.metric("Produtos vendidos (simulado)", sum([random.randint(0,5) for _ in meus_produtos]))
    st.markdown("### Últimos produtos")
    for p in meus_produtos[-5:]:
        st.markdown(f"- {p['name']} - R$ {p['price']:.2f} - {p['category']}")

@require_login
def criar_produto():
    st.header("Criar Produto")
    with st.form("form_produto"):
        nome = st.text_input("Nome do produto")
        preco = st.number_input("Preço (R$)", min_value=0.0, step=1.0)
        categoria = st.selectbox("Categoria", ["Curso", "E-book", "Template", "Serviço", "Outro"])
        descricao = st.text_area("Descrição")
        imagem = st.file_uploader("Imagem (opcional)", type=["jpg","png","jpeg"])
        submitted = st.form_submit_button("Salvar")
        if submitted:
            if not nome or preco <= 0 or not descricao:
                st.error("Preencha todos os campos corretamente")
            else:
                st.session_state.produtos.append({
                    "id": generate_id(),
                    "owner": st.session_state.current_user,
                    "name": nome,
                    "price": preco,
                    "category": categoria,
                    "description": descricao,
                    "image": save_image_bytes(imagem),
                    "created_at": datetime.now().isoformat()
                })
                st.success(f"Produto '{nome}' criado com sucesso!")

@require_login
def listar_produtos():
    st.header("Meus Produtos")
    meus_produtos = [p for p in st.session_state.produtos if p["owner"]==st.session_state.current_user]
    if not meus_produtos:
        st.info("Nenhum produto cadastrado")
    else:
        df = pd.DataFrame(meus_produtos)
        st.dataframe(df[["id","name","price","category","created_at"]])
        csv = export_products_csv()
        if csv:
            st.download_button("Exportar CSV", data=csv, file_name="meus_produtos.csv")

@require_login
def sair():
    st.session_state.current_user = None
    st.success("Você saiu da conta")
    st.experimental_rerun()


if page == "Dashboard":
    dashboard()
elif page == "Criar Produto":
    criar_produto()
elif page == "Meus Produtos":
    listar_produtos()
elif page == "Sair":
    sair()


st.markdown(
    f"<div style='padding:10px 30px; color:#888; font-size:13px; text-align:center;'>Startify - Plataforma original de produtos digitais © {datetime.now().year}</div>",
    unsafe_allow_html=True
)
