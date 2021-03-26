import src.services.data_service as svc
from src.data.owners import Owner

active_account: Owner = None


def reload_account():
    global active_account
    if not active_account:
        return

    active_account = svc.find_account_by_email(active_account.email)
