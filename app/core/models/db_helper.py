from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_scoped_session, async_sessionmaker

from asyncio import current_task

from app.core.config import settings


class DataBaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            pool_size=5,  
            max_overflow=10,
            pool_timeout=30,  
            pool_recycle=1800
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task
        )

        return session

    async def session_depends(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session

db_helper = DataBaseHelper(
    url=settings.db.url,
    echo=settings.db.echo
)