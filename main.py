import sys
import os

from typing import List
from pathlib import Path

from jira_reporter.helpers import get_logger, arg_parse, read_config, get_out_files_name, is_file_already_processed

from jira_reporter.connections import JiraConnectionGenerator, JiraReporterConnectionException
from jira_reporter.file_readers import WorklogReader, WorklogReaderException, RAWWorklog, JiraWorklogReader, JiraWorklog
from jira_reporter.validators import (RawWorkflowValidator, JiraTaskExistanceValidator,
                                      JiraReporterValidationError, JiraProjectsRigthsValidator)
from jira_reporter.data_proividers import WorklogProvider, WorklogProviderException
from jira_reporter.aggregators import Aggregator
from jira_reporter.processor import JiraWorklogAdder, JiraWorklogRemover, WorkflowRemovingResult
from jira_reporter.out import WorklogAdderResultWriter


if __name__ == '__main__':
    execution_arguments = arg_parse(sys.argv[1:])
    logger = get_logger(execution_arguments)
    logger.info("The Jira Reporting Automator just started. :)")

    # get configuration
    logger.info("Reading config file...")
    config = read_config(execution_arguments.config_file)

    jira_connection_factory = JiraConnectionGenerator()
    try:
        jira_connection = jira_connection_factory.get_jira_connection(config)
    except JiraReporterConnectionException as connection_exception:
        logger.critical("Cannot create jira connection.")
        exit(1)

    if execution_arguments.mode == 'add':
        # LOADING DATAFILE
        logger.info("Reading input file...")
        worklog_reader = WorklogReader()

        if is_file_already_processed(execution_arguments.input_file):
            logger.info("File was already processed. STOP!")
            logger.info("See help page: How to process input file again.")
            exit(5)

        try:
            with open(execution_arguments.input_file, "r", newline='') as csvfile:
                raw_worklogs: List[RAWWorklog] = worklog_reader.load_worklog_file(csvfile)
        except WorklogReaderException as reader_exception:
            logger.critical("Failed: %s", repr(reader_exception))
            exit(2)

        # BASIC VALIDATION
        logger.info("Basic validation...")
        validator = RawWorkflowValidator()
        try:
            validator.validate(raw_worklogs)
        except JiraReporterValidationError as e:
            logger.critical(f"Incorrect worklog(s) format! {raw_worklogs}")
            exit(3)

        # PARSING LOADED RAWWORKLOGS
        logger.info("Parsing worklogs...")
        worklog_provider = WorklogProvider(raw_worklogs)
        worklogs = worklog_provider.get_worklogs()

        # AGERAGATION
        logger.info("Aggregating worklogs...")
        aggregator = Aggregator()
        aggregated_worklogs = aggregator.aggregate_worklogs(worklogs)

        # CHECK IF TASKS EXISTS:
        logger.info("Checking if issues exist...")
        existance_validator = JiraTaskExistanceValidator(jira_connection)
        existance_validator.validate(aggregated_worklogs)

        # # CHECK IF USER HAS RIGHTS TO LOG WORK IN PROJECTS:
        # logger.info("Checking if user has appropriate rights to log work...")
        # project_rights_validator = JiraProjectsRigthsValidator(jira_connection)
        # project_rights_validator.validate(aggregated_worklogs)


        if execution_arguments.dry_run:
            logger.warning("DRY RUN! Stop!")
            exit(0)

        # LOG TIME
        logger.info("Adding worklogs...")
        jira_worker = JiraWorklogAdder(jira_connection)
        worklog_results = jira_worker.log_work(aggregated_worklogs)
        logger.debug("... OK")

        # worklog_results = []

        # WRITE RESULST TO FILES
        logger.info("Writing results...")
        ok_file, err_file = get_out_files_name(execution_arguments.input_file)

        result_writer = WorklogAdderResultWriter()
        with open(ok_file, "w", newline='') as ok_h, open(err_file, "w", newline='') as err_h:
            result_writer.write_to_file(ok_h, err_h, worklog_results)
        logger.debug("... OK")

    elif execution_arguments.mode == 'remove':
        # LOADING Datafile
        logger.debug("Reading input file with worklogs...")
        reader = JiraWorklogReader(logger)
        try:
            with open(execution_arguments.input_file, "r", newline='') as csvfile:
                jiraworklogs: List[JiraWorklog] = reader.load_from_file(csvfile)
        except WorklogReaderException as reader_exception:
            logger.error("Failed: %s", repr(reader_exception))
            exit(2)

        print(repr(jiraworklogs))


        processor = JiraWorklogRemover(jira_connection)

        result = processor.remove_worklogs(jiraworklogs)

        print(repr(result))

