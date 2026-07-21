import streamlit as st
import json
import random
import requests
from io import BytesIO
from PIL import Image, ImageFilter

# Configuración de página responsive y limpia
st.set_page_config(
    page_title="Futbol Games",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Cargar base de datos JSON
@st.cache_data
def cargar_datos():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: No se encontró el archivo data.json.")
        return {
            "preguntados": [], 
            "adivina_jugador": [], 
            "palabras_mr_white": [],
            "jugador_borroso": []
        }

DATA = cargar_datos()

# Función para descargar e intensificar/reducir el desenfoque en caché
@st.cache_data
def obtener_imagen_procesada(url_imagen, nivel_desenfoque):
    try:
        headers = {'User-Agent': 'FutbolGamesApp/1.0'}
        response = requests.get(url_imagen, headers=headers, timeout=5)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        
        if nivel_desenfoque > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=nivel_desenfoque))
        return img
    except Exception:
        return None

# ---------------------------------------------------------------------------
# INTERFAZ PRINCIPAL (TABS)
# ---------------------------------------------------------------------------
st.title("⚽ Futbol Games")

tab1, tab2, tab3, tab4 = st.tabs([
    "🕵️ El impostor", 
    "🧠 Preguntados", 
    "👟 Adivina el Jugador", 
    "🖼️ Foto Borrosa"
])

# ===========================================================================
# 1. JUEGO: MR. WHITE (IMPOSTOR)
# ===========================================================================
with tab1:
    st.header("El Impostor")
    
    col1, col2 = st.columns(2)
    with col1:
        num_jugadores = st.number_input("Número de Jugadores", min_value=4, max_value=15, value=6, step=1)
    with col2:
        num_impostores = st.number_input("Número de Impostores", min_value=1, max_value=3, value=1, step=1)
        
    if num_impostores >= num_jugadores - 1:
        st.error("¡Debe haber más inocentes que impostores!")
        num_impostores = 1

    st.markdown("##### 👥 Nombres de los participantes:")
    nombres_ingresados = []
    
    cols_nombres = st.columns(2)
    for i in range(num_jugadores):
        col = cols_nombres[i % 2]
        nombre = col.text_input(
            f"Jugador {i + 1}", 
            value=f"Jugador {i + 1}", 
            key=f"input_nombre_{i}"
        ).strip()
        nombres_ingresados.append(nombre if nombre else f"Jugador {i + 1}")

    if "mw_roles" not in st.session_state:
        st.session_state.mw_roles = None
        st.session_state.mw_palabra = ""
        st.session_state.mw_revelados = {}
        st.session_state.mw_nombres = []

    def iniciar_mr_white():
        palabra = random.choice(DATA.get("palabras_mr_white", ["Fútbol"])) if DATA.get("palabras_mr_white") else "Fútbol"
        roles = ["Tripulante"] * (num_jugadores - num_impostores) + ["Mr. White"] * num_impostores
        random.shuffle(roles)
        st.session_state.mw_roles = roles
        st.session_state.mw_palabra = palabra
        st.session_state.mw_nombres = nombres_ingresados
        st.session_state.mw_revelados = {i: False for i in range(num_jugadores)}

    if st.button("🎲 Generar / Reiniciar Juego", key="btn_mw_init"):
        iniciar_mr_white()

    if st.session_state.mw_roles and len(st.session_state.mw_roles) == num_jugadores:
        st.subheader("🔑 Revela tu rol en secreto:")
        
        for idx, rol in enumerate(st.session_state.mw_roles):
            nombre_actual = st.session_state.mw_nombres[idx] if idx < len(st.session_state.mw_nombres) else f"Jugador {idx + 1}"
            
            with st.expander(f"👤 {nombre_actual}"):
                if not st.session_state.mw_revelados[idx]:
                    if st.button(f"👀 Mostrar rol de {nombre_actual}", key=f"rev_{idx}"):
                        st.session_state.mw_revelados[idx] = True
                        st.rerun()
                else:
                    if rol == "Mr. White":
                        st.markdown(f"### 🟥 **{nombre_actual}**, eres **EL IMPOSTOR**")
                        st.write("No sabes cuál es el jugador/palabra secreta. ¡Disimula!")
                    else:
                        st.markdown(f"### 🟩 **{nombre_actual}**, eres **INOCENTE**")
                        st.write(f"La palabra secreta es: **{st.session_state.mw_palabra}**")
                    
                    if st.button("🔒 Ocultar de nuevo", key=f"ocultar_{idx}"):
                        st.session_state.mw_revelados[idx] = False
                        st.rerun()

