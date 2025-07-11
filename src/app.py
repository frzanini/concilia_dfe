import streamlit as st
import pandas as pd

st.set_page_config(page_title="Concilia Documentos Fiscais", layout="wide")
st.title("📄 Comparador de Documentos Fiscais (Excel)")
st.markdown("Envie 2 ou 3 arquivos Excel e configure a leitura de cada um antes de comparar.")

# Upload individual de arquivos
uploaded_files = [
    st.file_uploader("🟦 Arquivo 1", type=["xlsx"], key="file1"),
    st.file_uploader("🟧 Arquivo 2", type=["xlsx"], key="file2"),
    st.file_uploader("🟨 Arquivo 3 (opcional)", type=["xlsx"], key="file3")
]

valid_files = [f for f in uploaded_files if f is not None]
if len(valid_files) < 2:
    st.warning("Você deve enviar pelo menos 2 arquivos.")
    st.stop()

dfs = []
colunas_usadas = []

st.subheader("⚙️ Configuração de Leitura por Arquivo")

# Coletar configurações individuais
for i, file in enumerate(valid_files):
    with st.expander(f"📄 Configurar leitura - Arquivo {i+1}: {file.name}", expanded=True):
        try:
            # Carrega apenas as abas disponíveis
            xls = pd.ExcelFile(file)
            aba = st.selectbox(f"🗂️ Aba a ser lida ({file.name})", xls.sheet_names, key=f"sheet_{i}")

            tem_cabecalho = st.checkbox("Possui cabeçalho (linha de títulos)?", value=True, key=f"header_{i}")
            linha_inicial = st.number_input("📍 Linha onde começam os dados (1 = primeira)", min_value=1, value=1 if tem_cabecalho else 1, key=f"startrow_{i}")

            # Entrada manual da coluna de comparação
            coluna_chave = st.text_input("🔑 Nome da coluna a ser usada na comparação", key=f"coluna_chave_{i}")

            if coluna_chave:
                df = pd.read_excel(
                    file,
                    sheet_name=aba,
                    header=0 if tem_cabecalho else None,
                    skiprows=linha_inicial - (1 if tem_cabecalho else 0)
                )

                if coluna_chave not in df.columns:
                    st.warning(f"⚠️ A coluna '{coluna_chave}' não foi encontrada em {file.name}. Verifique o nome exato.")
                else:
                    df[coluna_chave] = df[coluna_chave].astype(str).str.strip()
                    dfs.append(df)
                    colunas_usadas.append(coluna_chave)
                    st.success(f"✅ {file.name}: {len(df)} linhas carregadas da aba '{aba}'.")
            else:
                st.info("✏️ Digite o nome da coluna que deseja comparar.")
        except Exception as e:
            st.error(f"Erro ao processar {file.name}: {e}")
            st.stop()

# Executar comparação se tudo estiver certo
if len(dfs) >= 2 and len(dfs) == len(colunas_usadas) and st.button("🔍 Comparar documentos"):
    try:
        conjuntos = []
        for df, coluna in zip(dfs, colunas_usadas):
            chaves = df[coluna].dropna().astype(str).str.strip()
            conjuntos.append(set(chaves))

        intersecao = set.intersection(*conjuntos)
        st.subheader("🔁 Documentos em comum")
        st.write(f"✅ Total em comum: **{len(intersecao)}**")
        st.dataframe(pd.DataFrame({"Comuns": list(intersecao)}))

        # Faltantes e excedentes por arquivo
        for i in range(1, len(conjuntos)):
            faltando = conjuntos[0] - conjuntos[i]
            excedente = conjuntos[i] - conjuntos[0]

            st.markdown(f"❗ Faltando no arquivo {uploaded_files[i].name}: {len(faltando)}")
            st.dataframe(pd.DataFrame({f"Faltando no {uploaded_files[i].name}": list(faltando)}))

            st.markdown(f"📤 Excedentes no arquivo {uploaded_files[i].name}: {len(excedente)}")
            st.dataframe(pd.DataFrame({f"Excedentes no {uploaded_files[i].name}": list(excedente)}))
    except Exception as e:
        st.error(f"Erro na comparação: {e}")
