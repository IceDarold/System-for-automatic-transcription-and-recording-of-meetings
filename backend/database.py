from sqlalchemy import create_engine, event as sa_event, text, inspect as sa_inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.pool import NullPool
from core.config import settings
import logging
import time
from alembic.config import Config
from alembic import command
import os

# Get a logger instance (logging is configured in app.py or logging_config.py)
logger = logging.getLogger(__name__) # Use module name for library loggers

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
Base = declarative_base() # Define Base at module level

# Initialize engine and SessionLocal as None at module level
# They will be configured by init_db()
engine = None
SessionLocal = None

def init_db():
    """Initialize database connection, run migrations, and configure SessionLocal"""
    global engine, SessionLocal  # Declare intent to modify global variables
    max_retries = 5
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Create engine with connection timeout
            current_engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections after 1 hour
                connect_args={"connect_timeout": 10},  # 10 seconds timeout
                client_encoding='utf8'
            )
            
            # Test connection
            with current_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            
            logger.info("Successfully connected to the database")
            
            # Run migrations
            try:
                alembic_ini_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
                alembic_cfg = Config(alembic_ini_path)
                # Important: Provide the script location for Alembic
                alembic_cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "alembic"))
                
                # Alembic needs a connection to run migrations online.
                # We pass the engine's URL to AlembicConfig for it to create its own engine/connection.
                # Alternatively, one could pass a connection directly to command.upgrade if context is managed.
                # For simplicity with existing env.py, ensuring sqlalchemy.url is set is often easiest.
                alembic_cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

                command.upgrade(alembic_cfg, "head")
                logger.info("Database migrations completed successfully")
            except Exception as e:
                logger.error(f"Error running migrations: {str(e)}")
                raise
            
            engine = current_engine # Assign to global engine
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return engine
            
        except SQLAlchemyError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise
    return None # Should not be reached if successful

# Remove automatic initialization:
# # Initialize database
# try:
#     engine = init_db()
# except Exception as e:
#     logger.error(f"Critical error initializing database: {str(e)}")
#     raise

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Moved into init_db
# Base = declarative_base() # Moved to top

def get_db():
    """Get database session with error handling"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close() 

def check_db_connection():
    """Check if database connection is working"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False 