# ===========================================================================
# 2. JUEGO: PREGUNTADOS
# ===========================================================================
with tab2:
    st.header("🧠 Trivia Futbolera")
    
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
        st.session_state.quiz_index = 0
        st.session_state.quiz_respondido = False
        st.session_state.quiz_es_correcto = False
        st.session_state.quiz_respuesta_correcta = ""
        if DATA.get("preguntados"):
            st.session_state.quiz_lista = random.sample(DATA["preguntados"], len(DATA["preguntados"]))
        else:
            st.session_state.quiz_lista = []

    def reiniciar_quiz():
        st.session_state.quiz_score = 0
        st.session_state.quiz_index = 0
        st.session_state.quiz_respondido = False
        st.session_state.quiz_es_correcto = False
        st.session_state.quiz_respuesta_correcta = ""
        if DATA.get("preguntados"):
            st.session_state.quiz_lista = random.sample(DATA["preguntados"], len(DATA["preguntados"]))

    if st.session_state.quiz_lista and st.session_state.quiz_index < len(st.session_state.quiz_lista):
        pregunta_actual = st.session_state.quiz_lista[st.session_state.quiz_index]
        
        st.metric(label="Puntuación Actual", value=f"{st.session_state.quiz_score} pts")
        st.markdown(f"### Pregunta {st.session_state.quiz_index + 1}:")
        st.info(pregunta_actual["pregunta"])
        
        with st.form(key=f"form_quiz_{st.session_state.quiz_index}"):
            opcion_elegida = st.radio("Selecciona tu respuesta:", pregunta_actual["opciones"])
            enviar_respuesta = st.form_submit_button("Validar Respuesta")
            
            if enviar_respuesta and not st.session_state.quiz_respondido:
                st.session_state.quiz_respondido = True
                st.session_state.quiz_respuesta_correcta = pregunta_actual["correcta"]
                
                if opcion_elegida == pregunta_actual["correcta"]:
                    st.session_state.quiz_score += 10
                    st.session_state.quiz_es_correcto = True
                else:
                    st.session_state.quiz_es_correcto = False

        if st.session_state.quiz_respondido:
            if st.session_state.quiz_es_correcto:
                st.success("¡Excelente! Respuesta correcta (+10 pts).")
            else:
                st.error(f"❌ Incorrecto. La respuesta correcta era: **{st.session_state.quiz_respuesta_correcta}**")
                
            if st.button("Siguiente Pregunta ➔", key=f"btn_next_quiz_{st.session_state.quiz_index}"):
                st.session_state.quiz_index += 1
                st.session_state.quiz_respondido = False
                st.session_state.quiz_es_correcto = False
                st.session_state.quiz_respuesta_correcta = ""
                st.rerun()
    else:
        st.success("🎉 ¡Has completado todas las preguntas disponibles!")
        st.metric(label="Puntuación Final", value=f"{st.session_state.quiz_score} pts")
        
    if st.button("🔄 Reiniciar Trivia", key="btn_reset_quiz"):
        reiniciar_quiz()
        st.rerun()

# ===========================================================================
# 3. JUEGO: ADIVINA EL JUGADOR (CARRERA)
# ===========================================================================
with tab3:
    st.header("👟 ¿Quién es el futbolista?")
    st.caption("Adivina la identidad del jugador analizando su trayectoria cronológica de clubes.")

    if "guess_index" not in st.session_state:
        st.session_state.guess_index = 0
        st.session_state.guess_revelado = False
        st.session_state.guess_feedback = ""
        if DATA.get("adivina_jugador"):
            st.session_state.guess_lista = random.sample(DATA["adivina_jugador"], len(DATA["adivina_jugador"]))
        else:
            st.session_state.guess_lista = []

    def reiniciar_guess():
        st.session_state.guess_index = 0
        st.session_state.guess_revelado = False
        st.session_state.guess_feedback = ""
        if DATA.get("adivina_jugador"):
            st.session_state.guess_lista = random.sample(DATA["adivina_jugador"], len(DATA["adivina_jugador"]))

    if st.session_state.guess_lista and st.session_state.guess_index < len(st.session_state.guess_lista):
        jugador_actual = st.session_state.guess_lista[st.session_state.guess_index]
        
        st.markdown("#### Historial de Clubes:")
        st.warning(jugador_actual["historial"])
        
        intento = st.text_input("Escribe el nombre del futbolista:", key=f"input_guess_{st.session_state.guess_index}").strip()
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button("🎯 Adivinar", key="btn_adivinar"):
                if intento.lower() in jugador_actual["nombre"].lower() and len(intento) > 2:
                    st.session_state.guess_feedback = "correcto"
                    st.session_state.guess_revelado = True
                else:
                    st.session_state.guess_feedback = "incorrecto"
        with col_g2:
            if st.button("🔓 Revelar Respuesta", key="btn_revelar"):
                st.session_state.guess_revelado = True
                st.session_state.guess_feedback = "revelado"

        if st.session_state.guess_feedback == "correcto":
            st.success(f"¡Correcto! Es **{jugador_actual['nombre']}**.")
        elif st.session_state.guess_feedback == "incorrecto":
            st.error("Ese no es... ¡Sigue intentando o revela el resultado!")
            
        if st.session_state.guess_revelado:
            if st.session_state.guess_feedback in ["revelado", "incorrecto"]:
                st.info(f"El jugador oculto es: **{jugador_actual['nombre']}**")
                
            if st.button("Siguiente Jugador ➔", key="btn_next_guess"):
                st.session_state.guess_index += 1
                st.session_state.guess_revelado = False
                st.session_state.guess_feedback = ""
                st.rerun()
    else:
        st.success("🏆 ¡Impresionante! Has terminado la lista de jugadores.")
        
    if st.button("🔄 Reiniciar Adivina el Jugador"):
        reiniciar_guess()
        st.rerun()

