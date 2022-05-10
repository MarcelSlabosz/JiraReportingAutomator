from typing import List
import functools
import operator
import math
import datetime
import logging

from jira_reporter.data_proividers import Worklog


class Aggregator:
    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self._aggregate = {}
        self._minimal_time_in_sec = 60

    def set_round_time(self, minutes):
        self._minimal_time_in_sec = 60 * minutes

    def aggregate_worklogs(self, worklogs):
        self.__map(worklogs)
        return self.__reduce()

    def __map(self, worklogs):
        worklog : Worklog
        for worklog in worklogs:
            self.__append_worklog(worklog)

    def __append_worklog(self, worklog: Worklog):

        # get day
        day_key = worklog.work_date.strftime('%Y%m%d')
        if not day_key in self._aggregate.keys():
            new_list = {}
            self._aggregate[day_key] = new_list
        items_for_day = self._aggregate[day_key]

        # get key for issue
        if not worklog.issue_key in items_for_day.keys():
            new_issue = {}
            items_for_day[worklog.issue_key] = new_issue
        items_for_issue = items_for_day[worklog.issue_key]

        # get items for description
        if not worklog.description in items_for_issue.keys():
            new_description = {}
            items_for_issue[worklog.description] = new_description
        items_for_description = items_for_issue[worklog.description]

        # get overtime:
        if not worklog.is_overtime in items_for_description.keys():
            new_list = []
            items_for_description[worklog.is_overtime] = new_list
        items_for_overtime:List = items_for_description[worklog.is_overtime]

        # append
        items_for_overtime.append(worklog)

    def __reduce(self):
        output_worklogs = []

        for day_key, day_data in self._aggregate.items():
            for issue_keym, issue_data in day_data.items():
                for desc_key, desc_data in issue_data.items():
                    for is_overtime_key, is_overtime_data in desc_data.items():
                        time_list = list(map(lambda worklog: worklog.work_time_minutes, is_overtime_data))
                        sum_time = functools.reduce(operator.add, time_list)
                        sum_time_seconds = sum_time.seconds
                        sum_time_sec = math.ceil(sum_time_seconds/self._minimal_time_in_sec)*self._minimal_time_in_sec
                        sum_time_final = datetime.timedelta(seconds=sum_time_sec)

                        realtime_list = list(map(lambda worklog: worklog.work_time_secondes, is_overtime_data))
                        sum_real_time = functools.reduce(operator.add, realtime_list)

                        first_worklog = is_overtime_data[0]
                        output_worklogs.append(Worklog(first_worklog[0], first_worklog[1], first_worklog[2],
                                                       sum_time_final, first_worklog[4], sum_real_time))

        return output_worklogs