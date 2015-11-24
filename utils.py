import time
import RPi.GPIO as GPIO
import wiringpi2 as wiringpi
from decorators import logged


class Gpio:
    def __init__(self, outs=[], ins=[]):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.cleanup()
        for o in outs:
            GPIO.setup(o, GPIO.OUT)
        for i in ins:
            GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def turn_on(self, led, verbose=False):
        GPIO.output(led, 1)
        if verbose:
            print('{}: on'.format(led))

    def turn_off(self, led, verbose=False):
        GPIO.output(led, 0)
        if verbose:
            print('{}: off'.format(led))


class Led:
    def __init__(self, reds=None, blues=None, greens=None, verbose=True):
        self.reds = reds or [19, 13, 6, 12]
        self.blues = blues or [27, 18, 4, 23, 16]
        self.greens = greens or [5, 17, 22, 24, 25]
        self.gpio = Gpio(outs=self.all)
        self.verbose = verbose

    @property
    def all(self):
        return self.reds + self.greens + self.blues

    @logged(message='On')
    def leds_on(self, leds=None):
        leds = leds or self.all
        for led in leds:
            self.gpio.turn_on(led)

    @logged(message='Off')
    def leds_off(self, leds=None):
        leds = leds or self.all
        for led in leds:
            self.gpio.turn_off(led)

    @logged(message='Step up')
    def step_up(self, leds=None, frequency=0.25):
        leds = leds or self.all
        for led in leds:
            self.gpio.turn_on(led)
            time.sleep(frequency)

    @logged(message='Step down')
    def step_down(self, leds=None, frequency=0.25):
        leds = leds or self.all
        for led in leds:
            self.gpio.turn_off(led)
            time.sleep(frequency)

    @logged(message='Cycle')
    def cycle(self, leds=None, frequency=0.25, how='full'):
        leds = leds or self.all
        for led in leds:
            self.gpio.turn_on(led)
            time.sleep(frequency)
            self.gpio.turn_off(led)
            time.sleep(frequency)
        if how == 'full':
            for led in leds[::-1][1:]:
                self.gpio.turn_on(led)
                time.sleep(frequency)
                self.gpio.turn_off(led)
                time.sleep(frequency)

    @logged(message='Warming up...')
    def warm_up(self, leds=None, frequency=0.25):
        middle = len(self.all) / 2
        if len(self.all) % 2 == 0:
            for i in range(middle):
                led1 = self.all[middle - 1 - i]
                led2 = self.all[middle + i]
                self.leds_on([led1, led2])
                time.sleep(frequency)
                self.leds_off([led1, led2])
        else:
            self.leds_on([self.all[middle]])
            time.sleep(frequency)
            self.leds_off([self.all[middle]])
            for i in range(middle - 1):
                led1 = self.all[middle - 1 - i]
                led2 = self.all[middle + 1 + i]
                self.leds_on([led1, led2])
                time.sleep(frequency)
                self.leds_off([led1, led2])

    @logged(message='Flickering...')
    def flicker(self, leds=None, frequency=0.04, times=20, ends_with='off'):
        leds = leds or self.all
        for _ in range(times):
            self.leds_on(leds)
            time.sleep(frequency)
            self.leds_off(leds)
            time.sleep(frequency)
            if ends_with == 'on':
                self.leds_on(leds)
                time.sleep(frequency)

    @logged(message='Pulsing...')
    def pulse(self, leds=[1], frequency=0.001, times=5):
        io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_PINS)
        io.pinMode(1, io.PWM_OUTPUT)
        for led in leds:
            io.pwmWrite(led, 0)
            value = 0
            increment = 4
            increasing = True
            count = 0

            while count < times:
                io.pwmWrite(led, value)

                if increasing:
                    value += increment
                    time.sleep(frequency)
                else:
                    value -= increment
                    time.sleep(frequency)

                if (value >= 1024):
                    increasing = False

                if (value <= 0):
                    count = count + 1
                    print(count)
                    increasing = True

                time.sleep(frequency)
        GPIO.cleanup()
