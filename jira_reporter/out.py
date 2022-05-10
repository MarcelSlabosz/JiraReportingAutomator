from typing import List, Tuple
import io
import shutil

from jira_reporter.processor import IssueWorklogAddingResult
from jira_reporter.processor import WorkflowRemovingResult


class WorklogAdderResultWriter:
    def write_to_file(self, ok_file_handler, err_file_handler, results: List[IssueWorklogAddingResult]):
        ok_string: io.StringIO
        error_string: io.StringIO
        ok_string, error_string = self.results_to_stirngio(results)

        shutil.copyfileobj(ok_string, ok_file_handler)
        shutil.copyfileobj(error_string, err_file_handler)

    def results_to_stirngio(self, results: List[IssueWorklogAddingResult]) -> Tuple[io.StringIO, io.StringIO]:
        ok_buf = io.StringIO()
        err_buff = io.StringIO()

        ok_buf.write("worklog_id,issue_key,work_time_minutes,date")
        err_buff.write('issue_key,is_overtime,description,work_time_minutes,work_date,work_time_secondes,error_message')

        for result in results:
            if result.status:
                ok_buf.write("\n%s,%s,%s,%s" % (result.worklog_id, result.worklog.issue_key,
                                                result.worklog.work_time_minutes,
                                                result.worklog.work_date))
            elif not result.status:
                err_buff.write("\n%s,%s,%s,%s,%s,%s,%s"
                               % (result.worklog.issue_key,
                                  result.worklog.is_overtime,
                                  result.worklog.description,
                                  result.worklog.work_time_minutes,
                                  result.worklog.work_date,
                                  result.worklog.work_time_secondes,
                                  result.message,
                               ))

        ok_buf.seek(0)
        err_buff.seek(0)
        return ok_buf, err_buff


class WorklogRemoverResultWriter:
    def write_to_file(self, out_file_handler, results: List[WorkflowRemovingResult]):
        out_string: io.StringIO = self.results_to_stirngio(results)

        shutil.copyfileobj(out_string, out_file_handler)

    def results_to_stirngio(self, results: List[WorkflowRemovingResult]) -> io.StringIO:
        out_buf = io.StringIO()

        out_buf.write("worklog_id,status,message")

        for result in results:
            out_buf.write("\n%s,%s,%s" % (result.worklog_id, result.status, result.message))

        out_buf.seek(0)
        return out_buf
