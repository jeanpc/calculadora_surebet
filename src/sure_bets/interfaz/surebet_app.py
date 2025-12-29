
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import streamlit as st
from sure_bets.util.calculadora_surebet import compute_surebet_two_way, compute_surebet_three_way, compute_surebet_two_way_with_max, compute_surebet_three_way_with_max

st.title('Calculadora de Surebet (2 y 3 vías)')

# Manejar parámetros GET de la URL
def cargar_desde_url():
    """Cargar valores desde parámetros GET de la URL"""
    query_params = st.query_params
    linea_url = ""
    redondeo_url = False
    
    # Si hay parámetros, crear una línea similar a la que se pega manualmente
    if any(param in query_params for param in ['Fecha', 'Local', 'Visitante', 'C1', 'C2', 'C3']):
        fecha = query_params.get('Fecha', '')
        local = query_params.get('Local', '')
        visitante = query_params.get('Visitante', '')
        c1 = query_params.get('C1', '')
        c2 = query_params.get('C2', '')  # Puede estar vacío para 2 eventos
        c3 = query_params.get('C3', '')
        
        # Construir línea simulando el formato de pegado con cuotas y letras concatenadas
        linea_url = f"{fecha}\t{local}\t{visitante}\t{c1}"
        if c2:  # Si C2 no está vacío, es un evento de 3 vías
            linea_url += f"\t{c2}\t{c3}"
        else:  # Si C2 está vacío, es un evento de 2 vías
            linea_url += f"\t{c3}"
    
    # Obtener el parámetro de redondeo
    if query_params:
        redondeo_param = query_params.get('Redondeo', '').lower()
        redondeo_url = redondeo_param == 'true'
    
    return linea_url, redondeo_url

# Cargar línea desde URL si hay parámetros
linea_url, redondeo_desde_url = cargar_desde_url()
linea_default = linea_url if linea_url else ""

linea = st.text_input('Pega una línea (puede ser del CSV o solo cuotas, ej: 2025-07-20 2:30,Inter Miami CF,Nashville SC,0.24,1.93O,4.3D,4.05D)', value=linea_default)

# Crear columnas para los checkboxes
cols_checkboxes = st.columns(2)
with cols_checkboxes[0]:
    use_max = st.checkbox('Usar montos máximos por cuota', value=True)
with cols_checkboxes[1]:
    redondeo_entero = st.checkbox('Redondeo a entero', value=redondeo_desde_url)

# Inicializar inversión total solo si no existe y no hay montos calculados
if 'inversion_total' not in st.session_state:
    st.session_state['inversion_total'] = 100.0

# Si ya se calcularon montos, mostrar la suma como inversión total
bet_a = st.session_state.get('bet_a', None)
bet_b = st.session_state.get('bet_b', None)
bet_c = st.session_state.get('bet_c', None)
montos = [m for m in [bet_a, bet_b, bet_c] if isinstance(m, (float, int))]
if montos:
    suma_montos = sum(montos)
    st.session_state['inversion_total'] = suma_montos
investment = st.number_input('Inversión total', min_value=1.0, value=st.session_state['inversion_total'], step=1.0, disabled=use_max)

# Inicializar valores de cuotas editables en session_state
if 'cuota_1' not in st.session_state:
    st.session_state['cuota_1'] = 0.0
if 'cuota_x' not in st.session_state:
    st.session_state['cuota_x'] = 0.0
if 'cuota_2' not in st.session_state:
    st.session_state['cuota_2'] = 0.0
max_a = max_b = max_c = None

import re
import io
import pandas as pd

cuotas = []
letras_casa = []
teams = []
bet_a = bet_b = bet_c = None
profit_percentage = None
mensaje_resultado = ""

