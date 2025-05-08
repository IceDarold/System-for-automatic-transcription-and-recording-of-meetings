import pytest
import os
import logging

# Устанавливаем APP_ENV до всех остальных импортов!
# Это КЛЮЧЕВОЙ момент, чтобы core.config.Settings правильно выбрал .env.test
os.environ["APP_ENV"] = "test"

from typing import Callable, Dict, Optional, Any, Iterator, Generator
from datetime import date, time, timedelta, datetime
import tempfile
from pathlib import Path

# sqlalchemy, passlib и т.д. импортируются после APP_ENV, что нормально
from sqlalchemy import text, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from passlib.context import CryptContext

# Теперь импортируем модули ПОСЛЕ установки APP_ENV
from core.config import settings # settings теперь должен быть сконфигурирован для теста
from core.security import create_access_token, get_password_hash
from models import User, Meeting
from models.user import UserRole
from models.meeting import AccessLevel, MeetingStatus
from database import Base, get_db, init_db # Import init_db
from backend.app import app
from fastapi.testclient import TestClient
from core.auth import get_current_user

# Configure logging for tests
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

POSTGRES_TEST_DATABASE_URL = settings.DATABASE_URL

logger.info(f"DEBUG (conftest): APP_ENV='{os.environ.get('APP_ENV')}'")
logger.info(f"DEBUG (conftest): settings.POSTGRES_USER='{settings.POSTGRES_USER}'")
logger.info(f"DEBUG (conftest): settings.DATABASE_URL being used: '{settings.DATABASE_URL}'")
logger.info(f"DEBUG (conftest): POSTGRES_TEST_DATABASE_URL for db_engine: '{POSTGRES_TEST_DATABASE_URL}'")

# Improved password hiding for logging
def get_safe_db_url(url: str) -> str:
    # Эту функцию можно упростить, так как пароль теперь в settings
    try:
        from sqlalchemy.engine.url import make_url
        db_url = make_url(url)
        # Создаем копию URL с замаскированным паролем
        safe_url = db_url._replace(password="****").render_as_string(hide_password=False)
        return safe_url
    except Exception:
        # Фоллбэк, если парсинг URL не удался
        # Попробуем просто заменить пароль из settings, если он там есть
        password_to_hide = getattr(settings, 'POSTGRES_PASSWORD', None)
        if password_to_hide:
            return url.replace(password_to_hide, '****')
        return "<Could not mask password in URL>"

@pytest.fixture(scope="session")
def db_engine() -> Generator[Engine, None, None]:
    engine: Optional[Engine] = None
    # URL for подключения берется из settings, который уже должен быть настроен
    db_url_to_use = settings.DATABASE_URL 
    if not db_url_to_use:
        logger.error("CRITICAL: settings.DATABASE_URL is not set after configuration! Cannot create db_engine.")
        pytest.fail("settings.DATABASE_URL is not configured")
        # return # Добавим return для mypy # This line is unreachable after pytest.fail
        
    try:
        safe_url = get_safe_db_url(db_url_to_use)
        logger.info(f"Attempting to initialize integration test database via init_db(): {safe_url}")
        
        # Call init_db to create engine and run migrations
        # init_db now returns the engine instance
        initialized_engine = init_db()
        if initialized_engine is None:
            logger.error("CRITICAL: init_db() failed to return an engine.")
            pytest.fail("init_db() failed to return an engine.")
            # return # Unreachable

        engine = initialized_engine
        logger.info(f"Database initialized and migrations run. Using engine: {engine}")
        # Base.metadata.create_all(bind=engine) # This might be redundant if migrations are comprehensive
        yield engine
        # logger.info("Dropping PostgreSQL test database tables.")
        # Base.metadata.drop_all(bind=engine) # Consider if migrations/init_db should handle full cleanup
    except Exception as e:
        logger.warning(f"Failed to initialize database with init_db() or PostgreSQL ({e}). Falling back to SQLite for tests.")
        # Fallback to SQLite if init_db (which includes migrations) fails with the primary DB
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            # poolclass=StaticPool # StaticPool is already imported by name
        )
        logger.info("Using SQLite (in-memory) for integration tests (fallback). Applying schema directly.")
        Base.metadata.create_all(bind=engine) # Apply schema for SQLite fallback
        yield engine
        logger.info("Dropping SQLite (in-memory) test database tables.")
        Base.metadata.drop_all(bind=engine)
    finally:
        if engine is not None:
            logger.info("Disposing of database engine.")
            engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine: Engine):
    """Provides a transactional scope for integration tests."""
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    logger.debug(f"DB session {id(session)} created for test.")
    
    yield session
    
    logger.debug(f"Closing DB session {id(session)}.")
    session.close()
    logger.debug("Rolling back transaction.")
    transaction.rollback()
    logger.debug("Closing DB connection.")
    connection.close()

# Часть A: Фикстуры для Пользователей и Аутентификации

@pytest.fixture(scope="session")
def password_context() -> CryptContext:
    """Provides a CryptContext instance for password hashing and verification."""
    return CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture
