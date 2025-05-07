import logging
import logging.config
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

from pythonjsonlogger import jsonlogger

from core.config import settings

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = record.created
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

        log_record['pathname'] = record.pathname
        log_record['lineno'] = record.lineno
        log_record['funcName'] = record.funcName


def setup_logging():
    log_dir = Path(settings.LOG_FILE).parent
    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating log directory {log_dir}: {e}", file=sys.stderr)
            # Fallback to current directory if log directory creation fails
            settings.LOG_FILE = Path(__file__).parent.parent / "app.log"
            print(f"Logging to {settings.LOG_FILE}", file=sys.stderr)

    log_level = settings.LOG_LEVEL.upper()
    
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard' if settings.LOG_FORMAT != 'json' else 'json',
            'stream': 'ext://sys.stdout',
        }
    }

    if settings.LOG_FILE:
        handlers['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard' if settings.LOG_FORMAT != 'json' else 'json',
            'filename': settings.LOG_FILE,
            'maxBytes': settings.LOG_ROTATION_MAX_BYTES,
            'backupCount': settings.LOG_ROTATION_BACKUP_COUNT,
            'encoding': 'utf-8',
        }
    
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s - %(message)s',
            },
            'json': {
                '()': CustomJsonFormatter,
                'format': '%(levelname)s %(asctime)s %(name)s %(pathname)s %(lineno)d %(funcName)s %(message)s'
            },
        },
        'handlers': handlers,
        'root': {
            'handlers': list(handlers.keys()),
            'level': log_level,
        },
        'loggers': {
            'uvicorn.error': {
                'level': log_level,
                'handlers': list(handlers.keys()), 
                'propagate': False
            },
            'uvicorn.access': {
                'level': log_level,
                'handlers': list(handlers.keys()), 
                'propagate': False
            },
            'sqlalchemy.engine': {
                'level': 'WARNING' if log_level == 'INFO' else log_level, # Reduce SQLAlchemy verbosity for INFO
                'handlers': list(handlers.keys()),
                'propagate': False
            },
            'alembic': {
                'level': 'INFO' if log_level == 'INFO' else log_level, # Reduce Alembic verbosity for INFO
                'handlers': list(handlers.keys()),
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(settings.PROJECT_NAME)
    logger.info(f"Logging configured. Level: {log_level}, Format: {settings.LOG_FORMAT}, File: {settings.LOG_FILE if 'file' in handlers else 'Console only'}")

# Ensure python-json-logger is in requirements.txt
# pip install python-json-logger 