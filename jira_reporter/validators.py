from typing import List
from abc import ABC
import logging

import re

import jira

from jira_reporter import JiraReporterException
from jira_reporter.file_readers import RAWWorklog
from jira_reporter.data_proividers import Worklog


class JiraReporterValidationError(JiraReporterException):
    pass


class AbstractItemsValidator(ABC):
    def validate(self, items:List) -> bool:
        raise NotImplemented


class RawWorkflowValidator(AbstractItemsValidator):
    def __init__(self):
        self.__logger = logging.getLogger(__name__)

    def validate(self, items: List) -> bool:
        keys_are_corrects = self.__check_worklog_key_correctness(items)
        if not keys_are_corrects:
            raise JiraReporterValidationError("Some work log doesn't provide issue key.")

        return True

    def __check_worklog_key_correctness(self, records: List[RAWWorklog]) -> bool:

        self.__logger.debug("Checking of extracting keys from activity...")
        to_ret = True
        pattern = re.compile("^[A-Z0-9_&\.]+\-\d+")
        for worklog in records:
            self.__logger.debug("Worklog %s", repr(worklog.activity))
            match = re.search(pattern, worklog.activity)
            self.__logger.debug(repr(match))
            if match:
                self.__logger.debug("\tOK")
            else:
                self.__logger.error("Worklog %s doesn't provide issue key", repr(worklog))
                to_ret = False
        return to_ret


class JiraTaskExistanceValidator(AbstractItemsValidator):

    def __init__(self, jira_connection) -> None:
        self.__jira_connection = jira_connection
        self.__logger = logging.getLogger(__name__)

    def validate(self, items: List) -> bool:
        keys = self.__generate_keys_set(items)
        ok = self.__check_existance(keys)

        if not ok:
            raise JiraReporterValidationError('At least one jira issue does not exists.')

        return True

    @staticmethod
    def __generate_keys_set(items: List) -> set:
        keys = set()
        worklog: Worklog
        for worklog in items:
            keys.add(worklog.issue_key)
        return keys

    def __check_existance(self, keys: set):
        is_ok = True
        for issue_key in keys:
            self.__logger.debug(issue_key)
            try:
                issue = self.__jira_connection.issue(issue_key, fields='summary')
                self.__logger.debug(issue.fields.summary)
            except jira.exceptions.JIRAError as ex:
                self.__logger.warn(repr(ex))
                is_ok = False
        return is_ok


class JiraProjectsRigthsValidator(AbstractItemsValidator):

    def __init__(self, jira_connection) -> None:
        self.__jira_connection = jira_connection
        self.__logger = logging.getLogger(__name__)

    def validate(self, items: List) -> bool:
        keys = self.__get_projects_keys(items)
        projects_has_log_rights = self.__check_projects_log_rights(keys)
        is_ok = self.__reduce_rigths(projects_has_log_rights)

        if not is_ok:
            self.__print_rights_lacks(projects_has_log_rights)

        return is_ok

    def __get_projects_keys(self, issues):
        project_keys_set = set()
        for issue in issues:
            key = "-".join(issue.issue_key.split("-")[:-1])
            project_keys_set.add(key)

        return project_keys_set

    def __check_projects_log_rights(self, projects_keys):
        project_perms = {}
        for project_keys in projects_keys:
            permissions = self.__jira_connection.my_permissions(projectKey="DLSD")
            perms = permissions.get("permissions", {}).keys()
            project_perms[project_keys] = 'WORK_ON_ISSUES' in perms

        return project_perms

    @staticmethod
    def __reduce_rigths(projects_rights:dict) -> bool:
        for k,v in projects_rights.items():
            if not v:
                return False
        return True

    def __print_rights_lacks(self, projects_rights:dict) -> None:
        for k,v in projects_rights.items():
            if not v:
                self.__logger.warning("You haven't rights to log in project %s", k)