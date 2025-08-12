from typing import Iterable, Optional

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        frozen = True


# Identifier used in the Asana API to identify each resource
type Gid = str


class NamedRef(BaseModel):
    """
    Base class for all resources that include an identifier (gid) and name.
    """

    gid: Gid
    name: str
    permalink_url: Optional[str] = None


class Photo(BaseModel):
    """
    Encapsulates the data for a user photo.

    See: https://developers.asana.com/reference/getuser
    """

    image_21x21: str
    image_27x27: str
    image_36x36: str
    image_60x60: str
    image_128x128: str


class UserCompact(NamedRef):
    """
    The compact details for a user.

    See: https://developers.asana.com/reference/users#usercompact
    """

    pass


class User(UserCompact):
    """
    Full details for a user.

    See: https://developers.asana.com/reference/users
    """

    email: str
    photo: Photo


class Workspace(NamedRef):
    """
    The compact details for a named workspace.

    See: https://developers.asana.com/reference/workspaces#workspacecompact
    """

    pass


class WorkspaceMembership(BaseModel):
    """
    Encapsulates the membership of a user in a given workspace.

    See: https://developers.asana.com/reference/workspace-memberships
    """

    gid: Gid
    user: UserCompact
    workspace: Workspace


class Team(NamedRef):
    """
    The compact details for a named team.

    See: https://developers.asana.com/reference/teams#teamcompact
    """

    pass


class TeamMembership(BaseModel):
    """
    Encapsulates the membership of a user in a given team.

    See: https://developers.asana.com/reference/team-memberships
    """

    gid: Gid
    user: UserCompact
    team: Team


class Project(NamedRef):
    """
    The compact details for a named project.

    See: https://developers.asana.com/reference/projects#projectcompact
    """

    pass


class TaskCompact(NamedRef):
    """
    The compact details to a named task.

    See: https://developers.asana.com/reference/tasks#taskcompact
    """

    pass


class TaskList(NamedRef):
    """
    The details for a specific task list.

    See: https://developers.asana.com/reference/user-task-lists
    """

    owner: UserCompact
    workspace: Workspace


class Section(NamedRef):
    """
    The compact details for a named section
    """

    pass


class Task(NamedRef):
    """
    The details for a task.

    See: https://developers.asana.com/reference/tasks
    """

    class ProjectMembership(BaseModel):
        project: Project

    class SectionMembership(BaseModel):
        section: Section

    assignee: Optional[UserCompact]
    memberships: Iterable[ProjectMembership | SectionMembership]
    projects: Iterable[Project]
    workspace: Workspace
