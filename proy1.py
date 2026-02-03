import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Comprobación extra.
try:
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        # Accedemos a la clave
        clave_actual = st.secrets["connections"]["gsheets"]["private_key"]
        # Si tiene "\\n" literales (doble barra), los cambiamos por saltos reales
        if "\\n" in clave_actual:
            st.secrets["connections"]["gsheets"]["private_key"] = clave_actual.replace("\\n", "\n")
except Exception as e:
    pass # Si falla, seguimos normal

# 1. Configuración
st.set_page_config(page_title="Nuestros Planes", page_icon="❤️")
st.title("❤️ Nuestra Agenda Compartida")

# 2. Conexión con Google Sheets
# ttl=0 significa que no guarde memoria caché, para que se actualice al instante
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Leemos la hoja completa
    return conn.read(worksheet="Hoja 1", ttl=0) # Asegúrate que tu pestaña se llama "Hoja 1"

def guardar_datos(df):
    # Escribimos los datos de vuelta
    conn.update(worksheet="Hoja 1", data=df)

# Cargar datos al inicio
try:
    df = cargar_datos()
except Exception as e:
    st.error(f"⚠️ AQUÍ ESTÁ EL ERROR REAL: {e}")
    st.stop()

# 3. Formulario para añadir
st.subheader("📝 Nuevo Plan")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    nuevo_plan = st.text_input("¿Qué hacemos?", placeholder="Ej: Ir a la bolera")
with col2:
    categoria = st.selectbox("Tipo", ["Peli/Serie", "Comida", "Viaje", "Otro"])
with col3:
    st.write("")
    st.write("")
    if st.button("Añadir"):
        if nuevo_plan:
            nueva_fila = pd.DataFrame([{"Plan": nuevo_plan, "Categoria": categoria, "Hecho": False}])
            # Unimos y nos aseguramos de no perder datos
            df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
            guardar_datos(df_actualizado)
            st.success("¡Guardado en la nube! ☁️")
            st.rerun()

st.divider()

# 4. Lista de planes
st.subheader("📌 Lista de Pendientes")

if not df.empty:
    for index, row in df.iterrows():
        col_check, col_text, col_del = st.columns([0.5, 3, 0.5])
        
        # Checkbox
        estado_actual = row["Hecho"]
        # Convertimos a bool python por si viene como texto de google sheets
        if isinstance(estado_actual, str):
            estado_actual = estado_actual.upper() == "TRUE"
            
        check = col_check.checkbox("Hecho", value=bool(estado_actual), key=f"check_{index}", label_visibility="hidden")
        
        col_text.write(f"**{row['Categoria']}:** {row['Plan']}")
        
        if col_del.button("🗑️", key=f"del_{index}"):
            df = df.drop(index)
            guardar_datos(df)
            st.rerun()

        # Si cambia el checkbox
        if check != bool(estado_actual):
            df.at[index, "Hecho"] = check
            guardar_datos(df)
            st.rerun()
else:
    st.info("La lista está vacía.")
