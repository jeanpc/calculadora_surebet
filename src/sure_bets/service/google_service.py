import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def agregar_fila_google_sheets(sheet_id, nombre_hoja, nueva_fila, credenciales_json='credentials.json', tipo=''):
    """
    Agrega una fila a una hoja de cálculo de Google Sheets.
    Usa el secret de Streamlit Cloud si está disponible, o el archivo local si no.
    Si el tipo es 'middle', pinta la celda de Mercado con color verde claro 2.
    """
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = None
    try:
        import streamlit as st
        try:
            # Usar el bloque [gcp_service_account] de secrets.toml
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        except Exception:
            creds = Credentials.from_service_account_file(credenciales_json, scopes=scopes)
    except ImportError:
        creds = Credentials.from_service_account_file(credenciales_json, scopes=scopes)
    gc = gspread.authorize(creds)

    # Abre la hoja de cálculo y la hoja específica
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.worksheet(nombre_hoja)

    # Obtiene los encabezados actuales
    headers = worksheet.row_values(1)
    # Ordena los valores según los encabezados
    row = [nueva_fila.get(col, '') for col in headers]

    # Agregar la fila
    worksheet.append_row(row, value_input_option='USER_ENTERED')

    # Si el tipo es 'middle', aplicar color verde claro 2 a la celda de Mercado
    if tipo == 'middle':
        try:
            # Encontrar el índice de la columna Mercado
            mercado_col_idx = None
            for i, header in enumerate(headers):
                if header.strip().lower() == 'mercado':
                    mercado_col_idx = i + 1  # gspread usa índices 1-based
                    break

            if mercado_col_idx is not None:
                # Obtener la última fila (la que acabamos de agregar)
                last_row = len(worksheet.get_all_values())
                cell_range = gspread.utils.rowcol_to_a1(last_row, mercado_col_idx)

                                # Verde claro 2 de la paleta de Google Sheets (#b6d7a8)
                worksheet.format(cell_range, {
                    "backgroundColor": {
                        "red": 182/255,
                        "green": 215/255,
                        "blue": 168/255
                    }
                })
        except Exception as e:
            print(f"No se pudo aplicar formato a la celda de Mercado: {e}")

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
