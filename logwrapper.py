import logging
import os
from logging.handlers import RotatingFileHandler

# Log configuration constants
LOG_INFO = {
    "reldir": "log/pycom",
    "basename": "pycom.log",
    "filesize": 48 * 1024 * 1024,
    "fbkcount": 6,
}


class Log:
    def __init__(self) -> None:
        """
        Initialize the logger.
        """
        log_dirname: str = os.path.join(os.path.expanduser("~"), LOG_INFO["reldir"])
        if not os.path.exists(log_dirname):
            os.makedirs(log_dirname, exist_ok=True)

        logname: str = os.path.normpath(os.path.join(log_dirname, LOG_INFO["basename"]))
        formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s - %(filename)s:%(lineno)d - [%(levelname)s] - %(message)s"
        )

        self.logger: logging.Logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        ch: logging.StreamHandler = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        rfh: RotatingFileHandler = RotatingFileHandler(
            filename=logname,
            mode="a",
            maxBytes=LOG_INFO["filesize"],
            backupCount=LOG_INFO["fbkcount"],
            encoding="utf-8",
        )
        rfh.setLevel(logging.INFO)
        rfh.setFormatter(formatter)

        self.logger.addHandler(ch)
        self.logger.addHandler(rfh)


# Global logger instance
logger = Log()

if __name__ == "__main__":
    # logger.logger.debug("test")
    logger.logger.info("test")
    # logger.logger.warning("test")
    # logger.logger.error("test")
    # logger.logger.critical("test")
    # logger.logger.exception("test")
