# Guía de Despliegue en Streamlit Cloud

## ¿Qué incluye este documento?
Este archivo unifica la guía de despliegue, la lista de verificación y los pasos necesarios para usar la app en Streamlit Cloud con Neon y Google Sheets.

## Requisitos Previos
- Cuenta en [Streamlit Cloud](https://share.streamlit.io)
- Repositorio Git (GitHub, GitLab, etc.) con el código
- Cuenta en [Neon](https://neon.tech) con DB PostgreSQL creada
- Cuenta de servicio en Google Cloud si vas a usar Google Sheets

## Pasos de Configuración

### 1. Conectar Repositorio a Streamlit Cloud
- Ve a https://share.streamlit.io
- Haz clic en "New app"
- Selecciona tu repositorio, rama y archivo principal: `src/sure_bets/interfaz/surebet_app.py`
- Haz clic en "Deploy"

### 2. Configurar Secrets en Streamlit Cloud
- En tu dashboard de Streamlit Cloud, ve a **Settings** > **Secrets**
- Copia el contenido del archivo `.streamlit/secrets.toml.example`
- Reemplaza los valores con los reales

Ejemplo de contenido de `secrets.toml`:

```toml
db_url = "postgresql://usuario:contraseña@host:puerto/base?sslmode=require"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
... (resto del JSON convertido a TOML)
```

### 3. Variables necesarias

#### `db_url` (Base de Datos)
- Obtenida desde tu proyecto Neon
- Debe incluir `?sslmode=require` al final
- No la pongas directamente en el código

#### `gcp_service_account` (Google Sheets)
- Obtenida desde tu archivo `credentials.json` de la cuenta de servicio
- Agrega el JSON completo en el bloque TOML de Secrets

## Funcionalidad Ya Implementada
- Autenticación de usuarios con bcrypt
- Base de datos PostgreSQL con tabla `users`
- Cambio dinámico de nombre de hoja por usuario
- Persistencia de configuración en Neon
- Métodos actualizados para compatibilidad con Streamlit moderno
- Pool de conexión optimizado para Streamlit Cloud (`NullPool`)
- Archivo de ejemplo de secrets: `.streamlit/secrets.toml.example`

## Flujo de Autenticación
1. El usuario abre la app
2. Ve la pantalla de login en la barra lateral
3. Puede **Ingresar** o **Registrarse**
4. Al registrarse, elige su nombre de hoja inicial
5. La configuración se guarda en la DB de Neon
6. Cada usuario puede cambiar su hoja sin afectar a otros

## Checklist de Configuración
- [ ] Crear la DB en Neon
- [ ] Configurar `db_url` en Streamlit Cloud Secrets
- [ ] Configurar `gcp_service_account` en Streamlit Cloud Secrets (si usas Google Sheets)
- [ ] Conectar el repo y desplegar la app
- [ ] Probar registro e inicio de sesión
- [ ] Probar cambio de nombre de hoja
- [ ] Probar cálculo de surebet
- [ ] Probar subida a Google Sheets (si está configurado)

## Pruebas Locales
1. Crea `.streamlit/secrets.toml` localmente (no lo agregues a git)
2. Copia el contenido de `.streamlit/secrets.toml.example`
3. Reemplaza con tus valores reales
4. Ejecuta:

```bash
streamlit run src/sure_bets/interfaz/surebet_app.py
```

## Notas Importantes
- No subas `credentials.json` ni `.streamlit/secrets.toml` al repositorio.
- Usa siempre `st.secrets["db_url"]` y `st.secrets["gcp_service_account"]`.
- Streamlit redeploya automáticamente cuando cambias Secrets.

## Solución de Problemas

### Error de conexión con la base de datos
- Verifica que `db_url` está bien configurado
- Revisa que Neon está activo
- Comprueba que `?sslmode=require` está presente

### Usuario o contraseña incorrectos
- Verifica credenciales
- Asegúrate de usar el usuario correcto

### No se pudo obtener la fila de Google Sheets
- Verifica `gcp_service_account` en Secrets
- Asegúrate de que la hoja existe
- Revisa permisos de la cuenta de servicio
