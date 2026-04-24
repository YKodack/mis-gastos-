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
        src = st.text_input("Fuente (Sueldo, Venta, etc.)")
        m = st.number_input("Cantidad ($)", min_value=0.0)
        if st.form_submit_button("Guardar Ingreso"):
            nuevo = pd.DataFrame([[f.strftime("%d/%m/%Y"), src, m]], columns=df_ingresos.columns)
            pd.concat([df_ingresos, nuevo]).to_csv(ARCHIVOS["ingresos"], index=False)
            st.rerun()

elif tipo == "Gasto":
    with st.sidebar.form("f_gas"):
        f = st.date_input("Fecha")
        cat = st.selectbox("Categoría", ["Comida", "Transporte", "Estudios", "Cine/Ocio", "Ventas", "Otros"])
        desc = st.text_input("Descripción")
        m = st.number_input("Cantidad ($)", min_value=0.0)
        if st.form_submit_button("Guardar Gasto"):
            nuevo = pd.DataFrame([[f.strftime("%d/%m/%Y"), cat, desc, m]], columns=df_gastos.columns)
            pd.concat([df_gastos, nuevo]).to_csv(ARCHIVOS["gastos"], index=False)
            st.rerun()

else:
    with st.sidebar.form("f_deu"):
        persona = st.text_input("¿A quién le debes?")
        con = st.text_input("¿Por qué?")
        m = st.number_input("Monto de la deuda ($)", min_value=0.0)
        est = st.selectbox("Estado", ["Pendiente", "Pagado"])
        if st.form_submit_button("Guardar Deuda"):
            nuevo = pd.DataFrame([[persona, con, m, est]], columns=df_deudas.columns)
            pd.concat([df_deudas, nuevo]).to_csv(ARCHIVOS["deudas"], index=False)
            st.rerun()

# --- DASHBOARD PRINCIPAL ---
total_ing = df_ingresos["Monto"].sum()
total_gas = df_gastos["Monto"].sum()
# Solo sumamos las deudas que dicen "Pendiente"
total_deu = df_deudas[df_deudas["Estado"] == "Pendiente"]["Monto"].sum()
saldo_real = total_ing - total_gas

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Ingresos", f"${total_ing:,.2f}")
col2.metric("💸 Total Gastos", f"${total_gas:,.2f}")
col3.metric("⚠️ Debes (Pendiente)", f"${total_deu:,.2f}", delta_color="inverse")
col4.metric("⚖️ Saldo Actual", f"${saldo_real:,.2f}")

st.divider()

# --- SECCIÓN DE ADMINISTRACIÓN ---
st.subheader("📝 Gestión de Tablas y Gráficas")
t1, t2, t3 = st.tabs(["📊 Gráficas de Control", "🧾 Ver Ingresos y Gastos", "🚩 Control de Deudas"])

with t1:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.write("**Distribución de Gastos**")
        if not df_gastos.empty:
            res = df_gastos.groupby("Categoría")["Monto"].sum()
            fig, ax = plt.subplots()
            res.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=plt.cm.Pastel1.colors)
            st.pyplot(fig)
    with col_g2:
        st.write("**Estado de Deudas**")
        if not df_deudas.empty:
            res_d = df_deudas.groupby("Estado")["Monto"].sum()
            fig2, ax2 = plt.subplots()
            res_d.plot(kind='bar', color=['red', 'green'], ax=ax2)
            st.pyplot(fig2)

with t2:
    st.info("Puedes editar los montos directamente en la tabla y dar clic en 'Sincronizar'")
    c_i, c_g = st.columns(2)
    with c_i:
        st.write("**Tabla de Ingresos**")
        ed_i = st.data_editor(df_ingresos, num_rows="dynamic", key="i_ed", use_container_width=True)
        if st.button("Sincronizar Ingresos"):
            ed_i.to_csv(ARCHIVOS["ingresos"], index=False)
            st.rerun()
    with c_g:
        st.write("**Tabla de Gastos**")
        ed_g = st.data_editor(df_gastos, num_rows="dynamic", key="g_ed", use_container_width=True)
        if st.button("Sincronizar Gastos"):
            ed_g.to_csv(ARCHIVOS["gastos"], index=False)
            st.rerun()

with t3:
    st.write("**Listado de Cuentas por Pagar**")
    ed_d = st.data_editor(df_deudas, num_rows="dynamic", key="d_ed", use_container_width=True)
    if st.button("Actualizar Deudas"):
        ed_d.to_csv(ARCHIVOS["deudas"], index=False)
        st.rerun()
