import time
import traceback
from abc import ABC

from PduLibrary.Errors.ErrorCodes import ERROR_WHILE_FETCHING_PDU_INFO, ERROR_WHILE_FETCHING_PORT_INFO, \
    ERROR_WHILE_POWERING_ON_PORT, ERROR_WHILE_POWERING_OFF_PORT, ERROR_WHILE_REBOOTING_PORT
from PduLibrary.Exception.PduLibraryException import PduLibraryException
from raritan import rpc
from raritan.rpc import pdumodel

from PduLibrary.Common.BaseObject import BaseObject


class RaritanLibraryManager(BaseObject, ABC):

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
            agent = rpc.Agent("https", ip, username, password)
            pdu = pdumodel.Pdu("/model/pdu/0", agent)
            metadata = pdu.getMetaData()
            outlets = pdu.getOutlets()
            output['manufacturer'] = metadata.nameplate.manufacturer
            output['model'] = metadata.nameplate.model
            output['serialNumber'] = metadata.nameplate.serialNumber
            output['ctrlBoardSerial'] = metadata.ctrlBoardSerial
            output['fwRevision'] = metadata.fwRevision
            output['macAddress'] = metadata.macAddress
            output['voltage'] = metadata.nameplate.rating.voltage
            output['current'] = metadata.nameplate.rating.current
            output['frequency'] = metadata.nameplate.rating.frequency
            output['power'] = metadata.nameplate.rating.power
            output['outlets'] = []

            for outlet in outlets:
                outlet_metadata = outlet.getMetaData()
                outlet_state = outlet.getState()
                output['outlets'].append({
                    "portNumber": int(outlet_metadata.label),
                    "portName": 'Outlet ' + outlet_metadata.label
                                if outlet.getSettings().name == ''
                                else outlet.getSettings().name,
                    "portStatus": 'ON' if outlet_state.powerState.val == 1 else 'OFF'
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
            agent = rpc.Agent("https", ip, username, password)
            pdu = pdumodel.Pdu("/model/pdu/0", agent)
            outlet = pdu.getOutlets()[port - 1]
            metadata = outlet.getMetaData()
            output['receptacleType'] = metadata.receptacleType
            output['current'] = metadata.rating.current
            output['minVoltage'] = metadata.rating.minVoltage
            output['maxVoltage'] = metadata.rating.maxVoltage
            output['sensorData'] = {
                'voltage': outlet.getSensors().voltage.getReading().value,
                'current': outlet.getSensors().current.getReading().value,
                'activeEnergy': outlet.getSensors().activeEnergy.getReading().value,
                'lineFrequency': outlet.getSensors().lineFrequency.getReading().value
            }
            output['stateData'] = {
                'available': outlet.getState().available,
                'powerState': 'ON' if outlet.getState().powerState.val == 1 else 'OFF',
                'lastPowerStateChangeTime': str(outlet.getState().lastPowerStateChange)
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
        # agent = rpc.Agent("https", "107.110.49.71", "admin", "siso@123")
        try:
            agent = rpc.Agent("https", ip, username, password)
            pdu = pdumodel.Pdu("/model/pdu/0", agent)
            outlet = pdu.getOutlets()[port - 1]
            outlet.setPowerState(pdumodel.Outlet.PowerState(1))
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
            agent = rpc.Agent("https", ip, username, password)
            pdu = pdumodel.Pdu("/model/pdu/0", agent)
            outlet = pdu.getOutlets()[port - 1]
            outlet.setPowerState(pdumodel.Outlet.PowerState(0))
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
            agent = rpc.Agent("https", ip, username, password)
            pdu = pdumodel.Pdu("/model/pdu/0", agent)
            outlet = pdu.getOutlets()[port - 1]
            outlet.setPowerState(pdumodel.Outlet.PowerState(0))
            time.sleep(2)
            outlet.setPowerState(pdumodel.Outlet.PowerState(1))
            self._Logger.info('Reboot Successful - Port :: ' + str(port) + ' in PDU :: ' + str(ip))
        except Exception as err:
            self._Logger.error('Error while Rebooting Port :: ' + str(port)
                               + ' in PDU :: ' + str(ip)
                               + ' Error :: ' + str(err))
            self._Logger.error(traceback.print_exc())
            raise PduLibraryException(ERROR_WHILE_REBOOTING_PORT, str(err))
        return output

    def get_data_from_meta_data(self, metadata):
        output = dict()
        try:
            for element in metadata.elements:
                element_info = metadata.__getattribute__(element)
                if 'str' in str(type(element_info)) or 'int' in str(type(element_info)) or 'float' in str(
                        type(element_info)) or 'bool' in str(type(element_info)):
                    output[element] = element_info
                elif element_info.__getattribute__('elements'):
                    output[element] = dict()
                    for element_level_2 in element_info.__getattribute__('elements'):
                        element_info_level_2 = element_info.__getattribute__(element_level_2)
                        if 'str' in str(type(element_info_level_2)) \
                                or 'int' in str(type(element_info_level_2)) \
                                or 'float' in str(type(element_info_level_2)) \
                                or 'bool' in str(type(element_info_level_2)):
                            output[element][element_level_2] = element_info_level_2
                        elif element_info_level_2.__getattribute__('elements'):
                            output[element][element_level_2] = dict()
                            for element_level_3 in element_info_level_2.__getattribute__('elements'):
                                try:
                                    output[element][element_level_2][
                                        element_level_3] = element_info_level_2.__getattribute__(element_level_3)
                                except Exception as err:
                                    self._Logger.error('Error while reading 3rd level info :: ' + str(err))
                                    self._Logger.error(traceback.print_exc())
        except Exception as err:
            self._Logger.error('Error while parsing metadata :: ' + str(err))
            self._Logger.error(traceback.print_exc())
        return output

    def get_data_from_sensor_data(self, sensor_data):
        output = dict()
        try:
            for element in sensor_data.elements:
                if element == 'outletState':
                    output[element] = sensor_data.__getattribute__(
                        element).getState().value if sensor_data.__getattribute__(element) else 'NA'
                else:
                    output[element] = sensor_data.__getattribute__(
                        element).getReading().value if sensor_data.__getattribute__(element) else 'NA'
        except Exception as err:
            self._Logger.error('Error while parsing sensor_data :: ' + str(err))
            self._Logger.error(traceback.print_exc())
        return output

    def get_data_from_state_data(self, state_data):
        output = dict()
        try:
            for element in state_data.elements:
                element_info = state_data.__getattribute__(element)
                if 'str' in str(type(element_info)) or 'int' in str(type(element_info)) or 'float' in str(
                        type(element_info)) or 'bool' in str(type(element_info)):
                    output[element] = element_info
                elif 'LedState' in str(type(element_info)):
                    output['ledState'] = dict()
                    for element_info_level_2 in element_info.__getattribute__('elements'):
                        output['ledState'][element_info_level_2] = element_info.__getattribute__(element_info_level_2)
                else:
                    output[element] = str(element_info) if element_info else ''
        except Exception as err:
            self._Logger.error('Error while parsing state data :: ' + str(err))
            self._Logger.error(traceback.print_exc())
        return output
