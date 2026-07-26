import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Configuración de la página web
st.set_page_config(page_title="Calculadora de Riesgo Suicidio 3D", page_icon="🩺", layout="wide")

st.title("🩺 Calculadora de Riesgo de Suicidio (Modelo 3D)")
st.write("Visualización interactiva basada estrictamente en las tres variables de tus apuntes (MDRS, SIS y LSARS-II).")

st.markdown("---")

# Layout en dos columnas: Izquierda controles, Derecha Gráfico 3D
col_izquierda, col_derecha = st.columns([1, 2])

with col_izquierda:
    st.subheader("Variables Clínicas")
    
    # Ejes corregidos según tu esquema original
    mdrs_score = st.slider("Eje X: Gravedad Médica (MDRS)", 
                           min_value=0.0, max_value=10.0, value=5.0, step=0.5,
                           help="Medical Damage Rating Scale. Umbral crítico >= 5.")
    
    sis_score = st.slider("Eje Y: Intención Objetiva (SIS)", 
                          min_value=0.0, max_value=30.0, value=7.0, step=1.0,
                          help="Suicide Intent Scale (Beck). Umbral crítico > 7.")
    
    lsars_cfr = st.slider("Eje Z: Potencial del Método (LSARS-II / CFR %)", 
                          min_value=0.0, max_value=100.0, value=80.0, step=1.0,
                          help="Lethality of Suicide Attempt Rating Scale / Case Fatality Rate. Umbral crítico > 80%.")

    st.markdown("---")
    
    # --- LÓGICA DE ALERTA CLÍNICA BASADA EN TUS UMBRALES ---
    alta_gravedad = mdrs_score >= 5
    alta_intencion = sis_score > 7
    alta_letalidad = lsars_cfr > 80
    
    st.subheader("Perfil de Riesgo Determinado:")
    
    if not alta_intencion and not alta_letalidad and not alta_gravedad:
        st.success("**🟢 RIESGO BAJO**\n\nNinguno de los tres umbrales críticos se ha superado. Gesto de baja letalidad, bajo daño y baja intencionalidad.")
        
    elif alta_intencion and alta_letalidad:
        if alta_gravedad:
            st.error("**🔴 RIESGO EXTREMO (Convergencia Total)**\n\nConfluencia de alta intención, método letal y daño médico grave. Perfil crítico.")
        else:
            st.error("**🚨 RIESGO CRÍTICO (Supervivencia Milagrosa)**\n\nAlta intención y método letal, pero el daño médico real (MDRS) es bajo por factores puramente fortuitos.")
            
    elif alta_gravedad and not alta_intencion:
        st.warning("**Base: 🟠 RIESGO MÉDICO CRÍTICO (Error de Cálculo)**\n\nBaja intención autoinformada, pero el daño físico real (MDRS) compromete la vida por un error en la previsión del paciente.")
        
    elif alta_intencion and not alta_letalidad and not alta_gravedad:
        st.warning("**🟡 RIESGO ALTO (Paradoja Cognitiva)**\n\nFuerte deseo de morir (SIS alta). Aunque el método falló y no hay daño, el riesgo de escalada futura es elevado.")
        
    else:
        st.warning("**⚠️ RIESGO MODERADO-ALTO**\n\nCombinación intermedia de factores. Requiere una evaluación clínica detallada del entorno y antecedentes.")

with col_derecha:
    st.subheader("Representación del Espacio Tridimensional")
    st.caption("Puedes arrastrar el ratón para rotar la gráfica si lo deseas.")

    # --- MATEMÁTICAS ADAPTADAS A TUS EJES (X=MDRS, Y=SIS, Z=LSARS) ---
    x_range = np.linspace(0, 10, 40)
    y_range = np.linspace(0, 30, 40)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Mapeamos los rangos a un comportamiento de cúspide matemática
    x_norm = (X / 10.0) * 5 - 2.5
    y_norm = (Y / 30.0) * 4
    
    Z_calc = np.sign(x_norm) * (np.abs(x_norm) + np.sqrt(np.maximum(0, x_norm**2 + (y_norm/3)**3)))**(1/3)
    Z = (Z_calc + 2) * (100 / 4)  
    Z = np.clip(Z, 0, 100) 

    # Posición del paciente proyectada exactamente SOBRE la superficie matemática
    paciente_x = mdrs_score
    paciente_y = sis_score
    
    # Recalculamos Z_paciente usando la misma fórmula de la superficie para (mdrs_score, sis_score)
    px_norm = (paciente_x / 10.0) * 5 - 2.5
    py_norm = (paciente_y / 30.0) * 4
    
    pz_calc = np.sign(px_norm) * (np.abs(px_norm) + np.sqrt(np.maximum(0, px_norm**2 + (py_norm/3)**3)))**(1/3)
    paciente_z = (pz_calc + 2) * (100 / 4)
    paciente_z = float(np.clip(paciente_z, 0, 100))

    # CREAR LA GRÁFICA CON PLOTLY
    fig = go.Figure()

    # 1. Dibujar la superficie matemática (en color negro/gris oscuro brillante)
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale=[[0, '#1a1a1a'], [0.5, '#3b3b3b'], [1, '#000000']],
        showscale=False,
        opacity=0.8,
        name="Superficie de Riesgo"
    ))

    # 2. Dibujar el punto rojo interactivo del paciente actual
    fig.add_trace(go.Scatter3d(
        x=[paciente_x], y=[paciente_y], z=[paciente_z],
        mode='markers',
        marker=dict(size=9, color='#ff0000', opacity=1.0, symbol='circle',
                    line=dict(color='white', width=2)),
        name="Paciente Actual"
    ))

    # Configuración de los ejes pulida al máximo para evitar solapamientos
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis=dict(
                title=dict(
                    text='Gravedad Médica (MDRS)',
                    font=dict(size=11)
                ),
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                title=dict(
                    text='Intención Objetiva (SIS)',
                    font=dict(size=11)
                ),
                tickfont=dict(size=10)
            ),
            zaxis=dict(
                title=dict(
                    text='Potencial del Método (LSARS-II %)',
                    font=dict(size=11)
                ),
                tickfont=dict(size=10)
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.8),
            camera=dict(
                # Modificados x e y para rotar la perspectiva un poco a la derecha en órbita
                eye=dict(x=-0.85, y=-1.55, z=0.85),
                center=dict(x=0, y=0, z=-0.1),
                up=dict(x=0, y=0, z=1)
            )
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    # Mostrar gráfico en la web
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("📋 **Estructura metodológica:** Eje X (Daño biológico real), Eje Y (Fuerza cognitiva/planificación del deseo de morir) y Eje Z (Peligrosidad intrínseca de la acción elegida).")

# Pie de página destacado con la autoría
st.markdown("---")
st.markdown(
    """
    <div style="text-align: left; padding: 10px;">
        <h3 style="margin: 0; color: #4A5568; font-weight: 600;">
            Creada por Carlos Gómez Sánchez-Lafuente
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)
