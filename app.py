import streamlit as st
import pandas as pd
from fpdf import FPDF

# Configuración de la página
st.set_page_config(
    page_title="Sistema Inteligente de Importación Premium",
    page_icon="📦",
    layout="wide"
)

# Mostrar Banner Corporativo de Portada
NOMBRE_IMAGEN_PORTADA = "1792639987089.jpg"

try:
    st.image(NOMBRE_IMAGEN_PORTADA, use_container_width=True)
except Exception:
    st.title("🚢 Sistema de Gestión Inteligente de Importación Marítima Premium")

st.markdown("Optimización de Costos, Alertas de Carga Pesada y Márgenes de Venta")

# Sidebar para parámetros globales con guía explicativa de procedencia
st.sidebar.header("🎛️ Parámetros de la Importación")
st.sidebar.markdown(
    "💡 *Nota:* Estos valores son suministrados por la naviera, "
    "la agencia aduanal y los operadores logísticos locales. Afectan "
    "directamente el prorrateo y el costo final de nacionalización."
)

flete = st.sidebar.number_input("Costo de Flete ($) [Naviera/Transporte]", value=2500.0, step=100.0)
seguro = st.sidebar.number_input("Costo de Seguro ($) [Póliza]", value=300.0, step=50.0)
aranceles = st.sidebar.number_input("Aranceles / Impuestos ($) [Aduana]", value=1500.0, step=100.0)
gastos_locales = st.sidebar.number_input("Gastos Operativos Locales ($) [Puerto/Terminal]", value=1000.0, step=50.0)

