from unittest import TestCase, mock
import datetime

from jira_reporter.validators import RawWorkflowValidator, JiraTaskExistanceValidator,  JiraReporterValidationError
from jira_reporter.file_readers import RAWWorklog
from jira_reporter.data_proividers import Worklog

import jira


class TestRawWorkflowValidator(TestCase):

    def setUp(self) -> None:
        self.validator = RawWorkflowValidator()

    def test_vaild_records1(self):
        records = [
            RAWWorklog('TEST-12 - my activity', '00:00:01', '2020-10-25T17:06:21+02:00', '2020-07-15T17:21:03+02:00')
        ]

        self.validator.validate(records)

    def test_vaild_records2(self):
        records = [
            RAWWorklog('my activity', '00:00:01', '2020-10-25T17:06:21+02:00', '2020-07-15T17:21:03+02:00')
        ]

        with self.assertRaises(JiraReporterValidationError):
            self.validator.validate(records)


class TestJiraTaskExistanceValidator(TestCase):

    def raise_jira_error(self, code, message, link):
        raise jira.exceptions.JIRAError(code, message, link)

    def return_issue_object(self, key, summary):
        mock_obj = mock.Mock()
        mock_obj.fields.summary.returns = summary
        return mock_obj

    def test_validate_unexisting_issue(self):

        worklogs = [Worklog('BIGDBIINC-112122', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                            datetime.datetime(2020, 10, 25,
                                              tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                            datetime.timedelta(seconds=882)
                            )
                    ]

        jira_con = mock.Mock()

        jira_con.issue.side_effect = lambda *args, **kwargs: self.raise_jira_error(404, 'Issue Does Not Exist',
                                                                     'https://jira.test.test/rest/api/2/issue/BIGDBIINC-11212222222?fields=summary')

        validator = JiraTaskExistanceValidator(jira_con)

        with self.assertRaises(JiraReporterValidationError):
            validator.validate(worklogs)

    def test_item_ok(self):
        worklogs = [Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                            datetime.datetime(2020, 10, 25,
                                              tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                            datetime.timedelta(seconds=882)
                            )
                    ]

        jira_con = mock.Mock()

        jira_con.issue.side_effect = lambda *args, **kwargs: self.return_issue_object('BIGDBIINC-1121', 'sth')

        validator = JiraTaskExistanceValidator(jira_con)

        result = validator.validate(worklogs)

        self.assertTrue(result)