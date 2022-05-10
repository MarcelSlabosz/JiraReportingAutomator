import logging

from jira import JIRA
import jira.exceptions

from jira_reporter import JiraReporterException


class JiraReporterConnectionException(JiraReporterException):
    pass

class JiraConnectionGenerator:

    def __init__(self) -> None:
        self.__logger = logging.getLogger(__name__)

    def __prepate__connection_params(self, configuration):
        connection_params = dict(configuration['JIRA'])
        connection_params['pass'] = '*****'
        self.__logger.debug("Configuration for Jira connectio %s", repr(connection_params))
        self.__logger.info("Creating jira connection...")
        return configuration

    def __create_connection(self, configuration):
        try:
            conf = {
                "server": configuration["JIRA"]["host"]
            }
            jira_connection = JIRA(conf, basic_auth=(configuration["JIRA"]["user"], configuration["JIRA"]["pass"]))
            self.__logger.debug(jira_connection)
            self.__logger.debug("...OK")
        except Exception as exception:
            self.__logger.error("Failed: %s", repr(exception))
            raise JiraReporterConnectionException(repr(exception))

        return jira_connection

    def get_jira_connection(self, configuration) -> JIRA:
        connection_config = self.__prepate__connection_params(configuration)
        jira_connection = self.__create_connection(connection_config)
        return jira_connection
