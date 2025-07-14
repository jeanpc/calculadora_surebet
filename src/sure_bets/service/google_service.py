import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def agregar_fila_google_sheets(sheet_id, nombre_hoja, nueva_fila, credenciales_json='credentials.json'):
    """
    Agrega una fila a una hoja de cálculo de Google Sheets.
    Usa el secret de Streamlit Cloud si está disponible, o el archivo local si no.
    """
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    try:
        import streamlit as st
        creds_dict = None
        if hasattr(st, "secrets") and "GOOGLE_CREDS" in st.secrets:
            import json
            creds_dict = json.loads(st.secrets["GOOGLE_CREDS"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        else:
            creds = Credentials.from_service_account_file(credenciales_json, scopes=scopes)
        gc = gspread.authorize(creds)
    except ImportError:
        # Si no está streamlit, usar archivo local
        creds = Credentials.from_service_account_file(credenciales_json, scopes=scopes)
        gc = gspread.authorize(creds)

    # Abre la hoja de cálculo y la hoja específica
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.worksheet(nombre_hoja)

    # Obtiene los encabezados actuales
    headers = worksheet.row_values(1)
    # Ordena los valores según los encabezados
    row = [nueva_fila.get(col, '') for col in headers]
    worksheet.append_row(row, value_input_option='USER_ENTERED')
    print('¡Fila agregada a tu Google Sheet!')

if __name__ == '__main__':
    # Ejemplo de uso
    SHEET_ID = '12SVwnUNClwV_hpg6V6O4hGhouq-Z9Suy2NyAmgNT2c4'  # Copia el ID de la URL de tu Google Sheet
    NOMBRE_HOJA = 'Surebets-2025'  # Cambia por el nombre de tu hoja
    nueva_fila = {
        'Casa': 'DDB',
        'Teams': 'Inter Miami - Nashville',
        'Mercado': '1X2',
        'NumApuestas': 1,
        'Evento1': '1',
        'Cuota1': 1.93,
        'Monto1': 529.0,
        'Total1': 529.0,
        'Evento2': 'X',
        'Cuota2': 4.3,
        'Monto2': 717.93,
        'Total2': 717.93,
        'Evento3': '2',
        'Cuota3': 4.05,
        'Monto3': 25.0,
        'Total3': 25.0
    }
    agregar_fila_google_sheets(SHEET_ID, NOMBRE_HOJA, nueva_fila, credenciales_json='src/service/credentials.json')