# Carga de archivo CSV o Excel
st.markdown("---")
st.subheader("📋 Detalle de Productos y Proyección Comercial")
uploaded_file = st.file_uploader("Cargue su archivo CSV o Excel con el inventario de productos", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_productos = pd.read_csv(uploaded_file)
        else:
            df_productos = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        df_productos = None
else:
    # Datos de prueba completos con peso, volumen y atributos detallados
    df_productos = pd.DataFrame({
        "Producto": ["Taladro Percutor 1/2\"", "Taladro Inalámbrico 20V", "Juego de Llaves"],
        "Cantidad": [150, 200, 300],
        "Costo Unitario FOB ($)": [10.0, 10.0, 10.0],
        "Precio Venta Estimado ($)": [28.5, 42.0, 12.5],
        "Peso Unitario (kg)": [2.3, 1.8, 1.4],
        "Volumen Unitario (m3)": [0.015, 0.012, 0.008],
        "Partida Arancelaria": ["8467.21.00", "8467.21.00", "8204.12.00"]
    })

if df_productos is not None:
    cols_lower = {str(c).strip().lower(): c for c in df_productos.columns}
    
    col_prod = next((cols_lower[c] for c in cols_lower if any(x in c for x in ['prod', 'item', 'desc', 'nombre'])), None)
    col_cant = next((cols_lower[c] for c in cols_lower if any(x in c for x in ['cant', 'unid', 'qty'])), None)
    col_fob = next((cols_lower[c] for c in cols_lower if any(x in c for x in ['fob', 'costo', 'precio_compra', 'costo_u'])), None)
    col_venta = next((cols_lower[c] for c in cols_lower if any(x in c for x in ['venta', 'precio_v', 'pvp', 'precio'])), None)
    col_peso = next((cols_lower[c] for c in cols_lower if any(x in c for x in ['peso', 'weight'])), None)
    col_vol = next((cols_lower[c] for c in cols_lower if any(x in c for x in ['vol', 'cbm', 'm3'])), None)
    col_part = next((cols_lower[c] for c in cols_lower if any(x in c for x in ['partida', 'arancel', 'hs_code'])), None)

    rename_dict = {}
    if col_prod: rename_dict[col_prod] = "Producto"
    if col_cant: rename_dict[col_cant] = "Cantidad"
    if col_fob: rename_dict[col_fob] = "Costo Unitario FOB ($)"
    if col_venta: rename_dict[col_venta] = "Precio Venta Estimado ($)"
    if col_peso: rename_dict[col_peso] = "Peso Unitario (kg)"
    if col_vol: rename_dict[col_vol] = "Volumen Unitario (m3)"
    if col_part: rename_dict[col_part] = "Partida Arancelaria"
    
    df_productos = df_productos.rename(columns=rename_dict)

    if "Producto" not in df_productos.columns:
        df_productos["Producto"] = [f"Producto {i+1}" for i in range(len(df_productos))]
    if "Cantidad" not in df_productos.columns:
        df_productos["Cantidad"] = 1
    if "Costo Unitario FOB ($)" not in df_productos.columns:
        df_productos["Costo Unitario FOB ($)"] = 10.0
    if "Precio Venta Estimado ($)" not in df_productos.columns:
        df_productos["Precio Venta Estimado ($)"] = df_productos["Costo Unitario FOB ($)"] * 1.5
    if "Peso Unitario (kg)" not in df_productos.columns:
        df_productos["Peso Unitario (kg)"] = 2.0
    if "Volumen Unitario (m3)" not in df_productos.columns:
        df_productos["Volumen Unitario (m3)"] = 0.01
    if "Partida Arancelaria" not in df_productos.columns:
        df_productos["Partida Arancelaria"] = "0000.00.00"

    df_productos["Cantidad"] = pd.to_numeric(df_productos["Cantidad"], errors='coerce').fillna(1)
    df_productos["Costo Unitario FOB ($)"] = pd.to_numeric(df_productos["Costo Unitario FOB ($)"], errors='coerce').fillna(0.0)
    df_productos["Precio Venta Estimado ($)"] = pd.to_numeric(df_productos["Precio Venta Estimado ($)"], errors='coerce').fillna(0.0)
    df_productos["Peso Unitario (kg)"] = pd.to_numeric(df_productos["Peso Unitario (kg)"], errors='coerce').fillna(0.0)
    df_productos["Volumen Unitario (m3)"] = pd.to_numeric(df_productos["Volumen Unitario (m3)"], errors='coerce').fillna(0.0)

    df_productos["FOB Parcial"] = df_productos["Cantidad"] * df_productos["Costo Unitario FOB ($)"]
    fob_total = df_productos["FOB Parcial"].sum()

    cif_total = fob_total + flete + seguro
    costo_total_importacion = cif_total + aranceles + gastos_locales
    factor_multiplicador = costo_total_importacion / fob_total if fob_total > 0 else 1.0

    df_productos["Costo Final Unitario ($)"] = df_productos["Costo Unitario FOB ($)"] * factor_multiplicador
    df_productos["Costo Total Item ($)"] = df_productos["Cantidad"] * df_productos["Costo Final Unitario ($)"]
    df_productos["Margen Unitario ($)"] = df_productos["Precio Venta Estimado ($)"] - df_productos["Costo Final Unitario ($)"]
    df_productos["Rentabilidad (%)"] = (df_productos["Margen Unitario ($)"] / df_productos["Costo Final Unitario ($)"]) * 100

    # ORDENAR COLUMNAS CON ANCHO EQUILIBRADO PARA PRODUCTO
    columnas_principales = [
        "Producto", "Cantidad", "Costo Unitario FOB ($)", "Precio Venta Estimado ($)", 
        "Costo Final Unitario ($)", "Costo Total Item ($)", "Margen Unitario ($)", 
        "Rentabilidad (%)", "Peso Unitario (kg)", "Volumen Unitario (m3)", "Partida Arancelaria"
    ]
    otras_columnas = [c for c in df_productos.columns if c not in columnas_principales]
    df_productos = df_productos[columnas_principales + otras_columnas]

    st.info("💡 **Guía de Navegación:** Despliegue el menú lateral tocando el símbolo **<<** superior izquierdo si desea ajustar los parámetros. Deslice horizontalmente sobre la tabla para explorar todas las métricas detalladas.")
    
    st.dataframe(
        df_productos,
        column_config={
            "Producto": st.column_config.TextColumn("Producto", width="medium"),
            "Cantidad": st.column_config.NumberColumn("Cantidad", format="%d"),
            "Costo Unitario FOB ($)": st.column_config.NumberColumn("Costo FOB ($)", format="$%.2f"),
            "Precio Venta Estimado ($)": st.column_config.NumberColumn("Precio Venta ($)", format="$%.2f"),
            "Costo Final Unitario ($)": st.column_config.NumberColumn("Costo Final Unitario ($)", format="$%.2f"),
            "Costo Total Item ($)": st.column_config.NumberColumn("Costo Total Item ($)", format="$%.2f"),
            "Margen Unitario ($)": st.column_config.NumberColumn("Margen Unitario ($)", format="$%.2f"),
            "Rentabilidad (%)": st.column_config.NumberColumn("Rentabilidad (%)", format="%.1f%%"),
            "Peso Unitario (kg)": st.column_config.NumberColumn("Peso (kg)", format="%.2f"),
            "Volumen Unitario (m3)": st.column_config.NumberColumn("Volumen (m3)", format="%.3f")
        },
        use_container_width=True
    )

    # Indicadores Clave (KPIs) con descripciones analíticas detalladas al margen
    st.markdown("---")
    st.subheader("📊 Análisis Financiero y Logístico Global")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Costo Total Importación", f"${costo_total_importacion:,.2f}")
        st.caption("Suma de CIF + Aranceles + Gastos Locales. Representa la inversión total puesta en bodega.")
    with col2:
        st.metric("Factor Multiplicador", f"{factor_multiplicador:.3f}")
        st.caption("Coeficiente de costo real: Multiplique cada dólar FOB en origen por este factor para hallar su costo nacionalizado.")
    with col3:
        impacto_flete = (flete / fob_total * 100) if fob_total > 0 else 0
        st.metric("Impacto Flete / FOB Global", f"{impacto_flete:.1f}%")
        st.caption("Relación porcentual del flete frente al FOB. Evalúa la eficiencia y peso del transporte marítimo.")
    with col4:
        if impacto_flete > 60:
            estado_carga = "ROJO"
            color_alerta = "🔴 ALERTA ROJA (Global): Flete crítico (>60% del FOB)"
        elif impacto_flete >= 30:
            estado_carga = "AMARILLO"
            color_alerta = "🟡 ALERTA AMARILLA (Global): Flete moderadamente pesado (30%-60% del FOB)"
        else:
            estado_carga = "VERDE"
            color_alerta = "🟢 VERDE (Global): Flete óptimo (<30% del FOB)"
            
        st.metric("Estado Carga Global", estado_carga)
        st.caption("Semáforo logístico del embarque según el impacto porcentual del flete sobre la mercancía.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🚨 Alerta Global de Carga")
    if estado_carga == "ROJO":
        st.sidebar.error(color_alerta)
    elif estado_carga == "AMARILLO":
        st.sidebar.warning(color_alerta)
    else:
        st.sidebar.success(color_alerta)

    def generar_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font('helvetica', 'B', 18)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 14, 'SISTEMA INTELIGENTE DE IMPORTACION - REPORTE PREMIUM', 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font('helvetica', 'B', 13)
        pdf.cell(0, 8, '1. Resumen Financiero y Logistico (Global)', 0, 1)
        pdf.set_font('helvetica', '', 11)
        pdf.set_text_color(50, 50, 50)
        
        pdf.cell(0, 7, f'Valor FOB Total: ${fob_total:,.2f}', 0, 1)
        pdf.cell(0, 7, f'Flete: ${flete:,.2f} | Seguro: ${seguro:,.2f}', 0, 1)
        pdf.cell(0, 7, f'Alerta Carga Pesada (Embarque): {estado_carga} ({impacto_flete:.1f}% del FOB)', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('helvetica', 'B', 13)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 8, '2. Detalle de Productos y Margenes Comerciales', 0, 1)
        pdf.set_font('helvetica', '', 11)
        pdf.set_text_color(50, 50, 50)
        
        for _, row in df_productos.iterrows():
            prod = str(row['Producto'])
            cant = int(row['Cantidad'])
            fob_u = float(row['Costo Unitario FOB ($)'])
            costo_u = float(row['Costo Final Unitario ($)'])
            margen_u = float(row['Margen Unitario ($)'])
            rent = float(row['Rentabilidad (%)'])
            costo_t = float(row['Costo Total Item ($)'])
            peso_u = float(row['Peso Unitario (kg)'])
            vol_u = float(row['Volumen Unitario (m3)'])
            
            pdf.cell(0, 7, f"Producto: {prod} | Cant: {cant} | FOB U: ${fob_u:,.2f}", 0, 1)
            pdf.cell(0, 7, f"  -> Costo Final Unit.: ${costo_u:,.2f} | Margen: ${margen_u:,.2f} | Rent: {rent:.1f}%", 0, 1)
            pdf.cell(0, 7, f"  -> Peso U: {peso_u:.2f} kg | Vol U: {vol_u:.3f} m3 | Total Item: ${costo_t:,.2f}", 0, 1)
            pdf.ln(4)
            
        pdf.ln(4)
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 8, f"Costo Total Importacion: ${costo_total_importacion:,.2f}", 0, 1)
        pdf.cell(0, 8, f"Factor Multiplicador Global: {factor_multiplicador:.3f}", 0, 1)
        pdf.ln(6)
        
        # 3. APÉNDICE: GLOSARIO TÉCNICO
        pdf.set_font('helvetica', 'B', 13)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 8, '3. Apendice: Glosario Tecnico de Comercio Internacional', 0, 1)
        pdf.set_font('helvetica', '', 9.5)
        pdf.set_text_color(60, 60, 60)
        
        glosario_items = [
            "- Valor FOB: Costo neto de la mercancia en origen (fabrica o puerto de embarque).",
            "- Factor Multiplicador: Coeficiente global para determinar el costo real puesto en bodega por cada dolar invertido.",
            "- Impacto Flete/FOB: Relacion porcentual entre el costo del flete y el FOB; mide si la carga es ligera o pesada.",
            "- Costo Final Unitario: Costo real de cada unidad ya nacionalizada (incluye flete, seguro, aranceles y gastos locales).",
            "- Rentabilidad: Porcentaje de ganancia neta estimada respecto al costo final unitario del producto."
        ]
        for item in glosario_items:
            pdf.cell(0, 5.5, item, 0, 1)
        
        pdf.ln(8)
        pdf.set_font('helvetica', 'B', 11)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 7, 'Aprobado y Validado por:', 0, 1)
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, 'Prof. Jesus Pulido - Asesor en Comercio Internacional Inteligente', 0, 1)
        pdf.cell(0, 6, 'Asesoria y Gestion Logistica - Version Premium', 0, 1)
        pdf.ln(6)
        
        try:
            pdf.image('IMG-20261020-WA0010.jpg', x=20, y=pdf.get_y(), w=40)
        except:
            pass
            
        return bytes(pdf.output())

    st.markdown("---")
    if st.button("📥 Generar y Descargar Reporte PDF Premium"):
        pdf_bytes = generar_pdf()
        st.download_button(
            label="📥 Descargar PDF Generado",
            data=pdf_bytes,
            file_name="Reporte_Importacion_Premium.pdf",
            mime="application/pdf"
        )

