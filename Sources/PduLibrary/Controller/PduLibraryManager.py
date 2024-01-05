import datetime

from PduLibrary import __version__
from PduLibrary.Common.BaseObject import BaseObject
from PduLibrary.Common.Singleton import Singleton
from PduLibrary.PDUManager.ApcLibraryManager import ApcLibraryManager
from PduLibrary.PDUManager.DliLibraryManager import DliLibraryManager
from PduLibrary.PDUManager.RaritanLibraryManager import RaritanLibraryManager
from PduLibrary.PDUManager.AtenLibraryManager import AtenLibraryManager


class PduLibraryManager(BaseObject, Singleton):

    def Factory(self, manufacturer="raritan"):
        """Factory Method to instantiate the object of actual library manager
        @param manufacturer: The manufacturer in lowercase
        @return: The object of the actual library manager which serves the request
        """
        pdu_managers = {
            "raritan": RaritanLibraryManager(),
            "dli": DliLibraryManager(),
            "apc": ApcLibraryManager(),
            "aten": AtenLibraryManager()
        }
        return pdu_managers[manufacturer]

    def __init__(self):
        """
        Initializes the class
        """
        BaseObject.__init__(self)
        self._working_folder_path = '.'

    def get_version(self):
        """
        Gets the version of Common IP PDU Library
        @return: Version of Common IP PDU Library
        """
        self._Logger.info('Getting version information from %s-%s' % ('PduLibrary', __version__))
        return 'PduLibrary:' + __version__

    def get_pdu_info(self, manufacturer, ip, username, password):
        """
        Gets PDU Information
        @param manufacturer: The manufacturer - Raritan/APC/DLI/Aten
        @param ip: IP of PDU
        @param username: Username of PDU
        @param password: Password of PDU
        @return: The PDU information
        """
        self._Logger.info('Getting PDU Metadata information from %s' % ip)
        output = dict()
        output['manufacturer'] = ''
        output['model'] = ''
        output['serialNumber'] = ''
        output['ctrlBoardSerial'] = ''
        output['fwRevision'] = ''
        output['macAddress'] = ''
        output['voltage'] = ''
        output['current'] = ''
        output['frequency'] = ''
        output['power'] = ''
        output['outlets'] = []
        '''
        '{
        "manufacturer": "<manufacturer name>",
        "model": "<model name>",
        "serialNumber": "<serial number>",
        "ctrlBoardSerial": "<control board serial number>",
        "fwRevision": "<fw version>",
        "macAddres": "<mac address>",
        "voltage": "<voltage>",
        "current": "<current",
        "frequency": "<frequency>",
        "power": "<power>",
        "outlets": [{
            "portNumber": "<port number>",
            "portName": "<port name>",
            "portStatus": "<port status>"
        }]
        }
        '''
        return self.Factory(manufacturer.lower()).get_pdu_info(ip, username, password, output)

    def get_port_info(self, manufacturer, ip, username, password, port):
        """
        Gets Port/Outlet Information
        @param manufacturer: The manufacturer - Raritan/APC/DLI/Aten
        @param ip: IP of PDU
        @param username: Username of PDU
        @param password: Password of PDU
        @param port: Port/Outlet Number
        @return: The Port/Outlet information
        """
        self._Logger.info('Getting Port Metadata information from %s for port %s' % (ip, port))
        output = dict()
        output['portNumber'] = port
        output['receptacleType'] = ''
        output['current'] = ''
        output['minVoltage'] = ''
        output['maxVoltage'] = ''
        output['sensorData'] = {
            'voltage': '',
            'current': '',
            'activeEnergy': '',
            'lineFrequency': ''
        }
        output['stateData'] = {
            'available': None,
            'powerState': '',
            'lastPowerStateChangeTime': ''
        }
        '''
        {
            "portNumber”: "<port number>",
            "receptacleType": "<plug type>",
            "current": "<current>",
            "minVoltage: "<min voltage>",
            "maxVoltage": "<max voltage>",
            "sensorData": {
                "voltage": "<voltage>",
                "current": "<current>",
                "activeEnergy": "<activeEnergy>",
                "lineFrequency": "<lineFrequency>"
            },
            "stateData": {
                "available”: "<boolean>",
                "powerState": "<powerstate>"
                “lastPowerStateChangeTime": "<date-time>"
            }
        }
        '''
        return self.Factory(manufacturer.lower()).get_port_info(ip, username, password, port, output)

    def power_on(self, manufacturer, ip, username, password, port):
        """
        Power ON the outlet
        @param manufacturer: The manufacturer - Raritan/APC/DLI/Aten
        @param ip: IP of PDU
        @param username: Username of PDU
        @param password: Password of PDU
        @param port: Port/Outlet Number
        @return: The Status of Power ON request
        """
        self._Logger.info('Powering ON in PDU %s for Port %s' % (ip, port))
        output = dict()
        output['powerState'] = 'ON'
        output['lastPowerStateChangeTime'] = str(datetime.datetime.now())
        return self.Factory(manufacturer.lower()).power_on(ip, username, password, port, output)

    def power_off(self, manufacturer, ip, username, password, port):
        """
        Power Off the outlet
        @param manufacturer: The manufacturer - Raritan/APC/DLI/Aten
        @param ip: IP of PDU
        @param username: Username of PDU
        @param password: Password of PDU
        @param port: Port/Outlet Number
        @return: The Status of Power Off request
        """
        self._Logger.info('Powering Off in PDU %s for Port %s' % (ip, port))
        output = dict()
        output['powerState'] = 'OFF'
        output['lastPowerStateChangeTime'] = str(datetime.datetime.now())
        return self.Factory(manufacturer.lower()).power_off(ip, username, password, port, output)

    def reboot(self, manufacturer, ip, username, password, port):
        """
        Reboots the outlet
        @param manufacturer: The manufacturer - Raritan/APC/DLI/Aten
        @param ip: IP of PDU
        @param username: Username of PDU
        @param password: Password of PDU
        @param port: Port/Outlet Number
        @return: The Status of Reboot request
        """
        self._Logger.info('Rebooting PDU %s for Port %s' % (ip, port))
        output = dict()
        output['powerState'] = 'ON'
        output['lastPowerStateChangeTime'] = str(datetime.datetime.now())
        return self.Factory(manufacturer.lower()).reboot(ip, username, password, port, output)
