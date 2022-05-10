from collections import namedtuple
from typing import List
import logging

from jira_reporter.data_proividers import Worklog
from jira_reporter.file_readers import JiraWorklog

import jira

IssueWorklogAddingResult = namedtuple('IssueWorklogAddingResult', ['worklog', 'worklog_id', 'status', 'message'])
WorkflowRemovingResult = namedtuple('WorkflowRemovingResult', ['worklog_id', 'status', 'message'])


class JiraWorklogAdder:
    def __init__(self, jira_connection) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__jira_connection = jira_connection

    def log_work(self, worklogs: List[Worklog]) -> List:
        logged_workhours: List[IssueWorklogAddingResult] = []

        worklog:Worklog
        for worklog in worklogs:
            try:
                issue = self.__jira_connection.issue(worklog.issue_key, fields='summary,comment')
                self.__logger.debug(issue.fields.summary)
                worklog_id = self.__jira_connection.add_worklog(worklog.issue_key, comment=worklog.description,
                                                                timeSpentSeconds=worklog.work_time_minutes.seconds,
                                                                started=worklog.work_date)
                logged_workhours.append(IssueWorklogAddingResult(worklog, worklog_id, True, 'logged'))

                self.__logger.debug(worklog)
            except jira.exceptions.JIRAError as ex:
                self.__logger.error(repr(ex))
                logged_workhours.append(IssueWorklogAddingResult(worklog, None, False, repr(ex)))

        return logged_workhours


class JiraWorklogRemover:
    def __init__(self, jira_connection) -> None:
        self.__logger = logging.getLogger(__name__)
        self.__jira_connection = jira_connection

    def remove_worklogs(self, worklogs:List[JiraWorklog]) -> List[WorkflowRemovingResult]:
        results = []
        worklog: JiraWorklog

        for worklog in worklogs:
            try:
                delete_result = self.__jira_connection.worklog(worklog.issue_key, worklog.worklog_id).delete()
                results.append(WorkflowRemovingResult(worklog.worklog_id, True, 'removed'))
            except jira.exceptions.JIRAError as e:
                results.append(WorkflowRemovingResult(worklog.worklog_id, False, repr(e)))
        return results