if linea:
    # Permitir tanto coma como tabulador como separador
    if '\t' in linea:
        partes = [x.strip() for x in linea.split('\t')]
    else:
        partes = [x.strip() for x in linea.split(',')]
    
    # Detectar fecha en el primer campo (acepta formatos con o sin segundos)
    import re
    fecha = ''
    equipos_idx = 0
    if partes:
        # Soporta: 2025-07-20 2:30 o 2025-07-20 02:30 o 2025-07-20 02:30:00
        if re.match(r'\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}(:\d{2})?$', partes[0]):
            fecha = partes[0]
            equipos_idx = 1
    
    # Equipos: los dos siguientes campos
    if len(partes) >= equipos_idx + 2:
        teams = [partes[equipos_idx], partes[equipos_idx + 1]]
    
    # Buscar cuotas: número (con decimal) seguido de una o más letras (ej: 1.93O, 4.3D, 3.95Ta)
    cuotas_letras = re.findall(r'(\d+\.\d+|\d+)([A-Za-z]+)', linea)
    
    # Si no hay letras (caso de parámetros URL), buscar solo números decimales
    if not cuotas_letras:
        # Buscar números decimales simples desde el índice después de los equipos
        cuotas_texto = partes[equipos_idx + 2:] if len(partes) > equipos_idx + 2 else []
        cuotas_numeros = []
        for cuota_str in cuotas_texto:
            try:
                cuota_val = float(cuota_str)
                cuotas_numeros.append(cuota_val)
            except ValueError:
                continue
        cuotas = cuotas_numeros[:3]  # Máximo 3 cuotas
        letras_casa = ['A', 'B', 'C'][:len(cuotas)]  # Letras por defecto
    else:
        cuotas = [float(c[0]) for c in cuotas_letras[:3]]
        letras_casa = [c[1] for c in cuotas_letras[:3]]
    
    # Rellenar los campos editables
    if len(cuotas) == 2:
        st.session_state['cuota_1'] = cuotas[0]
        st.session_state['cuota_2'] = cuotas[1]
        st.session_state['cuota_x'] = 0.0
    elif len(cuotas) == 3:
        st.session_state['cuota_1'] = cuotas[0]
        st.session_state['cuota_x'] = cuotas[1]
        st.session_state['cuota_2'] = cuotas[2]
cuotas_inputs = []
if st.session_state['cuota_1'] or st.session_state['cuota_2'] or st.session_state['cuota_x']:
    st.markdown('**Cuotas**')
    if st.session_state['cuota_x'] > 0:
        cols = st.columns(3)
        cuota_1 = cols[0].number_input('1', min_value=1.01, value=float(st.session_state['cuota_1']), step=0.01, key='input_cuota_1')
        cuota_x = cols[1].number_input('X', min_value=1.01, value=float(st.session_state['cuota_x']), step=0.01, key='input_cuota_x')
        cuota_2 = cols[2].number_input('2', min_value=1.01, value=float(st.session_state['cuota_2']), step=0.01, key='input_cuota_2')
        cuotas_inputs = [cuota_1, cuota_x, cuota_2]
    else:
        cols = st.columns(2)
        cuota_1 = cols[0].number_input('1', min_value=1.01, value=float(st.session_state['cuota_1']), step=0.01, key='input_cuota_1')
        cuota_2 = cols[1].number_input('2', min_value=1.01, value=float(st.session_state['cuota_2']), step=0.01, key='input_cuota_2')
        cuotas_inputs = [cuota_1, cuota_2]

