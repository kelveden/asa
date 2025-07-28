import json
from typing import List

import requests
from requests import Session, Response
from requests.auth import AuthBase

from asa.asana.model import (
    User,
    WorkspaceMembership,
    TeamCompact,
    TeamMembership,
    ProjectCompact,
    TaskList,
    Task,
    SectionCompact,
)

ASANA_API_BASE = "https://app.asana.com/api/1.0"
TASK_OPT_FIELDS = "assignee.name,memberships.section.name,name,assignee_name,projects,workspace,workspace.name,projects.name,permalink_url"
PROJECT_OPT_FIELDS = "permalink_url,name"
TEAM_OPT_FIELDS = "permalink_url,name"


class AsanaClient:
    class AsanaAuth(AuthBase):
        def __init__(self, token: str):
            self.token = token

        def __call__(self, r):
            r.headers["Authorization"] = f"Bearer {self.token}"
            return r

    def _send_request(self, url: str, method: str = "get"):
        def _response_hook(resp_: Response, *args, **kwargs):
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

        req = requests.Request(
            method,
            f"{ASANA_API_BASE}{url}",
            auth=self.AsanaAuth(self.token),
            hooks={"response": _response_hook},
        ).prepare()

        resp = Session().send(req)
        resp.raise_for_status()

        return resp.json()["data"]

    def __init__(self, token: str, verbose: bool):
        self.token = token
        self.verbose = verbose

    # https://developers.asana.com/reference/getuser
    def get_user(self, *, user_id: str) -> User:
        data = self._send_request(f"/users/{user_id}")
        return User.model_validate(data)

    # https://developers.asana.com/reference/getworkspacemembershipsforuser
    def get_workspace_memberships(self, *, user_id: str = "me") -> List[WorkspaceMembership]:
        data = self._send_request(f"/users/{user_id}/workspace_memberships")
        return [WorkspaceMembership.model_validate(wm) for wm in data]

    # https://developers.asana.com/reference/getteamsforuser
    def get_teams(self, *, workspace: str, user_id: str = "me") -> List[TeamCompact]:
        data = self._send_request(
            f"/users/{user_id}/teams?workspace={workspace}&opt_fields={TEAM_OPT_FIELDS}"
        )
        return [TeamCompact.model_validate(t) for t in data]

    # https://developers.asana.com/reference/getteammembershipsforteam
    def get_team_members(self, *, team_id: str) -> List[TeamMembership]:
        data = self._send_request(f"/teams/{team_id}/team_memberships")
        return [TeamMembership.model_validate(tm) for tm in data]

    # https://developers.asana.com/reference/getprojectsforteam
    def get_projects_by_team(self, *, team_id: str) -> List[ProjectCompact]:
        data = self._send_request(f"/teams/{team_id}/projects?opt_fields={PROJECT_OPT_FIELDS}")
        return [ProjectCompact.model_validate(p) for p in data]

    # https://developers.asana.com/reference/gettasksforproject
    def get_project_incomplete_tasks(self, *, project_id: str) -> List[Task]:
        data = self._send_request(
            f"/projects/{project_id}/tasks?limit=100&completed_since=now&opt_fields={TASK_OPT_FIELDS}"
        )
        return [Task.model_validate(t) for t in data]

    # https://developers.asana.com/reference/getusertasklistforuser
    def get_user_task_list(self, *, workspace: str, user_id: str = "me") -> TaskList:
        data = self._send_request(f"/users/{user_id}/user_task_list?workspace={workspace}")
        return TaskList.model_validate(data)

    # https://developers.asana.com/reference/gettasksforusertasklist
    def get_user_incomplete_tasks(self, *, task_list_id: str) -> List[Task]:
        data = self._send_request(
            f"/user_task_lists/{task_list_id}/tasks?limit=100&completed_since=now&opt_fields={TASK_OPT_FIELDS}"
        )
        return [Task.model_validate(t) for t in data]

    # https://developers.asana.com/reference/getsectionsforproject
    def get_sections_by_project(self, *, project_id: str) -> List[SectionCompact]:
        data = self._send_request(f"/projects/{project_id}/sections")
        return [SectionCompact.model_validate(s) for s in data]

    # https://developers.asana.com/reference/searchtasksforworkspace
    def search_tasks(self, *, workspace_id: str, project_id: str, search_text: str) -> List[Task]:
        data = self._send_request(
            f"/workspaces/{workspace_id}/tasks/search?text={search_text}&opt_fields={TASK_OPT_FIELDS}&projects.any={project_id}"
        )
        return [Task.model_validate(t) for t in data]
