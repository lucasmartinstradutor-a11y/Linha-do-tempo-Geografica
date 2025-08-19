# app.py
import re
import io
from datetime import datetime
from typing import List

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Linha do Tempo de Geografia", page_icon="🗺️", layout="wide")

# ===================== CONFIG =====================
# ID da sua planilha:
SHEET_ID = "1Q3IsRvT5KmR72NtWYuHSqKz50xdP9S4a-U5z6UAacTQ"

# CSV da primeira aba (sem precisar de GID):
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# Colunas esperadas (qualquer capitalização): period, title, description, theme
REQUIRED_COLS = ["period", "title", "description", "theme"]


# ===================== UTIL =====================
def first_year_from_text(text: str) -> int:
    """
    Extrai o primeiro ano (4 dígitos) do texto.
    Se não achar, retorna 10**9 para empurrar para o final.
    """
    if not isinstance(text, str):
        return 10**9
    m = re.search(r"(\d{4})", text)
    return int(m.group(1)) if m else 10**9


def split_themes(theme_str: str) -> List[str]:
    """
    Divide a coluna de temas em lista de temas.
    Aceita separações como 'e', '/', ',', ';' etc.
    """
    if not isinstance(theme_str, str):
        return []
    # divide por ' e ' (pt), vírgula, ponto e vírgula, barra ou &.
    parts = re.split(r"\s+e\s+|[,;/&]", theme_str, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mapeia nomes de colunas (case-insensitive) para o esperado: period,title,description,theme.
    """
    colmap = {c.lower().strip(): c for c in df.columns}
    out = pd.DataFrame()
    for want in REQUIRED_COLS:
        # tenta achar a coluna correspondente ignorando maiúsc/minúsc
        if want in colmap:
            out[want] = df[colmap[want]]
        else:
            # fallback para nomes próximos
            fallback = None
            for c in df.columns:
                if want in c.lower():
                    fallback = c
                    break
            if fallback is not None:
                out[want] = df[fallback]
            else:
                out[want] = ""
    return out


@st.cache_data(show_spinner=False)
def load_data_from_sheet() -> pd.DataFrame:
    """
    Lê o CSV público do Google Sheets e normaliza as colunas.
    Se falhar, retorna um pequeno dataset local (fallback).
    """
    try:
        df = pd.read_csv(CSV_URL)
        df = normalize_columns(df)
    except Exception:
        # Fallback local (poucos eventos) se não conseguir ler a planilha
        data = [
            {
                "period": "A partir de 1760",
                "title": "Primeira Revolução Industrial",
                "description": "Transição da manufatura para a maquinofatura, uso do carvão e máquina a vapor.",
                "theme": "Geografia Econômica",
            },
            {
                "period": "1884-1885",
                "title": "Conferência de Berlim",
                "description": "Formalização da 'Partilha da África' pelas potências europeias.",
                "theme": "Geopolítica",
            },
            {
                "period": "1939-1945",
                "title": "Segunda Guerra Mundial",
                "description": "Consolidou EUA e URSS como superpotências; início da ordem bipolar.",
                "theme": "Geopolítica",
            },
        ]
        df = pd.DataFrame(data)
    # enriquecimentos:
    df["year_key"] = df["period"].apply(first_year_from_text)
    df["themes_list"] = df["theme"].apply(split_themes)
    return df


def filter_df(df: pd.DataFrame, selected_themes: List[str], query: str) -> pd.DataFrame:
    # filtro por temas (se nenhum selecionado, não filtra)
    if selected_themes:
        df = df[df["themes_list"].apply(lambda lst: any(t in lst for t in selected_themes))]
    # filtro por texto
    if query:
        q = query.strip().lower()
        mask = (
            df["title"].astype(str).str.lower().str.contains(q)
            | df["description"].astype(str).str.lower().str.contains(q)
            | df["period"].astype(str).str.lower().str.contains(q)
            | df["theme"].astype(str).str.lower().str.contains(q)
        )
        df = df[mask]
    return df.sort_values(["year_key", "title"], ascending=[True, True])


# ===================== UI =====================
st.title("Linha do Tempo de Temas Geográficos")
st.caption("Do Século XVIII ao XXI • dados vindos de planilha do Google Sheets")

df = load_data_from_sheet()

# Painel de filtros
with st.sidebar:
    st.header("Filtros")
    all_themes = sorted({t for lst in df["themes_list"] for t in lst})
    selected = st.multiselect("Temas", options=all_themes, default=[])
    query = st.text_input("Busca (título/descrição/tema)", "")
    st.markdown("---")
    st.write(f"Eventos carregados: **{len(df)}**")

filtered = filter_df(df, selected, query)

# Baixar CSV filtrado
csv_bytes = filtered[REQUIRED_COLS].to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Baixar CSV (filtrado)", data=csv_bytes, file_name="timeline_filtrado.csv", mime="text/csv")

st.write("")  # espaçamento

# ===== CSS para timeline =====
st.markdown(
    """
<style>
.tl-container {
  position: relative;
  margin: 0 auto;
  padding: 12px 0 12px 0;
}
.tl-line {
  position: absolute;
  top: 0; bottom: 0;
  left: 50%;
  width: 3px;
  background: #d1d5db;
  transform: translateX(-50%);
}
.tl-item {
  display: grid;
  grid-template-columns: 1fr 60px 1fr;
  gap: 14px;
  align-items: center;
  margin: 14px 0;
}
.tl-dot {
  width: 16px; height: 16px; 
  background: #9ca3af; 
  border-radius: 9999px;
  margin: 0 auto;
}
.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.period { color:#6b7280; font-size: 0.9rem; margin-bottom: 6px; }
.title  { color:#111827; font-weight: 700; margin-bottom: 6px; font-size: 1.05rem; }
.desc   { color:#374151; font-size: 0.95rem; }
.theme  { color:#8b5cf6; font-size: 0.85rem; margin-top: 8px; }
</style>
""",
    unsafe_allow_html=True,
)

# ===== Render =====
st.markdown('<div class="tl-container"><div class="tl-line"></div>', unsafe_allow_html=True)

# alterna L/R
for i, row in filtered.iterrows():
    left_html = f"""
    <div class="card">
      <div class="period">{row['period']}</div>
      <div class="title">{row['title']}</div>
      <div class="desc">{str(row['description'])[:160]}{"..." if len(str(row['description']))>160 else ""}</div>
      <div class="theme">{" • ".join(row["themes_list"])}</div>
    </div>
    """

    right_html = f"""
    <div class="card">
      <div class="period">{row['period']}</div>
      <div class="title">{row['title']}</div>
      <div class="desc">{str(row['description'])[:160]}{"..." if len(str(row['description']))>160 else ""}</div>
      <div class="theme">{" • ".join(row["themes_list"])}</div>
    </div>
    """

    # coluna de detalhes: usa popover (um “quase-modal” super simples)
    with st.container():
        st.markdown('<div class="tl-item">', unsafe_allow_html=True)

        # lado esquerdo
        c1, c2, c3 = st.columns([1, 0.16, 1])
        if i % 2 == 0:
            c1.markdown(left_html, unsafe_allow_html=True)
            c3.write("")  # vazio
        else:
            c1.write("")  # vazio
            c3.markdown(right_html, unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="tl-dot"></div>', unsafe_allow_html=True)
            with st.popover("Ver detalhes"):
                st.markdown(f"### {row['title']}")
                st.write(row["description"])
                st.caption("Feche o popover para voltar à linha do tempo.")

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # fecha tl-container

if filtered.empty:
    st.info("Nenhum evento encontrado com os filtros atuais.")
