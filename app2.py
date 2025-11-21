import streamlit as st
import pandas as pd
import zipfile
import os

st.set_page_config(page_title="Test - Carga de Datos", layout="wide")

st.title("🔍 Diagnóstico de Carga de Datos - USTA")

# Mostrar información del sistema
st.subheader("📁 Información del Sistema")

try:
    directorio_actual = os.getcwd()
    st.success(f"✅ Directorio actual: `{directorio_actual}`")
except Exception as e:
    st.error(f"❌ Error obteniendo directorio: {e}")

try:
    archivos = os.listdir('.')
    st.success(f"✅ Archivos encontrados: {len(archivos)}")
    
    with st.expander("Ver lista completa de archivos"):
        for archivo in sorted(archivos):
            st.write(f"- {archivo}")
except Exception as e:
    st.error(f"❌ Error listando archivos: {e}")

# Intentar cargar el ZIP
st.markdown("---")
st.subheader("📦 Intentando cargar ZIP...")

ZIP_PATH = "delitos_con_poblacion_limpio.zip"

if os.path.exists(ZIP_PATH):
    st.success(f"✅ **Archivo ZIP encontrado:** `{ZIP_PATH}`")
    
    # Obtener tamaño del archivo
    try:
        tamaño_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
        st.info(f"📏 Tamaño del archivo: {tamaño_mb:.2f} MB")
    except Exception as e:
        st.warning(f"No se pudo obtener el tamaño: {e}")
    
    # Intentar abrir el ZIP
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            archivos_zip = zip_ref.namelist()
            st.success(f"✅ **ZIP válido** con {len(archivos_zip)} archivo(s)")
            
            st.write("**Archivos dentro del ZIP:**")
            for archivo in archivos_zip:
                st.write(f"- `{archivo}`")
            
            # Intentar leer el primer CSV encontrado
            csv_files = [f for f in archivos_zip if f.endswith('.csv')]
            
            if csv_files:
                csv_name = csv_files[0]
                st.info(f"📄 Intentando leer: `{csv_name}`")
                
                try:
                    with zip_ref.open(csv_name) as file:
                        # Intentar diferentes encodings
                        encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
                        df = None
                        
                        for encoding in encodings:
                            try:
                                file.seek(0)
                                df = pd.read_csv(file, encoding=encoding, nrows=10)
                                st.success(f"✅ **CSV cargado correctamente** con encoding: `{encoding}`")
                                break
                            except Exception as enc_error:
                                continue
                        
                        if df is not None:
                            # Mostrar información del DataFrame
                            st.markdown("---")
                            st.subheader("✅ ¡Datos Cargados Exitosamente!")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📊 Columnas", df.shape[1])
                            with col2:
                                st.metric("📝 Filas (muestra)", len(df))
                            with col3:
                                memoria = df.memory_usage(deep=True).sum() / 1024
                                st.metric("💾 Memoria", f"{memoria:.1f} KB")
                            
                            st.markdown("**Vista previa:**")
                            st.dataframe(df, use_container_width=True)
                            
                            st.markdown("**Columnas disponibles:**")
                            for col in df.columns:
                                st.write(f"- `{col}` ({df[col].dtype})")
                            
                            st.success("🎉 **¡Todo funciona correctamente!** Ahora puedes usar el código completo del dashboard.")
                        else:
                            st.error("❌ No se pudo leer el CSV con ningún encoding")
                            
                except Exception as e:
                    st.error(f"❌ Error al leer CSV: {e}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                st.error("❌ No se encontraron archivos CSV dentro del ZIP")
                
    except zipfile.BadZipFile:
        st.error("❌ El archivo no es un ZIP válido o está corrupto")
        st.info("💡 Intenta volver a comprimir el archivo CSV")
    except Exception as e:
        st.error(f"❌ Error al abrir ZIP: {e}")
        import traceback
        st.code(traceback.format_exc())
else:
    st.error(f"❌ **No se encontró el archivo:** `{ZIP_PATH}`")
    
    st.warning("🔍 **Archivos disponibles en el directorio:**")
    try:
        for archivo in os.listdir('.'):
            icono = "📦" if archivo.endswith('.zip') else "📄"
            st.write(f"{icono} `{archivo}`")
    except:
        st.write("No se pudieron listar los archivos")
    
    st.markdown("---")
    st.info("""
    **💡 Solución:**
    
    1. Ve a tu repositorio en GitHub: https://github.com/Suarez5479/consultoria
    2. Verifica que el archivo `delitos_con_poblacion_limpio.zip` esté en la raíz
    3. Si no está, súbelo con: **Add file → Upload files**
    4. Asegúrate de que el nombre sea exactamente: `delitos_con_poblacion_limpio.zip`
    """)

# Pie de página
st.markdown("---")
st.caption("🔧 Diagnóstico realizado - Universidad Santo Tomás")
