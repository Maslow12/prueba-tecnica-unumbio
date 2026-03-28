import logging
import sys

class Logger:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    def __init__(self, name="AppLogger"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            console_handler = logging.StreamHandler(stream=sys.stdout)
            console_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(console_handler)

    def _get_formatter(self):
        formats = {
            logging.INFO: f"{self.GREEN}%(message)s{self.RESET}",
            logging.ERROR: f"{self.RED}ERROR: %(message)s{self.RESET}",
            logging.WARNING: f"{self.YELLOW}WARNING: %(message)s{self.RESET}",
        }
        
        class ColorFormatter(logging.Formatter):
            def format(self, record):
                log_fmt = formats.get(record.levelno, "%(message)s")
                formatter = logging.Formatter(log_fmt)
                return formatter.format(record)
                
        return ColorFormatter()

    def info(self, message):
        self.logger.info(message)
        
    def error(self, message):
        self.logger.error(message)

    def warn(self, message):
        self.logger.warning(message)
