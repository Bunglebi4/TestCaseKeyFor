from advanced_alchemy.extensions.litestar import (
    AlembicAsyncConfig,
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)

from app.core import settings

session_config = AsyncSessionConfig(expire_on_commit=False)

sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.database_url,
    session_config=session_config,
    alembic_config=AlembicAsyncConfig(
        script_config="alembic.ini",
    ),
)
