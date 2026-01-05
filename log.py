import datetime
from turtle import color

# Codes couleurs ANSI pour le terminal
COLORS = {
    "INFO": "\033[36m",     # Cyan
    "WARN": "\033[33m",     # Jaune
    "ERROR": "\033[31m",    # Rouge
    "SUCCESS": "\033[32m",  # Vert
    "RESET": "\033[0m"      # Reset
}

def print_log(message, level="INFO"):
    """
    Affiche un log coloré avec timestamp
    #level: INFO, WARN, ERROR, SUCCESS
    """
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    color = COLORS.get(level.upper(), COLORS["INFO"])
    if level.upper() == "TITLE":
        print(f"{color}{message}{color}")
    else:
        print(f"{color}[{level.upper()}] {timestamp} : {message}{color}")