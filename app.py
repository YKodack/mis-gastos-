import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configuración profesional
st.set_page_config(page_title="Mi Wallet Inteligente", page_icon="💳", layout="wide")

# Estilo visual
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Mi Panel de Control Financiero")

# --- ARCHIVOS ---
ARCHIVO = "contabilidad_total.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO):
        return pd.read_csv(ARCHIVO)
    return pd.DataFrame(columns=["Fecha", "Tipo", "Categoría", "Descripción", "Monto"])

df = cargar_datos()

# --- REGISTRO LATERAL ---
st.sidebar.header("🎯 Nuevo Movimiento")
with st.sidebar.form("registro", clear_on_submit=True):
    tipo = st.selectbox("Tipo", ["Gasto", "Ingreso"])
    cat = st.selectbox("Categoría", [
        "Sueldo Cine", "Ventas Snacks", "Comida", "Facultad", 
        "Viajes", "Cine/Ocio", "Deudas", "Otros"
    ])
    desc = st.text_input("Descripción")
    monto = st.number_input("Monto ($)", min_value=0.0, step=10.0)
    fecha = st.date_input("Fecha", datetime.now())
    
    if st.form_submit_button("Guardar"):
        nuevo = pd.DataFrame([[fecha.strftime("%Y-%m-%d"), tipo, cat, desc, monto]], columns=df.columns)
        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_csv(ARCHIVO, index=False)
        st.toast("¡Guardado!", icon="✅")
        st.rerun()

# --- MÉTRICAS ---
total_ing = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
total_gas = df[df["Tipo"] == "Gasto"]["Monto"].sum()
balance = total_ing - total_gas

c1, c2, c3 = st.columns(3)
c1.metric("💰 Ingresos", f"${total_ing:,.2f}")
c2.metric("💸 Gastos", f"${total_gas:,.2f}")
c3.metric("⚖️ Disponible", f"${balance:,.2f}")

st.divider()

# --- PESTAÑAS INTERACTIVAS ---
tab1, tab2, tab3 = st.tabs(["📊 Gráficas", "📑 Libro Contable", "✈️ Viajes"])

with tab1:
    if not df[df["Tipo"] == "Gasto"].empty:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_pie = px.pie(df[df["Tipo"] == "Gasto"], values='Monto', names='Categoría', 
                           title='¿En qué gasto más?', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_g2:
            fig_bar = px.bar(df[df["Tipo"] == "Gasto"], x='Categoría', y='Monto', 
                            title='Gastos por Categoría', color='Categoría')
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Registra un gasto para ver el análisis.")

with tab2:
    st.subheader("Historial de Cuentas")
    st.write("Puedes editar cualquier celda directamente.")
    
    # Tabla editable
    df_edit = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="main_editor")
    
    col_b1, col_b2 = st.columns([1, 4])
    with col_b1:
        if st.button("💾 Guardar Cambios"):
            df_edit.to_csv(ARCHIVO, index=False)
            st.success("¡Sincronizado!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("🗑️ Zona de Borrado")
    if not df.empty:
        if st.button("❌ Borrar ÚLTIMO registro"):
            df = df[:-1]
            df.to_csv(ARCHIVO, index=False)
            st.warning("Último movimiento eliminado.")
            st.rerun()
    else:
        st.write("No hay nada que borrar todavía.")

with tab3:
    st.subheader("Plan de Viajes")
    presupuesto = st.number_input("¿Cuánto quieres juntar para tu viaje?", min_value=0.0, value=2000.0)
    gastado_viaje = df[df["Categoría"] == "Viajes"]["Monto"].sum()
    st.write(f"Has gastado **${gastado_viaje:,.2f}** en viajes.")
    
    if presupuesto > 0:
        progreso = min(max(balance / presupuesto, 0.0), 1.0)
        st.progress(progreso)
        st.write(f"Tu disponible actual cubre el **{progreso*100:.1f}%** de tu meta.")
