import traceback
from abc import ABC

import dlipower

from PduLibrary.Common.BaseObject import BaseObject
from PduLibrary.Errors.ErrorCodes import ERROR_WHILE_FETCHING_PDU_INFO, ERROR_WHILE_FETCHING_PORT_INFO,\
    ERROR_WHILE_POWERING_ON_PORT, ERROR_WHILE_POWERING_OFF_PORT, ERROR_WHILE_REBOOTING_PORT
from PduLibrary.Exception.PduLibraryException import PduLibraryException


class DliLibraryManager(BaseObject, ABC):

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
        try:
            switch = dlipower.PowerSwitch(hostname=ip, userid=username, password=password)
            output['manufacturer'] = 'DLI'
            output['outlets'] = []
            for outlet in switch.statuslist():
                output['outlets'].append({
                    "portNumber": outlet[0],
                    "portName": outlet[1],
                    "portStatus": outlet[2]
                })
        except Exception as err:
            self._Logger.error('Error while getting pdu info :: ' + str(err))
            self._Logger.error(traceback.print_exc())
            raise PduLibraryException(ERROR_WHILE_FETCHING_PDU_INFO, str(err))
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
        try:
            switch = dlipower.PowerSwitch(hostname=ip, userid=username, password=password)
            output['stateData'] = {
                'available': True,
                'powerState': switch.status(port),
                'lastPowerStateChangeTime': ''
            }
        except Exception as err:
            self._Logger.error('Error while getting pdu info :: ' + str(err))
            self._Logger.error(traceback.print_exc())
            raise PduLibraryException(ERROR_WHILE_FETCHING_PORT_INFO, str(err))
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
            switch = dlipower.PowerSwitch(hostname=ip, userid=username, password=password)
            # https://dlipower.readthedocs.io/en/latest/dlipower_module.html#dlipower.PowerSwitch.on
            # Turn on power to an outlet
            # False = Success
            # True = Fail
            status = switch.on(port)
            # status will be True if the operation is success else False
            self._Logger.info(f'Status of Power ON in DLI :: {status}')
            if status:
                self._Logger.info('Powered ON Failed - Port :: ' + str(port) + ' in PDU :: ' + str(ip))
                output['powerState'] = 'OFF'
            else:
                self._Logger.info('Powered ON Successful - Port :: ' + str(port) + ' in PDU :: ' + str(ip))
                output['powerState'] = 'ON'
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
            switch = dlipower.PowerSwitch(hostname=ip, userid=username, password=password)
            # https://dlipower.readthedocs.io/en/latest/dlipower_module.html#dlipower.PowerSwitch.off
            # Turn off a power to an outlet
            # False = Success
            # True = Fail
            status = switch.off(port)
            # status will be True if the operation is success else False
            self._Logger.info(f'Status of Power Off in DLI :: {status}')
            if status:
                output['powerState'] = 'ON'
                self._Logger.info('Powered Off Failed - Port :: ' + str(port) + ' in PDU :: ' + str(ip))
            else:
                output['powerState'] = 'OFF'
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
            switch = dlipower.PowerSwitch(hostname=ip, userid=username, password=password)
            # https://dlipower.readthedocs.io/en/latest/dlipower_module.html#dlipower.PowerSwitch.cycle
            # Cycle power to an outlet
            # False = Power off Success
            # True = Power off Fail
            # Note, does not return any status info about the power on part of the operation by design
            status = switch.cycle(port)
            # Status will be True if the operation is success else False
            self._Logger.info(f'Status of Reboot in DLI :: {status}')
            if status:
                self._Logger.info('Reboot Failed - Port :: ' + str(port) + ' in PDU :: ' + str(ip))
                output['powerState'] = 'OFF'
            else:
                self._Logger.info('Reboot Successful - Port :: ' + str(port) + ' in PDU :: ' + str(ip))
                output['powerState'] = 'ON'
        except Exception as err:
            self._Logger.error('Error while Rebooting Port :: ' + str(port)
                               + ' in PDU :: ' + str(ip)
                               + ' Error :: ' + str(err))
            self._Logger.error(traceback.print_exc())
            raise PduLibraryException(ERROR_WHILE_REBOOTING_PORT, str(err))
        return output
