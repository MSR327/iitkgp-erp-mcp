import keyring
import os
from dotenv import load_dotenv

SERVICE_NAME = "iitkgp-erp-mcp"


def get_credentials() -> tuple[str, str]:
    load_dotenv()

    roll = os.getenv("ROLL_NUMBER") or keyring.get_password(SERVICE_NAME, "roll_number")
    password = os.getenv("PASSWORD") or keyring.get_password(SERVICE_NAME, "password")

    if not roll or not password:
        raise ValueError(
            "Credentials not found. Run 'iitkgp-erp-setup' or create a .env file."
        )

    return roll, password


def save_credentials(roll: str, password: str):
    keyring.set_password(SERVICE_NAME, "roll_number", roll)
    keyring.set_password(SERVICE_NAME, "password", password)


def clear_credentials():
    keyring.delete_password(SERVICE_NAME, "roll_number")
    keyring.delete_password(SERVICE_NAME, "password")
