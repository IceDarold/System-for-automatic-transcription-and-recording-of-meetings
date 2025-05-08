from sqlalchemy import create_engine, event as sa_event, text, inspect as sa_inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.pool import NullPool
from core.config import settings
import logging
import time
import os
import importlib
from pathlib import Path

# Get a logger instance (logging is configured in app.py or logging_config.py)
logger = logging.getLogger(__name__) # Use module name for library loggers

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
Base = declarative_base() # Define Base at module level

# Initialize engine and SessionLocal as None at module level
# They will be configured by init_db()
engine = None
SessionLocal = None

def init_db():
    """Initialize database connection and configure SessionLocal. Returns engine and session factory."""
    global engine, SessionLocal
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            current_engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={"connect_timeout": 10},
                client_encoding='utf8'
            )
            
            with current_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            
            logger.info("Successfully connected to the database")
            
            # Import all models to ensure Base.metadata is populated
            def import_all_models_for_create_all():
                 models_dir = Path(__file__).resolve().parent / "models"
                 for py_file in models_dir.glob("*.py"):
                      if py_file.name != "__init__.py":
                           module_name = f"models.{py_file.stem}"
                           try:
                                importlib.import_module(module_name)
                                logger.debug(f"Imported {module_name} for metadata.")
                           except ImportError as ie:
                                logger.warning(f"Could not import {module_name}: {ie}")
            
            import_all_models_for_create_all()
            logger.info("Creating database tables based on models (if they don't exist)...")
            Base.metadata.create_all(bind=current_engine)
            logger.info("Database tables checked/created successfully.")
            
            engine = current_engine
            local_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            SessionLocal = local_session_factory
            logger.info("Engine and SessionLocal initialized.")
            return engine, local_session_factory
            
        except SQLAlchemyError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise
                
    logger.error("init_db loop completed without successful initialization.")
    return None, None

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