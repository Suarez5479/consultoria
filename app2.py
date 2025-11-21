import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os
import warnings
import requests  # 👈 AGREGAR ESTA LÍNEA
from io import StringIO  # 👈 AGREGAR ESTA LÍNEA
warnings.filterwarnings('ignore')

# =====================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# =====================================================================
st.set_page_config(
    page_title="Análisis de Delitos - USTA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
    <style>
    :root {
        --usta-blue: #002D72;
        --usta-gold: #FDB813;
        --usta-dark: #1A1A1A;
        --usta-light: #F8FAFC;
        --usta-gray: #2D3748;
    }

    .main-header {
        background: linear-gradient(135deg, var(--usta-blue) 0%, #003C91 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
        text-align: center;
    }

    .main-title {
        color: #FFFFFF !important;
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .subtitle {
        color: #E2E8F0;
        font-size: 1.15rem;
        font-weight: 400;
        margin-top: 0.4rem;
    }

    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid var(--usta-gold);
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--usta-blue);
        margin: 0.3rem 0;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #718096;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .kpi-box {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #E2E8F0;
        text-align: center;
        transition: all 0.3s ease;
    }

    .kpi-box:hover {
        border-color: var(--usta-gold);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(253, 184, 19, 0.2);
    }

    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: var(--usta-blue);
        margin: 0.2rem 0;
    }

    .kpi-label {
        font-size: 0.75rem;
        color: #4A5568;
        font-weight: 600;
    }

    .filter-container {
        background: #F7FAFC;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .filter-title {
        color: var(--usta-blue);
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        letter-spacing: 0.5px;
    }

    [data-testid="stSidebar"] {
        background-color: var(--usta-light);
        border-right: 2px solid #E2E8F0;
    }

    .stButton>button {
        background-color: var(--usta-gold);
        color: #002D72;
        border-radius: 6px;
        border: none;
        padding: 0.6rem 1.1rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #E0A600;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    .stDataFrame {
        border-radius: 8px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    h2, h3, h4 {
        color: var(--usta-blue) !important;
        font-weight: 700 !important;
    }

    .stats-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    
    /* Quitar fondos transparentes bajo títulos */
    .element-container {
        background: transparent !important;
    }

/* Colores de los tags seleccionados en multiselect */
[data-baseweb="tag"] {
    background-color: rgba(0, 45, 114, 0.55) !important; /* Azul transparente */
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 500 !important;
}

/* Icono X dentro del tag */
[data-baseweb="tag"] svg {
    fill: #FFFFFF !important;
}

/* Hover en los tags */
[data-baseweb="tag"]:hover {
    background-color: rgba(0, 45, 114, 0.75) !important; /* Hover: menos transparente */
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

/* Borde del contenedor multiselect */
[data-baseweb="select"] > div {
    border-color: #CBD5E0 !important;
}

/* Opciones del dropdown */
[data-baseweb="popover"] {
    background-color: #F7FAFC !important;
}
    </style>
""", unsafe_allow_html=True)

# Paleta de colores roja personalizada
PALETA_ROJA = [
    '#A50021', '#D82632', '#F76D5E', '#FFD044', '#FFE099',
    '#FFFFBF', '#E0FFFF', '#AAF7FF', '#72D8FF', '#3FA0FF', 
    '#267DD4', '#145CA5'
]

# =====================================================================
# FUNCIÓN PARA CARGAR DATOS DESDE ZIP
# =====================================================================
@st.cache_data(show_spinner=False)
def cargar_datos_desde_zip(zip_path, csv_filename):
    """
    Carga un CSV desde un archivo ZIP en el repositorio
    
    Args:
        zip_path: Ruta al archivo .zip (ej: 'delitos_con_poblacion_limpio.zip')
        csv_filename: Nombre del CSV dentro del ZIP (ej: 'delitos_con_poblacion_limpio.csv')
    """
    try:
        # Verificar que el ZIP existe
        if not os.path.exists(zip_path):
            st.error(f"❌ No se encontró el archivo: {zip_path}")
            st.info(f"🔍 Buscando en: {os.getcwd()}")
            st.info(f"📁 Archivos disponibles: {os.listdir('.')}")
            return None
        
        # Extraer y leer el CSV del ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Listar archivos en el ZIP
            archivos_en_zip = zip_ref.namelist()
            st.info(f"📦 Archivos en el ZIP: {', '.join(archivos_en_zip)}")
            
            # Buscar el archivo CSV
            if csv_filename not in archivos_en_zip:
                st.error(f"❌ El archivo '{csv_filename}' no está en el ZIP")
                st.info(f"Archivos disponibles: {', '.join(archivos_en_zip)}")
                return None
            
            # Leer el CSV directamente desde el ZIP
            with zip_ref.open(csv_filename) as file:
                # Intentar con diferentes encodings
                try:
                    df = pd.read_csv(file, encoding='utf-8')
                except UnicodeDecodeError:
                    file.seek(0)  # Volver al inicio del archivo
                    try:
                        df = pd.read_csv(file, encoding='latin1')
                    except:
                        file.seek(0)
                        df = pd.read_csv(file, encoding='cp1252')
        
        return df
        
    except zipfile.BadZipFile:
        st.error("❌ El archivo no es un ZIP válido")
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

# =====================================================================
# CARGA AUTOMÁTICA DE DATOS
# =====================================================================
# 🎯 RUTAS CORREGIDAS - Solo el nombre del archivo (está en la raíz del repo)
ZIP_PATH = "delitos_con_poblacion_limpio.zip"  # ✅ Archivo en la raíz del repositorio GitHub
CSV_FILENAME = "delitos_con_poblacion_limpio.csv"  # ✅ Nombre del CSV dentro del ZIP

# Cargar datos con indicador de progreso
if 'df' not in st.session_state:
    st.info("📦 Cargando datos desde el repositorio...")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("🔓 Extrayendo archivo ZIP...")
    progress_bar.progress(33)
    
    status_text.text("📊 Leyendo datos CSV...")
    progress_bar.progress(66)
    
    df = cargar_datos_desde_zip(ZIP_PATH, CSV_FILENAME)
    
    if df is not None:
        status_text.text("✅ Datos cargados correctamente")
        progress_bar.progress(100)
        st.session_state['df'] = df
        st.success(f"✅ {len(df):,} registros cargados exitosamente")
        progress_bar.empty()
        status_text.empty()
    else:
        progress_bar.empty()
        status_text.empty()
        st.error("❌ No se pudieron cargar los datos")
        
        # Mostrar diagnóstico detallado
        st.warning("🔍 **Diagnóstico del problema:**")
        st.code(f"Directorio actual: {os.getcwd()}")
        st.code(f"Archivos en raíz: {os.listdir('.')}")
        
        st.info("""
        **✅ Solución:**
        
        Tu estructura en GitHub debe ser:
        ```
        consultoria/
        ├── app2.py  (o app.py)
        ├── requirements.txt
        └── delitos_con_poblacion_limpio.zip  ← Debe estar aquí
        ```
        
        **Verifica en GitHub:**
        1. Ve a: https://github.com/Suarez5479/consultoria
        2. Asegúrate de ver el archivo `delitos_con_poblacion_limpio.zip` en la lista
        3. Si no está, súbelo a la raíz del repositorio (NO en carpetas)
        """)
        st.stop()

df = st.session_state.get('df', None)
# ================================================================
# VERIFICACIÓN DE DATOS Y CONFIGURACIÓN DE INTERFAZ
# ================================================================
if df is not None and not df.empty:
    # Encabezado principal
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">Análisis de Delitos en Colombia</h1>
        <p class="subtitle">Modelo Estrella 2018-2024 | Universidad Santo Tomás</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    if os.path.exists("logo-santo-tomas.png"):
        st.sidebar.image("logo-santo-tomas.png", width=200)
    st.sidebar.markdown("---")
    st.sidebar.title("Navegación")

    sections = [
        "Inicio",
        "Información General",
        "Análisis Temporal",
        "Tipos de Delito",
        "Armas y Medios",
        "Análisis Geográfico",
        "Perfil de Víctimas",
        "Modelo Estrella",
        "Hallazgos Principales"
    ]
    selected_section = st.sidebar.radio("", sections)

    st.sidebar.markdown("---")
    st.sidebar.metric("Total Registros", f"{len(df):,}")
    st.sidebar.metric("Total Columnas", df.shape[1])
    if "AÑO" in df.columns:
        años = pd.to_numeric(df["AÑO"], errors="coerce").dropna()
        if len(años) > 0:
            st.sidebar.metric("Rango Años", f"{int(años.min())} - {int(años.max())}")

    # ================================================================
    # SECCION: INICIO
    # ================================================================
    if selected_section == "Inicio":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Registros Totales</div>
                    <div class='metric-value'>{len(df):,}</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            memoria = df.memory_usage(deep=True).sum() / 1024**2
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>Memoria Utilizada</div>
                    <div class='metric-value'>{memoria:.2f} MB</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            if 'AÑO' in df.columns:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-label'>Años de Cobertura</div>
                        <div class='metric-value'>{df['AÑO'].nunique()}</div>
                    </div>
                """, unsafe_allow_html=True)
        with col4:
            if 'TIPO_DELITO' in df.columns:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-label'>Tipos de Delito</div>
                        <div class='metric-value'>{df['TIPO_DELITO'].nunique()}</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Resumen Ejecutivo")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Objetivos del Análisis**
            - Identificar patrones temporales
            - Analizar distribución geográfica
            - Caracterizar perfiles de víctimas
            - Evaluar uso de armas
            - Apoyar políticas públicas
            """)
        with col2:
            st.markdown("""
            **Estructura de Datos**
            - Periodo: 2018-2024
            - Cobertura: Nacional
            - Granularidad: Municipal
            - Dimensiones: Temporal, Geográfica, Víctimas, Armas, Delitos
            - Modelo: Estrella
            """)
        
        st.markdown("---")
        st.subheader("Vista Previa de Datos")
        st.dataframe(df.head(10), use_container_width=True, height=400)

    # ============================================================
    # SECCION: INFORMACION GENERAL
    # ============================================================
    elif selected_section == "Información General":
        st.header("Información General de la Base de Datos")
        
        st.subheader("Estadísticas Generales")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
                <div class='kpi-box'>
                    <div class='kpi-label'>Total Registros</div>
                    <div class='kpi-value'>{len(df):,}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class='kpi-box'>
                    <div class='kpi-label'>Total Columnas</div>
                    <div class='kpi-value'>{df.shape[1]}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if "DEPARTAMENTO" in df.columns:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-label'>Departamentos</div>
                        <div class='kpi-value'>{df['DEPARTAMENTO'].nunique()}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if "MUNICIPIO" in df.columns:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-label'>Municipios</div>
                        <div class='kpi-value'>{df['MUNICIPIO'].nunique()}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col5:
            if "TIPO_DELITO" in df.columns:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-label'>Tipos Delito</div>
                        <div class='kpi-value'>{df['TIPO_DELITO'].nunique()}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if "AÑO" in df.columns:
                años_unicos = df[df["AÑO"] != "NO REPORTADO"]["AÑO"].nunique()
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-label'>Años Cobertura</div>
                        <div class='kpi-value'>{años_unicos}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if "ARMAS_MEDIOS" in df.columns:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-label'>Tipos Armas</div>
                        <div class='kpi-value'>{df['ARMAS_MEDIOS'].nunique()}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if "GENERO" in df.columns:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-label'>Cat. Género</div>
                        <div class='kpi-value'>{df['GENERO'].nunique()}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col4:
            memoria = df.memory_usage(deep=True).sum() / 1024**2
            st.markdown(f"""
                <div class='kpi-box'>
                    <div class='kpi-label'>Memoria</div>
                    <div class='kpi-value'>{memoria:.1f} MB</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Detalle de Columnas")
        
        columnas_info = []
        for i, col in enumerate(df.columns, 1):
            columnas_info.append({
                '#': i,
                'Columna': col,
                'Tipo': str(df[col].dtype),
                'Valores Únicos': df[col].nunique(),
                'Nulos': df[col].isnull().sum(),
                '% Nulos': f"{(df[col].isnull().sum() / len(df) * 100):.2f}%"
            })
        columnas_df = pd.DataFrame(columnas_info)
        st.dataframe(columnas_df, use_container_width=True, height=450)

    # ================================================================
    # SECCIÓN: ANÁLISIS TEMPORAL
    # ================================================================
    elif selected_section == "Análisis Temporal":
        st.header("Análisis Temporal de Delitos")

        if 'AÑO' in df.columns:
            # Limpieza de datos
            df_clean = df[df['AÑO'] != 'NO REPORTADO'].copy()
            df_clean['AÑO'] = pd.to_numeric(df_clean['AÑO'], errors='coerce')
            df_clean = df_clean.dropna(subset=['AÑO'])
            df_clean['AÑO'] = df_clean['AÑO'].astype(int)

            # FILTROS GLOBALES
            st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-title'>FILTROS INTERACTIVOS</div>", unsafe_allow_html=True)
            
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                años_disponibles = sorted(df_clean['AÑO'].unique())
                años_seleccionados = st.multiselect(
                    "Años:",
                    options=años_disponibles,
                    default=años_disponibles,
                    key="filtro_años_temporal"
                )
            
            with col_f2:
                if 'DEPARTAMENTO' in df_clean.columns:
                    deptos_disponibles = sorted(df_clean['DEPARTAMENTO'].unique())
                    deptos_seleccionados = st.multiselect(
                        "Departamentos:",
                        options=deptos_disponibles,
                        default=deptos_disponibles[:5] if len(deptos_disponibles) > 5 else deptos_disponibles,
                        key="filtro_deptos_temporal"
                    )
                else:
                    deptos_seleccionados = None
            
            with col_f3:
                if 'TIPO_DELITO' in df_clean.columns:
                    delitos_disponibles = sorted(df_clean['TIPO_DELITO'].unique())
                    delitos_seleccionados = st.multiselect(
                        "Tipos de Delito:",
                        options=delitos_disponibles,
                        default=delitos_disponibles[:5] if len(delitos_disponibles) > 5 else delitos_disponibles,
                        key="filtro_delitos_temporal"
                    )
                else:
                    delitos_seleccionados = None
            
            with col_f4:
                n_top_visual = st.number_input(
                    "Top N para visualizar:",
                    min_value=3,
                    max_value=20,
                    value=10,
                    step=1,
                    key="n_top_temporal"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Aplicar filtros
            df_filtrado = df_clean[df_clean['AÑO'].isin(años_seleccionados)]
            if deptos_seleccionados and 'DEPARTAMENTO' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['DEPARTAMENTO'].isin(deptos_seleccionados)]
            if delitos_seleccionados and 'TIPO_DELITO' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['TIPO_DELITO'].isin(delitos_seleccionados)]

            if len(df_filtrado) == 0:
                st.warning("No hay datos para los filtros seleccionados. Intenta ampliar la selección.")
            else:
                # KPIs
                year_counts = df_filtrado['AÑO'].value_counts().sort_index()
                año_max = year_counts.idxmax()
                año_min = year_counts.idxmin()
                variacion = ((year_counts.iloc[-1] - year_counts.iloc[0]) / year_counts.iloc[0] * 100) if len(year_counts) > 1 else 0

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Registros Filtrados</div>
                            <div class='kpi-value'>{len(df_filtrado):,}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Año Más Delitos</div>
                            <div class='kpi-value'>{año_max}</div>
                            <div class='kpi-label'>{year_counts[año_max]:,} registros</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Año Menos Delitos</div>
                            <div class='kpi-value'>{año_min}</div>
                            <div class='kpi-label'>{year_counts[año_min]:,} registros</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col4:
                    color_var = '#16A34A' if variacion < 0 else '#DC2626'
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Variación Total</div>
                            <div class='kpi-value' style='color: {color_var};'>{variacion:+.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

                # Gráficas principales
                col1, col2 = st.columns(2)

                with col1:
                    fig = px.line(
                        x=year_counts.index,
                        y=year_counts.values,
                        markers=True,
                        title='Evolución de Delitos por Año',
                        labels={'x': 'Año', 'y': 'Número de Delitos'}
                    )
                    fig.update_traces(
                        line_color=PALETA_ROJA[-1],
                        line_width=3,
                        marker=dict(size=12, color=PALETA_ROJA[-3], line=dict(width=2, color='white'))
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        hovermode='x unified',
                        height=450
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = px.pie(
                        values=year_counts.values,
                        names=year_counts.index,
                        title='Distribución Porcentual por Año',
                        color_discrete_sequence=PALETA_ROJA[::-1],
                        hole=0.4
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=450)
                    st.plotly_chart(fig, use_container_width=True)

                # Análisis por Delito
                if 'TIPO_DELITO' in df_filtrado.columns:
                    st.markdown("---")
                    st.subheader("Análisis por Tipo de Delito")
                    
                    top_delitos_temporal = df_filtrado['TIPO_DELITO'].value_counts().head(n_top_visual)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            y=top_delitos_temporal.index,
                            x=top_delitos_temporal.values,
                            orientation='h',
                            marker=dict(
                                color=top_delitos_temporal.values,
                                colorscale=[[0, PALETA_ROJA[5]], [1, PALETA_ROJA[0]]],
                                showscale=False
                            ),
                            text=top_delitos_temporal.values,
                            textposition='outside'
                        ))
                        fig.update_layout(
                            title=f'Top {n_top_visual} Delitos Más Frecuentes',
                            xaxis_title='Casos',
                            yaxis_title='',
                            plot_bgcolor='white',
                            height=450,
                            yaxis={'categoryorder': 'total ascending'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        delito_max = top_delitos_temporal.index[0]
                        casos_max = top_delitos_temporal.values[0]
                        delito_min = top_delitos_temporal.index[-1]
                        casos_min = top_delitos_temporal.values[-1]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=['Mayor Casos', 'Menor Casos'],
                            y=[casos_max, casos_min],
                            marker=dict(color=[PALETA_ROJA[0], PALETA_ROJA[5]]),
                            text=[f"{delito_max}<br>{casos_max:,}", f"{delito_min}<br>{casos_min:,}"],
                            textposition='outside'
                        ))
                        fig.update_layout(
                            title='Delitos con Mayor y Menor Frecuencia',
                            yaxis_title='Número de Casos',
                            plot_bgcolor='white',
                            height=450
                        )
                        st.plotly_chart(fig, use_container_width=True)

    # ================================================================
    # SECCIÓN: TIPOS DE DELITO (CORREGIDA)
    # ================================================================
    elif selected_section == "Tipos de Delito":
        st.header("Análisis de Tipos de Delito")

        if 'TIPO_DELITO' in df.columns:
            # FILTROS GLOBALES
            st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-title'>FILTROS INTERACTIVOS</div>", unsafe_allow_html=True)
            
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                if 'AÑO' in df.columns:
                    df_temp = df[df['AÑO'] != 'NO REPORTADO'].copy()
                    años_disponibles = sorted(pd.to_numeric(df_temp['AÑO'], errors='coerce').dropna().unique().astype(int))
                    años_seleccionados = st.multiselect(
                        "Años:",
                        options=años_disponibles,
                        default=años_disponibles,
                        key="filtro_años_delito"
                    )
                else:
                    años_seleccionados = None
            
            with col_f2:
                if 'DEPARTAMENTO' in df.columns:
                    deptos_disponibles = sorted([str(x) for x in df['DEPARTAMENTO'].dropna().unique()])
                    deptos_seleccionados = st.multiselect(
                        "Departamentos:",
                        options=deptos_disponibles,
                        default=deptos_disponibles[:5] if len(deptos_disponibles) > 5 else deptos_disponibles,
                        key="filtro_deptos_delito"
                    )
                else:
                    deptos_seleccionados = None
            
            with col_f3:
                if 'ARMAS_MEDIOS' in df.columns:
                    armas_disponibles = sorted([str(x) for x in df['ARMAS_MEDIOS'].dropna().unique()])
                    armas_seleccionadas = st.multiselect(
                        "Armas/Medios:",
                        options=armas_disponibles,
                        default=armas_disponibles[:5] if len(armas_disponibles) > 5 else armas_disponibles,
                        key="filtro_armas_delito"
                    )
                else:
                    armas_seleccionadas = None
            
            with col_f4:
                n_delitos = st.number_input(
                    "Top N Delitos:",
                    min_value=3,
                    max_value=30,
                    value=10,
                    step=1,
                    key="n_delitos_visual"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Aplicar filtros
            df_filtrado = df.copy()
            if años_seleccionados and 'AÑO' in df_filtrado.columns:
                df_filtrado['AÑO_NUM'] = pd.to_numeric(df_filtrado['AÑO'], errors='coerce')
                df_filtrado = df_filtrado[df_filtrado['AÑO_NUM'].isin(años_seleccionados)]
            if deptos_seleccionados and 'DEPARTAMENTO' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['DEPARTAMENTO'].isin(deptos_seleccionados)]
            if armas_seleccionadas and 'ARMAS_MEDIOS' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['ARMAS_MEDIOS'].isin(armas_seleccionadas)]

            if len(df_filtrado) == 0:
                st.warning("No hay datos para los filtros seleccionados.")
            else:
                # KPIs
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Registros Filtrados</div>
                            <div class='kpi-value'>{len(df_filtrado):,}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Tipos de Delito</div>
                            <div class='kpi-value'>{df_filtrado['TIPO_DELITO'].nunique()}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    delito_mas_comun = df_filtrado['TIPO_DELITO'].value_counts().index[0]
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Delito Más Común</div>
                            <div class='kpi-value' style='font-size: 0.9rem;'>{delito_mas_comun[:20]}...</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col4:
                    casos_max = df_filtrado['TIPO_DELITO'].value_counts().values[0]
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Casos del Más Común</div>
                            <div class='kpi-value'>{casos_max:,}</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                
                # Gráfica principal de barras
                top_delitos = df_filtrado['TIPO_DELITO'].value_counts().head(n_delitos)
                total_delitos = df_filtrado['TIPO_DELITO'].value_counts().sum()
                
                df_delitos_viz = pd.DataFrame({
                    'Delito': top_delitos.index,
                    'Frecuencia': top_delitos.values,
                    'Porcentaje': (top_delitos.values / total_delitos * 100).round(2)
                })

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=df_delitos_viz['Delito'],
                    x=df_delitos_viz['Frecuencia'],
                    orientation='h',
                    marker=dict(
                        color=df_delitos_viz['Frecuencia'],
                        colorscale=[[0, PALETA_ROJA[5]], [1, PALETA_ROJA[0]]],
                        showscale=False,
                        line=dict(color='white', width=1)
                    ),
                    text=[f"{pct:.1f}% ({freq:,})" for pct, freq in zip(df_delitos_viz['Porcentaje'], df_delitos_viz['Frecuencia'])],
                    textposition='outside',
                    textfont=dict(size=10),
                    hovertemplate='<b>%{y}</b><br>Casos: %{x:,}<br>Porcentaje: %{text}<extra></extra>'
                ))
                
                fig.update_layout(
                    title=f'Top {n_delitos} Tipos de Delito Más Frecuentes',
                    xaxis_title='Número de Casos',
                    yaxis_title='',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=500,
                    yaxis={'categoryorder': 'total ascending'},
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

                # Segunda fila: Mayor vs Menor + Distribución
                st.markdown("---")
                st.subheader("Análisis Comparativo")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    delito_max = top_delitos.index[0]
                    casos_max = top_delitos.values[0]
                    delito_min = top_delitos.index[-1]
                    casos_min = top_delitos.values[-1]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['Mayor Casos', 'Menor Casos'],
                        y=[casos_max, casos_min],
                        marker=dict(color=[PALETA_ROJA[0], PALETA_ROJA[5]]),
                        text=[f"{delito_max}<br>{casos_max:,}", f"{delito_min}<br>{casos_min:,}"],
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>Casos: %{y:,}<extra></extra>'
                    ))
                    fig.update_layout(
                        title='Delitos con Mayor y Menor Frecuencia',
                        yaxis_title='Número de Casos',
                        plot_bgcolor='white',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.pie(
                        values=top_delitos.head(5).values,
                        names=top_delitos.head(5).index,
                        title='Top 5 Delitos - Distribución',
                        hole=0.4,
                        color_discrete_sequence=PALETA_ROJA
                    )
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent',
                        hovertemplate='<b>%{label}</b><br>Casos: %{value:,}<br>Porcentaje: %{percent}<extra></extra>'
                    )
                    fig.update_layout(showlegend=True, height=400)
                    st.plotly_chart(fig, use_container_width=True)

                # Análisis detallado por delito seleccionado
                if 'ARMAS_MEDIOS' in df_filtrado.columns:
                    st.markdown("---")
                    st.subheader("Análisis Detallado por Delito")
                    
                    delito_seleccionado = st.selectbox(
                        "Selecciona un delito para análisis detallado:",
                        options=top_delitos.head(20).index.tolist(),
                        key="delito_detallado"
                    )
                    
                    df_delito = df_filtrado[df_filtrado['TIPO_DELITO'] == delito_seleccionado]
                    
                    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                    
                    with col_kpi1:
                        st.markdown(f"""
                            <div class='kpi-box' style='padding: 0.5rem;'>
                                <div class='kpi-label' style='font-size: 0.65rem;'>Total Casos</div>
                                <div class='kpi-value' style='font-size: 1.2rem;'>{len(df_delito):,}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col_kpi2:
                        if 'DEPARTAMENTO' in df_delito.columns:
                            dept_mas_afectado = df_delito['DEPARTAMENTO'].value_counts().index[0]
                            st.markdown(f"""
                                <div class='kpi-box' style='padding: 0.5rem;'>
                                    <div class='kpi-label' style='font-size: 0.65rem;'>Depto. Más Afectado</div>
                                    <div class='kpi-value' style='font-size: 0.85rem;'>{dept_mas_afectado}</div>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    with col_kpi3:
                        if 'DEPARTAMENTO' in df_delito.columns:
                            casos_dept = df_delito['DEPARTAMENTO'].value_counts().iloc[0]
                            st.markdown(f"""
                                <div class='kpi-box' style='padding: 0.5rem;'>
                                    <div class='kpi-label' style='font-size: 0.65rem;'>Casos en ese Depto</div>
                                    <div class='kpi-value' style='font-size: 1.2rem;'>{casos_dept:,}</div>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    with col_kpi4:
                        porcentaje_total = (len(df_delito) / len(df_filtrado)) * 100
                        st.markdown(f"""
                            <div class='kpi-box' style='padding: 0.5rem;'>
                                <div class='kpi-label' style='font-size: 0.65rem;'>% del Total Filtrado</div>
                                <div class='kpi-value' style='font-size: 1.2rem;'>{porcentaje_total:.2f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    col_grafica, col_pie = st.columns([2, 1])
                    
                    with col_grafica:
                        n_armas_mostrar = st.number_input(
                            "Número de armas a mostrar:",
                            min_value=5,
                            max_value=20,
                            value=10,
                            step=1,
                            key="n_armas_delito_detalle"
                        )
                        
                        armas_delito = df_delito['ARMAS_MEDIOS'].value_counts().head(n_armas_mostrar)
                        total_armas_delito = df_delito['ARMAS_MEDIOS'].value_counts().sum()
                        
                        df_armas_viz = pd.DataFrame({
                            'Arma': armas_delito.index,
                            'Frecuencia': armas_delito.values,
                            'Porcentaje': (armas_delito.values / total_armas_delito * 100).round(2)
                        })
                        
                        colores = [PALETA_ROJA[2] if i != 0 else PALETA_ROJA[0] 
                                  for i in range(len(df_armas_viz))]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            y=df_armas_viz['Arma'],
                            x=df_armas_viz['Frecuencia'],
                            orientation='h',
                            marker=dict(color=colores),
                            text=[f"{pct:.1f}% ({freq:,})" for pct, freq in zip(df_armas_viz['Porcentaje'], df_armas_viz['Frecuencia'])],
                            textposition='outside',
                            textfont=dict(size=9),
                            hovertemplate='<b>%{y}</b><br>Casos: %{x:,}<br>% del delito: %{text}<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title=f'Armas/Medios Utilizados en {delito_seleccionado}',
                            xaxis_title='Frecuencia',
                            yaxis_title='',
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            height=400,
                            yaxis={'categoryorder': 'total ascending'},
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col_pie:
                        # PIE CHART que se adapta al número de armas seleccionadas
                        top_armas_pie_detalle = armas_delito.head(n_armas_mostrar)
                        fig = px.pie(
                            values=top_armas_pie_detalle.values,
                            names=top_armas_pie_detalle.index,
                            title=f'Top {n_armas_mostrar} Armas (%)',
                            hole=0.4,
                            color_discrete_sequence=PALETA_ROJA
                        )
                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent',
                            hovertemplate='<b>%{label}</b><br>Casos: %{value:,}<br>Porcentaje: %{percent}<extra></extra>'
                        )
                        fig.update_layout(showlegend=True, height=400)
                        st.plotly_chart(fig, use_container_width=True)

    # ================================================================
    # SECCIÓN: TIPOS DE DELITO (CORREGIDA)
    # ================================================================
    elif selected_section == "Tipos de Delito":
        st.header("Análisis de Tipos de Delito")

        if 'TIPO_DELITO' in df.columns:
            # FILTROS GLOBALES
            st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-title'>FILTROS INTERACTIVOS</div>", unsafe_allow_html=True)
            
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                if 'AÑO' in df.columns:
                    df_temp = df[df['AÑO'] != 'NO REPORTADO'].copy()
                    años_disponibles = sorted(pd.to_numeric(df_temp['AÑO'], errors='coerce').dropna().unique().astype(int))
                    años_seleccionados = st.multiselect(
                        "Años:",
                        options=años_disponibles,
                        default=años_disponibles,
                        key="filtro_años_delito"
                    )
                else:
                    años_seleccionados = None
            
            with col_f2:
                if 'DEPARTAMENTO' in df.columns:
                    deptos_disponibles = sorted([str(x) for x in df['DEPARTAMENTO'].dropna().unique()])
                    deptos_seleccionados = st.multiselect(
                        "Departamentos:",
                        options=deptos_disponibles,
                        default=deptos_disponibles[:5] if len(deptos_disponibles) > 5 else deptos_disponibles,
                        key="filtro_deptos_delito"
                    )
                else:
                    deptos_seleccionados = None
            
            with col_f3:
                if 'ARMAS_MEDIOS' in df.columns:
                    armas_disponibles = sorted([str(x) for x in df['ARMAS_MEDIOS'].dropna().unique()])
                    armas_seleccionadas = st.multiselect(
                        "Armas/Medios:",
                        options=armas_disponibles,
                        default=armas_disponibles[:5] if len(armas_disponibles) > 5 else armas_disponibles,
                        key="filtro_armas_delito"
                    )
                else:
                    armas_seleccionadas = None
            
            with col_f4:
                n_delitos = st.number_input(
                    "Top N Delitos:",
                    min_value=3,
                    max_value=30,
                    value=10,
                    step=1,
                    key="n_delitos_visual"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Aplicar filtros de forma eficiente
            mask = pd.Series([True] * len(df), index=df.index)
            
            if años_seleccionados and 'AÑO' in df.columns:
                año_num = pd.to_numeric(df['AÑO'], errors='coerce')
                mask &= año_num.isin(años_seleccionados)
            
            if deptos_seleccionados and 'DEPARTAMENTO' in df.columns:
                mask &= df['DEPARTAMENTO'].isin(deptos_seleccionados)
            
            if armas_seleccionadas and 'ARMAS_MEDIOS' in df.columns:
                mask &= df['ARMAS_MEDIOS'].isin(armas_seleccionadas)
            
            df_filtrado = df[mask].copy()

            if len(df_filtrado) == 0:
                st.warning("No hay datos para los filtros seleccionados.")
            else:
                # KPIs
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Registros Filtrados</div>
                            <div class='kpi-value'>{len(df_filtrado):,}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Tipos de Delito</div>
                            <div class='kpi-value'>{df_filtrado['TIPO_DELITO'].nunique()}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    delito_mas_comun = df_filtrado['TIPO_DELITO'].value_counts().index[0]
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Delito Más Común</div>
                            <div class='kpi-value' style='font-size: 0.9rem;'>{delito_mas_comun[:20]}...</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col4:
                    casos_max = df_filtrado['TIPO_DELITO'].value_counts().values[0]
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Casos del Más Común</div>
                            <div class='kpi-value'>{casos_max:,}</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                
                # Gráfica principal de barras
                top_delitos = df_filtrado['TIPO_DELITO'].value_counts().head(n_delitos)
                total_delitos = df_filtrado['TIPO_DELITO'].value_counts().sum()
                
                df_delitos_viz = pd.DataFrame({
                    'Delito': top_delitos.index,
                    'Frecuencia': top_delitos.values,
                    'Porcentaje': (top_delitos.values / total_delitos * 100).round(2)
                })

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=df_delitos_viz['Delito'],
                    x=df_delitos_viz['Frecuencia'],
                    orientation='h',
                    marker=dict(
                        color=df_delitos_viz['Frecuencia'],
                        colorscale=[[0, PALETA_ROJA[5]], [1, PALETA_ROJA[0]]],
                        showscale=False,
                        line=dict(color='white', width=1)
                    ),
                    text=[f"{pct:.1f}% ({freq:,})" for pct, freq in zip(df_delitos_viz['Porcentaje'], df_delitos_viz['Frecuencia'])],
                    textposition='outside',
                    textfont=dict(size=10),
                    hovertemplate='<b>%{y}</b><br>Casos: %{x:,}<br>Porcentaje: %{text}<extra></extra>'
                ))
                
                fig.update_layout(
                    title=f'Top {n_delitos} Tipos de Delito Más Frecuentes',
                    xaxis_title='Número de Casos',
                    yaxis_title='',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=500,
                    yaxis={'categoryorder': 'total ascending'},
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

                # Segunda fila: Mayor vs Menor + Distribución
                st.markdown("---")
                st.subheader("Análisis Comparativo")
                
                col1, col2 = st.columns(1)
                
                with col1:
                    delito_max = top_delitos.index[0]
                    casos_max = top_delitos.values[0]
                    delito_min = top_delitos.index[-1]
                    casos_min = top_delitos.values[-1]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['Mayor Casos', 'Menor Casos'],
                        y=[casos_max, casos_min],
                        marker=dict(color=[PALETA_ROJA[0], PALETA_ROJA[5]]),
                        text=[f"{delito_max}<br>{casos_max:,}", f"{delito_min}<br>{casos_min:,}"],
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>Casos: %{y:,}<extra></extra>'
                    ))
                    fig.update_layout(
                        title='Delitos con Mayor y Menor Frecuencia',
                        yaxis_title='Número de Casos',
                        plot_bgcolor='white',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:

                    # Usar el Top N seleccionado en los filtros globales
                    top_delitos_n = top_delitos.head(n_delitos)

                    fig = px.pie(
                        values=top_delitos_n.values,
                        names=top_delitos_n.index,
                        title=f'Top {n_delitos} Delitos - Distribución',
                        hole=0.4,
                        color_discrete_sequence=PALETA_ROJA
                    )

                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent',
                        hovertemplate='<b>%{label}</b><br>Casos: %{value:,}<br>Porcentaje: %{percent}<extra></extra>'
                    )

                    fig.update_layout(showlegend=True, height=400)

                    st.plotly_chart(fig, use_container_width=True)



                # Análisis detallado por delito seleccionado
                if 'ARMAS_MEDIOS' in df_filtrado.columns:
                    st.markdown("---")
                    st.subheader("Análisis Detallado por Delito")
                    
                    delito_seleccionado = st.selectbox(
                        "Selecciona un delito para análisis detallado:",
                        options=top_delitos.head(20).index.tolist(),
                        key="delito_detallado"
                    )
                    
                    df_delito = df_filtrado[df_filtrado['TIPO_DELITO'] == delito_seleccionado]
                    
                    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                    
                    with col_kpi1:
                        st.markdown(f"""
                            <div class='kpi-box' style='padding: 0.5rem;'>
                                <div class='kpi-label' style='font-size: 0.65rem;'>Total Casos</div>
                                <div class='kpi-value' style='font-size: 1.2rem;'>{len(df_delito):,}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col_kpi2:
                        if 'DEPARTAMENTO' in df_delito.columns:
                            dept_mas_afectado = df_delito['DEPARTAMENTO'].value_counts().index[0]
                            st.markdown(f"""
                                <div class='kpi-box' style='padding: 0.5rem;'>
                                    <div class='kpi-label' style='font-size: 0.65rem;'>Depto. Más Afectado</div>
                                    <div class='kpi-value' style='font-size: 0.85rem;'>{dept_mas_afectado}</div>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    with col_kpi3:
                        if 'DEPARTAMENTO' in df_delito.columns:
                            casos_dept = df_delito['DEPARTAMENTO'].value_counts().iloc[0]
                            st.markdown(f"""
                                <div class='kpi-box' style='padding: 0.5rem;'>
                                    <div class='kpi-label' style='font-size: 0.65rem;'>Casos en ese Depto</div>
                                    <div class='kpi-value' style='font-size: 1.2rem;'>{casos_dept:,}</div>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    with col_kpi4:
                        porcentaje_total = (len(df_delito) / len(df_filtrado)) * 100
                        st.markdown(f"""
                            <div class='kpi-box' style='padding: 0.5rem;'>
                                <div class='kpi-label' style='font-size: 0.65rem;'>% del Total Filtrado</div>
                                <div class='kpi-value' style='font-size: 1.2rem;'>{porcentaje_total:.2f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    col_grafica, col_pie = st.columns([2, 1])
                    
                    with col_grafica:
                        n_armas_mostrar = st.number_input(
                            "Número de armas a mostrar:",
                            min_value=5,
                            max_value=20,
                            value=10,
                            step=1,
                            key="n_armas_delito_detalle"
                        )
                        
                        armas_delito = df_delito['ARMAS_MEDIOS'].value_counts().head(n_armas_mostrar)
                        total_armas_delito = df_delito['ARMAS_MEDIOS'].value_counts().sum()
                        
                        df_armas_viz = pd.DataFrame({
                            'Arma': armas_delito.index,
                            'Frecuencia': armas_delito.values,
                            'Porcentaje': (armas_delito.values / total_armas_delito * 100).round(2)
                        })
                        
                        colores = [PALETA_ROJA[2] if i != 0 else PALETA_ROJA[0] 
                                  for i in range(len(df_armas_viz))]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            y=df_armas_viz['Arma'],
                            x=df_armas_viz['Frecuencia'],
                            orientation='h',
                            marker=dict(color=colores),
                            text=[f"{pct:.1f}% ({freq:,})" for pct, freq in zip(df_armas_viz['Porcentaje'], df_armas_viz['Frecuencia'])],
                            textposition='outside',
                            textfont=dict(size=9),
                            hovertemplate='<b>%{y}</b><br>Casos: %{x:,}<br>% del delito: %{text}<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title=f'Armas/Medios Utilizados en {delito_seleccionado}',
                            xaxis_title='Frecuencia',
                            yaxis_title='',
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            height=400,
                            yaxis={'categoryorder': 'total ascending'},
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col_pie:
                        # PIE CHART que se adapta al número de armas seleccionadas
                        top_armas_pie_detalle = armas_delito.head(n_armas_mostrar)
                        fig = px.pie(
                            values=top_armas_pie_detalle.values,
                            names=top_armas_pie_detalle.index,
                            title=f'Top {n_armas_mostrar} Armas (%)',
                            hole=0.4,
                            color_discrete_sequence=PALETA_ROJA
                        )
                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent',
                            hovertemplate='<b>%{label}</b><br>Casos: %{value:,}<br>Porcentaje: %{percent}<extra></extra>'
                        )
                        fig.update_layout(showlegend=True, height=400)
                        st.plotly_chart(fig, use_container_width=True)

    # ================================================================
    # SECCIÓN: ARMAS Y MEDIOS (CORREGIDA Y MEJORADA)
    # ================================================================
    elif selected_section == "Armas y Medios":
        st.header("Análisis de Armas y Medios")

        if 'ARMAS_MEDIOS' in df.columns:
            # FILTROS GLOBALES
            st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-title'>FILTROS INTERACTIVOS</div>", unsafe_allow_html=True)
            
            col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
            
            with col_f1:
                if 'AÑO' in df.columns:
                    df_temp = df[df['AÑO'] != 'NO REPORTADO'].copy()
                    años_disponibles = sorted(pd.to_numeric(df_temp['AÑO'], errors='coerce').dropna().unique().astype(int))
                    años_seleccionados_armas = st.multiselect(
                        "Años:",
                        options=años_disponibles,
                        default=años_disponibles,
                        key="filtro_años_armas"
                    )
                else:
                    años_seleccionados_armas = None
            
            with col_f2:
                if 'DEPARTAMENTO' in df.columns:
                    deptos_disponibles = sorted([str(x) for x in df['DEPARTAMENTO'].dropna().unique()])
                    deptos_seleccionados_armas = st.multiselect(
                        "Departamentos:",
                        options=deptos_disponibles,
                        default=deptos_disponibles[:5] if len(deptos_disponibles) > 5 else deptos_disponibles,
                        key="filtro_deptos_armas"
                    )
                else:
                    deptos_seleccionados_armas = None
            
            with col_f3:
                if 'TIPO_DELITO' in df.columns:
                    delitos_disponibles = sorted([str(x) for x in df['TIPO_DELITO'].dropna().unique()])
                    delitos_seleccionados_armas = st.multiselect(
                        "Tipos de Delito:",
                        options=delitos_disponibles,
                        default=delitos_disponibles[:5] if len(delitos_disponibles) > 5 else delitos_disponibles,
                        key="filtro_delitos_armas"
                    )
                else:
                    delitos_seleccionados_armas = None
            
            with col_f4:
                # NUEVO FILTRO DE ARMAS
                armas_disponibles_filtro = sorted([str(x) for x in df['ARMAS_MEDIOS'].dropna().unique()])
                armas_seleccionadas_filtro = st.multiselect(
                    "Armas/Medios:",
                    options=armas_disponibles_filtro,
                    default=armas_disponibles_filtro,
                    key="filtro_armas_principal"
                )
            
            with col_f5:
                n_armas = st.number_input(
                    "Top N Armas:",
                    min_value=5,
                    max_value=30,
                    value=10,
                    step=1,
                    key="n_armas_visual"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Aplicar filtros de forma eficiente (sin copias innecesarias)
            # Crear máscara booleana para todos los filtros
            mask = pd.Series([True] * len(df), index=df.index)
            
            if años_seleccionados_armas and 'AÑO' in df.columns:
                año_num = pd.to_numeric(df['AÑO'], errors='coerce')
                mask &= año_num.isin(años_seleccionados_armas)
            
            if deptos_seleccionados_armas and 'DEPARTAMENTO' in df.columns:
                mask &= df['DEPARTAMENTO'].isin(deptos_seleccionados_armas)
            
            if delitos_seleccionados_armas and 'TIPO_DELITO' in df.columns:
                mask &= df['TIPO_DELITO'].isin(delitos_seleccionados_armas)
            
            if armas_seleccionadas_filtro and 'ARMAS_MEDIOS' in df.columns:
                mask &= df['ARMAS_MEDIOS'].isin(armas_seleccionadas_filtro)
            
            # Aplicar la máscara una sola vez
            df_filtrado_armas = df[mask].copy()

            if len(df_filtrado_armas) == 0:
                st.warning("No hay datos para los filtros seleccionados.")
            else:
                # KPIs
                armas_counts = df_filtrado_armas['ARMAS_MEDIOS'].value_counts()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Registros Filtrados</div>
                            <div class='kpi-value'>{len(df_filtrado_armas):,}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Tipos de Armas</div>
                            <div class='kpi-value'>{df_filtrado_armas['ARMAS_MEDIOS'].nunique()}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    arma_mas_usada = armas_counts.index[0]
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Arma Más Usada</div>
                            <div class='kpi-value' style='font-size: 0.9rem;'>{arma_mas_usada[:20]}...</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col4:
                    casos_arma_max = armas_counts.values[0]
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Casos con Esa Arma</div>
                            <div class='kpi-value'>{casos_arma_max:,}</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

                # Primera fila: Barras y Pie (FILTRADO)
                col1, col2 = st.columns([2, 1])

                with col1:
                    top_armas = armas_counts.head(n_armas)
                    fig = px.bar(
                        x=top_armas.values,
                        y=top_armas.index,
                        orientation='h',
                        title=f'Top {n_armas} Armas/Medios Más Utilizados',
                        labels={'x': 'Frecuencia', 'y': 'Arma/Medio'},
                        color=top_armas.values,
                        color_continuous_scale=PALETA_ROJA
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        height=480,
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # PIE FILTRADO - Se adapta al número de armas del filtro
                    top_armas_pie = armas_counts.head(n_armas)
                    fig = px.pie(
                        values=top_armas_pie.values,
                        names=top_armas_pie.index,
                        title=f'Top {n_armas} Armas/Medios',
                        hole=0.4,
                        color_discrete_sequence=PALETA_ROJA[::-1]
                    )
                    fig.update_traces(textposition='inside', textinfo='percent')
                    fig.update_layout(showlegend=True, height=480)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Segunda fila: Mayor vs Menor y Evolución
                st.markdown("---")
                st.subheader("Análisis Comparativo")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    arma_max = top_armas.index[0]
                    casos_max = top_armas.values[0]
                    arma_min = top_armas.index[-1]
                    casos_min = top_armas.values[-1]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['Mayor Uso', 'Menor Uso'],
                        y=[casos_max, casos_min],
                        marker=dict(color=[PALETA_ROJA[0], PALETA_ROJA[5]]),
                        text=[f"{arma_max}<br>{casos_max:,}", f"{arma_min}<br>{casos_min:,}"],
                        textposition='outside'
                    ))
                    fig.update_layout(
                        title='Armas con Mayor y Menor Uso',
                        yaxis_title='Número de Casos',
                        plot_bgcolor='white',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                                
                    # Evolución temporal FILTRADA - Se adapta al Top N seleccionado
                    if 'AÑO' in df_filtrado_armas.columns:
                        df_temp_armas = df_filtrado_armas[df_filtrado_armas['AÑO'] != 'NO REPORTADO'].copy()
                        df_temp_armas['AÑO'] = pd.to_numeric(df_temp_armas['AÑO'], errors='coerce')
                        df_temp_armas = df_temp_armas.dropna(subset=['AÑO'])

                        # Determinar armas para la evolución según el Top N seleccionado
                        armas_para_evolucion = armas_counts.head(n_armas).index.tolist()
                        titulo_evol = f"Evolución Top {n_armas} Armas/Medios"

                        df_evol_armas = df_temp_armas[df_temp_armas['ARMAS_MEDIOS'].isin(armas_para_evolucion)]

                        if len(df_evol_armas) > 0:
                            evol_armas = df_evol_armas.groupby(['AÑO', 'ARMAS_MEDIOS']).size().reset_index(name='Casos')

                            fig = px.line(
                                evol_armas,
                                x='AÑO',
                                y='Casos',
                                color='ARMAS_MEDIOS',
                                title=titulo_evol,
                                markers=True,
                                color_discrete_sequence=PALETA_ROJA[:len(armas_para_evolucion)]
                            )
                            fig.update_layout(plot_bgcolor='white', height=400)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("No hay datos temporales para las armas seleccionadas.")

                
                # Mapa de calor con filtros independientes
                if 'DEPARTAMENTO' in df_filtrado_armas.columns:
                    st.markdown("---")
                    st.subheader("Mapa de Calor: Armas vs Departamentos")
                    
                    col_config1, col_config2 = st.columns([1, 4])
                    
                    with col_config1:
                        n_departamentos_armas = st.number_input(
                            "Top Departamentos:",
                            min_value=5,
                            max_value=33,
                            value=10,
                            step=1,
                            key="dep_armas_hm"
                        )
                        n_armas_hm = st.number_input(
                            "Top Armas:",
                            min_value=5,
                            max_value=20,
                            value=8,
                            step=1,
                            key="armas_hm"
                        )
                        escala = st.selectbox(
                            "Escala de color:",
                            ["Reds", "YlOrRd", "OrRd"],
                            key="escala_armas"
                        )
                    
                    with col_config2:
                        top_deps = df_filtrado_armas['DEPARTAMENTO'].value_counts().head(n_departamentos_armas).index
                        top_arms = df_filtrado_armas['ARMAS_MEDIOS'].value_counts().head(n_armas_hm).index
                        
                        df_hm = df_filtrado_armas[df_filtrado_armas['DEPARTAMENTO'].isin(top_deps) & 
                                                   df_filtrado_armas['ARMAS_MEDIOS'].isin(top_arms)]
                        heatmap_data = pd.crosstab(df_hm['DEPARTAMENTO'], df_hm['ARMAS_MEDIOS'])
                        
                        fig = px.imshow(
                            heatmap_data,
                            labels=dict(x="Arma/Medio", y="Departamento", color="Frecuencia"),
                            x=heatmap_data.columns,
                            y=heatmap_data.index,
                            color_continuous_scale=escala,
                            aspect="auto",
                            title=f"Concentración: Top {n_departamentos_armas} Departamentos vs Top {n_armas_hm} Armas",
                            text_auto=True
                        )
                        fig.update_layout(height=500)
                        fig.update_xaxes(side="bottom", tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
    # ================================================================
    # SECCIÓN: ANÁLISIS GEOGRÁFICO
    # ================================================================
    elif selected_section == "Análisis Geográfico":
        st.header("Análisis Geográfico de los Delitos")

        if 'DEPARTAMENTO' in df.columns:
            # FILTROS GLOBALES
            st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-title'>FILTROS INTERACTIVOS</div>", unsafe_allow_html=True)
            
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                deptos_disponibles_geo = sorted([str(x) for x in df['DEPARTAMENTO'].dropna().unique()])
                deptos_seleccionados_geo = st.multiselect(
                    "Departamentos:",
                    options=deptos_disponibles_geo,
                    default=deptos_disponibles_geo[:10] if len(deptos_disponibles_geo) > 10 else deptos_disponibles_geo,
                    key="filtro_deptos_geo"
                )
            
            with col_f2:
                if 'AÑO' in df.columns:
                    df_temp = df[df['AÑO'] != 'NO REPORTADO'].copy()
                    años_disponibles_geo = sorted(pd.to_numeric(df_temp['AÑO'], errors='coerce').dropna().unique().astype(int))
                    años_seleccionados_geo = st.multiselect(
                        "Años:",
                        options=años_disponibles_geo,
                        default=años_disponibles_geo,
                        key="filtro_años_geo"
                    )
                else:
                    años_seleccionados_geo = None
            
            with col_f3:
                if 'TIPO_DELITO' in df.columns:
                    delitos_disponibles_geo = sorted([str(x) for x in df['TIPO_DELITO'].dropna().unique()])
                    delitos_seleccionados_geo = st.multiselect(
                        "Tipos de Delito:",
                        options=delitos_disponibles_geo,
                        default=delitos_disponibles_geo[:5] if len(delitos_disponibles_geo) > 5 else delitos_disponibles_geo,
                        key="filtro_delitos_geo"
                    )
                else:
                    delitos_seleccionados_geo = None
            
            with col_f4:
                top_n_geo = st.number_input(
                    "Top N Visualizar:",
                    min_value=3,
                    max_value=20,
                    value=10,
                    step=1,
                    key="n_deptos_visual"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Aplicar filtros
            df_filtrado_geo = df[df['DEPARTAMENTO'].isin(deptos_seleccionados_geo)].copy()
            if años_seleccionados_geo and 'AÑO' in df_filtrado_geo.columns:
                df_filtrado_geo['AÑO_NUM'] = pd.to_numeric(df_filtrado_geo['AÑO'], errors='coerce')
                df_filtrado_geo = df_filtrado_geo[df_filtrado_geo['AÑO_NUM'].isin(años_seleccionados_geo)]
            if delitos_seleccionados_geo and 'TIPO_DELITO' in df_filtrado_geo.columns:
                df_filtrado_geo = df_filtrado_geo[df_filtrado_geo['TIPO_DELITO'].isin(delitos_seleccionados_geo)]

            if len(df_filtrado_geo) == 0:
                st.warning("No hay datos para los filtros seleccionados.")
            else:
                # KPIs
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Registros Filtrados</div>
                            <div class='kpi-value'>{len(df_filtrado_geo):,}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Departamentos</div>
                            <div class='kpi-value'>{df_filtrado_geo['DEPARTAMENTO'].nunique()}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    if "MUNICIPIO" in df_filtrado_geo.columns:
                        st.markdown(f"""
                            <div class='kpi-box'>
                                <div class='kpi-label'>Municipios</div>
                                <div class='kpi-value'>{df_filtrado_geo['MUNICIPIO'].nunique()}</div>
                            </div>
                        """, unsafe_allow_html=True)
                with col4:
                    if "TIPO_DELITO" in df_filtrado_geo.columns:
                        st.markdown(f"""
                            <div class='kpi-box'>
                                <div class='kpi-label'>Tipos de Delito</div>
                                <div class='kpi-value'>{df_filtrado_geo['TIPO_DELITO'].nunique()}</div>
                            </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # Evolución temporal por departamento
                if 'AÑO' in df_filtrado_geo.columns:
                    st.subheader("Evolución Temporal por Departamento")
                    
                    df_evol = df_filtrado_geo[df_filtrado_geo['AÑO'] != 'NO REPORTADO'].copy()
                    df_evol['AÑO'] = pd.to_numeric(df_evol['AÑO'], errors='coerce')
                    df_evol = df_evol.dropna(subset=['AÑO'])
                    
                    top_deps_evol = df_evol['DEPARTAMENTO'].value_counts().head(top_n_geo).index
                    df_top_deps = df_evol[df_evol['DEPARTAMENTO'].isin(top_deps_evol)]
                    
                    evol_deps = df_top_deps.groupby(['AÑO', 'DEPARTAMENTO']).size().reset_index(name='Casos')
                    
                    fig = px.line(
                        evol_deps,
                        x='AÑO',
                        y='Casos',
                        color='DEPARTAMENTO',
                        title=f'Evolución Temporal: Top {top_n_geo} Departamentos',
                        markers=True,
                        color_discrete_sequence=PALETA_ROJA
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Análisis de delitos
                st.subheader("Análisis de Delitos por Departamento")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    top_delitos_geo = df_filtrado_geo['TIPO_DELITO'].value_counts().head(top_n_geo)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        y=top_delitos_geo.index,
                        x=top_delitos_geo.values,
                        orientation='h',
                        marker=dict(
                            color=top_delitos_geo.values,
                            colorscale=[[0, PALETA_ROJA[5]], [1, PALETA_ROJA[0]]],
                            showscale=False
                        ),
                        text=top_delitos_geo.values,
                        textposition='outside'
                    ))
                    fig.update_layout(
                        title=f'Top {top_n_geo} Delitos en Zona Seleccionada',
                        xaxis_title='Casos',
                        yaxis_title='',
                        plot_bgcolor='white',
                        height=450,
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    delito_max_geo = top_delitos_geo.index[0]
                    casos_max_geo = top_delitos_geo.values[0]
                    delito_min_geo = top_delitos_geo.index[-1]
                    casos_min_geo = top_delitos_geo.values[-1]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['Mayor Casos', 'Menor Casos'],
                        y=[casos_max_geo, casos_min_geo],
                        marker=dict(color=[PALETA_ROJA[0], PALETA_ROJA[5]]),
                        text=[f"{delito_max_geo[:30]}<br>{casos_max_geo:,}", 
                              f"{delito_min_geo[:30]}<br>{casos_min_geo:,}"],
                        textposition='outside',
                        textfont=dict(size=9)
                    ))
                    fig.update_layout(
                        title='Delito con Mayor y Menor Incidencia',
                        yaxis_title='Número de Casos',
                        plot_bgcolor='white',
                        height=450
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Pie y Treemap
                col1, col2 = st.columns(2)
                
                top_deptos_viz = df_filtrado_geo['DEPARTAMENTO'].value_counts().head(top_n_geo)
                
                with col1:
                    fig = px.pie(
                        values=top_deptos_viz.values,
                        names=top_deptos_viz.index,
                        title=f"Distribución Top {top_n_geo} Departamentos",
                        hole=0.4,
                        color_discrete_sequence=PALETA_ROJA[::-1]
                    )
                    fig.update_traces(textposition='inside', textinfo='percent')
                    fig.update_layout(showlegend=True, height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.treemap(
                        names=top_deptos_viz.index,
                        parents=[""] * len(top_deptos_viz),
                        values=top_deptos_viz.values,
                        title=f'Mapa de Árbol: Top {top_n_geo} Departamentos',
                        color=top_deptos_viz.values,
                        color_continuous_scale=PALETA_ROJA
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Mapa de calor
                if 'TIPO_DELITO' in df_filtrado_geo.columns:
                    st.markdown("---")
                    st.subheader("Mapa de Calor: Departamentos vs Tipos de Delito")
                    
                    col_config1, col_config2 = st.columns([1, 4])
                    
                    with col_config1:
                        n_deps_hm = st.number_input(
                            "Top Departamentos:",
                            min_value=5,
                            max_value=33,
                            value=12,
                            step=1,
                            key="deps_delitos_hm"
                        )
                        n_delitos_hm = st.number_input(
                            "Top Delitos:",
                            min_value=5,
                            max_value=20,
                            value=10,
                            step=1,
                            key="delitos_deps_hm"
                        )
                        escala_geo = st.selectbox(
                            "Escala de color:",
                            ["Reds", "YlOrRd", "OrRd"],
                            key="escala_geo"
                        )
                    
                    with col_config2:
                        top_deps_hm = df_filtrado_geo['DEPARTAMENTO'].value_counts().head(n_deps_hm).index
                        top_delitos_hm = df_filtrado_geo['TIPO_DELITO'].value_counts().head(n_delitos_hm).index
                        
                        df_hm_geo = df_filtrado_geo[df_filtrado_geo['DEPARTAMENTO'].isin(top_deps_hm) & 
                                                     df_filtrado_geo['TIPO_DELITO'].isin(top_delitos_hm)]
                        heatmap_geo = pd.crosstab(df_hm_geo['DEPARTAMENTO'], df_hm_geo['TIPO_DELITO'])
                        
                        heatmap_geo_pct = heatmap_geo.div(heatmap_geo.sum(axis=1), axis=0) * 100
                        
                        fig = px.imshow(
                            heatmap_geo,
                            labels=dict(x="Tipo de Delito", y="Departamento", color="Frecuencia"),
                            x=heatmap_geo.columns,
                            y=heatmap_geo.index,
                            color_continuous_scale=escala_geo,
                            aspect="auto",
                            title=f"Concentración: Top {n_deps_hm} Departamentos vs Top {n_delitos_hm} Delitos"
                        )
                        
                        fig.update_traces(
                            text=heatmap_geo_pct.round(1).astype(str) + '%',
                            texttemplate='%{text}',
                            textfont={"size": 8}
                        )
                        
                        fig.update_layout(height=550)
                        fig.update_xaxes(side="bottom", tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)

    # ================================================================
    # SECCIÓN: PERFIL DE VÍCTIMAS (CORREGIDA)
    # ================================================================
    elif selected_section == "Perfil de Víctimas":
        st.header("Análisis del Perfil de Víctimas")

        # Limpieza de datos de edad
        if "AGRUPA_EDAD_PERSONA" in df.columns:
            mapeo_edad = {
                "-": "NO REPORTADO",
                "NO REPORTA": "NO REPORTADO",
                "NO RESPORTADO": "NO REPORTADO",
                "ADOLSECENTES": "ADOLESCENTES"
            }
            df["AGRUPA_EDAD_PERSONA"] = (
                df["AGRUPA_EDAD_PERSONA"].astype(str).str.upper().str.strip().replace(mapeo_edad)
            )

        # FILTROS GLOBALES
        st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
        st.markdown("<div class='filter-title'>FILTROS INTERACTIVOS</div>", unsafe_allow_html=True)
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            if 'DEPARTAMENTO' in df.columns:
                deptos_disponibles_victimas = sorted([str(x) for x in df['DEPARTAMENTO'].dropna().unique()])
                deptos_seleccionados_victimas = st.multiselect(
                    "Departamentos:",
                    options=deptos_disponibles_victimas,
                    default=deptos_disponibles_victimas[:5] if len(deptos_disponibles_victimas) > 5 else deptos_disponibles_victimas,
                    key="filtro_deptos_victimas"
                )
            else:
                deptos_seleccionados_victimas = None
        
        with col_f2:
            if 'AÑO' in df.columns:
                df_temp = df[df['AÑO'] != 'NO REPORTADO'].copy()
                años_disponibles_victimas = sorted(pd.to_numeric(df_temp['AÑO'], errors='coerce').dropna().unique().astype(int))
                años_seleccionados_victimas = st.multiselect(
                    "Años:",
                    options=años_disponibles_victimas,
                    default=años_disponibles_victimas,
                    key="filtro_años_victimas"
                )
            else:
                años_seleccionados_victimas = None
        
        with col_f3:
            if 'TIPO_DELITO' in df.columns:
                delitos_disponibles_victimas = sorted([str(x) for x in df['TIPO_DELITO'].dropna().unique()])
                delitos_seleccionados_victimas = st.multiselect(
                    "Tipos de Delito:",
                    options=delitos_disponibles_victimas,
                    default=delitos_disponibles_victimas[:5] if len(delitos_disponibles_victimas) > 5 else delitos_disponibles_victimas,
                    key="filtro_delitos_victimas"
                )
            else:
                delitos_seleccionados_victimas = None
        
        with col_f4:
            if 'GENERO' in df.columns:
                generos_disponibles = sorted([str(x) for x in df['GENERO'].dropna().unique()])
                generos_seleccionados = st.multiselect(
                    "Género:",
                    options=generos_disponibles,
                    default=generos_disponibles,
                    key="filtro_genero"
                )
            else:
                generos_seleccionados = None
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Aplicar filtros
        df_filtrado_victimas = df.copy()
        if deptos_seleccionados_victimas and 'DEPARTAMENTO' in df_filtrado_victimas.columns:
            df_filtrado_victimas = df_filtrado_victimas[df_filtrado_victimas['DEPARTAMENTO'].isin(deptos_seleccionados_victimas)]
        if años_seleccionados_victimas and 'AÑO' in df_filtrado_victimas.columns:
            df_filtrado_victimas['AÑO_NUM'] = pd.to_numeric(df_filtrado_victimas['AÑO'], errors='coerce')
            df_filtrado_victimas = df_filtrado_victimas[df_filtrado_victimas['AÑO_NUM'].isin(años_seleccionados_victimas)]
        if delitos_seleccionados_victimas and 'TIPO_DELITO' in df_filtrado_victimas.columns:
            df_filtrado_victimas = df_filtrado_victimas[df_filtrado_victimas['TIPO_DELITO'].isin(delitos_seleccionados_victimas)]
        if generos_seleccionados and 'GENERO' in df_filtrado_victimas.columns:
            df_filtrado_victimas = df_filtrado_victimas[df_filtrado_victimas['GENERO'].isin(generos_seleccionados)]

        if len(df_filtrado_victimas) == 0:
            st.warning("No hay datos para los filtros seleccionados.")
        else:
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-label'>Víctimas Total</div>
                        <div class='kpi-value'>{len(df_filtrado_victimas):,}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if 'GENERO' in df_filtrado_victimas.columns:
                    genero_predominante = df_filtrado_victimas['GENERO'].value_counts().index[0]
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Género Predominante</div>
                            <div class='kpi-value'>{genero_predominante}</div>
                        </div>
                    """, unsafe_allow_html=True)
            with col3:
                if 'AGRUPA_EDAD_PERSONA' in df_filtrado_victimas.columns:
                    edad_predominante = df_filtrado_victimas['AGRUPA_EDAD_PERSONA'].value_counts().index[0]
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>Grupo Edad Predominante</div>
                            <div class='kpi-value' style='font-size: 0.9rem;'>{edad_predominante}</div>
                        </div>
                    """, unsafe_allow_html=True)
            with col4:
                if 'GENERO' in df_filtrado_victimas.columns:
                    pct_genero = (df_filtrado_victimas['GENERO'].value_counts().values[0] / len(df_filtrado_victimas)) * 100
                    st.markdown(f"""
                        <div class='kpi-box'>
                            <div class='kpi-label'>% Género Predominante</div>
                            <div class='kpi-value'>{pct_genero:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

            if "GENERO" in df_filtrado_victimas.columns:
                st.subheader("Distribución de Víctimas por Género")

                genero_counts = df_filtrado_victimas["GENERO"].value_counts().reset_index()
                genero_counts.columns = ["Género", "Víctimas"]

                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        genero_counts,
                        names="Género",
                        values="Víctimas",
                        hole=0.4,
                        title="Distribución por Género",
                        color_discrete_sequence=PALETA_ROJA[::-1]
                    )
                    fig.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        genero_counts,
                        x="Género",
                        y="Víctimas",
                        title="Víctimas por Género",
                        color="Víctimas",
                        color_continuous_scale=PALETA_ROJA
                    )
                    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
                    st.plotly_chart(fig, use_container_width=True)

            if "AGRUPA_EDAD_PERSONA" in df_filtrado_victimas.columns:
                st.markdown("---")
                st.subheader("Distribución por Grupo de Edad")

                edad_count = df_filtrado_victimas.groupby("AGRUPA_EDAD_PERSONA").size().reset_index(name="Víctimas")
                edad_count = edad_count.sort_values("Víctimas", ascending=False)

                col1, col2 = st.columns(2)
                
                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=edad_count["Víctimas"],
                        y=edad_count["AGRUPA_EDAD_PERSONA"],
                        mode="markers+lines",
                        line=dict(color=PALETA_ROJA[-2], width=2),
                        marker=dict(size=16, color=PALETA_ROJA[-1], line=dict(color="white", width=2))
                    ))
                    fig.update_layout(
                        title="Víctimas por Grupo de Edad",
                        xaxis_title="Número de Víctimas",
                        yaxis_title="Grupo de Edad",
                        plot_bgcolor="white",
                        height=450
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        edad_count,
                        y="AGRUPA_EDAD_PERSONA",
                        x="Víctimas",
                        orientation='h',
                        title="Comparación de Grupos de Edad",
                        color="Víctimas",
                        color_continuous_scale=PALETA_ROJA
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        height=450,
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Análisis combinado Género x Edad
                st.markdown("---")
                st.subheader("Análisis Combinado: Género x Edad")
                
                if 'GENERO' in df_filtrado_victimas.columns:
                    cross_genero_edad = pd.crosstab(
                        df_filtrado_victimas['AGRUPA_EDAD_PERSONA'],
                        df_filtrado_victimas['GENERO']
                    )
                    
                    fig = px.bar(
                        cross_genero_edad.reset_index(),
                        x='AGRUPA_EDAD_PERSONA',
                        y=cross_genero_edad.columns.tolist(),
                        title='Distribución de Víctimas por Género y Edad',
                        labels={'value': 'Número de Víctimas', 'variable': 'Género'},
                        color_discrete_sequence=PALETA_ROJA[:len(cross_genero_edad.columns)],
                        barmode='group'
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        height=450,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # ================================================================
    # SECCIÓN: MODELO ESTRELLA
    # ================================================================
    elif selected_section == "Modelo Estrella":
        st.header("Estructura del Modelo Estrella")
        
        st.markdown("""
        ### Arquitectura del Modelo Dimensional
        
        Este modelo estrella permite análisis OLAP (Online Analytical Processing) 
        eficiente de los datos de criminalidad en Colombia.
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            #### Tabla de Hechos: fact_delitos
            
            **Métricas:**
            - `CANTIDAD`: Número de delitos
            - `latitud`, `longitud`: Coordenadas geográficas
            - `FECHA_HECHO`: Fecha del delito
            
            **Claves Foráneas (FK):**
            - `fecha_key` → dim_tiempo
            - `ubicacion_key` → dim_ubicacion
            - `victima_key` → dim_victima
            - `arma_key` → dim_arma_medio
            - `delito_key` → dim_tipo_delito
            
            #### Tablas de Dimensión:
            
            **1. dim_tiempo**
            - fecha_key (PK)
            - AÑO, MES, DIA
            - DIA_SEMANA, PERIODO
            
            **2. dim_ubicacion**
            - ubicacion_key (PK)
            - DEPARTAMENTO, MUNICIPIO
            - CODIGO_DANE
            
            **3. dim_victima**
            - victima_key (PK)
            - GENERO, AGRUPA_EDAD_PERSONA
            - ESCOLARIDAD (si aplica)
            
            **4. dim_arma_medio**
            - arma_key (PK)
            - ARMAS_MEDIOS
            - CATEGORIA_ARMA
            
            **5. dim_tipo_delito**
            - delito_key (PK)
            - TIPO_DELITO, DELITO
            - CATEGORIA_DELITO
            """)
        
        with col2:
            st.info("""
            **Granularidad:**
            
            Un registro en la tabla 
            de hechos representa un 
            delito específico con sus 
            características completas.
            
            ---
            
            **Ventajas:**
            
            - Consultas rápidas
            - Fácil de entender
            - Optimizado para BI
            - Escalable
            - Flexible para análisis
            """)
            
            st.success("""
            **Casos de Uso:**
            
            - Análisis temporal
            - Segmentación geográfica
            - Perfiles de víctimas
            - Patrones delictivos
            - Políticas públicas
            """)

    # ================================================================
    # SECCIÓN: HALLAZGOS PRINCIPALES (NUEVA)
    # ================================================================
    elif selected_section == "Hallazgos Principales":
        st.header("Hallazgos Principales y Conclusiones")
        
        st.markdown("""
        Este resumen presenta las conclusiones más relevantes extraídas del análisis de los datos de seguridad y convivencia.
        """)
        
        # 1. Tendencia Temporal
        if 'AÑO' in df.columns and (df['AÑO'] != 'NO REPORTADO').any():
            df_clean = df[df['AÑO'] != 'NO REPORTADO'].copy()
            df_clean['AÑO'] = pd.to_numeric(df_clean['AÑO'], errors='coerce')
            df_clean = df_clean.dropna(subset=['AÑO'])
            year_counts = df_clean['AÑO'].value_counts().sort_index()
            variacion = ((year_counts.iloc[-1] - year_counts.iloc[0]) / year_counts.iloc[0] * 100) if len(year_counts) > 1 and year_counts.iloc[0] != 0 else 0
            
            st.markdown(f"""
            ### 1. Tendencia Temporal
            - **Variación de Delitos:** Se observa una **variación del {variacion:+.1f}%** entre el año inicial y el final del periodo, indicando una tendencia general.
            - **Picos:** El **año con más delitos ({year_counts.idxmax()})** requiere un análisis específico de los factores desencadenantes.
            """)
            st.markdown("---")

        # 2. Concentración Delictiva
        if 'TIPO_DELITO' in df.columns:
            top_delito = df['TIPO_DELITO'].value_counts().index[0]
            top_5_delitos = df['TIPO_DELITO'].value_counts().head(5).sum()
            total = len(df)
            porcentaje_top_5 = (top_5_delitos / total) * 100
            
            st.markdown(f"""
            ### 2. Concentración Delictiva
            - **Delito Predominante:** El **{top_delito}** es el delito más frecuente en el periodo analizado.
            - **Concentración de Frecuencia:** El **Top 5** de delitos concentra aproximadamente el **{porcentaje_top_5:.1f}%** del total de casos, confirmando que la intervención debe priorizar estas categorías.
            """)
            st.markdown("---")
            
        # 3. Focos Geográficos
        if 'DEPARTAMENTO' in df.columns and 'MUNICIPIO' in df.columns:
            top_depto = df['DEPARTAMENTO'].value_counts().index[0]
            top_municipio = df['MUNICIPIO'].value_counts().index[0]
            st.markdown(f"""
            ### 3. Focos Geográficos
            - **Departamento Más Afectado:** El **{top_depto}** lidera el número absoluto de delitos.
            - **Municipios Críticos:** El municipio de **{top_municipio}** requiere una intervención prioritaria por ser el punto de mayor concentración.
            - **Composición Delictiva:** Los Mapas de Calor muestran que la **composición porcentual de delitos varía significativamente** entre departamentos, lo que valida la necesidad de estrategias de seguridad **localizadas**.
            """)
            st.markdown("---")

        # 4. Uso de Medios
        if 'ARMAS_MEDIOS' in df.columns:
            top_arma = df['ARMAS_MEDIOS'].value_counts().index[0]
            st.markdown(f"""
            ### 4. Uso de Medios
            - **Arma/Medio Común:** El **{top_arma}** es el medio más utilizado, lo cual guía las acciones de control.
            - **Patrones Regionales:** El Mapa de Calor (Armas vs. Departamentos) permite identificar patrones de uso, por ejemplo, departamentos donde el **arma de fuego** tiene una penetración porcentual inusualmente alta.
            """)
            st.markdown("---")
            
        # 5. Vulnerabilidad de Víctimas
        if 'GENERO' in df.columns and 'AGRUPA_EDAD_PERSONA' in df.columns:
            top_genero = df['GENERO'].value_counts().index[0]
            top_edad = df['AGRUPA_EDAD_PERSONA'].value_counts().index[0]
            st.markdown(f"""
            ### 5. Vulnerabilidad de Víctimas
            - **Género Dominante:** Las víctimas son predominantemente de **{top_genero}**.
            - **Grupo de Edad:** El grupo de edad **{top_edad}** es el más afectado, lo cual informa la focalización de campañas de prevención.
            """)
            st.markdown("---")

        # Conclusión Final
        st.markdown("""
        ### Conclusiones Generales
        
        Los hallazgos presentados evidencian patrones claros que requieren atención diferenciada:
        
        1. **Priorización Estratégica:** Los recursos deben concentrarse en los delitos y zonas de mayor incidencia.
        2. **Enfoque Territorial:** Las estrategias deben adaptarse a las características específicas de cada departamento.
        3. **Prevención Focalizada:** Las campañas preventivas deben dirigirse a los grupos poblacionales más vulnerables.
        4. **Control de Medios:** Las políticas de control de armas deben considerar los patrones regionales identificados.
        5. **Monitoreo Continuo:** Es fundamental mantener sistemas de seguimiento para detectar cambios en las tendencias.
        
        Este análisis proporciona una base sólida para la toma de decisiones informadas en materia de seguridad pública.
        """)

else:
    # CASO: No hay datos cargados
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">Error de Carga</h1>
            <p class="subtitle">No se pudo cargar el archivo de datos</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.error("""
    **No se pudo cargar el archivo de datos.**
    
    Por favor verifica:
    1. Que el archivo exista en la ruta especificada
    2. Que tengas permisos de lectura
    3. Que el formato del archivo sea válido (CSV)
    4. Que el archivo contenga las columnas esperadas
    
    **Ruta esperada:**
    ```
    C:\\Users\\ASUS\\OneDrive - Universidad Santo Tomás\\
    SANTO TOMAS\\8-SEMESTRE\\CONSULTORIA\\
    Datos-abiertos-Seguridad-y-Convivencia\\
    delitos_con_poblacion_limpio.csv
    ```
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #718096; padding: 2rem;'>
        <p style='margin: 0;'><strong>Universidad Santo Tomás</strong></p>
        <p style='margin: 0.5rem 0;'>Análisis Exploratorio de Datos de Seguridad y Convivencia</p>
        <p style='margin: 0; font-size: 0.9rem;'>Consultoría e Investigación | 2024-2025</p>
    </div>
""", unsafe_allow_html=True)