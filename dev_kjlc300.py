# -*- coding: utf-8 -*-
"""
Driver for the Kurt J. Lesker KJLC 300 series convection-enhanced Pirani
vacuum gauge module.

The KJLC 300 provides a Pirani/convection vacuum gauge with an integrated
controller and display. This driver reads the pressure through the gauge's
ASCII serial command protocol over the RS-485 interface. The pressure is read
with the RD command and returned in units of Torr.

The gauge address used in serial commands is configured as InternalAddress
in DeviceSpecificParams. The KJLC 300 manual describes device addresses as
hexadecimal values from 00 through FF, with a factory default address of 01.
Because commands are sent as #<InternalAddress><command>\\r, the configured
address should include any required leading zero, for example "01".

The manual lists the factory-default serial settings as 19200 baud, 8 data
bits, no parity, and 1 stop bit. Commands sent to the gauge begin with #,
responses from the gauge begin with *, and each command is terminated with a
carriage return.

For the 15-pin D-sub connector, the RS-485 pin assignment is:
DATA B / RS-485 (+) on pin 1,
DATA A / RS-485 (-) on pin 2,
power ground on pin 4.

This pin assignment may differ from that of the RS-485 adapter being used, so
a custom cable may be required.
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
        internal_address = self.device["DeviceSpecificParams"]["InternalAddress"]
        query = f'#{internal_address}{command}\r'.encode(encoding="ASCII")
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
        if rsp.startswith("?"):
            raise LoggerError(
                f"Received an error response: '{rsp}'")
        if not rsp.startswith(f"*{internal_address} "):
            raise LoggerError(
                f"Didn't receive correct acknowledgement (response received: '{rsp}')")
        return rsp[4:]

    def read_pressure(self):
        """Read pressure."""
        rsp = self.query("RD")
        return float(rsp)

    def get_values(self):
        """Read channels."""
        chans = self.device['Channels']
        readings = {}
        for channel_id, chan in chans.items():
            if chan['Type'] in ['Pressure']:
                value = self.read_pressure()
                readings[channel_id] = value
            else:
                raise LoggerError(
                    f'Unknown channel type \'{chan["Type"]}\' for channel \'{channel_id}\''
                    +f' of device \'{self.device["Device"]}\'')
        return readings
