import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuração da página
st.set_page_config(
    page_title="Linha do Tempo de Geografia",
    page_icon="🌍",
    layout="wide"
)

# --- Configuração das Fontes de Dados (Planilhas) ---
SHEET_ID = "1Q3IsRvT5KmR72NtWYuHSqKz50xdP9S4a-U5z6UAacTQ"

# Dicionário com os nomes, GIDs e tipos de cada aba
SOURCES = {
    "Geografia Mundial": {"gid": "0", "type": "timeline"},
    "História do Brasil": {"gid": "SEU_GID_AQUI", "type": "timeline"},
    "Líderes do Brasil": {"gid": "918682842", "type": "leaders"}
}

# Função para carregar os dados
@st.cache_data(ttl=600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.dropna(how='all', inplace=True)
        return df
    except Exception as e:
        st.error(f"Não foi possível carregar os dados da planilha. Verifique o link, o GID e as permissões de compartilhamento. Erro: {e}")
        return pd.DataFrame()

# --- Função de Geração de HTML para a Linha do Tempo ---

def generate_timeline_html(df):
    """Gera o código HTML para a linha do tempo visual a partir de um DataFrame."""
    timeline_css = """
    <style>
        body { font-family: 'Inter', sans-serif; margin: 0; padding: 0; }
        .timeline-container { position: relative; padding: 2rem 0; max-width: 1000px; margin: 0 auto; }
        .timeline-container::before { content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 3px; height: 100%; background-color: #D1D5DB; }
        .timeline-item { padding: 10px 40px; position: relative; width: 50%; box-sizing: border-box; }
        .timeline-item.left { left: 0; }
        .timeline-item.right { left: 50%; }
        .timeline-item::after { content: ''; position: absolute; width: 20px; height: 20px; right: -10px; background-color: white; border: 4px solid #FF9F55; top: 25px; border-radius: 50%; z-index: 1; }
        .timeline-item.right::after { left: -10px; }
        .timeline-content { padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); }
        .timeline-content h2 { font-size: 1.25rem; font-weight: bold; color: #374151; }
        .timeline-content p { font-size: 0.9rem; line-height: 1.6; color: #4B5563; }
        .timeline-date { font-size: 0.875rem; font-weight: 500; color: #6B7280; margin-bottom: 0.5rem; }
        .timeline-theme { display: inline-block; background-color: #FFF7ED; color: #FB923C; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; margin-top: 1rem; }
        @media screen and (max-width: 768px) {
            .timeline-container::before { left: 10px; }
            .timeline-item { width: 100%; padding-left: 50px; padding-right: 10px; }
            .timeline-item.left, .timeline-item.right { left: 0%; }
            .timeline-item.left::after, .timeline-item.right::after { left: 1px; }
        }
    </style>
    """
    items_html = ""
    for index, row in df.iterrows():
        position = "left" if index % 2 == 0 else "right"
        items_html += f"""
        <div class="timeline-item {position}">
            <div class="timeline-content">
                <div class="timeline-date">{row['Data']}</div>
                <h2>{row['Titulo']}</h2>
                <p>{row['Descricao']}</p>
                <div class="timeline-theme">{row['Tema']}</div>
            </div>
        </div>
        """
    return f"<html><head>{timeline_css}</head><body><div class='timeline-container'>{items_html}</div></body></html>"

# --- Interface Principal ---

st.title("🌍 Linha do Tempo e Análises Geográficas")

# Seletor na barra lateral para escolher a visualização
selected_source_name = st.sidebar.radio(
    "Escolha a visualização:",
    options=list(SOURCES.keys())
)

source_info = SOURCES[selected_source_name]
selected_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={source_info['gid']}"
df = load_data(selected_url)

st.markdown(f"### Visualizando: **{selected_source_name}**")

if not df.empty:
    # --- Lógica para adaptar os dados e renderizar ---
    
    filtered_df = pd.DataFrame()

    if source_info['type'] == 'timeline':
        # Renomeia as colunas para o padrão da linha do tempo
        df.columns = ['Data', 'Titulo', 'Descricao', 'Tema']
        
        # Adiciona o filtro de tema
        st.sidebar.header("Filtros")
        themes = df['Tema'].dropna().unique()
        filter_options = ["Todos"] + sorted(list(themes))
        selected_theme = st.sidebar.selectbox("Selecione um Tema:", options=filter_options)

        filtered_df = df if selected_theme == "Todos" else df[df['Tema'] == selected_theme]
        st.markdown(f"Exibindo eventos para: **{selected_theme}**")

    elif source_info['type'] == 'leaders':
        # Adapta as colunas dos líderes para o formato da linha do tempo
        df.columns = ['Data', 'Titulo', 'Descricao', 'Tema'] # 'Períodos' vira o 'Tema'
        filtered_df = df # Mostra todos os líderes, sem filtro de tema

    # --- Renderização ---
    if not filtered_df.empty:
        # Gera e renderiza o HTML da linha do tempo
        timeline_html = generate_timeline_html(filtered_df)
        height = 100 + (len(filtered_df) * 180) # Altura calculada
        components.html(timeline_html, height=height, scrolling=True)
    else:
        st.warning("Nenhum evento encontrado para a seleção atual.")

else:
    st.info("Aguardando o carregamento dos dados... Certifique-se de que o GID da planilha está correto e que ela está compartilhada publicamente.")

# Rodapé
st.markdown("---")
st.markdown("Aplicação desenvolvida com Python e Streamlit.")