def user_factory(db_session, password_context: CryptContext) -> Callable[..., User]:
    """Factory fixture to create User instances."""
    def _create_user(
        email: str,
        raw_password: str = "testpassword123",
        hashed_password: str = None,
        role: str = UserRole.user.value,
        first_name: Optional[str] = "Test",
        last_name: Optional[str] = "User",
        is_active: bool = True,
        commit: bool = True
    ) -> User:
        if hashed_password is None:
            hashed_password = get_password_hash(raw_password)
        user = User(
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            role=role
        )
        db_session.add(user)
        if commit:
            try:
                db_session.commit()
                db_session.refresh(user)
            except Exception as e:
                db_session.rollback()
                raise e
        else:
            try:
                db_session.flush()
                db_session.refresh(user)
            except:
                pass
        return user
    return _create_user

@pytest.fixture
def auth_headers_factory() -> Callable[[User], Dict[str, str]]:
    """Factory fixture to create authentication headers for a user."""
    def _create_auth_headers(user: User) -> Dict[str, str]:
        token = create_access_token(data={"sub": str(user.id)})
        return {"Authorization": f"Bearer {token}"}
    return _create_auth_headers

@pytest.fixture
def default_test_user(user_factory) -> User:
    """Provides a default user instance for tests, created once per test if needed."""
    # Using a fixed email allows reusing this user across different parts of a test setup if required,
    # but user_factory ensures it's created cleanly in the test's db session transaction.
    return user_factory(email="default_test_user@example.com")

# Часть B: Фикстуры для Сущностей

@pytest.fixture
def meeting_factory(db_session) -> Callable[..., Meeting]:
    """Factory fixture to create Meeting instances."""
    def _create_meeting(
        created_by_user: User,
        title: str = "Default Test Meeting",
        meeting_date: Optional[date] = None,
        start_time_val: Optional[time] = None,
        end_time_val: Optional[time] = None,
        duration: Optional[int] = 3600,
        description: Optional[str] = "Default meeting description.",
        location: Optional[str] = "Default Test Location",
        is_online: bool = False,
        is_published: bool = False,
        access_level: str = AccessLevel.public.value,
        status: str = MeetingStatus.pending.value,
        processing_progress: int = 0,
        commit: bool = True
    ) -> Meeting:
        
        default_date = date(2024, 1, 1)
        default_start_time = time(10, 0, 0)
        default_end_time = time(11, 0, 0)

        current_date = meeting_date if meeting_date is not None else default_date
        current_start_time = start_time_val if start_time_val is not None else default_start_time
        current_end_time = end_time_val if end_time_val is not None else default_end_time

        if current_end_time <= current_start_time and duration is None:
            current_end_time = (datetime.combine(current_date, current_start_time) + timedelta(seconds=3600)).time()
        
        calculated_duration = duration
        if calculated_duration is None and current_start_time and current_end_time:
            start_dt = datetime.combine(default_date, current_start_time)
            end_dt = datetime.combine(default_date, current_end_time)
            if end_dt > start_dt:
                calculated_duration = int((end_dt - start_dt).total_seconds())
            else:
                calculated_duration = 3600 

        meeting = Meeting(
            title=title,
            date=current_date,
            start_time=current_start_time,
            end_time=current_end_time,
            duration=calculated_duration,
            description=description,
            location=location,
            is_online=is_online,
            is_published=is_published,
            access_level=access_level,
            created_by_id=created_by_user.id,
            status=status,
            processing_progress=processing_progress
        )
        db_session.add(meeting)
        if commit:
            try:
                db_session.commit()
                db_session.refresh(meeting)
            except Exception as e:
                db_session.rollback()
                raise e
        else:
            try:
                db_session.flush()
                db_session.refresh(meeting)
            except:
                pass
        return meeting
    return _create_meeting

# Часть C: Централизованная Фикстура client

@pytest.fixture(scope="function")
def client(db_session) -> Iterator[TestClient]:
    """
    Provides a FastAPI TestClient with overridden dependencies for database sessions.
    Ensures that each test runs with a fresh database state due to db_session fixture.
    """
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

# Часть D: Управление Временными Файлами (Шаг 5)

@pytest.fixture(scope="function")
def tmp_file_factory() -> Generator[Callable[..., Path], None, None]:
    """Factory fixture to create temporary files that are automatically cleaned up."""
    created_files = []

    def _create_tmp_file(
        suffix: str = ".tmp",
        content: bytes = b"default test content",
        # size: Optional[int] = None # Optional: Add size param if needed to create large files efficiently
    ) -> Path:
        # Create a temporary file that persists after closing initially
        with tempfile.NamedTemporaryFile(suffix=suffix, mode='wb', delete=False) as tmp_file:
            file_path = Path(tmp_file.name)
            tmp_file.write(content)
            # Optional: If size is specified and larger than content, fill the rest
            # if size and len(content) < size:
            #     tmp_file.write(b'\0' * (size - len(content)))
            
        created_files.append(file_path)
        logger.debug(f"Created temporary file: {file_path}")
        return file_path

    yield _create_tmp_file # Provide the factory function to the test

    # Cleanup phase: executed after the test function finishes
    logger.debug(f"Cleaning up {len(created_files)} temporary files.")
    for file_path in created_files:
        try:
            if file_path.exists():
                os.remove(file_path)
                logger.debug(f"Removed temporary file: {file_path}")
            else:
                logger.warning(f"Temporary file {file_path} not found during cleanup, might have been removed by test.")
        except OSError as e:
            # Log error if cleanup fails, but don't fail the test run
            logger.error(f"Error removing temporary file {file_path}: {e}", exc_info=True) 