# ===========================================================================
# 4. JUEGO: FOTO BORROSA
# ===========================================================================
with tab4:
    st.header("🖼️ Foto Borrosa")
    st.caption("Adivina qué jugador se oculta tras la imagen desenfocada.")

    if "blur_index" not in st.session_state:
        st.session_state.blur_index = 0
        st.session_state.blur_desenfoque = 16
        st.session_state.blur_revelado = False
        st.session_state.blur_feedback = ""
        if DATA.get("jugador_borroso"):
            st.session_state.blur_lista = random.sample(DATA["jugador_borroso"], len(DATA["jugador_borroso"]))
        else:
            st.session_state.blur_lista = []

    def reiniciar_blur():
        st.session_state.blur_index = 0
        st.session_state.blur_desenfoque = 16
        st.session_state.blur_revelado = False
        st.session_state.blur_feedback = ""
        if DATA.get("jugador_borroso"):
            st.session_state.blur_lista = random.sample(DATA["jugador_borroso"], len(DATA["jugador_borroso"]))

    if st.session_state.blur_lista and st.session_state.blur_index < len(st.session_state.blur_lista):
        jugador_blur = st.session_state.blur_lista[st.session_state.blur_index]
        
        # Procesar la imagen con desenfoque dinámico
        img_procesada = obtener_imagen_procesada(jugador_blur["imagen_url"], st.session_state.blur_desenfoque)
        
        # Mostrar la imagen centrada usando 3 columnas
        c_left, c_center, c_right = st.columns([1, 2, 1])
        with c_center:
            if img_procesada:
                st.image(img_procesada, use_container_width=True)
            else:
                st.warning("No se pudo cargar la imagen del jugador.")

        # Campo para ingresar la respuesta
        intento_blur = st.text_input("¿Quién es este futbolista?", key=f"input_blur_{st.session_state.blur_index}").strip()

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("🎯 Comprobar", key="btn_blur_check"):
                if intento_blur.lower() in jugador_blur["nombre"].lower() and len(intento_blur) > 2:
                    st.session_state.blur_feedback = "correcto"
                    st.session_state.blur_desenfoque = 0
                    st.session_state.blur_revelado = True
                else:
                    st.session_state.blur_feedback = "incorrecto"
        
        with col_b2:
            if st.button("🔍 Aclarar foto", key="btn_blur_hint"):
                st.session_state.blur_desenfoque = max(0, st.session_state.blur_desenfoque - 4)
                st.rerun()

        with col_b3:
            if st.button("🔓 Revelar", key="btn_blur_reveal"):
                st.session_state.blur_desenfoque = 0
                st.session_state.blur_revelado = True
                st.session_state.blur_feedback = "revelado"

        # Retroalimentación
        if st.session_state.blur_feedback == "correcto":
            st.success(f"¡Correcto! Es **{jugador_blur['nombre']}**.")
        elif st.session_state.blur_feedback == "incorrecto":
            st.error("Incorrecto... Pide una pista aclarando la foto o sigue intentándolo.")

        if st.session_state.blur_revelado:
            if st.session_state.blur_feedback in ["revelado", "incorrecto"]:
                st.info(f"El futbolista es: **{jugador_blur['nombre']}**")
                
            if st.button("Siguiente Jugador ➔", key="btn_next_blur"):
                st.session_state.blur_index += 1
                st.session_state.blur_desenfoque = 16
                st.session_state.blur_revelado = False
                st.session_state.blur_feedback = ""
                st.rerun()
    else:
        st.success("🎉 ¡Has completado todos los jugadores en Foto Borrosa!")

    if st.button("🔄 Reiniciar Foto Borrosa", key="btn_reset_blur"):
        reiniciar_blur()
        st.rerun()
