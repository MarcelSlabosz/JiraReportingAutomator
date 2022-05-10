import csv
from typing import List
import logging

from enum import Enum
from collections import namedtuple

from jira_reporter import JiraReporterException


RAWWorklog = namedtuple('RAWWorklog', ['activity', 'duration', 'start_time', 'end_time'])
JiraWorklog = namedtuple('JiraWorklog', ['worklog_id', 'issue_key', 'work_time_minutes', 'date'])


class WorklogReaderException(JiraReporterException):
    pass


class WorklogFileFormat(Enum):
    TopTrackerExport = 1


class WorklogReader:
    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__register_dialects()

    @staticmethod
    def __register_dialects():
        csv.register_dialect('toptracker', delimiter=',', quoting=csv.QUOTE_NONE)

    def load_worklog_file(self, file_handler, file_format: WorklogFileFormat = WorklogFileFormat.TopTrackerExport) \
            -> List[RAWWorklog]:
        """Read worklogs file to RAWWorklog format
        """
        if file_format == WorklogFileFormat.TopTrackerExport:
            raw_worklogs = self.__read_toptracker_file(file_handler)
            self.__logger.debug("Read records: %s", repr(raw_worklogs))
            return raw_worklogs
        else:
            raise WorklogReaderException("Unknown file format")

    @staticmethod
    def __read_toptracker_file(file_handler) -> List[RAWWorklog]:
        records = []
        reader = csv.reader(file_handler, dialect='toptracker')
        for row in reader:
            records.append(RAWWorklog(row[0], row[3], row[9], row[10]))
        return records[1:]  # omit headers


class JiraWorklogReader:
    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__register_dialect()

    @staticmethod
    def __register_dialect():
        csv.register_dialect('jira_worklogs', delimiter=',', quoting=csv.QUOTE_NONE)

    def load_from_file(self, file_handler) -> List[JiraWorklog]:
        records: List[JiraWorklog] = []
        reader = csv.reader(file_handler, dialect='jira_worklogs')
        for row in reader:
            records.append(JiraWorklog(row[0], row[1], row[2], row[3]))
        return records[1:]  # omit headers