# Agrupar montos máximos si se usan
if use_max:
    st.markdown('**Montos máximos (solo un valor por vez)**')
    
    # Inicializar valores en session_state
    if 'max_a_val' not in st.session_state:
        st.session_state['max_a_val'] = 100.0  # Valor por defecto para Máx 1
    if 'max_b_val' not in st.session_state:
        st.session_state['max_b_val'] = 0.0  
    if 'max_c_val' not in st.session_state:
        st.session_state['max_c_val'] = 0.0
    
    # Contador para forzar recreación de widgets cuando hay cambios
    if 'max_widget_counter' not in st.session_state:
        st.session_state['max_widget_counter'] = 0
    
    if st.session_state['cuota_x'] > 0:
        cols_max = st.columns(3)
        
        # Crear los inputs con keys únicas para forzar recreación cuando sea necesario
        widget_suffix = f"_{st.session_state['max_widget_counter']}"
        
        with cols_max[0]:
            max_a_input = st.number_input('Máx 1', min_value=0.0, value=st.session_state['max_a_val'], step=1.0, key=f'max_a_key{widget_suffix}')
        with cols_max[1]:
            max_b_input = st.number_input('Máx X', min_value=0.0, value=st.session_state['max_b_val'], step=1.0, key=f'max_b_key{widget_suffix}')
        with cols_max[2]:
            max_c_input = st.number_input('Máx 2', min_value=0.0, value=st.session_state['max_c_val'], step=1.0, key=f'max_c_key{widget_suffix}')
            
        # Detectar cambios y aplicar exclusión mutua con protección anti-bucle
        cambio_detectado = False
        rerun_flag_key = 'rerun_scheduled'
        
        # Solo procesar si no hay un rerun ya programado
        if not st.session_state.get(rerun_flag_key, False):
            if max_a_input > 0 and (st.session_state['max_b_val'] > 0 or st.session_state['max_c_val'] > 0):
                st.session_state['max_a_val'] = max_a_input
                st.session_state['max_b_val'] = 0.0
                st.session_state['max_c_val'] = 0.0
                st.session_state['max_widget_counter'] += 1
                st.session_state[rerun_flag_key] = True
                cambio_detectado = True
                st.rerun()
            elif max_b_input > 0 and (st.session_state['max_a_val'] > 0 or st.session_state['max_c_val'] > 0):
                st.session_state['max_a_val'] = 0.0
                st.session_state['max_b_val'] = max_b_input
                st.session_state['max_c_val'] = 0.0
                st.session_state['max_widget_counter'] += 1
                st.session_state[rerun_flag_key] = True
                cambio_detectado = True
                st.rerun()
            elif max_c_input > 0 and (st.session_state['max_a_val'] > 0 or st.session_state['max_b_val'] > 0):
                st.session_state['max_a_val'] = 0.0
                st.session_state['max_b_val'] = 0.0
                st.session_state['max_c_val'] = max_c_input
                st.session_state['max_widget_counter'] += 1
                st.session_state[rerun_flag_key] = True
                cambio_detectado = True
                st.rerun()
            else:
                # Actualizar valores normalmente si no hay conflicto
                st.session_state['max_a_val'] = max_a_input
                st.session_state['max_b_val'] = max_b_input
                st.session_state['max_c_val'] = max_c_input
        else:
            # Limpiar el flag después de un rerun
            st.session_state[rerun_flag_key] = False
        
        # Guardar si hay cambio para mostrarlo después
        if cambio_detectado:
            st.session_state['mensaje_exclusion'] = "💡 Se ha seleccionado un monto máximo. Los otros campos se han limpiado automáticamente."
        
        max_a = st.session_state['max_a_val'] if st.session_state['max_a_val'] > 0 else None
        max_b = st.session_state['max_b_val'] if st.session_state['max_b_val'] > 0 else None
        max_c = st.session_state['max_c_val'] if st.session_state['max_c_val'] > 0 else None
        
    else:
        cols_max = st.columns(2)
        
        # Para 2 vías con keys únicas
        widget_suffix = f"_{st.session_state['max_widget_counter']}"
        
        with cols_max[0]:
            max_a_input = st.number_input('Máx 1', min_value=0.0, value=st.session_state['max_a_val'], step=1.0, key=f'max_a_key{widget_suffix}')
        with cols_max[1]:
            max_b_input = st.number_input('Máx 2', min_value=0.0, value=st.session_state['max_b_val'], step=1.0, key=f'max_b_key{widget_suffix}')
            
        # Detectar cambios para 2 vías con protección anti-bucle
        cambio_detectado = False
        rerun_flag_key = 'rerun_scheduled'
        
        # Solo procesar si no hay un rerun ya programado
        if not st.session_state.get(rerun_flag_key, False):
            if max_a_input > 0 and st.session_state['max_b_val'] > 0:
                st.session_state['max_a_val'] = max_a_input
                st.session_state['max_b_val'] = 0.0
                st.session_state['max_widget_counter'] += 1
                st.session_state[rerun_flag_key] = True
                cambio_detectado = True
                st.rerun()
            elif max_b_input > 0 and st.session_state['max_a_val'] > 0:
                st.session_state['max_a_val'] = 0.0
                st.session_state['max_b_val'] = max_b_input
                st.session_state['max_widget_counter'] += 1
                st.session_state[rerun_flag_key] = True
                cambio_detectado = True
                st.rerun()
            else:
                # Actualizar valores normalmente si no hay conflicto
                st.session_state['max_a_val'] = max_a_input
                st.session_state['max_b_val'] = max_b_input
        else:
            # Limpiar el flag después de un rerun
            st.session_state[rerun_flag_key] = False
        
        # Guardar si hay cambio para mostrarlo después
        if cambio_detectado:
            st.session_state['mensaje_exclusion'] = "💡 Se ha seleccionado un monto máximo. El otro campo se ha limpiado automáticamente."
        
        max_a = st.session_state['max_a_val'] if st.session_state['max_a_val'] > 0 else None
        max_b = st.session_state['max_b_val'] if st.session_state['max_b_val'] > 0 else None

