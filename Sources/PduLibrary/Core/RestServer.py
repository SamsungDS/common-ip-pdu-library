import os
import socket
import webbrowser
from time import sleep

import requests
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_restful_swagger import swagger
from gevent.pywsgi import WSGIServer
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from PduLibrary.Common.BaseObject import BaseObject
from PduLibrary.Common.Singleton import Singleton
from PduLibrary.Errors.ErrorCodes import *
from PduLibrary.Exception.PduLibraryException import PduLibraryException
from PduLibrary.RestResource.GetPduInfo import GetPduInfo
from PduLibrary.RestResource.GetPortInfo import GetPortInfo
from PduLibrary.RestResource.GetVersion import GetVersion
from PduLibrary.RestResource.PowerOff import PowerOff
from PduLibrary.RestResource.PowerOn import PowerOn
from PduLibrary.RestResource.Reboot import Reboot


class RestServer(BaseObject, Singleton):
    """
    Rest Server Main implementation
    """
    default_hostname = '0.0.0'
    default_port = '3586'
    default_rest_server_shutdown_timeout_in_secs = '120'

    rest_server_supervisor_conf_program_name = 'uth_testexecutor_REST_SERVER_%s'
    rest_server_state_file_name = '.restserverstate'

    url_shutdown_rest_server = '/v1/shutdownserver'
    url_rest_api_spec = '/v1/spec'
    url_swagger_docs = '/docs'

    url_service_logs = '/servicelogs'

    def __init__(self, rest_server_working_folder_path=None):
        BaseObject.__init__(self)
        self._rest_server_working_folder_path = None
        if rest_server_working_folder_path is None:
            self._rest_server_working_folder_path = os.getcwd()
        else:
            self._rest_server_working_folder_path = rest_server_working_folder_path

        if not os.path.exists(self._rest_server_working_folder_path):
            try:
                os.makedirs(self._rest_server_working_folder_path)
            except Exception as ex:
                self._Logger.error('Cannot Create working folder path for rest server. Details :%s' % str(ex))
                raise PduLibraryException(REST_SERVER_WORKING_FOLDER_CREATE_FAILURE, str(ex))

        self._rest_server_state_file_path = os.path.join(self._rest_server_working_folder_path,
                                                         RestServer.rest_server_state_file_name)

        self._rest_app = None
        self._rest_api_v1 = None

        shutdowntimeout = 60
        if not shutdowntimeout:
            shutdowntimeout = RestServer.default_rest_server_shutdown_timeout_in_secs

        self._rest_server_shutdown_timeout_in_secs = int(shutdowntimeout)

        self._rest_server_url_prefix = ''

    def _check_rest_server_status(self):
        """
        Checks if the rest service is running or not
        """
        return os.path.exists(self._rest_server_state_file_path)

    def _create_rest_server_state_file(self):
        """
        Creates a file to show rest server status
        """
        self.touch_file(self._rest_server_state_file_path)

    def _delete_rest_server_state_file(self):
        """
        Deletes a file to show rest server status (i.e. rest server is not running)
        """
        if os.path.exists(self._rest_server_state_file_path):
            self._Logger.info('Removing Rest Server State File Path')
            os.remove(self._rest_server_state_file_path)
            self._Logger.info('Removed Rest Server State File Path')

    def get_rest_server_wsgi_app(self):
        """
        Returns WSGI app instance, if the instance is not available, it will create the instance
        """
        if not self._rest_app:
            self._prepare_rest_server()

        return self._rest_app

    def _prepare_rest_server(self):
        """
        Prepares the Flask / WSGI App instance
        """
        self._rest_app = Flask(__name__)

        if self._rest_server_url_prefix:
            self._rest_app.config['APPLICATION_ROOT'] = self._rest_server_url_prefix
            self._rest_app.wsgi_app = DispatcherMiddleware(
                Flask('DummyRootApp'),
                {self._rest_server_url_prefix: self._rest_app.wsgi_app}
            )

        self._Logger.info("Attaching swagger doc support")
        self._rest_api_v1 = swagger.docs(Api(self._rest_app), apiVersion='0.1', api_spec_url=self.url_rest_api_spec)

        self._Logger.info("Providing support for Cross Origin Resource Sharing")
        CORS(self._rest_app)

        # Adding Rest resources to Flask
        self._register_resources_v1()

    def start_rest_server(self, debug_mode=False, force_start=False, **server_options):
        """
        Starts the rest server
        """
        self._prepare_rest_server()

        rest_server_host = self.get_rest_server_host()
        rest_server_port = self.get_rest_server_port()

        '''
        if self._check_rest_server_status():
            raise PduLibraryException(REST_SERVER_ALREADY_RUNNING)
        '''

        self._create_rest_server_state_file()

        self._Logger.info('Launching TestExecutor Rest Server. Details :')
        self._Logger.info('     Host : %s' % rest_server_host)
        self._Logger.info('     Port : %s' % rest_server_port)
        self._Logger.info('     Debug Mode : %s' % debug_mode)
        self._Logger.info('     Server Options : %s' % server_options)
        self._Logger.info('     Force Start : %s' % force_start)

        try:
            self._server_object = WSGIServer((rest_server_host, rest_server_port), self._rest_app)

            self._rest_app.run(rest_server_host, rest_server_port)

            self._Logger.info('Server shutdown')
            self._delete_rest_server_state_file()
        except Exception as ex:
            self._Logger.debug('Error while starting rest server. Details : %s' % str(ex))
            self._delete_rest_server_state_file()
            raise PduLibraryException(ERROR_WHILE_STARTING_REST_SERVER, str(ex))

    def _get_rest_server_url(self):
        """
        Gets the Rest server URL
        """
        host = self.get_rest_server_host()
        port = self.get_rest_server_port()

        if host == self.default_hostname:
            host = '127.0.0.1'

        return 'http://%s:%s' % (host, port)

    def get_rest_server_host(self):
        """
        Gets the Rest server host
        """
        host_from_config = '0.0.0.0'
        if not host_from_config:
            host_from_config = self.default_hostname

        return host_from_config

    def get_rest_server_port(self):
        """
        Gets the Rest server port
        """
        port_from_config = '3489'
        if not port_from_config:
            port_from_config = self.default_port

        return int(port_from_config)

    def _get_local_ip(self):
        """
        Get Local IP Address using socket
        """
        try:
            ip_address = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in
                          [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        except socket.gaierror as ex:
            self._Logger.info('Error while getting local ip. Details: %s' % str(ex))
            ip_address = self.get_rest_server_host()
        except socket.error as ex:
            self._Logger.info('Error while getting local ip. Details: %s' % str(ex))
            ip_address = self.get_rest_server_host()
        return ip_address

    def stop_rest_server(self, ignore_stop_failure):
        """
        Stops the running Rest Server
        """
        if not self._check_rest_server_status():
            if not ignore_stop_failure:
                raise PduLibraryException(REST_SERVER_NOT_RUNNING)
            else:
                return
        rest_server_url = self._get_rest_server_url()
        timeout = False

        if self._server_object:
            self._server_object.stop()
            self._delete_rest_server_state_file()
        else:
            shutdown_url = '%s%s' % (rest_server_url, self.url_shutdown_rest_server)
            try:
                requests.post(shutdown_url)
                self._Logger.info('Posted a shutdown request')
            except Exception as ex:
                if not ignore_stop_failure:
                    self._Logger.info('Error while posting shutdown request. Details: %s' % str(ex))
                    raise PduLibraryException(REST_SERVER_SHUTDOWN_REQUEST_FAILED, str(ex))
                else:
                    self._Logger.warning('Ignoring failure to stop Rest Server')
                    self._delete_rest_server_state_file()
                    return
            self._Logger.debug(
                'Proceeding to wait for request to be completed for %s minutes' %
                self._rest_server_shutdown_timeout_in_secs)
            time_waited = 0
            while os.path.exists(self._rest_server_state_file_path):
                sleep(1)
                time_waited += 1
                if time_waited > self._rest_server_shutdown_timeout_in_secs:
                    timeout = True
                    break

            if not timeout:
                self._Logger.info('Rest server shutdown complete')
            else:
                if not ignore_stop_failure:
                    raise PduLibraryException(REST_SERVER_SHUTDOWN_REQUEST_TIMEDOUT)
                else:
                    self._Logger.warning('Ignoring failure to stop Rest Server')
                    self._delete_rest_server_state_file()
            return

    def show_api_spec(self):
        """
        Shows API Specification in browser
        """
        if self._check_rest_server_status():
            api_spec_url = self._get_rest_server_url() + RestServer.url_rest_api_spec + '.html'
            webbrowser.open_new_tab(api_spec_url)
        else:
            raise PduLibraryException(REST_SERVER_NOT_RUNNING)

    def touch_file(self, file_path, times=None):
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

    def _register_resources_v1(self):
        """
        Register the REST APIs that needs to be exposed
        :return: None
        """
        # RestResource Endpoints
        self._rest_api_v1.add_resource(GetVersion, '/v1/get_version')
        self._rest_api_v1.add_resource(GetPduInfo, '/v1/get_pdu_info')
        self._rest_api_v1.add_resource(GetPortInfo, '/v1/get_port_info')
        self._rest_api_v1.add_resource(PowerOn, '/v1/power_on')
        self._rest_api_v1.add_resource(PowerOff, '/v1/power_off')
        self._rest_api_v1.add_resource(Reboot, '/v1/reboot')
