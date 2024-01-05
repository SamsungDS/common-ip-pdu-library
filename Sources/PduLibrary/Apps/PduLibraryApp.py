import getpass
import os
import sys
import logging.config

from datetime import datetime
from inspect import isclass, ismodule

from pkg_resources import resource_filename
from cliff.app import App
from cliff.commandmanager import CommandManager
from PduLibrary import __description__, __version__

from PduLibrary.Core.RestServer import RestServer
from PduLibrary.Controller.PduLibraryManager import PduLibraryManager
# Below Import statements are required to resolve class name to class object dynamically
from PduLibrary.Exception.PduLibraryException import PduLibraryException


def touch_file(file_path, times=None):
    """
    Check if folder path exists, and create if not available
    Creates file in append mode

    Args:
        file_path:path of the file which needs to be created or updated
        times:timestamp to track file modification time
    Returns:
        None
    Raises:
        None
    """
    file_base_path = os.path.dirname(file_path)
    if not os.path.exists(file_base_path):
        os.makedirs(file_base_path)

    with open(file_path, 'a'):
        os.utime(file_path, times)


def get_logged_in_user():
    return getpass.getuser()


def get_abs_path(path):
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


class PduLibraryApp(App):
    logs_folder_path = os.path.normpath('~/.PduLibrary/Logs')
    logs_file_name = 'PduLibrary.log'
    rest_server_working_folder_name = 'RestServer'
    working_folder_path = os.getcwd()
    rest_server_supervisor_conf_program_name = 'pdu_library_REST_SERVER'

    def __init__(self, argv):
        """
        The constructor for PduLibraryApp class
        """
        # self._rest_server_working_folder_path
        super(PduLibraryApp, self).__init__(
            description=__description__,
            version=__version__,
            command_manager=CommandManager('PduLibrary.commands'),
            # interactive_app_factory=InteractiveApp,
            deferred_help=True
        )

        # Working folder Path setup
        working_folder_path = '.'
        self._working_folder_path = get_abs_path(working_folder_path)

        if not os.path.exists(self._working_folder_path):
            os.makedirs(self._working_folder_path)

        # Rest Server Setup
        _rest_server_working_folder_Name = 'pdu_library_RestServer'
        if not _rest_server_working_folder_Name:
            _rest_server_working_folder_Name = PduLibraryApp.rest_server_working_folder_name

        self._rest_server_working_folder_path = os.path.join(self._working_folder_path,
                                                             _rest_server_working_folder_Name)

        if not os.path.exists(self._rest_server_working_folder_path):
            os.makedirs(self._rest_server_working_folder_path)

        self._rest_server = None
        self._pdu_manager = PduLibraryManager.get_instance()

    def initialize_app(self, argv):
        """
        Initializes the Main pdu_library Ap
        """
        if ('-h' in argv) or ('help' in argv) or ('--help' in argv):
            return

        self.LOG.info('Initializing App')
        self.LOG.info('Initializing Rest Server')
        self._rest_server = RestServer.get_instance(self._rest_server_working_folder_path)
        self.LOG.info('Initialized Rest Server')

    def configure_logging(self):
        """
        Configure logging logic for the app based on the logging configuration file
        """
        log_config_file_path = resource_filename('PduLibrary', 'Conf/PduLibrary_Log.conf')

        if (hasattr(self, 'options')) and (hasattr(self.options, 'log_file')) and self.options.log_file:
            log_file_path = get_abs_path(self.options.log_file)
        else:
            logs_folder_path_from_config = './Logs'
            if not logs_folder_path_from_config:
                logs_folder_path_from_config = PduLibraryApp.logs_folder_path

            logs_folder_path = get_abs_path(logs_folder_path_from_config)

            if not os.path.exists(logs_folder_path):
                os.makedirs(logs_folder_path)

            log_file_name_from_config = 'pdu_library_log'

            if not log_file_name_from_config:
                log_file_name_from_config = PduLibraryApp.logs_file_name

            log_file_path = os.path.join(logs_folder_path, log_file_name_from_config)

        LOGGING_CONFIG = {
            'version': 1,
            'loggers': {
                '': {  # root logger
                    'level': 'NOTSET',
                    'handlers': ['debug_console_handler', 'info_rotating_file_handler', 'error_file_handler',
                                 'critical_mail_handler'],
                },
                'my.package': {
                    'level': 'WARNING',
                    'propagate': False,
                    'handlers': ['info_rotating_file_handler', 'error_file_handler'],
                },
            },
            'handlers': {
                'debug_console_handler': {
                    'level': 'DEBUG',
                    'formatter': 'info',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                },
                'info_rotating_file_handler': {
                    'level': 'INFO',
                    'formatter': 'info',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'Logs/info.log',
                    'mode': 'a',
                    'maxBytes': 1048576,
                    'backupCount': 10
                },
                'error_file_handler': {
                    'level': 'WARNING',
                    'formatter': 'error',
                    'class': 'logging.FileHandler',
                    'filename': 'Logs/error.log',
                    'mode': 'a',
                },
                'critical_mail_handler': {
                    'level': 'CRITICAL',
                    'formatter': 'error',
                    'class': 'logging.handlers.SMTPHandler',
                    'mailhost': 'localhost',
                    'fromaddr': 'monitoring@domain.com',
                    'toaddrs': ['dev@domain.com', 'qa@domain.com'],
                    'subject': 'Critical error with application name'
                }
            },
            'formatters': {
                'info': {
                    'format': '%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s'
                },
                'error': {
                    'format': '%(asctime)s-%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s'
                },
            },

        }

        logging.config.dictConfig(config=LOGGING_CONFIG)

    def shutdown_app(self, argv, return_code):
        """
        Shut-downs the rest server app
        """
        if (return_code == -1) and argv and (argv[0] == 'restserver') and (argv[1] == 'start'):
            self.stop_rest_server(True)

    def start_rest_server(self, force_start=False):
        """
        Starts the rest server
        """
        if not self._rest_server:
            self.LOG.info('Initializing Rest Server')
            self._rest_server = RestServer.get_instance(self._rest_server_working_folder_path)
            self.LOG.info('Initialized Rest Server')
        self.LOG.info('Starting rest server')
        self._rest_server.start_rest_server(force_start=force_start)

    def stop_rest_server(self, ignore_stop_failure=False):
        """
        Stops the rest server
        """
        self.LOG.info('Stopping rest server')
        if self._rest_server:
            try:
                self._rest_server.stop_rest_server(ignore_stop_failure)
            except Exception as e:
                self.LOG.error('Cannot shutdown Rest Server. Details -- %s' % str(e))
                if not ignore_stop_failure:
                    raise e

    def get_rest_server_network_config(self):
        """
        Gets the rest server network configuration and returns (host, port) as a tuple
        """
        network_host = self._rest_server.get_rest_server_host()
        network_port = self._rest_server.get_rest_server_port()
        return network_host, network_port

    def set_rest_server_network_config(self, host, port):
        """
        Sets the rest server network configuration with specified host and port
        """
        self._rest_server.set_rest_server_host(host)
        self._rest_server.set_rest_server_port(port)

    def show_rest_api_spec(self):
        """
        Shows the API spec in a browser
        """
        self._rest_server.show_rest_api_spec()

    def set_rest_url_prefix(self, url_prefix):
        """
        Set the rest server's url prefix details as per the argument
        """
        return ''

    def get_rest_url_prefix(self):
        """
        Get the rest server's url prefix details
        """
        return ''

    def get_rest_server_wsgi_app(self):
        """
        Get the rest server's wsgi app instance
        """
        return self._rest_server.get_rest_server_wsgi_app()

    def register_rest_server_as_service(self):
        """
        Register the rest server service
        """
        self.LOG.info('Registering TestExecutor rest server from supervisor service')
        if self._rest_server:
            self._rest_server.register_as_service()

    def deregister_rest_server_as_service(self):
        """
        Deregister the rest server service
        """
        self.LOG.info('De-registering TestExecutor rest server from supervisor service')
        if self._rest_server:
            self._rest_server.deregister_as_service()

    # Sample Command
    def get_version(self):
        """
        App implementation of get_version command.
        :return: version string of the current application
        """
        value = self._pdu_manager.get_version()
        self.LOG.info('Version of PduLibrary  : %s' % value)
        return value

    def _get_object(self, class_name, *args, **kwargs):
        """
        resolves the class name to a class object and returns a class object
        """
        self.LOG.debug('Resolving class information using name  [%s]' % class_name)
        return_object = None
        _class = None
        if class_name in globals():
            _type = globals()[class_name]
            if isclass(_type):
                _class = _type
            elif ismodule(_type):
                _class = getattr(_type, class_name)
            return_object = _class(*args, *kwargs)

        return return_object

def main():
    """
    Main method for the Test Executor App
    :return: exit code of the application
    """
    argv = sys.argv[1:]
    datetime.strptime('2021-06-28', '%Y-%m-%d')
    uth_test_executor_app = PduLibraryApp(argv)

    try:
        return_code = uth_test_executor_app.run(argv)
        uth_test_executor_app.shutdown_app(argv, return_code)
        return return_code
    except (KeyboardInterrupt, SystemExit):
        return_code = -1
        uth_test_executor_app.shutdown_app(argv, return_code)
        return 0


if __name__ == '__main__':
    returnCode = main()
    exit(returnCode)