# Crear columnas para el botón y el mensaje
col_boton, col_mensaje = st.columns([1, 2])

with col_boton:
    calcular_clicked = st.button('Calcular Surebet')

with col_mensaje:
    # Mostrar mensaje de exclusión mutua si existe con la misma altura que el botón
    if 'mensaje_exclusion' in st.session_state and st.session_state['mensaje_exclusion']:
        # Usar markdown con estilo compacto y colores acordes al tema oscuro
        st.markdown(
            f"""
            <div style="
                display: flex; 
                align-items: center; 
                height: 38px; 
                background-color: #262730; 
                border: 1px solid #454545; 
                border-radius: 6px; 
                padding: 0 12px; 
                margin-top: 0;
                font-size: 14px;
                color: #fafafa;
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            ">
                {st.session_state['mensaje_exclusion']}
            </div>
            """,
            unsafe_allow_html=True
        )
        # Limpiar el mensaje después de mostrarlo
        st.session_state['mensaje_exclusion'] = ""

if calcular_clicked:
    try:
        # Función para formatear montos según el checkbox de redondeo
        def formatear_monto(monto):
            if redondeo_entero:
                return f"{int(round(monto))}"
            else:
                return f"{monto:.2f}"
        
        if len(cuotas_inputs) == 2:
            if use_max:
                if not (max_a or max_b):
                    st.error('Debes ingresar al menos un monto máximo para calcular el surebet.')
                else:
                    profit_percentage, bet_a, bet_b, inv = compute_surebet_two_way_with_max(
                        cuotas_inputs[0], cuotas_inputs[1], max_a=max_a, max_b=max_b)
                    inversion_real = inv
                    st.session_state['inversion_total'] = inversion_real
                    st.session_state['bet_a'] = bet_a
                    st.session_state['bet_b'] = bet_b
                    st.session_state['bet_c'] = None
                    st.session_state['cuotas'] = cuotas_inputs
                    st.session_state['letras_casa'] = letras_casa
                    st.session_state['teams'] = teams
                    st.session_state['mercado'] = '±'
                    ganancia_neta = round((cuotas_inputs[0] * bet_a) - inversion_real, 2)
                    profit_percentage_display = round((ganancia_neta / inversion_real) * 100, 2)
                    st.session_state['profit_percentage'] = profit_percentage
                    mensaje_resultado = f"Ganancia neta: {ganancia_neta} ({profit_percentage_display:.2f}%)"
                    st.success(mensaje_resultado)
                    st.info(f"Apostar en A ({cuotas_inputs[0]}): {formatear_monto(bet_a)} | B ({cuotas_inputs[1]}): {formatear_monto(bet_b)}")
            else:
                profit_percentage, bet_a, bet_b = compute_surebet_two_way(cuotas_inputs[0], cuotas_inputs[1], investment)
                inversion_real = investment
                st.session_state['inversion_total'] = inversion_real
                st.session_state['bet_a'] = bet_a
                st.session_state['bet_b'] = bet_b
                st.session_state['bet_c'] = None
                st.session_state['cuotas'] = cuotas_inputs
                st.session_state['letras_casa'] = letras_casa
                st.session_state['teams'] = teams
                st.session_state['mercado'] = '±'
                ganancia_neta = round((cuotas_inputs[0] * bet_a) - inversion_real, 2)
                profit_percentage_display = round((ganancia_neta / inversion_real) * 100, 2)
                st.session_state['profit_percentage'] = profit_percentage
                mensaje_resultado = f"Ganancia neta: {ganancia_neta} ({profit_percentage_display:.2f}%)"
                st.success(mensaje_resultado)
                st.info(f"Apostar en A ({cuotas_inputs[0]}): {formatear_monto(bet_a)} | B ({cuotas_inputs[1]}): {formatear_monto(bet_b)}")
        elif len(cuotas_inputs) == 3:
            if use_max:
                if not (max_a or max_b or max_c):
                    st.error('Debes ingresar al menos un monto máximo para calcular el surebet.')
                else:
                    profit_percentage, bet_a, bet_b, bet_c, inv = compute_surebet_three_way_with_max(
                        cuotas_inputs[0], cuotas_inputs[1], cuotas_inputs[2], max_a=max_a, max_b=max_b, max_c=max_c)
                    inversion_real = inv
                    st.session_state['inversion_total'] = inversion_real
                    st.session_state['bet_a'] = bet_a
                    st.session_state['bet_b'] = bet_b
                    st.session_state['bet_c'] = bet_c
                    st.session_state['cuotas'] = cuotas_inputs
                    st.session_state['letras_casa'] = letras_casa
                    st.session_state['teams'] = teams
                    st.session_state['mercado'] = '1X2'
                    ganancia_neta = round((cuotas_inputs[0] * bet_a) - inversion_real, 2)
                    profit_percentage_display = round((ganancia_neta / inversion_real) * 100, 2)
                    st.session_state['profit_percentage'] = profit_percentage
                    mensaje_resultado = f"Ganancia neta: {ganancia_neta} ({profit_percentage_display:.2f}%)"
                    st.success(mensaje_resultado)
                    st.info(f"Apostar en A ({cuotas_inputs[0]}): {formatear_monto(bet_a)} | B ({cuotas_inputs[1]}): {formatear_monto(bet_b)} | C ({cuotas_inputs[2]}): {formatear_monto(bet_c)}")
            else:
                profit_percentage, bet_a, bet_b, bet_c = compute_surebet_three_way(cuotas_inputs[0], cuotas_inputs[1], cuotas_inputs[2], investment)
                inversion_real = investment
                st.session_state['inversion_total'] = inversion_real
                st.session_state['bet_a'] = bet_a
                st.session_state['bet_b'] = bet_b
                st.session_state['bet_c'] = bet_c
                st.session_state['cuotas'] = cuotas_inputs
                st.session_state['letras_casa'] = letras_casa
                st.session_state['teams'] = teams
                st.session_state['mercado'] = '1X2'
                ganancia_neta = round((cuotas_inputs[0] * bet_a) - inversion_real, 2)
                profit_percentage_display = round((ganancia_neta / inversion_real) * 100, 2)
                st.session_state['profit_percentage'] = profit_percentage
                mensaje_resultado = f"Ganancia neta: {ganancia_neta} ({profit_percentage_display:.2f}%)"
                st.success(mensaje_resultado)
                st.info(f"Apostar en A ({cuotas_inputs[0]}): {formatear_monto(bet_a)} | B ({cuotas_inputs[1]}): {formatear_monto(bet_b)} | C ({cuotas_inputs[2]}): {formatear_monto(bet_c)}")
        else:
            st.error('No se detectaron 2 o 3 cuotas válidas en la línea.')
    except Exception as e:
        st.error(f'Error al calcular: {e}')

