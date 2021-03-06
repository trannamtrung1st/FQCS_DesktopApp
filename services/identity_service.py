import os
from app_models.auth_info import AuthInfo
from app_constants import TOKEN_PATH, ISO_DATE_FORMAT, DEV_TOKEN_PATH
import datetime
import json
from services.thread_manager import ThreadManager
from services.refresh_or_logout_thread import RefreshOrLogoutThread
from app import helpers
from app_models.app_config import AppConfig
from FQCS import fqcs_api
import app_constants
LOGIN_SERVICE_TH_GR_KEY = "IdentityService"


class IdentityService:
    def __init__(self, auth_info: AuthInfo):
        self.__auth_info = auth_info

    def init_auth_info(self):
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH) as fi:
                token = json.load(fi)
                self.__auth_info.set_token_info(token)
        return

    def check_token(self):
        if AppConfig.instance().config["dev"]: return
        token = self.__auth_info.get_token_info()
        if (token is not None and 'expires_utc' in token):
            cur_exp_str = token['expires_utc']
            cur = datetime.datetime.utcnow()
            exp = datetime.datetime.strptime(cur_exp_str, ISO_DATE_FORMAT)
            min_diff_delta = exp - cur
            min_diff = min_diff_delta.total_seconds() / 60
            min_diff = 0 if min_diff < 0 else min_diff
            min_ref_diff = min_diff - 5
            min_ref_diff = 0 if min_ref_diff < 0 else min_ref_diff
            print('Refresh token in', min_ref_diff, 'mins')

            is_refresh = 'refresh_token' in token
            timeout_min = min_ref_diff if is_refresh else min_diff
            ThreadManager.instance().cancel_threads(
                group=LOGIN_SERVICE_TH_GR_KEY)
            rol_thread = RefreshOrLogoutThread(self, token, is_refresh,
                                               timeout_min * 60 * 1000)
            rol_thread.start()
            ThreadManager.instance().add_thread(rol_thread,
                                                LOGIN_SERVICE_TH_GR_KEY)
        return

    def log_in(self, username, password):
        if AppConfig.instance().config["dev"]:
            with open(DEV_TOKEN_PATH) as fi:
                dev_token = json.load(fi)
                return (True, dev_token)
        api_url = AppConfig.instance().config['api_url']
        result = fqcs_api.login(api_url, username, password)
        return result

    def save_token_json(self, token):
        self.__auth_info.set_token_info(token)
        with open(TOKEN_PATH, 'w') as fo:
            json.dump(token, fo, indent=2)

    def is_device_account(self, token):
        return app_constants.ROLE_DEVICE in token['roles']

    def log_out(self):
        ThreadManager.instance().cancel_threads(group=LOGIN_SERVICE_TH_GR_KEY)
        if not self.__auth_info.is_logged_in(): return
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
        self.__auth_info.set_token_info(None)
        return
