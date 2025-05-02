# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 16:55:25 2018

@author: Lothar Maisenbacher/MPQ
"""

import pyvisa
import logging
import numpy as np

import dev_generic

from defs import LoggerError

from defs import LoggerError

logger = logging.getLogger()

class Device(dev_generic.Device):

    def __init__(self, device):
        """Init device."""
        super().__init__(device) 
        self.init_visa()

    def read_power(self):
        """ Read power from device. """
        return float(self.visa_query('MEASure:POWer?'))
        
    def read_energy(self):
        """ Read energy from device. """
        return float(self.visa_query('MEASure:ENERgy?'))
    
    def close(self):
        """ Close connection to device. """
        self.visa_resource.close()
    
    def get_values(self):
        """Read channels."""
        chans = self.device['Channels']
        readings = {}
        for channel_id, chan in chans.items():
            if chan['Type'] == 'Power':
                value = self.read_power()
                readings[channel_id] = value
            elif chan['Type'] == 'Energy':
                value = self.read_energy()
                readings[channel_id] = value
            else:
                raise LoggerError(
                    f'Unknown channel type \'{chan["Type"]}\' for channel \'{channel_id}\''
                    +f' of device \'{self.device["Device"]}\'')
        return readings

