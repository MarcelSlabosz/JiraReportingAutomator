from unittest import TestCase, mock
import datetime

from jira_reporter.data_proividers import Worklog
from jira_reporter.aggregators import Aggregator


class TestAggregator(TestCase):

    def setUp(self) -> None:
        self._aggregator = Aggregator()

    def test_aggregate_same_worklogs(self):
        worklogs = [
            Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                datetime.datetime(2020, 10, 25,
                                  tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                datetime.timedelta(seconds=882)),
            Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                datetime.datetime(2020, 10, 25,
                                  tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                datetime.timedelta(seconds=882))
            ]

        result = self._aggregator.aggregate_worklogs(worklogs)
        expected = Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=30, seconds=0),
                           datetime.datetime(2020, 10, 25,
                                             tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                           datetime.timedelta(seconds=1764))
        self.assertEqual(len(result), 1)
        self.assertTupleEqual(result[0], expected)

    def test_aggregate_diff_overtime_worklogs(self):
        worklogs = [
            Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=882)),
            Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=882)),
            Worklog('BIGDBIINC-1121', True, 'testy', datetime.timedelta(minutes=15, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=882))
        ]

        result = self._aggregator.aggregate_worklogs(worklogs)
        expected1 = Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=30, seconds=0),
                           datetime.datetime(2020, 10, 25,
                                             tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                           datetime.timedelta(seconds=1764))
        expected2 = Worklog('BIGDBIINC-1121', True, 'testy', datetime.timedelta(minutes=15, seconds=0),
                            datetime.datetime(2020, 10, 25,
                                              tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                            datetime.timedelta(seconds=882))
        self.assertEqual(len(result), 2)
        self.assertSetEqual(set(result), {expected1, expected2})

    def test_aggregator_5min_round(self):
        worklogs = [
            Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=3, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=160)),
            Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=3, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=170))
        ]

        aggregator = Aggregator()
        aggregator.set_round_time(5)
        result = aggregator.aggregate_worklogs(worklogs)
        expected = Worklog('BIGDBIINC-1121', False, 'testy', datetime.timedelta(minutes=10, seconds=0),
                           datetime.datetime(2020, 10, 25,
                                             tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                           datetime.timedelta(seconds=330))
        self.assertEqual(len(result), 1)
        self.assertTupleEqual(result[0], expected)


    def test_aggregate_same_description_diff_issue(self):
        worklogs = [
            Worklog('BIGDBIINC-1', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=882)),
            Worklog('BIGDBIINC-1', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=882)),
            Worklog('BIGDBIINC-2', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                    datetime.datetime(2020, 10, 25,
                                      tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                    datetime.timedelta(seconds=882))
        ]

        result = self._aggregator.aggregate_worklogs(worklogs)
        expected1 = Worklog('BIGDBIINC-1', False, 'testy', datetime.timedelta(minutes=30, seconds=0),
                            datetime.datetime(2020, 10, 25,
                                              tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                            datetime.timedelta(seconds=1764))
        expected2 = Worklog('BIGDBIINC-2', False, 'testy', datetime.timedelta(minutes=15, seconds=0),
                            datetime.datetime(2020, 10, 25,
                                              tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
                            datetime.timedelta(seconds=882))
        self.assertEqual(len(result), 2)
        self.assertSetEqual(set(result), {expected1, expected2})
