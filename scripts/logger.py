"""
Logger module for StoicAlgo
Handles structured logging to files and console.
"""

import logging
import os
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class StoicLogger:
    """Custom logger for the StoicAlgo system."""
    
    def __init__(self, name: str = "StoicAlgo", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Daily run log path (JSON format for easy parsing)
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_log_path = self.log_dir / f"run_{today}.json"
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up console and file handlers."""
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler (rotating)
        log_file = self.log_dir / f"{self.name.lower()}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
    
    def log_run(self, run_data: dict):
        """Log a complete run to the daily JSON log."""
        run_data['timestamp'] = datetime.now().isoformat()
        
        # Read existing logs
        logs = []
        if self.daily_log_path.exists():
            try:
                with open(self.daily_log_path, 'r') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
        
        # Append new run
        logs.append(run_data)
        
        # Write back
        with open(self.daily_log_path, 'w') as f:
            json.dump(logs, f, indent=2, default=str)
        
        self.info(f"Run logged to {self.daily_log_path}")
    
    def log_step(self, step_name: str, status: str, details: dict = None):
        """Log a pipeline step."""
        log_entry = {
            'step': step_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        if status == 'success':
            self.info(f"✓ {step_name}: {status}")
        elif status == 'failed':
            self.error(f"✗ {step_name}: {status} - {details}")
        else:
            self.info(f"→ {step_name}: {status}")
        
        return log_entry


# Global logger instance
logger = StoicLogger()


def get_logger(name: str = None) -> StoicLogger:
    """Get a logger instance."""
    if name:
        return StoicLogger(name)
    return logger


if __name__ == "__main__":
    # Test the logger
    test_logger = get_logger("TestLogger")
    test_logger.info("This is an info message")
    test_logger.debug("This is a debug message")
    test_logger.warning("This is a warning")
    test_logger.error("This is an error")
    
    test_logger.log_step("quote_generation", "success", {"quote": "Test quote"})
    test_logger.log_run({
        "status": "completed",
        "steps": ["quote", "image", "video", "post"]
    })
