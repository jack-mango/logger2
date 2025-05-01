import labjack.ljm
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
            self.handle = labjack.ljm.openS("ANY", "ANY", device["Serial Number"])
        except labjack.ljm.LJMError as e:
            raise LoggerError(
                f"Connection to LabJack with serial number {device['Serial Number']} couldn't be opened")

    def read_voltage(self, channel):
        """Read voltage."""
        return labjack.ljm.eReadName(self.handle, "AIN" + str(channel))

    def get_values(self):
        """Read channels."""
        chans = self.device['Channels']
        readings = {}
        for channel_id, chan in chans.items():
            if chan['Type'] in ['Voltage']:
                value = self.read_voltage(chan['DeviceChannel'])
                readings[channel_id] = value
            else:
                raise LoggerError(
                    f'Unknown channel type \'{chan["Type"]}\' for channel \'{channel_id}\''
                    +f' of device \'{self.device["Device"]}\'')
        return readings
