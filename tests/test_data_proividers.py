from unittest import TestCase, mock
from typing import List
import datetime

from jira_reporter.data_proividers import WorklogProvider, WorklogProviderException, Worklog
from jira_reporter.file_readers import RAWWorklog

class TestWorklogProvider(TestCase):
    def test_get_worklogs(self):
        worklogs : List[RAWWorklog] = [
            RAWWorklog('BIGDBIINC-1121 - testy', '00:14:42', '2020-10-25T17:06:21+02:00', '2020-07-15T17:21:03+02:00')
        ]
        worklog_provider = WorklogProvider(raw_worklogs=worklogs)

        result = worklog_provider.get_worklogs()

        expected = Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=14, seconds=0),
                           datetime.datetime(2020, 10, 25,
                                             tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                           datetime.timedelta(seconds=882))

        self.assertEqual(len(result), 1)
        self.assertTupleEqual(result[0], expected)

    def test_get_woklog_overtime(self):
        worklogs : List[RAWWorklog] = [
            RAWWorklog('BIGDBIINC-1121 - (!) testy', '00:14:42', '2020-10-25T17:06:21+02:00', '2020-07-15T17:21:03+02:00')
        ]
        worklog_provider = WorklogProvider(raw_worklogs=worklogs)

        result = worklog_provider.get_worklogs()

        expected = Worklog('BIGDBIINC-1121', True, 'testy', datetime.timedelta(minutes=14, seconds=0),
                           datetime.datetime(2020, 10, 25,
                                             tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                           datetime.timedelta(seconds=882))

        self.assertEqual(len(result), 1)
        self.assertTupleEqual(result[0], expected)