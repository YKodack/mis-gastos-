import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

st.set_page_config(page_title="Mi Contabilidad Total", page_icon="💰", layout="wide")

st.title("🏦 Mi Gestión Financiera")
st.markdown("---")

# Archivos de datos
ARCHIVO_GASTOS = "mis_gastos.csv"
ARCHIVO_INGRESOS = "mis_ingresos.csv"

# Funciones para cargar datos
def cargar_datos(nombre_archivo, columnas):
    if os.path.exists(nombre_archivo):
        return pd.read_csv(nombre_archivo)
    else:
        return pd.DataFrame(columns=columnas)

df_gastos = cargar_datos(ARCHIVO_GASTOS, ["Fecha", "Categoría", "Descripción", "Monto"])
df_ingresos = cargar_datos(ARCHIVO_INGRESOS, ["Fecha", "Fuente", "Monto"])

# --- SECCIÓN DE ENTRADA ---
col_in, col_ga = st.columns(2)

with col_in:
    with st.form("form_ingreso", clear_on_submit=True):
        st.subheader("💵 Registrar Ingreso")
        f_ing = st.date_input("Fecha Ingreso", datetime.now())
        fuente = st.text_input("Fuente (Sueldo Cine, Ventas, etc.)")
        monto_ing = st.number_input("Monto Recibido ($)", min_value=0.0)
        if st.form_submit_button("Añadir Ingreso"):
            nuevo_i = pd.DataFrame([[f_ing.strftime("%d/%m/%Y"), fuente, monto_ing]], columns=df_ingresos.columns)
            df_ingresos = pd.concat([df_ingresos, nuevo_i], ignore_index=True)
            df_ingresos.to_csv(ARCHIVO_INGRESOS, index=False)
            st.rerun()

with col_ga:
    with st.form("form_gasto", clear_on_submit=True):
        st.subheader("💸 Registrar Gasto")
        f_gas = st.date_input("Fecha Gasto", datetime.now())
        cat = st.selectbox("Categoría", ["Comida", "Transporte", "Estudios", "Cine/Ocio", "Ventas", "Otros"])
        desc = st.text_input("¿En qué gastaste?")
        monto_gas = st.number_input("Monto Gastado ($)", min_value=0.0)
        if st.form_submit_button("Añadir Gasto"):
            nuevo_g = pd.DataFrame([[f_gas.strftime("%d/%m/%Y"), cat, desc, monto_gas]], columns=df_gastos.columns)
            df_gastos = pd.concat([df_gastos, nuevo_g], ignore_index=True)
            df_gastos.to_csv(ARCHIVO_GASTOS, index=False)
            st.rerun()

# --- BALANCE TOTAL ---
st.divider()
total_ingresos = df_ingresos["Monto"].sum()
total_gastos = df_gastos["Monto"].sum()
balance = total_ingresos - total_gastos

c1, c2, c3 = st.columns(3)
c1.metric("Total Ingresos", f"${total_ingresos:,.2f}")
c2.metric("Total Gastos", f"- ${total_gastos:,.2f}")
c3.metric("Disponible Real", f"${balance:,.2f}")

# --- TABLAS EDITABLES ---
st.divider()
st.subheader("📝 Edición Directa de Cuentas")

col_tab1, col_tab2 = st.columns(2)

with col_tab1:
    st.write("**Ingresos**")
    df_ing_edit = st.data_editor(df_ingresos, num_rows="dynamic", key="ed_ing", use_container_width=True)
    if st.button("💾 Guardar Ingresos"):
        df_ing_edit.to_csv(ARCHIVO_INGRESOS, index=False)
        st.rerun()

with col_tab2:
    st.write("**Gastos**")
    df_gas_edit = st.data_editor(df_gastos, num_rows="dynamic", key="ed_gas", use_container_width=True)
    if st.button("💾 Guardar Gastos"):
        df_gas_edit.to_csv(ARCHIVO_GASTOS, index=False)
        st.rerun()
