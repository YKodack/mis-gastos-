import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Mi Contabilidad Personal", page_icon="💰")

st.title("📊 Mi Control de Gastos")
st.markdown("---")

# Archivo donde se guardan los datos
ARCHIVO_DATOS = "mis_gastos.csv"

# Cargar datos existentes
if os.path.exists(ARCHIVO_DATOS):
    df = pd.read_csv(ARCHIVO_DATOS)
else:
    df = pd.DataFrame(columns=["Fecha", "Categoría", "Monto", "Descripción"])

# --- FORMULARIO PARA METER DATOS ---
with st.form("registro_gasto", clear_on_submit=True):
    st.subheader("📝 Registrar nuevo gasto")
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        cat = st.selectbox("Categoría", ["Comida", "Transporte", "Estudios", "Cine/Ocio", "Ventas/Negocio", "Otros"])
    
    with col2:
        monto = st.number_input("Monto ($)", min_value=0.0, step=5.0)
        desc = st.text_input("¿En qué gastaste?")

    if st.form_submit_button("Guardar Gasto"):
        if monto > 0:
            nuevo = pd.DataFrame([[fecha.strftime("%d/%m/%Y"), cat, monto, desc]], columns=df.columns)
            df = pd.concat([df, nuevo], ignore_index=True)
            df.to_csv(ARCHIVO_DATOS, index=False)
            st.success("¡Gasto guardado!")
            st.rerun()

# --- SECCIÓN PARA BORRAR ---
if not df.empty:
    st.divider()
    st.subheader("⚙️ Administrar Historial")
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        if st.button("🗑️ Borrar ÚLTIMO registro"):
            df = df[:-1] # Quita la última fila
            df.to_csv(ARCHIVO_DATOS, index=False)
            st.warning("Se eliminó el último registro.")
            st.rerun()
            
    with col_b2:
        if st.button("❗ Limpiar TODO el historial"):
            if os.path.exists(ARCHIVO_DATOS):
                os.remove(ARCHIVO_DATOS)
                st.error("Todo el historial ha sido borrado.")
                st.rerun()

    # --- TABLA Y GRÁFICA ---
    st.divider()
    st.subheader("📈 Resumen de mis Gastos")
    
    col_tab, col_gra = st.columns([2, 1])
    
    with col_tab:
        st.write("**Historial de Movimientos**")
        st.dataframe(df, use_container_width=True)
        st.write(f"### Total gastado: ${df['Monto'].sum():,.2f}")
    
    with col_gra:
        st.write("**Distribución por Categoría**")
        resumen = df.groupby("Categoría")["Monto"].sum()
        fig, ax = plt.subplots()
        resumen.plot(kind='pie', autopct='%1.1f%%', ax=ax, startangle=140)
        ax.set_ylabel("")
        st.pyplot(fig)
else:
    st.info("Aún no tienes gastos registrados.")
