from abc import ABC

from PduLibrary.Common.BaseObject import BaseObject


class AtenLibraryManager(BaseObject, ABC):

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
        output['manufacturer'] = 'Aten'
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
        return output
