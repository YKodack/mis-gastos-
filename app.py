import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Configuración de estilo "App"
st.set_page_config(page_title="Mi Administración Financiera", page_icon="📈", layout="wide")

st.title("📱 Mi Administrador de Cuentas")
st.markdown("---")

# Archivos de base de datos
ARCHIVOS = {
    "gastos": "mis_gastos.csv",
    "ingresos": "mis_ingresos.csv",
    "deudas": "mis_deudas.csv"
}

# Cargar datos de forma segura
def cargar(archivo, columnas):
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    return pd.DataFrame(columns=columnas)

df_gastos = cargar(ARCHIVOS["gastos"], ["Fecha", "Categoría", "Descripción", "Monto"])
df_ingresos = cargar(ARCHIVOS["ingresos"], ["Fecha", "Fuente", "Monto"])
df_deudas = cargar(ARCHIVOS["deudas"], ["A quién se le debe", "Concepto", "Monto", "Estado"])

# --- PANEL LATERAL (ENTRADA DE DATOS) ---
st.sidebar.header("➕ Registrar Movimiento")
tipo = st.sidebar.radio("¿Qué quieres registrar?", ["Gasto", "Ingreso", "Deuda"])

if tipo == "Ingreso":
    with st.sidebar.form("f_ing"):
        f = st.date_input("Fecha")
        src = st.text_input("Fuente (Sueldo Cine, Ventas, etc.)")
        m = st.number_input("Cantidad ($)", min_value=0.0)
        if st.form_submit_button("Guardar Ingreso"):
            nuevo = pd.DataFrame([[f.strftime("%d/%m/%Y"), src, m]], columns=df_ingresos.columns)
            pd.concat([df_ingresos, nuevo], ignore_index=True).to_csv(ARCHIVOS["ingresos"], index=False)
            st.rerun()

elif tipo == "Gasto":
    with st.sidebar.form("f_gas"):
        f = st.date_input("Fecha")
        cat = st.selectbox("Categoría", ["Comida", "Transporte", "Estudios", "Cine/Ocio", "Ventas", "Otros"])
        desc = st.text_input("Descripción")
        m = st.number_input("Cantidad ($)", min_value=0.0)
        if st.form_submit_button("Guardar Gasto"):
            nuevo = pd.DataFrame([[f.strftime("%d/%m/%Y"), cat, desc, m]], columns=df_gastos.columns)
            pd.concat([df_gastos, nuevo], ignore_index=True).to_csv(ARCHIVOS["gastos"], index=False)
            st.rerun()

else:
    with st.
