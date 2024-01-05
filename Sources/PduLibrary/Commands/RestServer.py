import logging
from argparse import ArgumentError
from PduLibrary.Common.Command import Command


def validate_url_prefix(value):
    """
    validates the give url prefix and returns the updated url prefix
    """
    if value:
        if not value.startswith('/'):
            raise ArgumentError(message='URL Prefix must start with a /', argument=value)

        value = value.rstrip('/')

    return value


class RestServer(Command):
    """
    Launching the rest server to support with scripts/commandline
    """
    LOG = logging.getLogger(__name__)

    def get_parser(self, program_name):
        """
        Command line argument definition for the rest server command line
        :param program_name:sub command of the rest server
                            supported commands for controlling rest server
                            start / stop / restart
                            showapispec
                            getnwcfg
                            geturlprefix
                            service
        """
        parser = super(RestServer, self).get_parser(program_name)

        subparser = parser.add_subparsers(
            title='Rest Server Commands',
            description='Commands to deal with builtin rest server',
            help='Rest Server command details',
            dest='rest_server_command',
            metavar='{rest_server_command}'
        )
        subparser.add_parser('start', help='Starts a Rest server')
        subparser.add_parser('stop', help='Stops a running Rest server')
        subparser.add_parser('restart', help='Restarts Rest server')

        subparser.add_parser('showapispec', help='Launches Rest server API Spec in a browser')

        subparser.add_parser('getnwcfg', help='Get Rest server network configurations')
        subparser.add_parser('geturlprefix', help='Gets URL Prefix of running Rest server')

        service_subparser = subparser.add_parser('service', help='Managing the Rest server service')
        service_command_group = service_subparser.add_mutually_exclusive_group()
        service_command_group.add_argument(
            '-r',
            '--register',
            action='store_true',
            help='Registers a Rest server as a supervisor service',
            required=False,
            dest='register_rest_server_as_service'
        )
        service_command_group.add_argument(
            '-d',
            '--deregister',
            action='store_true',
            help='Deregisters a Rest server as a supervisor service',
            required=False,
            dest='deregister_rest_server_as_service'
        )

        server_config_subparser = subparser.add_parser('setnwcfg',
                                                       help='Managing the Rest server network configuration')
        server_config_subparser.add_argument(
            '-u',
            '--host',
            action='store',
            help='Rest server host IP',
            required=True,
            dest='rest_server_host'
        )
        server_config_subparser.add_argument(
            '-p',
            '--port',
            action='store',
            help='Rest server port',
            required=True,
            dest='rest_server_port'
        )

        server_config_subparser = subparser.add_parser('seturlprefix', help='Managing the Rest server URL Prefix')
        server_config_subparser.add_argument(
            '-p',
            '--urlprefix',
            action='store',
            help='Sets the URL prefix for Rest Server',
            required=True,
            dest='rest_server_url_prefix',
            type=validate_url_prefix
        )

        return parser

    def take_action(self, parsed_arguments):
        """
        Command's main action definition
        This will be triggered when version command-line is executed
        :param parsed_arguments: command line arguments
        :return: None
        """
        if parsed_arguments.rest_server_command == 'stop':
            self.app.stop_rest_server()
            return True

        if parsed_arguments.rest_server_command == 'start':
            self.app.start_rest_server()
            return True

        if parsed_arguments.rest_server_command == 'restart':
            self.app.stop_rest_server(True)
            self.app.start_rest_server(True)
            return True

        if parsed_arguments.rest_server_command == 'getnwcfg':
            (network_host, network_port) = self.app.get_rest_server_network_config()

            self.LOG.info('Host : %s' % network_host)
            self.LOG.info('Port : %s' % network_port)

        if parsed_arguments.rest_server_command == 'setnwcfg':
            self.app.set_rest_server_network_config(parsed_arguments.rest_server_host,
                                                    parsed_arguments.rest_server_port)

            self.LOG.info('Setting network configuration')
            self.LOG.info('Host : %s' % parsed_arguments.rest_server_host)
            self.LOG.info('Port : %s' % parsed_arguments.rest_server_port)
            self.LOG.info('Restart the rest server to reflect this change')

        if parsed_arguments.rest_server_command == 'showapispec':
            self.app.show_rest_api_spec()

        if parsed_arguments.rest_server_command == 'seturlprefix':
            self.app.set_rest_url_prefix(parsed_arguments.rest_server_url_prefix)

            self.LOG.info('Successfully set the url prefix to %s' % parsed_arguments.rest_server_url_prefix)
            self.LOG.info('Restart the rest server to reflect this change')

        if parsed_arguments.rest_server_command == 'geturlprefix':
            _rest_server_url_prefix = self.app.get_rest_url_prefix()

            self.LOG.info('URL Prefix : %s' % _rest_server_url_prefix)

        if parsed_arguments.rest_server_command == 'service':
            if parsed_arguments.register_rest_server_as_service:
                self.app.register_rest_server_as_service()
                self.LOG.info('Registered rest server as a service')
            if parsed_arguments.deregister_rest_server_as_service:
                self.app.deregister_rest_server_as_service()
                self.LOG.info('De-registered rest server from service')
