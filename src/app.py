import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Concilia DFe", layout="wide")

# Cabeçalho formal
st.title("📄 Concilia DFe")
st.caption("Aplicação para comparar listas de Documentos Fiscais Eletrônicos (DF-e) contidas em planilhas eletrônicas.")

st.markdown("""
Este sistema permite identificar **incongruências documentais** entre duas ou três listas distintas de documentos fiscais, 
como **documentos não localizados** em determinada referência ou **documentos não previstos** em outra.
""")

# Layout de upload em 3 colunas
col1, col2, col3 = st.columns(3)

uploaded_files = []
configs = []

# Função para configurar cada arquivo
def configurar_arquivo(col, index, key_prefix):
    with col:
        file = st.file_uploader(f"📄 Arquivo {index + 1}", type=["xls", "xlsx"], key=f"{key_prefix}_file")
        if file:
            try:
                xls = pd.ExcelFile(file)
                with st.expander(f"⚙️ Configuração de leitura - {file.name}", expanded=True):
                    aba = st.selectbox(f"🗂️ Aba a ser considerada", xls.sheet_names, key=f"{key_prefix}_sheet")
                    tem_cabecalho = st.checkbox("📝 A planilha possui cabeçalho?", value=True, key=f"{key_prefix}_header")
                    linha_inicial = st.number_input(
                        "📍 Linha inicial dos dados (1 = primeira)", min_value=1,
                        value=2 if tem_cabecalho else 1, key=f"{key_prefix}_startrow"
                    )
                    coluna_chave = st.text_input("🔑 Nome exato da coluna com o número do documento fiscal", key=f"{key_prefix}_coluna")
                    
                    if coluna_chave:
                        df = pd.read_excel(
                            file,
                            sheet_name=aba,
                            header=0 if tem_cabecalho else None,
                            skiprows=linha_inicial - (1 if tem_cabecalho else 0)
                        )
                        if coluna_chave not in df.columns:
                            st.warning(f"⚠️ A coluna '{coluna_chave}' não foi localizada em {file.name}.")
                        else:
                            df[coluna_chave] = df[coluna_chave].astype(str).str.strip()
                            st.success(f"✅ {file.name}: {len(df)} registros lidos.")
                            return file, df, coluna_chave
                    else:
                        st.info("✏️ Informe o nome exato da coluna a ser utilizada como referência de comparação.")
            except Exception as e:
                st.error(f"Erro ao processar {file.name}: {e}")
    return None, None, None

# Configuração dos arquivos
for idx, (col, prefix) in enumerate(zip([col1, col2, col3], ["a", "b", "c"])):
    file, df, coluna = configurar_arquivo(col, idx, prefix)
    if file and df is not None:
        uploaded_files.append(file)
        configs.append((df, coluna))

if len(configs) < 2:
    st.warning("Envie e configure pelo menos dois arquivos para habilitar a conciliação.")
    st.stop()

# Função de exportação Excel
def gerar_excel(dict_dfs):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for nome, df in dict_dfs.items():
            df.to_excel(writer, index=False, sheet_name=nome[:31])
    output.seek(0)
    return output

# Comparar dois arquivos e mostrar resultados formalmente
def comparar_dois_arquivos(idx_a, idx_b):
    df_a, col_a = configs[idx_a]
    df_b, col_b = configs[idx_b]
    nome_a = uploaded_files[idx_a].name
    nome_b = uploaded_files[idx_b].name

    set_a = set(df_a[col_a].dropna().astype(str).str.strip())
    set_b = set(df_b[col_b].dropna().astype(str).str.strip())

    nao_localizado_em_b = list(set_a - set_b)
    nao_localizado_em_a = list(set_b - set_a)

    st.subheader(f"📊 Incongruências entre {nome_a} e {nome_b}")

    resultados = {}

    st.markdown(f"🔴 **Documentos não localizados em {nome_b}** ({len(nao_localizado_em_b)} registros)")
    df_b_falta = pd.DataFrame({f"Ausentes em {nome_b} (referência: {nome_a})": nao_localizado_em_b})
    st.dataframe(df_b_falta)
    resultados[f"Ausentes_em_{nome_b}"] = df_b_falta

    st.markdown(f"🔵 **Documentos não localizados em {nome_a}** ({len(nao_localizado_em_a)} registros)")
    df_a_falta = pd.DataFrame({f"Ausentes em {nome_a} (referência: {nome_b})": nao_localizado_em_a})
    st.dataframe(df_a_falta)
    resultados[f"Ausentes_em_{nome_a}"] = df_a_falta

    # Download
    excel_bytes = gerar_excel(resultados)
    st.download_button(
        label=f"📥 Baixar incongruências entre {nome_a} e {nome_b}",
        data=excel_bytes,
        file_name=f"incongruencias_{idx_a+1}_{idx_b+1}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Executar comparação
if st.button("🔍 Executar conciliação"):
    with st.spinner("Processando documentos fiscais..."):
        comparar_dois_arquivos(0, 1)
        if len(configs) >= 3:
            comparar_dois_arquivos(0, 2)
            comparar_dois_arquivos(1, 2)
