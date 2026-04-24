import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configuración visual
st.set_page_config(page_title="Mi Contador de Dinero", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    h1 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Control de Dinero Rápido")

# --- BASE DE DATOS ---
ARCHIVO = "mi_dinero.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO):
        return pd.read_csv(ARCHIVO)
    return pd.DataFrame(columns=["Fecha", "Concepto", "Monto", "Tipo"])

df = cargar_datos()

# --- PANEL DE SALDO (LO QUE TE QUEDA) ---
ingresos = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
gastos = df[df["Tipo"] == "Gasto"]["Monto"].sum()
saldo_actual = ingresos - gastos

st.subheader("💰 Mi Saldo Disponible")
st.metric(label="Dinero en la bolsa", value=f"${saldo_actual:,.2f}", delta=f"Gastado: -${gastos:,.2f}", delta_color="inverse")

st.divider()

# --- ENTRADA RÁPIDA ---
col_form, col_espacio = st.columns([1, 1])

with col_form:
    st.subheader("📝 ¿Qué pasó hoy?")
    with st.form("entrada_rapida", clear_on_submit=True):
        tipo_mov = st.radio("Elige uno:", ["Gasto 💸", "Ingreso 💵"], horizontal=True)
        concepto = st.text_input("¿Qué fue? (ej: Nómina, Uber, Comida)", placeholder="Escribe aquí...")
        monto = st.number_input("¿Cuánto dinero? ($)", min_value=0.0, step=1.0)
        
        if st.form_submit_button("¡Registrar ahora!"):
            tipo_final = "Ingreso" if "💵" in tipo_mov else "Gasto"
            nuevo = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y"), concepto, monto, tipo_final]], 
                                columns=df.columns)
            df = pd.concat([df, nuevo], ignore_index=True)
            df.to_csv(ARCHIVO, index=False)
            st.success(f"Registrado: {concepto} por ${monto}")
            st.rerun()

# --- TABLA Y GRÁFICA (SE ACTUALIZAN SOLAS) ---
st.divider()
col_tab, col_gra = st.columns([1.2, 1])

with col_tab:
    st.subheader("📋 Mi Historial")
    # Tabla estilo Excel para editar o borrar
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="editor")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Guardar cambios / Borrar filas"):
            df_editado.to_csv(ARCHIVO, index=False)
            st.rerun()
    with c2:
        if st.button("🗑️ Resetear todo (Cero)"):
            if os.path.exists(ARCHIVO):
                os.remove(ARCHIVO)
                st.rerun()

with col_gra:
    st.subheader("📊 Mis Gastos")
    if not df[df["Tipo"] == "Gasto"].empty:
        df_g = df[df["Tipo"] == "Gasto"]
        fig = px.pie(df_g, values='Monto', names='Concepto', hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay gastos todavía.")
