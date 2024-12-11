# src/utils/logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Union, Dict, Any
import traceback
import json
from functools import wraps

class PathJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Path objects and other special types"""
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Exception):
            return str(obj)
        return super().default(obj)

class LoggerSetup:
    """Custom logger setup with both file and console handlers"""
    
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    def __init__(self, log_dir: Union[str, Path] = 'logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create different log files for different purposes
        self.log_files = {
            'error': self.log_dir / 'error.log',
            'debug': self.log_dir / 'debug.log',
            'wallpaper': self.log_dir / 'wallpaper_operations.log'
        }
        
        # Set up the root logger
        self.setup_root_logger()
        
    def setup_root_logger(self):
        """Configure the root logger with console and file handlers"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(self.LOG_FORMAT, self.DATE_FORMAT))
        root_logger.addHandler(console_handler)
        
        # Add file handlers
        for log_type, log_file in self.log_files.items():
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG if log_type == 'debug' else logging.ERROR)
            file_handler.setFormatter(logging.Formatter(self.LOG_FORMAT, self.DATE_FORMAT))
            root_logger.addHandler(file_handler)

class WallpaperLogger:
    """Custom logger for wallpaper operations with context tracking"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Set context information for logging"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear current context"""
        self.context.clear()
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format message with context and extra information"""
        log_data = {
            'message': message,
            'context': self.context
        }
        if extra:
            log_data['extra'] = extra
        return json.dumps(log_data, cls=PathJSONEncoder)
    
    def debug(self, message: str, **extra):
        self.logger.debug(self._format_message(message, extra))
    
    def info(self, message: str, **extra):
        self.logger.info(self._format_message(message, extra))
    
    def warning(self, message: str, **extra):
        self.logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, **extra):
        self.logger.error(self._format_message(message, extra))
    
    def exception(self, message: str, **extra):
        extra['traceback'] = traceback.format_exc()
        self.logger.exception(self._format_message(message, extra))

# Decorators for logging and error handling
def log_operation(logger: Optional[WallpaperLogger] = None):
    """Decorator to log function calls and their outcomes"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = WallpaperLogger(func.__module__)
            
            logger.set_context(
                function=func.__name__,
                args=str(args),
                kwargs=str(kwargs)
            )
            
            try:
                logger.debug(f"Starting {func.__name__}")
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.exception(f"Error in {func.__name__}: {str(e)}")
                raise
            finally:
                logger.clear_context()
        return wrapper
    return decorator

class WallpaperError(Exception):
    """Base exception class for wallpaper operations"""
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()
        
        # Log the error automatically
        logger = WallpaperLogger(__name__)
        logger.error(message, error_code=error_code, **self.details)

class DownloadError(WallpaperError):
    """Error during wallpaper download"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DOWNLOAD_ERROR", details)

class WallpaperSetError(WallpaperError):
    """Error during wallpaper setting"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "WALLPAPER_SET_ERROR", details)

class APIError(WallpaperError):
    """Error during API operations"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "API_ERROR", details)