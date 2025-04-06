# 📁 migrations/env.py (настройка Alembic)
import os
from dotenv import load_dotenv
load_dotenv()
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Импорт моделей (если появятся позже)
# from yourapp.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DB_URL"))
print("✅ DSN:", repr(os.getenv("DB_URL")))
print("📡 DSN:", repr(config.get_main_option("sqlalchemy.url")))
fileConfig(config.config_file_name)

target_metadata = None  # если используешь SQLAlchemy модели — сюда их метаданные

# DB URL можно взять из переменных окружения или напрямую задать
config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DB_URL", "postgresql://postgres:your_password@localhost:5432/telegram_bot_chg")
)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
