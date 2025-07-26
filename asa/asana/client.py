import json
from typing import List

import requests
from requests import Session, Response
from requests.auth import AuthBase

from asa.asana.model import User, WorkspaceMembership, TeamCompact, TeamMembership, TaskCompact, ProjectCompact, TaskList

ASANA_API_BASE="https://app.asana.com/api/1.0"



class AsanaClient:
    class AsanaAuth(AuthBase):
        def __init__(self, token: str):
            self.token = token

        def __call__(self, r):
            r.headers['Authorization'] = f"Bearer {self.token}"
            return r

    def _send_request(self, url: str, method: str = "get"):
        def _response_hook(resp_: Response):
            if self.verbose:
                print("----------------------------")
                print(f"URL:              {resp_.request.method} {resp_.url}")
                print(f"Status:           {resp_.status_code} {resp_.reason}")
                print(f"Request headers:  {json.dumps(dict(resp_.request.headers))}")
                print(f"Response headers: {json.dumps(dict(resp_.headers))}")
                print("----------------------------")
                print("Response body:")
                print(resp_.text)
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

    def get_user(self, *, user_id: str) -> User:
        data = self._send_request(f"/users/{user_id}")
        return User.model_validate(data)

    def get_workspace_memberships(self, *, user_id: str = "me") -> List[WorkspaceMembership]:
        data = self._send_request(f"/users/{user_id}/workspace_memberships")
        return [WorkspaceMembership.model_validate(wm) for wm in data]

    def get_teams(self, *, workspace: str, user_id: str = "me") -> List[TeamCompact]:
        data = self._send_request(f"/users/{user_id}/teams?workspace={workspace}")
        return [TeamCompact.model_validate(t) for t in data]

    def get_team_members(self, *, team_id: str) -> List[TeamMembership]:
        data = self._send_request(f"/teams/{team_id}/team_memberships")
        return [TeamMembership.model_validate(tm) for tm in data]

    def get_projects_by_team(self, *, team_id: str) -> List[ProjectCompact]:
        data = self._send_request(f"/teams/{team_id}/projects")
        return [ProjectCompact.model_validate(p) for p in data]

    def get_project_incomplete_tasks(self, *, project_id: str) -> List[TaskCompact]:
        data = self._send_request(f"/projects/{project_id}/tasks?limit=100&completed_since=now&opt_fields=assignee.name,memberships.section.name,name,assignee_name")
        return [TaskCompact.model_validate(t) for t in data]

    def get_user_tasks(self, *, workspace: str, user_id: str = "me") -> TaskList:
        data = self._send_request(f"/users/{user_id}/user_task_list?workspace={workspace}")
        return TaskList.model_validate(data)

