import os
import streamlit as st
import bcrypt
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, DateTime, select, insert, update, delete
from sqlalchemy.pool import NullPool

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(128), unique=True, nullable=False),
    Column('password_hash', String(256), nullable=False),
    Column('sheet_name', String(128), nullable=False, default='Surebets-2026'),
)

sessions = Table(
    'sessions', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, nullable=False),
    Column('session_token', String(128), unique=True, nullable=False),
    Column('expires_at', DateTime, nullable=False),
)


def get_db_url():
    try:
        return st.secrets['db_url']
    except Exception:
        return os.environ.get('DB_URL')


@st.cache_resource
def get_engine():
    db_url = get_db_url()
    if not db_url:
        raise RuntimeError('No se encontró DB_URL. Configura st.secrets["db_url"] o la variable de entorno DB_URL.')
    # Usar NullPool para evitar problemas de reconexión en Streamlit Cloud
    engine = create_engine(db_url, echo=False, future=True, poolclass=NullPool)
    return engine


def create_tables():
    engine = get_engine()
    metadata.create_all(engine)


def hash_password(password: str) -> str:
    # bcrypt tiene límite de 72 bytes, truncar automáticamente
    password_bytes = password.encode('utf-8')[:72]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.checkpw(password_bytes, password_hash.encode('utf-8'))


def get_user(username: str):
    engine = get_engine()
    with engine.connect() as conn:
        stmt = select(users).where(users.c.username == username)
        return conn.execute(stmt).mappings().first()


def create_session(username: str, days: int = 30) -> str:
    user = get_user(username)
    if not user:
        raise ValueError('Usuario no encontrado.')
    token = bcrypt.gensalt(rounds=12).decode('utf-8').replace('/', '_')
    expires_at = datetime.utcnow() + timedelta(days=days)
    engine = get_engine()
    with engine.begin() as conn:
        stmt = insert(sessions).values(user_id=user['id'], session_token=token, expires_at=expires_at)
        conn.execute(stmt)
    return token


def get_session_user(token: str):
    engine = get_engine()
    with engine.connect() as conn:
        stmt = select(sessions.c.user_id).where(sessions.c.session_token == token).where(sessions.c.expires_at > datetime.utcnow())
        result = conn.execute(stmt).first()
        if not result:
            return None
        user_id = result[0]
        stmt2 = select(users).where(users.c.id == user_id)
        return conn.execute(stmt2).mappings().first()


def delete_session(token: str):
    engine = get_engine()
    with engine.begin() as conn:
        stmt = delete(sessions).where(sessions.c.session_token == token)
        conn.execute(stmt)


def delete_user_sessions(username: str):
    user = get_user(username)
    if not user:
        return
    engine = get_engine()
    with engine.begin() as conn:
        stmt = delete(sessions).where(sessions.c.user_id == user['id'])
        conn.execute(stmt)


def register_user(username: str, password: str, sheet_name: str = 'Surebets-2026'):
    if get_user(username):
        raise ValueError('El usuario ya existe.')
    password_hash = hash_password(password)
    engine = get_engine()
    with engine.begin() as conn:
        stmt = insert(users).values(username=username, password_hash=password_hash, sheet_name=sheet_name)
        conn.execute(stmt)


def authenticate_user(username: str, password: str) -> bool:
    user = get_user(username)
    if not user:
        return False
    return verify_password(password, user['password_hash'])


def get_user_sheet_name(username: str) -> str:
    user = get_user(username)
    return user['sheet_name'] if user else 'Surebets-2026'


def update_sheet_name(username: str, sheet_name: str):
    engine = get_engine()
    with engine.begin() as conn:
        stmt = update(users).where(users.c.username == username).values(sheet_name=sheet_name)
        result = conn.execute(stmt)
        if result.rowcount == 0:
            raise ValueError('Usuario no encontrado.')
