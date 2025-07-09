import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparador de Documentos Fiscais", layout="wide")
st.title("📄 Comparador de Documentos Fiscais (Excel)")
st.markdown("Faça upload de **2 ou 3 arquivos Excel**, indique a coluna de comparação, e veja os documentos faltantes.")

uploaded_files = st.file_uploader("Selecione até 3 arquivos Excel", type=["xlsx"], accept_multiple_files=True)

if len(uploaded_files) < 2:
    st.info("Envie pelo menos 2 arquivos para comparar.")
else:
    colname = st.text_input("Nome da coluna com a chave do documento fiscal", value="ChaveNFe")

    if colname:
        dfs = []
        for i, f in enumerate(uploaded_files):
            try:
                df = pd.read_excel(f)
                if colname not in df.columns:
                    st.error(f"❌ A coluna '{colname}' não foi encontrada no arquivo {f.name}.")
                    break
                df[colname] = df[colname].astype(str).str.strip()
                dfs.append(set(df[colname].dropna()))
                st.success(f"✅ {f.name}: {len(dfs[-1])} documentos carregados.")
            except Exception as e:

                st.error(f"❌ Erro ao processar {f.name}: {e}")
                break