# Botón para subir registro a Google Sheets
if st.button('Subir Apuesta'):
    try:
        from sure_bets.service.google_service import agregar_fila_google_sheets
        cuotas = st.session_state.get('cuotas', [])
        bet_a = st.session_state.get('bet_a', None)
        bet_b = st.session_state.get('bet_b', None)
        bet_c = st.session_state.get('bet_c', None)
        letras_casa = st.session_state.get('letras_casa', [])
        teams = st.session_state.get('teams', [])
        mercado = st.session_state.get('mercado', '')
        if len(cuotas) not in [2,3] or not teams:
            st.error('Primero ingresa una línea válida y calcula el surebet.')
        else:
            casa = ''.join(letras_casa)
            teams_str = ' - '.join(teams)
            cols = ['Fecha','Teams','Casa','Mercado','#Apuestas','Evento1','Cuota1','Monto1','Total1','Evento2','Cuota2','Monto2','Total2','Evento3','Cuota3','Monto3','Total3',
                    'Inver T','Win N','S/ G','%G']
            SHEET_ID = '12SVwnUNClwV_hpg6V6O4hGhouq-Z9Suy2NyAmgNT2c4'  # tu sheet id
            NOMBRE_HOJA = 'Surebets-2025'  # tu hoja
            def tofloat(val):
                try:
                    return float(val)
                except:
                    return ''
            cuota1 = tofloat(cuotas[0]) if len(cuotas) > 0 else ''
            cuota2 = tofloat(cuotas[1]) if len(cuotas) > 1 else ''
            cuota3 = tofloat(cuotas[2]) if len(cuotas) > 2 else ''
            monto1 = tofloat(bet_a) if bet_a is not None else ''
            monto2 = tofloat(bet_b) if bet_b is not None and len(cuotas) == 3 else ''
            monto3 = tofloat(bet_c) if bet_c is not None and len(cuotas) == 3 else ''
            if len(cuotas) == 2:
                cuota2 = ''
                monto2 = ''
                cuota3 = tofloat(cuotas[1])
                monto3 = tofloat(bet_b) if bet_b is not None else ''
            nueva_fila = {
                'Fecha': fecha,
                'Teams': teams_str,
                'Casa': casa,
                'Mercado': mercado,
                '#Apuestas': 1,
                'Evento1': '1',
                'Cuota1': cuota1,
                'Monto1': monto1,
                'Total1': '',  # Se asignará la fórmula después
                'Evento2': 'X',
                'Cuota2': cuota2,
                'Monto2': monto2,
                'Total2': '',  # Se asignará la fórmula después
                'Evento3': '2',
                'Cuota3': cuota3,
                'Monto3': monto3,
                'Total3': ''   # Se asignará la fórmula después
            }
            # Inver T: suma de montos (solo los que sean float/int)
            montos = [monto1, monto2, monto3]
            inver_t = sum([m for m in montos if isinstance(m, (float, int))])
            # Usar los mismos valores de ganancia neta y %G que la app
            profit_percentage = st.session_state.get('profit_percentage', None)
            if profit_percentage is not None:
                percent_g = round(profit_percentage, 2)
            else:
                percent_g = ''
            # Calcular la fila de inserción en Google Sheets (soporta local y nube)
            try:
                import gspread
                from google.oauth2.service_account import Credentials
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = None
                # Detectar si estamos en la nube (Streamlit Cloud)
                if hasattr(st.secrets, "gcp_service_account") and st.secrets["gcp_service_account"]:
                    # st.secrets['gcp_service_account'] puede ser un objeto tipo Config, convertir a dict plano
                    service_account_info = dict(st.secrets["gcp_service_account"])
                    # Convertir todos los valores a str (por si acaso)
                    service_account_info = {k: str(v) for k, v in service_account_info.items()}
                    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
                else:
                    creds = Credentials.from_service_account_file('src/sure_bets/service/credentials.json', scopes=scopes)
                gc = gspread.authorize(creds)
                sh = gc.open_by_key(SHEET_ID)
                worksheet = sh.worksheet(NOMBRE_HOJA)
                all_values = worksheet.get_all_values()
                next_row = len(all_values) + 1
            except Exception as e:
                import traceback
                st.warning(f"No se pudo obtener la fila de Google Sheets: {e}\n{traceback.format_exc()}")
                next_row = 2  # fallback si no se puede conectar
            nueva_fila['Total1'] = f'=E{next_row}*H{next_row}'
            nueva_fila['Total2'] = f'=E{next_row}*L{next_row}'
            nueva_fila['Total3'] = f'=E{next_row}*P{next_row}'
            nueva_fila['Inver T'] = f'=I{next_row}+M{next_row}+Q{next_row}'
            nueva_fila['Win N'] = f'=ROUND(G{next_row}*I{next_row},2)'
            nueva_fila['S/ G'] = f'=S{next_row}-R{next_row}'
            nueva_fila['%G'] = f'=ROUND(T{next_row}/R{next_row}*100,2)'
            SHEET_ID = '12SVwnUNClwV_hpg6V6O4hGhouq-Z9Suy2NyAmgNT2c4'  # tu sheet id
            NOMBRE_HOJA = 'Surebets-2025'  # tu hoja
            agregar_fila_google_sheets(SHEET_ID, NOMBRE_HOJA, nueva_fila, credenciales_json='src/sure_bets/service/credentials.json')
            st.success('¡Fila agregada a Google Sheets!')
    except Exception as e:
        st.error(f'Error al guardar en Google Sheets: {e}')
