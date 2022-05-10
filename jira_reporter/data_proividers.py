import re
import datetime
import math
import logging

from typing import List, Tuple

from collections import namedtuple

from jira_reporter import JiraReporterException
from jira_reporter.file_readers import RAWWorklog


Worklog = namedtuple('Worklog', ['issue_key', 'is_overtime', 'description', 'work_time_minutes', 'work_date', 'work_time_secondes'])


class WorklogProviderException(JiraReporterException):
    pass


class WorklogProvider:
    def __init__(self, raw_worklogs:List[RAWWorklog]):
        self.__logger = logging.getLogger(__name__)
        self.__raw_worklogs = raw_worklogs

    def get_worklogs(self) -> List[Worklog]:
        """Parse loaded worklogs file and returns  """
        return self.__parse_worklog_data()

    def __parse_worklog_data(self) -> List[Worklog]:
        worklogs_out : List[Worklog] = []
        pattern = re.compile(r"^([A-Z0-9_&\.]+\-\d+)( - (\(\!\))?(.*))?$")
        for worklog in self.__raw_worklogs:
            self.__logger.debug("RawWorklog %s", repr(worklog))
            match = re.search(pattern, worklog.activity)
            original_time_spent, time_spent = self.__parse_time_delta(worklog.duration)
            work_date = datetime.datetime.fromisoformat(worklog.start_time).replace(hour=0, minute=0, second=0, microsecond=0)
            self.__logger.debug("\t%s, %s, %s, %s, %s",
                                match.group(1), match.group(3) == '(!)', match.group(4), repr(time_spent), work_date.strftime("%Y-%m-%d"))
            worklogs_out.append(Worklog(match.group(1), match.group(3) == '(!)',
                                        match.group(4).strip() if match.group(4) else '',  time_spent, work_date, original_time_spent))
        return worklogs_out

    def __parse_time_delta(self, time_spent: str) -> Tuple[datetime.timedelta, datetime.timedelta]:
        components = time_spent.split(":")
        delta_t = datetime.timedelta(hours=int(components[0]), minutes=int(components[1]), seconds=int(components[2]))
        seconds = delta_t.seconds
        self.__logger.debug('\toriginal workflow time: %s', repr(delta_t))
        minut = math.ceil(seconds/60)
        return delta_t, datetime.timedelta(minutes=minut)
