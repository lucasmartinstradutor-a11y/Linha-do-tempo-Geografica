import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Linha do Tempo de Geografia",
    page_icon="🌍",
    layout="wide"
)

# URL da planilha do Google Sheets no formato de exportação CSV
SHEET_ID = "1Q3IsRvT5KmR72NtWYuHSqKz50xdP9S4a-U5z6UAacTQ"
SHEET_GID = "0"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"

# Função para carregar os dados, com cache para otimizar a performance
@st.cache_data(ttl=600) # Atualiza os dados a cada 10 minutos
def load_data(url):
    """Carrega os dados da planilha pública do Google Sheets."""
    try:
        df = pd.read_csv(url)
        # Remove linhas que estejam completamente vazias
        df.dropna(how='all', inplace=True)
        # CORREÇÃO: Renomeia as colunas para garantir consistência
        df.columns = ['Data', 'Titulo', 'Descricao', 'Tema']
        return df
    except Exception as e:
        st.error(f"Não foi possível carregar os dados da planilha. Verifique o link e as permissões de compartilhamento. Erro: {e}")
        return pd.DataFrame()

# Carrega os dados
df = load_data(GOOGLE_SHEET_URL)

# --- Interface do Usuário ---

st.title("🌍 Linha do Tempo Interativa de Temas Geográficos")
st.markdown("Do Século XVIII ao XXI, com dados carregados diretamente de uma planilha do Google Sheets.")

if not df.empty:
    # --- Barra Lateral para Filtros ---
    st.sidebar.header("Filtros")

    # Obtém os temas únicos da coluna "Tema"
    themes = df['Tema'].dropna().unique()
    # Adiciona a opção "Todos" no início da lista de temas
    filter_options = ["Todos"] + sorted(list(themes))

    # Cria o seletor de tema na barra lateral
    selected_theme = st.sidebar.selectbox(
        "Selecione um Tema:",
        options=filter_options
    )

    # --- Lógica de Filtragem ---
    if selected_theme == "Todos":
        filtered_df = df
    else:
        filtered_df = df[df['Tema'] == selected_theme]

    # --- Exibição da Linha do Tempo ---
    if not filtered_df.empty:
        st.markdown(f"### Exibindo eventos para: **{selected_theme}**")

        # Itera sobre cada linha do DataFrame filtrado para criar a linha do tempo
        for index, row in filtered_df.iterrows():
            # CORREÇÃO: Usa os novos nomes de coluna consistentes
            with st.expander(f"**{row['Data']}** - {row['Titulo']}"):
                st.markdown(f"**Tema:** `{row['Tema']}`")
                st.write(row['Descricao'])
    else:
        st.warning("Nenhum evento encontrado para o tema selecionado.")

else:
    st.info("Aguardando o carregamento dos dados...")

# Adiciona um rodapé
st.markdown("---")
st.markdown("Aplicação desenvolvida com Python e Streamlit.")
