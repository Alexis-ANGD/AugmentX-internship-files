import time
import sched
from ADCDifferentialPi import ADCDifferentialPi
from pylsl import StreamInfo, StreamOutlet

# I2C communication initialization using ADC library 
adc = ADCDifferentialPi(0x6a, 0x6c, 12)  # define I2C address according to module pins

# Global variables
angles = [0] * 8                         # empty array that contains measurements
channels = [5, 6, 7, 8, 1, 2, 3, 4]      # reorganize channel order according to module board numeration
Ts = 0.001                               # time step between samples in seconds
initial_time = time.time()               # record the initial time

# Create a new stream info
info = StreamInfo('CrayXRpi', 'ADC', 8, 1/Ts, 'float32', 'myuid34234')

# Define LSL stream outlet
outlet = StreamOutlet(info)

def read_adc():
    """Reads ADC module channels and stores the values in the global array angles."""
    for i in range(8):
        angles[i] = adc.read_raw(channels[i])

def send_data(scheduler):
    """Schedules the next data send, reads ADC values, and sends them via LSL."""
    scheduler.enter(Ts, Ts, send_data, (scheduler,))  # Schedule event 'send_data' to happen in Ts seconds
    read_adc()                                        # Read ADC values and save in global variable 'angles'
    outlet.push_sample(angles)                        # Send 'angles' via LSL
    print('Time: ', time.time()-initial_time, ' \t States: \t',
          ', '.join(map(str, angles)), '\n')

# Create and run the scheduler
my_scheduler = sched.scheduler(time.time, time.sleep)
my_scheduler.enter(Ts, Ts, send_data, (my_scheduler,))
print("Now sending data...")
my_scheduler.run()