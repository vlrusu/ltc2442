#!/usr/bin/env python

import spidev
import RPi.GPIO as GPIO
import time

LTC2449_KEEP_PREVIOUS_MODE             = 0x8000
LTC2449_KEEP_PREVIOUS_SPEED_RESOLUTION = 0x0000
LTC2449_SPEED_1X                       = 0x0000
LTC2449_SPEED_2X                       = 0x0008

LTC2449_CH0            =0xB000
LTC2449_CH1            =0xB800
LTC2449_CH2            =0xB100
LTC2449_CH3            =0xB900
LTC2449_CH4            =0xB200
LTC2449_CH5            =0xBA00
LTC2449_CH6            =0xB300
LTC2449_CH7            =0xBB00
LTC2449_CH8            =0xB400
LTC2449_CH9            =0xBC00
LTC2449_CH10           =0xB500
LTC2449_CH11           =0xBD00
LTC2449_CH12           =0xB600
LTC2449_CH13           =0xBE00
LTC2449_CH14           =0xB700
LTC2449_CH15           =0xBF00

LTC2449_P0_N1          =0xA000
LTC2449_P1_N0          =0xA800

LTC2449_P2_N3          =0xA100
LTC2449_P3_N2          =0xA900

LTC2449_P4_N5          =0xA200
LTC2449_P5_N4          =0xAA00

LTC2449_P6_N7          =0xA300
LTC2449_P7_N6          =0xAB00

LTC2449_P8_N9          =0xA400
LTC2449_P9_N8          =0xAC00

LTC2449_P10_N11        =0xA500
LTC2449_P11_N10        =0xAD00

LTC2449_P12_N13        =0xA600
LTC2449_P13_N12        =0xAE00

LTC2449_P14_N15        =0xA700
LTC2449_P15_N14        =0xAF00

LTC2449_OSR_64         =0xA010
LTC2449_OSR_128        =0xA020
LTC2449_OSR_256        =0xA030
LTC2449_OSR_512        =0xA040
LTC2449_OSR_1024       =0xA050
LTC2449_OSR_2048       =0xA060
LTC2449_OSR_4096       =0xA070
LTC2449_OSR_8192       =0xA080
LTC2449_OSR_16384      =0xA090
LTC2449_OSR_32768      =0xA0F0

LTC2442_OSRS = [LTC2449_OSR_64, LTC2449_OSR_128, LTC2449_OSR_256, LTC2449_OSR_512, LTC2449_OSR_1024, LTC2449_OSR_2048, LTC2449_OSR_4096, LTC2449_OSR_8192, LTC2449_OSR_16384, LTC2449_OSR_32768]
COMMAND_SINGLE_ENDED = [LTC2449_CH0, LTC2449_CH1, LTC2449_CH2, LTC2449_CH3]

EOCTIMEOUT = 200

class ltc2442(object):
    """Documentation for ltc2442

    """


 

    
    def __init__(self, bus=0, cs=1, busy = 6,  max_speed_hz=400000):
        """Initialize an SPI device using the SPIdev interface.  Port and device
        identify the device, for example the device /dev/spidev1.0 would be port
        1 and device 0.
        """

        self._bus = bus
        self._cs = cs
        self._spimode = 0b00
        self._busy = busy
        self._max_speed_hz = max_speed_hz
        self._osrmode = LTC2449_OSR_32768
        self._speed = LTC2449_SPEED_1X
        self._lsb = 7.4505805969E-9 # ideal LSB with 29 useful bits and 2V reference
        self._offset_code = 0 #ideal offset
        self._rawdata=[]
        self._adc_code = 0
        
        self.isInitialized = False
        GPIO.setmode(GPIO.BCM)


    def open(self):

        if self.isInitialized:
            return

        self._spi = spidev.SpiDev()
        GPIO.setup(self._busy, GPIO.IN)
        self._spi.open(self._bus, self._cs)
        self._spi.mode = self._spimode
        self._spi.max_speed_hz=self._max_speed_hz    
        self.isInitialized = True
 

    def close(self):
        """Closes the SPI connection 
        """
        self._spi.close()
        self.isInitialized = False

    

    def EOC_timeout(self,timeout):
        timer_count = 0 
        while 1:
            if GPIO.input(self._busy)==0:
                print "delay=",timer_count
                break
            timer_count = timer_count+1
            if timer_count > timeout:
                return 1
            else:
                time.sleep(0.001)

        return 0
        

    
    def set_osr_speed(self, osr, speed=1):
        """ Set OSR 
        """


        if speed == 2:
            self._speed = LTC2449_SPEED_2X
        else:
            self._speed = LTC2449_SPEED_1X


        self._osrmode = LTC2442_OSRS[osr]



    def code_to_voltage(self):

        self._adc_code -= 536870912;
        adc_voltage= float(self._adc_code+self._offset_code)*self._lsb; 
        return adc_voltage;
        
        
    def read_single(self,channel = 0 ):
        """ read a single ended channel

        """

        adc_command = COMMAND_SINGLE_ENDED[channel] | self._osrmode | self._speed
        print ("ADCCOMMAND=%.8x\n" % adc_command)
        
        return self.read(adc_command)
 

    def read_differential(self,cpos = 0, cneg = 1 ):
        """ read a differential, cpos is postitive and cneg is negative

        """
        COMMAND = 0
        if cpos==0 and cneg == 1:
            COMMAND = LTC2449_P0_N1
        elif cpos==1 and cneg == 0:
            COMMAND = LTC2449_P1_N0
        elif cpos==2 and cneg == 3:
            COMMAND = LTC2449_P2_N3
        elif cpos==3 and cneg == 2:
            COMMAND = LTC2449_P3_N2
        
        adc_command = COMMAND | self._osrmode | self._speed
        print ("ADCCOMMAND=%.8x\n" % adc_command)
        
        return self.read(adc_command)
   
    
    

            
        
    
    def read(self,command):


        if self.EOC_timeout(EOCTIMEOUT):
            return 1
        
        time.sleep(0.2)

        
        commandlist = [command >> (8*i) & 0xFF for i in range(15 // 8,-1,-1)]
        commandlist.append(0)
        commandlist.append(0)
#        print '[{}]'.format(', '.join(hex(x) for x in commandlist))
        reply = self._spi.xfer2(commandlist)
#        reply = self._spi.readbytes(4)
        self._rawdata = reply
        retc = reply[3] | reply[2]<<8 | reply[1]<<16 | (reply[0]&0x3F) <<24
        self._adc_code = retc


        return 0

    
