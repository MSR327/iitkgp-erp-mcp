import requests
import iitkgp_erp_login.erp as erp
from .credentials import get_credentials

SESSION = None
SSO_TOKEN = None


def get_session() -> requests.Session:
    global SESSION, SSO_TOKEN
    if SESSION:
        return SESSION
    return login()


def login(otp_input=None) -> requests.Session:
    global SESSION, SSO_TOKEN

    roll, password = get_credentials()

    headers = {
        "timeout": "20",
        "User-Agent": "Mozilla/5.0",
    }

    session = requests.Session()
    session.headers.update(headers)

    erp_login_args = {
        "roll_number": roll,
        "password": password,
        "session": session,
    }

    if otp_input:
        erp_login_args["OTP"] = otp_input

    try:
        SSO_TOKEN = erp.login(erp_login_args)
        SESSION = session
        return SESSION
    except Exception as e:
        SESSION = None
        SSO_TOKEN = None
        raise RuntimeError(f"ERP login failed: {e}")


def is_logged_in() -> bool:
    return SESSION is not None


def logout():
    global SESSION, SSO_TOKEN
    SESSION = None
    SSO_TOKEN = None
