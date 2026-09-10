from __future__ import annotations
import sys
from pathlib import Path
from loguru import logger

_CONSOLE_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)
_FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
_configured = False

def setup_logging(level: str = "DEBUG", log_to_file: bool = True, logs_dir: Path | None = None) -> None:
    global _configured
    if _configured:
        return
    logger.remove()
    logger.add(sys.stdout, format=_CONSOLE_FORMAT, level=level, colorize=True, backtrace=True, diagnose=True)
    if log_to_file:
        log_dir = logs_dir or Path("./logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        logger.add(log_dir / "styleiq_{time:YYYY-MM-DD}.log", format=_FILE_FORMAT, level="INFO",
                   rotation="1 day", retention="7 days", compression="gz", backtrace=True, diagnose=False)
    _configured = True
    logger.debug("Logging system initialized at level={level}", level=level)

def get_logger(name: str):
    return logger.bind(name=name)

def get_agent_logger(agent_name: str):
    return logger.bind(name=f"agent.{agent_name}")
