from pprint import pprint
from typing import Literal

import requests
from requests import Session, Response
from requests.auth import AuthBase

ASANA_API_BASE="https://app.asana.com/api/1.0"

class Asana:
    class AsanaAuth(AuthBase):
        def __init__(self, token: str):
            self.token = token

        def __call__(self, r):
            r.headers['Authorization'] = f"Bearer {self.token}"
            return r

    def _send_request(self, url: str, method: str = "get"):
        def _response_hook(resp: Response, *args, **kwargs):
            if self.verbose:
                print("----------------------------")
                print(f"URL:              {resp.request.method} {resp.url}")
                print(f"Status:           {resp.status_code} {resp.reason}")
                print(f"Request headers:  {resp.request.headers}")
                print(f"Response headers: {resp.headers}")
                print("----------------------------")
                print("BODY:")
                print(resp.text)
                print("----------------------------")

        req = requests.Request(method,
                               f"{ASANA_API_BASE}{url}",
                               auth=self.AsanaAuth(self.token),
                               hooks={"response": _response_hook}).prepare()

        resp = Session().send(req)
        resp.raise_for_status()

        return resp.json()["data"]

    def __init__(self, token: str, verbose: bool):
        self.token = token
        self.verbose = verbose

    def get_user(self, *, user_id: str):
        return self._send_request(f"/users/{user_id}")

    def get_user_tasks(self, *, user_id: str):
        return self._send_request(f"/users/me/user_task_list?workspace={workspace}")

