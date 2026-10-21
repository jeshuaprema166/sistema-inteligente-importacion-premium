import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Sistema Inteligente de Importación Premium",
    page_icon="📦",
    layout="wide"
)

# Estilo visual corporativo y limpio
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📦 Sistema de Gestión Inteligente de Importación Premium</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Optimización de Costos, Alertas de Carga Pesada y Rentabilidad</p>', unsafe_allow_html=True)

# Barra lateral para parámetros de importación
st.sidebar.header("🎛️ Parámetros de la Importación")
fob_total = st.sidebar.number_input("Valor FOB Total ($)", min_value=1.0, value=15000.0, step=500.0)
flete = st.sidebar.number_input("Costo de Flete ($)", min_value=0.0, value=2500.0, step=100.0)
seguro = st.sidebar.number_input("Costo de Seguro ($)", min_value=0.0, value=300.0, step=50.0)
aranceles = st.sidebar.number_input("Aranceles / Impuestos ($)", min_value=0.0, value=1500.0, step=50.0)
gastos_operativos = st.sidebar.number_input("Gastos Operativos Locales ($)", min_value=0.0, value=1000.0, step=50.0)

# 1. Lógica de Carga Pesada
cif = fob_total + flete + seguro
porcentaje_flete = (flete / fob_total) * 100 if fob_total > 0 else 0

st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ Alerta de Carga Pesada")
if porcentaje_flete > 60:
    alerta_peso = "ROJO"
    st.sidebar.error("🔴 ROJO: Carga extremadamente pesada/volumétrica (>60% del FOB)")
elif porcentaje_flete >= 30:
    alerta_peso = "NARANJA"
    st.sidebar.warning("🟡 NARANJA: Carga moderadamente pesada (30% - 60% del FOB)")
else:
    alerta_peso = "VERDE"
    st.sidebar.success("🟢 VERDE: Carga ligera / óptima (<30% del FOB)")

# Cálculo de Costo Total de Importación
costo_total_importacion = cif + aranceles + gastos_operativos
factor_multiplicador = costo_total_importacion / fob_total if fob_total > 0 else 0

# Sección de Productos / Inventario
st.markdown("### 📋 Detalle de Productos y Proyección de Venta")
uploaded_file = st.file_uploader("Cargue su archivo CSV con el inventario de productos", type=["csv"])

if uploaded_file is not None:
    df_productos = pd.read_csv(uploaded_file)
else:
    # Datos de ejemplo por defecto
    df_productos = pd.DataFrame({
        "Producto": ["Articulo A", "Articulo B", "Articulo C"],
        "Cantidad": [500, 300, 200],
        "Costo Unitario FOB ($)": [10.0, 20.0, 25.0],
        "Precio Venta Estimado ($)": [18.0, 35.0, 45.0]
    })

# Cálculos automáticos por ítem
df_productos["FOB Parcial"] = df_productos["Cantidad"] * df_productos["Costo Unitario FOB ($)"]
proporcion = df_productos["FOB Parcial"] / fob_total if fob_total > 0 else 0
df_productos["Gastos Asignados"] = proporcion * (flete + seguro + aranceles + gastos_operativos)
df_productos["Costo Total Item"] = df_productos["FOB Parcial"] + df_productos["Gastos Asignados"]
df_productos["Costo Unitario Final"] = df_productos["Costo Total Item"] / df_productos["Cantidad"]
df_productos["Margen Unitario ($)"] = df_productos["Precio Venta Estimado ($)"] - df_productos["Costo Unitario Final"]
df_productos["Rentabilidad (%)"] = (df_productos["Margen Unitario ($)"] / df_productos["Costo Unitario Final"]) * 100

st.dataframe(df_productos.style.format({
    "Costo Unitario FOB ($)": "${:.2f}",
    "Precio Venta Estimado ($)": "${:.2f}",
    "Costo Unitario Final": "${:.2f}",
    "Margen Unitario ($)": "${:.2f}",
    "Rentabilidad (%)": "{:.1f}%"
}), use_container_width=True)

# Métricas Generales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Costo Total Importación", f"${costo_total_importacion:,.2f}")
col2.metric("Factor Multiplicador", f"{factor_multiplicador:.3f}")
col3.metric("Impacto Flete / FOB", f"{porcentaje_flete:.1f}%")
col4.metric("Estado de Carga", alerta_peso)

# Generación de Reporte PDF Profesional
class PDFReport(FPDF):
    def header(self):
        # Cabecera Corporativa Alta y Bold
        self.set_fill_color(30, 58, 138)
        self.rect(0, 0, 215, 28, 'F')
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'SISTEMA INTELIGENTE DE IMPORTACIÓN - REPORTE PREMIUM', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Asesoría y Gestión Logística - Versión Premium', 0, 1, 'C')
        self.cell(0, 5, f'Página {self.page_no()}', 0, 0, 'C')

def generar_pdf():
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Datos Generales
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 8, '1. Resumen Financiero y Logístico', 0, 1)
    
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(95, 6, f"Valor FOB Total: ${fob_total:,.2f}", 0, 0)
    pdf.cell(95, 6, f"Costo Total Importación: ${costo_total_importacion:,.2f}", 0, 1)
    
    pdf.cell(95, 6, f"Flete: ${flete:,.2f} | Seguro: ${seguro:,.2f}", 0, 0)
    pdf.cell(95, 6, f"Factor Multiplicador: {factor_multiplicador:.3f}", 0, 1)
    
    # Estado de Carga Pesada adaptado sin emojis para PDF
    pdf.cell(95, 6, f"Alerta Carga Pesada: {alerta_peso} ({porcentaje_flete:.1f}% del FOB)", 0, 1)
    pdf.ln(5)
    
    # Detalle de Productos con Gastos Asignados en dos líneas
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 8, '2. Detalle de Productos y Gastos Asignados', 0, 1)
    
    pdf.set_font('helvetica', '', 9)
    for index, row in df_productos.iterrows():
        pdf.set_fill_color(240, 242, 245)
        pdf.cell(0, 6, f" Producto: {row['Producto']}  |  Cant: {row['Cantidad']}  |  FOB U: ${row['Costo Unitario FOB ($)']:.2f}", 0, 1, 'L', True)
        # Gastos Asignados particionados en dos líneas para orden perfecto
        pdf.cell(0, 5, f"    -> Costo Final Unitario: ${row['Costo Unitario Final']:.2f}  |  Margen: ${row['Margen Unitario ($)']:,.2f}", 0, 1, 'L')
        pdf.cell(0, 5, f"    -> Rentabilidad: {row['Rentabilidad (%)']:.1f}%  |  Costo Total Item: ${row['Costo Total Item']:,.2f}", 0, 1, 'L')
        pdf.ln(2)
        
    # Pie institucional con foto del profesor si está disponible
    pdf.ln(10)
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 6, 'Aprobado y Validado por:', 0, 1)
    pdf.set_font('helvetica', '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, 'Profesor Jesús - Especialista en Comercio Internacional', 0, 1)
    
    try:
        pdf.image('IMG-20261020-WA0010.jpg', x=160, y=pdf.get_y()-12, w=25)
    except:
        pass
        
    return pdf.output(dest='S').encode('latin1')

st.markdown("---")
if st.button("📥 Generar y Descargar Reporte PDF Premium"):
    pdf_bytes = generar_pdf()
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Reporte_Importacion_Premium.pdf" style="padding: 10px 20px; background-color: #1E3A8A; color: white; border-radius: 5px; text-decoration: none; font-weight: bold;">📥 Descargar PDF Generado</a>'
    st.markdown(href, unsafe_allow_html=True)
