import streamlit as st
import json
import random

# Configuración de página responsive y limpia
st.set_page_config(
    page_title="Futbol Games",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inyectar CSS personalizado para diseño limpio y optimización móvil
st.markdown("""
    <style>
        .main .block-container { padding-top: 2rem; max-width: 600px; }
        .stButton>button { width: 100%; border-radius: 8px; margin-top: 5px; }
        .game-box { padding: 20px; border-radius: 12px; background-color: #f0f2f6; margin-bottom: 20px; }
        h1, h2, h3 { text-align: center; }
    </style>
""", unsafe_with_html=True)

# Cargar base de datos JSON
@st.cache_data
def cargar_datos():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: No se encontró el archivo data.json.")
        return {"preguntados": [], "adivina_jugador": [], "palabras_mr_white": []}

DATA = cargar_datos()

# ---------------------------------------------------------------------------
# INTERFAZ PRINCIPAL (TABS)
# ---------------------------------------------------------------------------
st.title("⚽ Futbol Games")
st.write("¡Pon a prueba tus conocimientos futbolísticos y diviértete con amigos!")

tab1, tab2, tab3 = st.tabs(["🕵️ Mr. White", "🧠 Preguntados", "👟 Adivina el Jugador"])

# ===========================================================================
# 1. JUEGO: MR. WHITE (IMPOSTOR)
# ===========================================================================
with tab1:
    st.header("Mr. White (El Impostor)")
    st.caption("Juego local para reuniones. Pasa el teléfono para descubrir los roles en secreto.")
    
    # Parámetros del juego
    col1, col2 = st.columns(2)
    with col1:
        num_jugadores = st.number_input("Número de Jugadores", min_value=4, max_value=15, value=6, step=1)
    with col2:
        num_impostores = st.number_input("Número de Impostores (Mr. White)", min_value=1, max_value=3, value=1, step=1)
        
    if num_impostores >= num_jugadores - 1:
        st.error("¡Debe haber más tripulantes que impostores!")
        num_impostores = 1

    # Inicializar estado de Mr. White
    if 'mw_roles' not in st.session_state:
        st.session_state.mw_roles = None
        st.session_state.mw_palabra = ""
        st.session_state.mw_revelados = {}

    def iniciar_mr_white():
        palabra = random.choice(DATA["palabras_mr_white"]) if DATA["palabras_mr_white"] else "Fútbol"
        roles = ["Tripulante"] * (num_jugadores - num_impostores) + ["Mr. White"] * num_impostores
        random.shuffle(roles)
        st.session_state.mw_roles = roles
        st.session_state.mw_palabra = palabra
        st.session_state.mw_revelados = {i: False for i in range(num_jugadores)}

    if st.button("🎲 Generar / Reiniciar Partida", key="btn_mw_init"):
        iniciar_mr_white()

    # Mostrar la asignación de roles de forma segura
    if st.session_state.mw_roles:
        st.subheader("🔑 Revela tu rol en secreto:")
        
        for idx, rol in enumerate(st.session_state.mw_roles):
            with st.expander(f"👤 Jugador {idx + 1}"):
                if not st.session_state.mw_revelados[idx]:
                    if st.button("👀 Mostrar mi rol", key=f"rev_{idx}"):
                        st.session_state.mw_revelados[idx] = True
                        st.rerun()
                else:
                    if rol == "Mr. White":
                        st.markdown("### 🟥 Eres **Mr. White**")
                        st.write("No sabes la palabra. ¡Disimula y trata de descubrirla!")
                    else:
                        st.markdown("### 🟩 Eres **Tripulante**")
                        st.write(f"La palabra secreta es: **{st.session_state.mw_palabra}**")
                    
                    if st.button("🔒 Ocultar de nuevo", key=f"ocultar_{idx}"):
                        st.session_state.mw_revelados[idx] = False
                        st.rerun()

# ===========================================================================
# 2. JUEGO: PREGUNTADOS
# ===========================================================================
with tab2:
    st.header("🧠 Trivia Futbolera")
    
    # Inicializar variables de estado de Preguntados
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
        st.session_state.quiz_index = 0
        st.session_state.quiz_respondido = False
        st.session_state.quiz_feedback = ""
        if DATA["preguntados"]:
            st.session_state.quiz_lista = random.sample(DATA["preguntados"], len(DATA["preguntados"]))
        else:
            st.session_state.quiz_lista = []

    def reiniciar_quiz():
        st.session_state.quiz_score = 0
        st.session_state.quiz_index = 0
        st.session_state.quiz_respondido = False
        st.session_state.quiz_feedback = ""
        if DATA["preguntados"]:
            st.session_state.quiz_lista = random.sample(DATA["preguntados"], len(DATA["preguntados"]))

    if st.session_state.quiz_lista and st.session_state.quiz_index < len(st.session_state.quiz_lista):
        pregunta_actual = st.session_state.quiz_lista[st.session_state.quiz_index]
        
        st.metric(label="Puntuación Actual", value=f"{st.session_state.quiz_score} pts")
        st.markdown(f"### Pregunta {st.session_state.quiz_index + 1}:")
        st.info(pregunta_actual["pregunta"])
        
        # Formulario para evitar recargas inmediatas al clickear opciones
        with st.form(key=f"form_quiz_{st.session_state.quiz_index}"):
            opcion_elegida = st.radio("Selecciona tu respuesta:", pregunta_actual["opciones"])
            enviar_respuesta = st.form_submit_button("Validar Respuesta")
            
            if enviar_respuesta and not st.session_state.quiz_respondido:
                st.session_state.quiz_respondido = True
                if opcion_elegida == pregunta_actual["correcta"]:
                    st.session_state.quiz_score += 10
                    st.session_state.quiz_feedback = "correct"
                else:
                    st.session_state.quiz_feedback = f"incorrect_{pregunta_actual['correcta']}"
        
        # Retroalimentación visual fuera del formulario
        if st.session_state.quiz_respondido:
            if "correct" in st.session_state.quiz_feedback:
                st.success("¡Excelente! Respuesta correcta (+10 pts).")
            else:
                resp_correcta = st.session_state.quiz_feedback.split("_")[1]
                st.error(f"Incorrecto. La respuesta correcta era: **{resp_correcta}**")
                
            if st.button("Siguiente Pregunta ➔"):
                st.session_state.quiz_index += 1
                st.session_state.quiz_respondido = False
                st.session_state.quiz_feedback = ""
                st.rerun()
    else:
        st.success("🎉 ¡Has completado todas las preguntas disponibles!")
        st.metric(label="Puntuación Final", value=f"{st.session_state.quiz_score} pts")
        
    if st.button("🔄 Reiniciar Trivia"):
        reiniciar_quiz()
        st.rerun()

# ===========================================================================
# 3. JUEGO: ADIVINA EL JUGADOR
# ===========================================================================
with tab3:
    st.header("👟 ¿Quién es el futbolista?")
    st.caption("Adivina la identidad del jugador analizando su trayectoria cronológica de clubes.")

    if 'guess_index' not in st.session_state:
        st.session_state.guess_index = 0
        st.session_state.guess_revelado = False
        st.session_state.guess_feedback = ""
        if DATA["adivina_jugador"]:
            st.session_state.guess_lista = random.sample(DATA["adivina_jugador"], len(DATA["adivina_jugador"]))
        else:
            st.session_state.guess_lista = []

    def reiniciar_guess():
        st.session_state.guess_index = 0
        st.session_state.guess_revelado = False
        st.session_state.guess_feedback = ""
        if DATA["adivina_jugador"]:
            st.session_state.guess_lista = random.sample(DATA["adivina_jugador"], len(DATA["adivina_jugador"]))

    if st.session_state.guess_lista and st.session_state.guess_index < len(st.session_state.guess_lista):
        jugador_actual = st.session_state.guess_lista[st.session_state.guess_index]
        
        st.markdown("#### Historial de Clubes:")
        st.warning(jugador_actual["historial"])
        
        # Campo de entrada
        intento = st.text_input("Escribe el nombre del futbolista:", key=f"input_guess_{st.session_state.guess_index}").strip()
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button("🎯 Adivinar", key="btn_adivinar"):
                # Normalización básica de strings para tolerancia
                if intento.lower() in jugador_actual["nombre"].lower():
                    st.session_state.guess_feedback = "correcto"
                    st.session_state.guess_revelado = True
                else:
                    st.session_state.guess_feedback = "incorrecto"
        with col_g2:
            if st.button("🔓 Revelar Respuesta", key="btn_revelar"):
                st.session_state.guess_revelado = True
                st.session_state.guess_feedback = "revelado"

        # Manejo de retroalimentación
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