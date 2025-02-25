# -*- coding: utf-8 -*-
"""
A class to interface with the Lake Shore Model 218 Temperature Monitor via RS-232.

The Lake Shore Model 218 is a high-precision, multi-channel temperature monitor 
designed for cryogenic and non-cryogenic temperature measurements. It supports up 
to eight sensor inputs and can read various sensor types, including silicon diodes, 
platinum RTDs, and thermistors.
"""

import serial
import logging

import dev_generic

from defs import LoggerError

logger = logging.getLogger()

class Device(dev_generic.Device):

    def __init__(self, device):
        """
        Initialize device.

        device : dict
            Configuration dict of the device to initialize.
        """
        super(Device, self).__init__(device)
        try:
            self.connection = serial.Serial(
                device["Address"], timeout=device["Timeout"],
                **device.get('SerialConnectionParams', {}))
        except serial.SerialException:
            raise LoggerError(
                f"Serial connection on port {device['Address']} couldn't be opened")

    def query(self, command):
        """Query device with command `command` (str) and return response."""
        query = f'{command}\r\n'.encode(encoding="ASCII")
        n_write_bytes = self.connection.write(query)
        if n_write_bytes != len(query):
            raise LoggerError("Failed to write to device")
        rsp = self.connection.readline()
        try:
            rsp = rsp.decode(encoding="ASCII")
        except UnicodeDecodeError:
            raise LoggerError(f"Error in decoding response ('{rsp}') received")
        if rsp == '':
            raise LoggerError(
                "No response received")
        return rsp[4:]

    def read_temperature(self, chan):
        """Read temperature."""
        # Read pressure
        rsp = self.query(f"KRDG? {chan}")
        return float(rsp)

    def get_values(self):
        """Read channels."""
        chans = self.device['Channels']
        readings = {}
        for channel_id, chan in chans.items():
            if chan['Type'] in ['Temperature']:
                value = self.read_temperature(chan[''])
                readings[channel_id] = value
            else:
                raise LoggerError(
                    f'Unknown channel type \'{chan["Type"]}\' for channel \'{channel_id}\''
                    +f' of device \'{self.device["Device"]}\'')
        return readings
