from unittest import TestCase, mock
from io import StringIO

from jira_reporter.file_readers import WorklogReader, RAWWorklog, JiraWorklogReader, JiraWorklog, WorklogReaderException


class TestWorklogReader(TestCase):

    def setUp(self) -> None:
        self.data_reader = WorklogReader()

    def test_load_worklog_file(self):
        handler = StringIO()
        handler.write("""activity,project,workers,duration,time,duration_seconds,keyboard_hits,mouse_clicks,screenshot_count,start_time,end_time
BIGDBIINC-1121 - (!) testy,Praca,Marcel Słabosz,00:14:42,05:06pm July 15th - 05:21pm July 15th,882,0,0,0,2020-10-25T17:06:21+02:00,2020-07-15T17:21:03+02:00
BIGDBIINC-1121 - testy,Praca,Marcel Słabosz,00:14:42,05:06pm July 15th - 05:21pm July 15th,882,0,0,0,2020-10-25T17:06:21+02:00,2020-07-15T17:21:03+02:00""")
        handler.seek(0)

        result = self.data_reader.load_worklog_file(handler)
        expected = [
            RAWWorklog('BIGDBIINC-1121 - (!) testy', '00:14:42', '2020-10-25T17:06:21+02:00',
                       '2020-07-15T17:21:03+02:00'),
            RAWWorklog('BIGDBIINC-1121 - testy', '00:14:42', '2020-10-25T17:06:21+02:00', '2020-07-15T17:21:03+02:00')
        ]
        self.assertListEqual(result, expected)

    def test_unknown_worklog_file_format(self):
        handler = StringIO()
        with self.assertRaises(WorklogReaderException):
            result = self.data_reader.load_worklog_file(handler, file_format='unknown')


class TestJiraWorklogReader(TestCase):

    def setUp(self) -> None:
        self.data_reader = JiraWorklogReader()
        pass

    def test_load_from_file(self):
        handler = StringIO()
        handler.write("""worklog_id,issue_key,work_time_minutes,date
1,BIG-11,0:01:00,2020-10-25T17:06:21+02:00""")
        handler.seek(0)

        results = self.data_reader.load_from_file(handler)

        expected = JiraWorklog('1', 'BIG-11', '0:01:00', '2020-10-25T17:06:21+02:00')

        self.assertEqual(len(results), 1)
        self.assertTupleEqual(results[0], expected)
