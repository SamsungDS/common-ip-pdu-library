import telnetlib
import traceback
from abc import ABC

from PduLibrary.Common.BaseObject import BaseObject
from PduLibrary.Errors.ErrorCodes import ERROR_WHILE_POWERING_ON_PORT, ERROR_WHILE_POWERING_OFF_PORT,\
    ERROR_WHILE_REBOOTING_PORT
from PduLibrary.Exception.PduLibraryException import PduLibraryException


class ApcLibraryManager(BaseObject, ABC):

    def __init__(self):
        BaseObject.__init__(self)

    def get_pdu_info(self, ip, username, password, output):
        """
        Gets PDU Information
        @param ip: IP of PDU
        @param username: Username of PDU
        @param password: Password of PDU
        @param output: The default output
        @return: The PDU information
        """
        output['manufacturer'] = 'APC'
        return output

    def get_port_info(self, ip, username, password, port, output):
        """
        Gets Port/Outlet Information
        @param ip: IP of PDU
        @param username: Username of PDU
        @param password: Password of PDU
        @param port: Port/Outlet Number
        @param output: The default output
        @return: The Port/Outlet information
        """
        return output

    def power_on(self, ip, username, password, port, output):
        """
        Power On the port/outlet
        @param ip: PDU IP
        @param username: PDU Username
        @param password: PDU password
        @param port: Port/Outlet number
        @param output: The default output
        @return: Status of Power On request
        """
        try:
            telnet_session = telnetlib.Telnet(host=ip)
            telnet_session.read_until(b"User Name :")
            telnet_session.write(bytes(f"{username}\r\n", 'utf-8'))
            telnet_session.read_until(b"Password  :")
            telnet_session.write(bytes(f"{password}\r\n", 'utf-8'))
            telnet_session.read_until(b"Use tcpip command")
            command = bytes(f"olOn {port}\r\n", 'utf-8')
            telnet_session.write(command)
            telnet_session.read_until(b"E000: Success")
            self._Logger.info('Powered ON Successful - Port :: ' + str(port) + ' in PDU :: ' + str(ip))
        except Exception as err:
            self._Logger.error('Error while Powering ON Port :: ' + str(port)
                               + ' in PDU :: ' + str(ip)
                               + ' Error :: ' + str(err))
            self._Logger.error(traceback.print_exc())
            raise PduLibraryException(ERROR_WHILE_POWERING_ON_PORT, str(err))
        return output

    def power_off(self, ip, username, password, port, output):
        """
        Power Off the port/outlet
        @param ip: PDU IP
        @param username: PDU Username
        @param password: PDU password
        @param port: Port/Outlet number
        @param output: The default output
        @return: Status of Power Off request
        """
        try:
            telnet_session = telnetlib.Telnet(host=ip)
            telnet_session.read_until(b"User Name :")
            telnet_session.write(bytes(f"{username}\r\n", 'utf-8'))
            telnet_session.read_until(b"Password  :")
            telnet_session.write(bytes(f"{password}\r\n", 'utf-8'))
            telnet_session.read_until(b"Use tcpip command")
            command = bytes(f"olOff {port}\r\n", 'utf-8')
            telnet_session.write(command)
            telnet_session.read_until(b"E000: Success")
            self._Logger.info('Powered Off Successful - Port :: ' + str(port) + ' in PDU :: ' + str(ip))
        except Exception as err:
            self._Logger.error('Error while Powering Off Port :: ' + str(port)
                               + ' in PDU :: ' + str(ip)
                               + ' Error :: ' + str(err))
            self._Logger.error(traceback.print_exc())
            raise PduLibraryException(ERROR_WHILE_POWERING_OFF_PORT, str(err))
        return output

    def reboot(self, ip, username, password, port, output):
        """
        Reboots the port/outlet
        @param ip: PDU IP
        @param username: PDU Username
        @param password: PDU password
        @param port: Port/Outlet number
        @param output: The default output
        @return: Status of Reboot request
        """
        try:
            telnet_session = telnetlib.Telnet(host=ip)
            telnet_session.read_until(b"User Name :")
            telnet_session.write(bytes(f"{username}\r\n", 'utf-8'))
            telnet_session.read_until(b"Password  :")
            telnet_session.write(bytes(f"{password}\r\n", 'utf-8'))
            telnet_session.read_until(b"Use tcpip command")
            command = bytes(f"olReboot {port}\r\n", 'utf-8')
            telnet_session.write(command)
            telnet_session.read_until(b"E000: Success")
            self._Logger.info('Reboot Successful - Port :: ' + str(port) + ' in PDU :: ' + str(ip))
        except Exception as err:
            self._Logger.error('Error while Rebooting Port :: ' + str(port)
                               + ' in PDU :: ' + str(ip)
                               + ' Error :: ' + str(err))
            self._Logger.error(traceback.print_exc())
            raise PduLibraryException(ERROR_WHILE_REBOOTING_PORT, str(err))
        return output
