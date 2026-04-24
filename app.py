import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Mi Control Financiero", page_icon="💳", layout="wide")

# Estilo para que parezca una App moderna
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3; }
    </style>
    """, unsafe_allow_html=True)

st.title("📱 Mi Administrador de Dinero")
st.write(f"Resumen al día: **{datetime.now().strftime('%d/%m/%Y')}**")

# --- ARCHIVO DE DATOS ---
ARCHIVO = "mis_cuentas.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO):
        return pd.read_csv(ARCHIVO)
    return pd.DataFrame(columns=["Fecha", "Tipo", "Categoría", "Detalle", "Monto"])

df = cargar_datos()

# --- 1. RESUMEN RÁPIDO (TARJETAS) ---
ingresos_t = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
gastos_t = df[df["Tipo"] == "Gasto"]["Monto"].sum()
disponible = ingresos_t - gastos_t

c1, c2, c3 = st.columns(3)
c1.metric("💰 Entradas (Ingresos)", f"${ingresos_t:,.2f}")
c2.metric("💸 Salidas (Gastos)", f"${gastos_t:,.2f}")
c3.metric("⚖️ Saldo Disponible", f"${disponible:,.2f}")

st.divider()

# --- 2. REGISTRO FÁCIL (COLUMNA IZQUIERDA) Y GRÁFICA (DERECHA) ---
col_form, col_graph = st.columns([1, 1.5])

with col_form:
    st.subheader("➕ Nuevo Registro")
    with st.form("registro", clear_on_submit=True):
        tipo = st.radio("Tipo:", ["Gasto", "Ingreso"], horizontal=True)
        cat = st.selectbox("Categoría:", [
            "Sueldo Cine", "Venta Snacks", "Comida", "Facultad", 
            "Viajes", "Cine/Ocio", "Deudas", "Otros"
        ])
        det = st.text_input("¿En qué o de dónde?")
        mon = st.number_input("Cantidad ($):", min_value=0.0, step=10.0)
        fec = st.date_input("Fecha:", datetime.now())
        
        if st.form_submit_button("Añadir a la lista"):
            nuevo = pd.DataFrame([[fec.strftime("%Y-%m-%d"), tipo, cat, det, mon]], columns=df.columns)
            df = pd.concat([df, nuevo], ignore_index=True)
            df.to_csv(ARCHIVO, index=False)
            st.success("¡Guardado!")
            st.rerun()

with col_graph:
    st.subheader("📊 Gráfica Interactiva")
    if not df[df["Tipo"] == "Gasto"].empty:
        df_g = df[df["Tipo"] == "Gasto"]
        # Gráfica de pastel interactiva
        fig = px.pie(df_g, values='Monto', names='Categoría', 
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aquí aparecerá tu gráfica de pastel cuando registres gastos.")

# --- 3. TABLA ESTILO EXCEL (EDITABLE) ---
st.divider()
st.subheader("📝 Tu Historial (Estilo Excel)")
st.write("Haz doble clic en cualquier número o texto para cambiarlo. Al terminar, dale al botón de abajo.")

# El editor de datos permite borrar filas seleccionándolas y dando a la tecla 'Supr' o 'Delete'
df_editado = st.data_editor(
    df, 
    num_rows="dynamic", 
    use_container_width=True, 
    key="editor_excel",
    column_config={
        "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Ingreso", "Gasto"]),
        "Categoría": st.column_config.SelectboxColumn("Categoría", options=[
            "Sueldo Cine", "Venta Snacks", "Comida", "Facultad", "Viajes", "Cine/Ocio", "Deudas", "Otros"
        ])
    }
)

col_b1, col_b2 = st.columns([1, 4])
with col_b1:
    if st.button("💾 Guardar cambios"):
        df_editado.to_csv(ARCHIVO, index=False)
        st.success("¡Cuentas actualizadas!")
        st.rerun()

with col_b2:
    if st.button("🗑️ Borrar TODO"):
        if os.path.exists(ARCHIVO):
            os.remove(ARCHIVO)
            st.error("Se borró todo el historial.")
            st.rerun()
