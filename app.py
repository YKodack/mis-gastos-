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
        try:
            return pd.read_csv(archivo)
        except:
            return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

df_gastos = cargar(ARCHIVOS["gastos"], ["Fecha", "Categoría", "Descripción", "Monto"])
df_ingresos = cargar(ARCHIVOS["ingresos"], ["Fecha", "Fuente", "Monto"])
df_deudas = cargar(ARCHIVOS["deudas"], ["A quién se le debe", "Concepto", "Monto", "Estado"])

# --- PANEL LATERAL ---
st.sidebar.header("➕ Registrar Movimiento")
tipo = st.sidebar.radio("¿Qué quieres registrar?", ["Gasto", "Ingreso", "Deuda"])

if tipo == "Ingreso":
    with st.sidebar.form("f_ing", clear_on_submit=True):
        f = st.date_input("Fecha")
        src = st.text_input("Fuente (Sueldo, Ventas, etc.)")
        m = st.number_input("Cantidad ($)", min_value=0.0)
        if st.form_submit_button("Guardar Ingreso"):
            nuevo = pd.DataFrame([[f.strftime("%d/%m/%Y"), src, m]], columns=df_ingresos.columns)
            pd.concat([df_ingresos, nuevo], ignore_index=True).to_csv(ARCHIVOS["ingresos"], index=False)
            st.rerun()

elif tipo == "Gasto":
    with st.sidebar.form("f_gas", clear_on_submit=True):
        f = st.date_input("Fecha")
        cat = st.selectbox("Categoría", ["Comida", "Transporte", "Estudios", "Cine/Ocio", "Ventas", "Otros"])
        desc = st.text_input("Descripción")
        m = st.number_input("Cantidad ($)", min_value=0.0)
        if st.form_submit_button("Guardar Gasto"):
            nuevo = pd.DataFrame([[f.strftime("%d/%m/%Y"), cat, desc, m]], columns=df_gastos.columns)
            pd.concat([df_gastos, nuevo], ignore_index=True).to_csv(ARCHIVOS["gastos"], index=False)
            st.rerun()

else:
    with st.sidebar.form("f_deu", clear_on_submit=True):
        persona = st.text_input("¿A quién le debes?")
        con = st.text_input("¿Por qué?")
        m = st.number_input("Monto de la deuda ($)", min_value=0.0)
        est = st.selectbox("Estado", ["Pendiente", "Pagado"])
        if st.form_submit_button("Guardar Deuda"):
            nuevo = pd.DataFrame([[persona, con, m, est]], columns=df_deudas.columns)
            pd.concat([df_deudas, nuevo], ignore_index=True).to_csv(ARCHIVOS["deudas"], index=False)
            st.rerun()

# --- DASHBOARD PRINCIPAL ---
total_ing = df_ingresos["Monto"].sum()
total_gas = df_gastos["Monto"].sum()
# Convertimos deudas a numérico para evitar errores
df_deudas["Monto"] = pd.to_numeric(df_deudas["Monto"], errors='coerce').fillna(0)
total_deu = df_deudas[df_deudas["Estado"] == "Pendiente"]["Monto"].sum()
saldo_real = total_ing - total_gas

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Ingresos", f"${total_ing:,.2f}")
c2.metric("💸 Total Gastos", f"${total_gas:,.2f}")
c3.metric("⚠️ Debes", f"${total_deu:,.2f}", delta_color="inverse")
c4.metric("⚖️ Saldo Actual", f"${saldo_real:,.2f}")

st.divider()

# --- GESTIÓN ---
t1, t2, t3, t4 = st.tabs(["📊 Gráficas", "🧾 Historial", "🚩 Deudas", "🧹 Limpieza"])

with t1:
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.write("**Gastos por Categoría**")
        if not df_gastos.empty:
            res = df_gastos.groupby("Categoría")["Monto"].sum()
            fig, ax = plt.subplots()
            res.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=plt.cm.Pastel1.colors)
            ax.set_ylabel("")
            st.pyplot(fig)
    with c_g2:
        st.write("**Estado de tus Deudas**")
        if not df_deudas.empty:
            res_d = df_deudas.groupby("Estado")["Monto"].sum()
            fig2, ax2 = plt.subplots()
            res_d.plot(kind='bar', color=['#FF9999', '#99FF99'], ax=ax2)
            st.pyplot(fig2)

with t2:
    st.write("Edita directamente y guarda cambios.")
    col_i, col_g = st.columns(2)
    with col_i:
        st.write("**Tabla de Ingresos**")
        ei = st.data_editor(df_ingresos, num_rows="dynamic", key="ei")
        if st.button("Sincronizar Ingresos"):
            ei.to_csv(ARCHIVOS["ingresos"], index=False)
            st.rerun()
    with col_g:
        st.write("**Tabla de Gastos**")
        eg = st.data_editor(df_gastos, num_rows="dynamic", key="eg")
        if st.button("Sincronizar Gastos"):
            eg.to_csv(ARCHIVOS["gastos"], index=False)
            st.rerun()

with t3:
    st.write("**Cuentas por Pagar**")
    ed = st.data_editor(df_deudas, num_rows="dynamic", key="ed")
    if st.button("Actualizar Deudas"):
        ed.to_csv(ARCHIVOS["deudas"], index=False)
        st.rerun()

with t4:
    st.warning("⚠️ Acción permanente")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🗑️ Borrar ÚLTIMO Gasto"):
            if not df_gastos.empty:
                df_gastos[:-1].to_csv(ARCHIVOS["gastos"], index=False)
                st.rerun()
    with b2:
        if st.button("🗑️ Borrar ÚLTIMO Ingreso"):
            if not df_ingresos.empty:
                df_ingresos[:-1].to_csv(ARCHIVOS["ingresos"], index=False)
                st.rerun()
    with b3:
        if st.button("🔥 Limpiar TODAS las Deudas"):
            if os.path.exists(ARCHIVOS["deudas"]):
                os.remove(ARCHIVOS["deudas"])
                st.rerun()
