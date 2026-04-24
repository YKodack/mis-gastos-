iimport streamlit as st
import pandas as pd
import plotly.express as px # Usaremos Plotly para gráficas más interactivas
import os
from datetime import datetime

# Configuración de pantalla ancha y estilo
st.set_page_config(page_title="Mi Wallet Inteligente", page_icon="💳", layout="wide")

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Mi Panel de Control Financiero")
st.write(f"Hola, hoy es {datetime.now().strftime('%d de %B, %Y')}")

# --- ARCHIVOS ---
ARCHIVOS = {"datos": "contabilidad_completa.csv"}

def cargar_datos():
    if os.path.exists(ARCHIVOS["datos"]):
        return pd.read_csv(ARCHIVOS["datos"])
    return pd.DataFrame(columns=["Fecha", "Tipo", "Categoría", "Descripción", "Monto"])

df = cargar_datos()

# --- BARRA LATERAL: ENTRADA RÁPIDA ---
st.sidebar.header("🎯 Registrar Movimiento")
with st.sidebar.form("registro_rapido", clear_on_submit=True):
    tipo = st.selectbox("¿Qué es?", ["Gasto", "Ingreso"])
    cat = st.selectbox("Categoría", [
        "Sueldo Cine", "Ventas Snacks", "Comida", "Facultad", 
        "Viajes/Transporte", "Cine/Ocio", "Deudas", "Otros"
    ])
    desc = st.text_input("Detalle (ej. Uber, Venta gomitas, Tacos)")
    monto = st.number_input("Cantidad ($)", min_value=0.0, step=10.0)
    fecha = st.date_input("Fecha", datetime.now())
    
    if st.form_submit_button("Añadir a mi cuenta"):
        nuevo = pd.DataFrame([[fecha.strftime("%Y-%m-%d"), tipo, cat, desc, monto]], columns=df.columns)
        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_csv(ARCHIVOS["datos"], index=False)
        st.toast("¡Registro guardado!", icon="✅")
        st.rerun()

# --- PANEL DE CONTROL (MÉTRICAS) ---
total_ing = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
total_gas = df[df["Tipo"] == "Gasto"]["Monto"].sum()
balance = total_ing - total_gas

col1, col2, col3 = st.columns(3)
col1.metric("💰 Entradas Totales", f"${total_ing:,.2f}")
col2.metric("💸 Salidas Totales", f"${total_gas:,.2f}", delta=f"-{total_gas:,.2f}", delta_color="inverse")
col3.metric("⚖️ Disponible", f"${balance:,.2f}")

st.divider()

# --- SECCIONES INTERACTIVAS ---
tab1, tab2, tab3 = st.tabs(["📊 Análisis Visual", "📑 Libro Contable", "✈️ Planificador de Viajes"])

with tab1:
    st.subheader("¿A dónde se va mi dinero?")
    if not df[df["Tipo"] == "Gasto"].empty:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            # Gráfica de Pastel Interactiva
            df_gastos = df[df["Tipo"] == "Gasto"]
            fig_pie = px.pie(df_gastos, values='Monto', names='Categoría', 
                           title='Gastos por Categoría', hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_g2:
            # Gráfica de Barras de tiempo
            fig_bar = px.bar(df_gastos, x='Fecha', y='Monto', color='Categoría',
                            title='Mis Gastos en el Tiempo', barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Aún no hay gastos para graficar. ¡Registra uno en la izquierda!")

with tab2:
    st.subheader("Historial Editable")
    st.write("Haz doble clic en cualquier celda para corregir un dato y luego guarda los cambios.")
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="editor_principal")
    
    if st.button("💾 Sincronizar mis cuentas"):
        df_editado.to_csv(ARCHIVOS["datos"], index=False)
        st.success("¡Contabilidad actualizada!")
        st.rerun()

with tab3:
    st.subheader("Presupuesto para Viajes")
    gastos_viaje = df[df["Categoría"] == "Viajes/Transporte"]["Monto"].sum()
    st.write(f"Has gastado **${gastos_viaje:,.2f}** en viajes hasta ahora.")
    
    meta_viaje = st.number_input("Meta de ahorro para próximo viaje ($)", min_value=0.0, value=2000.0)
    progreso = min(balance / meta_viaje, 1.0) if meta_viaje > 0 else 0
    
    st.progress(progreso)
    st.write(f"Llevas el **{progreso*100:.1f}%** de tu meta de ahorro basándote en tu disponible actual.")
