# -*- coding: utf-8 -*-
"""
This module contains drivers for the Kurt J. Lesker KJLC 354 and KJLC 352 series ion pressure gauge
and the InstruTech IGM401 and IGM402 ion pressure gauge
(InstruTech seems to be the original manufacturer), and the Kurt J. Lesker KJLC 300 series Pirani
pressure gauge.
The KJLC352 and IGM402 gauges are combined gauges and have to capability to additionally read out
(two, but only the first is used here) Pirani gauges. To read out this pressure values when the ion
gauge is off, set `ReadCombinedPressure` in `DeviceSpecificParams` to True in the device
configuration file (but to False when using a KJLC 354 or IGM401 gauge). By default,
`ReadCombinedPressure` is set to False.
Some models of the ion gauges support reading out the status of the filament, which can activated
here by setting `ConfirmFilamentIsOn` in `DeviceSpecificParams` to True. If the filament is not on,
the pressure is not read out in this case. This will, however, also prevent a valid pressure
reading from the Pirani gauge of a combined gauge if its filament is off.
On the other hand, some older gauges do not support this feature, and it should be switched off.
By default, `ConfirmFilamentIsOn` is set to False.
It uses the two-wire RS-485 interface of the gauge
(not to be confused with a RS-232 interface, which uses the same 9-pin sub-D connector)
to read out the pressure in units of Torr.

Note the pin assignment of the RS-485 interface on the ion gauges:
DATA- on pin 6, DATA+ on pin 9, and ground on pin 4.
For the 300 series Pirani gauge, the pin assignment is:
DATA- on pin 2, DATA+ on pin 1, and ground on pin 4.
This might be different than the pin assignment of your RS-485 adapter
(such as e.g. those from StarTech) and a custom cable might needs to be used.
"""

import serial
import logging

import dev_generic
import dev_kjlc300

from defs import LoggerError

logger = logging.getLogger()

class Device(dev_kjlc300.Device):

    def __init__(self, device):
        """
        Initialize device.

        device : dict
            Configuration dict of the device to initialize.
        """
        super(Device, self).__init__(device)

    def read_pressure(self):
        """Read pressure."""
        if self.device["DeviceSpecificParams"].get('ConfirmFilamentIsOn', False):
            # Check whether filament is powered up and gauge is reading
            rsp = self.query("IGS")
            if rsp.startswith("0"):
                raise LoggerError(
                    "Filament is not powered up, no pressure reading available")
        # Read pressure
        if self.device["DeviceSpecificParams"].get('ReadCombinedPressure', False):
            rsp = self.query("RDS")
        else:
            rsp = self.query("RD")
        return float(rsp)
