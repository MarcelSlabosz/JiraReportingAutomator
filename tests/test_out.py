from unittest import TestCase
import datetime
from io import StringIO

from jira_reporter.out import WorklogAdderResultWriter
from jira_reporter.processor import IssueWorklogAddingResult
from jira_reporter.data_proividers import Worklog

class TestWorklogAdderResultWriter(TestCase):
    def test_results_to_stirngio_ok(self):
        result = [IssueWorklogAddingResult(
            Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=3, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=160))
            , 123213213, True, 'logged'
        )]

        writer = WorklogAdderResultWriter()

        ok_buff: StringIO
        err_buf: StringIO
        ok_buf, err_buf = writer.results_to_stirngio(result)

        expected_ok_buf = """worklog_id,issue_key,work_time_minutes,date
123213213,BIGDBIINC-1121,0:03:00,2020-10-25 00:00:00+02:00"""
        expected_err_buf = 'issue_key,is_overtime,description,work_time_minutes,work_date,work_time_secondes,error_message'

        self.assertEqual(ok_buf.getvalue(), expected_ok_buf)
        self.assertEqual(err_buf.getvalue(), expected_err_buf)

    def test_results_to_stirngio_err(self):

        result = [IssueWorklogAddingResult(
            Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=3, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=160))
            , 123213213, False, 'some error'
        )]

        writer = WorklogAdderResultWriter()

        ok_buff: StringIO
        err_buf: StringIO
        ok_buf, err_buf = writer.results_to_stirngio(result)

        expected_ok_buf = """worklog_id,issue_key,work_time_minutes,date"""
        expected_err_buf = """issue_key,is_overtime,description,work_time_minutes,work_date,work_time_secondes,error_message
BIGDBIINC-1121,False,testy,0:03:00,2020-10-25 00:00:00+02:00,0:02:40,some error"""

        self.assertEqual(ok_buf.getvalue(), expected_ok_buf)
        self.assertEqual(err_buf.getvalue(), expected_err_buf)

    def test_results_to_stirngio_mix(self):
        result = [IssueWorklogAddingResult(
            Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=3, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=160))
            , 123213213, True, 'logged'),
            IssueWorklogAddingResult(
            Worklog('BIGDBIINC-1122', False, 'testy err', datetime.timedelta(minutes=3, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=160))
            , 123213213, False, 'some error'
        )]

        writer = WorklogAdderResultWriter()

        ok_buff: StringIO
        err_buf: StringIO
        ok_buf, err_buf = writer.results_to_stirngio(result)

        expected_ok_buf = """worklog_id,issue_key,work_time_minutes,date
123213213,BIGDBIINC-1121,0:03:00,2020-10-25 00:00:00+02:00"""
        expected_err_buf = """issue_key,is_overtime,description,work_time_minutes,work_date,work_time_secondes,error_message
BIGDBIINC-1122,False,testy err,0:03:00,2020-10-25 00:00:00+02:00,0:02:40,some error"""

        self.assertEqual(ok_buf.getvalue(), expected_ok_buf)
        self.assertEqual(err_buf.getvalue(), expected_err_buf)



