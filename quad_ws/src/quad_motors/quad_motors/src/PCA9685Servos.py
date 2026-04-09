'''
    PCA9685 RC Servo Library

    Limited functionality designed to drive RC servos.

    For more robust features, such as bus collision avoidance,
    see Adafruit's PCA9685 library: https://github.com/adafruit/Adafruit_CircuitPython_PCA9685

'''
from smbus2 import SMBus
from time import sleep

# Register addresses
PCA9685_MODE1_REG = 0x00
PCA9685_MODE2_REG = 0x01
PCA9685_PRESCALE_REG = 0xFE
PCA9685_LED0_REG = 0x06

# Mode1 register values
PCA9685_MODE1_RESTART = 0x80
PCA9685_MODE1_EXTCLK = 0x40
PCA9685_MODE1_AUTOINC = 0x20
PCA9685_MODE1_SLEEP = 0x10
PCA9685_MODE1_SUBADR1 = 0x08
PCA9685_MODE1_SUBADR2 = 0x04
PCA9685_MODE1_SUBADR3 = 0x02
PCA9685_MODE1_ALLCALL = 0x01

# Mode2 register values
PCA9685_MODE2_OUTDRV_TPOLE = 0x04
PCA9685_MODE2_INVRT = 0x10
PCA9685_MODE2_OUTNE_TPHIGH = 0x01
PCA9685_MODE2_OUTNE_HIGHZ = 0x02
PCA9685_MODE2_OCH_ONACK = 0x08

# General values
PCA9685_SW_RESET = 0x06

# Special address
PCA9685_BROADCAST_ADDR = 0x00

# Masks
PCA9685_PWM_MASK = 0x0FFF

class PCA9685Servos:
    """
    Class interfacing with an PCA9685 16-channel PWM driver.
    :param int bus_index: RPi I2C bus number. Default bus: 1.    
    :param int address: I2C address of the PCA9685. Default address: 0x40.    
    """
    def __init__(
        self, 
        bus_index = 1,
        device_address=0x40      
    ):      
        self.bus_index = bus_index
        self.address = device_address
        self.reference_clock_speed_hz = 25000000
        self.pwm_frequency_hz = 50  
        self.min_pulse_width = 500  # DS3218SSG Pro minimum
        self.max_pulse_width = 2500  # DS3218SSG Pro maximum      
                   
        try:
            self.bus = SMBus(self.bus_index)      
            # Set PWM frequency
            self._write_byte(PCA9685_MODE1_REG, PCA9685_MODE1_SLEEP)
            prescale_val = int((self.reference_clock_speed_hz / (4096 * self.pwm_frequency_hz)) - 1)    
            self._write_byte(PCA9685_PRESCALE_REG, prescale_val)
            self._write_byte(PCA9685_MODE1_REG, ~PCA9685_MODE1_SLEEP) 
            sleep(0.005)
        except Exception as e:
            print(f"PCA9685 Initialization Failed: {e}")
            raise

    def __del__(self):
        try:
            self.bus.close()
        except:
            pass

    def _write_byte(self, reg, value, retries=3):
        """Internal helper to write byte data with retries."""
        for i in range(retries):
            try:
                self.bus.write_byte_data(self.address, reg, value)
                return True
            except OSError as e:
                if i == retries - 1:
                    print(f"I2C Write Failed to reg {hex(reg)} at address {hex(self.address)}: {e}")
                    raise
                sleep(0.001)
        return False

    def is_alive(self):
        try:
            # Fix: use self.address instead of self.bus_index
            self.bus.read_byte_data(self.address, PCA9685_MODE1_REG)
        except OSError:
            return False
        return True

    def set_pulse_width(self, channel, pulse_width):            
        '''
        :param int channel: 0 - 16 PCA9685 channel.  
        :param int pulse_width: Servo pulse width typically 1500 - 2500 microseconds.  
        '''
        if channel < 0 or channel > 15:
            return
        
        if pulse_width < self.min_pulse_width:
            pulse_width = self.min_pulse_width

        if pulse_width > self.max_pulse_width:
            pulse_width = self.max_pulse_width

        reg = PCA9685_LED0_REG + (channel * 0x04)
        
        # PCA9685 has 4096 steps in its 12-bit register.
        phase_begin = 0     
        phase_end = int(pulse_width * (4096.0 / 20000.0)) & 0x0FFF

        # Prepare 4 bytes for LED_ON_L, LED_ON_H, LED_OFF_L, LED_OFF_H
        data = [
            phase_begin & 0xFF,
            (phase_begin >> 8) & 0xFF,
            phase_end & 0xFF,
            (phase_end >> 8) & 0xFF
        ]

        # Write all 4 bytes in a single atomic block to prevent jitter/partial updates
        for i in range(3): # Retry logic
            try:
                self.bus.write_i2c_block_data(self.address, reg, data)
                return
            except OSError:
                if i == 2:
                    pass
                sleep(0.001)
        