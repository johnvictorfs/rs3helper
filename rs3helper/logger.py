from colorama import Fore

import logging


class CustomFormatter(logging.Formatter):
    """
    https://stackoverflow.com/a/56944256/10416161
    Logging Formatter to add colors and count warning / errors
    """

    file_numberline = f'{Fore.BLUE}(%(filename)s:%(lineno)d){Fore.RESET}'

    levelname = Fore.CYAN + '%(levelname)s' + Fore.RESET

    log_format = f'{levelname}: %(message)s {file_numberline}'

    FORMATS = {
        logging.DEBUG: Fore.LIGHTWHITE_EX + log_format + Fore.RESET,
        logging.INFO: Fore.LIGHTWHITE_EX + log_format + Fore.RESET,
        logging.WARNING: Fore.YELLOW + log_format + Fore.RESET,
        logging.ERROR: Fore.RED + log_format + Fore.RESET,
        logging.CRITICAL: Fore.RED + log_format + Fore.RESET
    }

    def format(self, record: logging.LogRecord):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)


def setup_logger(name: str = 'rs3helper', level=logging.INFO) -> logging.Logger:
    """
    Logger Setup
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(CustomFormatter())

    fh = logging.FileHandler(f'{name}.log')
    fh.setLevel(logging.DEBUG)

    # logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
