import RPi.GPIO as GPIO
import datetime

# Pins configuration (Correspondence name-number)
RedLightsPin = 3
DoorButtonPin = 8
LedPinW = 37
LedPinB = 29
LedPinY = 31
LedPinR = 33
RecordingPin = 35
BuzzerPin = 32

# GPIO configuration
GPIO.setmode(GPIO.BOARD)                                # configuration type (BOARD or BCM)
GPIO.setwarnings(False)
GPIO.setup(RedLightsPin, GPIO.OUT, initial=GPIO.LOW)    # Pin out, default low
GPIO.setup(DoorButtonPin, GPIO.IN)                      # Pin in
GPIO.setup(LedPinW, GPIO.OUT, initial=GPIO.LOW)         # Pin out, default low
GPIO.setup(LedPinB, GPIO.OUT, initial=GPIO.LOW)         # Pin out, default low
GPIO.setup(LedPinY, GPIO.OUT, initial=GPIO.LOW)         # Pin out, default low
GPIO.setup(LedPinR, GPIO.OUT, initial=GPIO.LOW)         # Pin out, default low
GPIO.setup(RecordingPin, GPIO.OUT, initial=GPIO.LOW)    # Pin out, default low

# Configuring the buzzer in PWM mode
GPIO.setup(BuzzerPin, GPIO.OUT, initial=GPIO.LOW)   # Pin out, default low
buzzer_pwm = GPIO.PWM(BuzzerPin, 3000)              # 3000 Hz frequency
buzzer_pwm.start(0)                                 # Start PWM with 0% duty cycle (off)

# Function get_time_date definition (using the datetime library)
def get_time_date():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S"), now.strftime("%d/%m/%Y")
