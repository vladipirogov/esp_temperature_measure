import network
import picoweb
import time
import machine
import ds18x20, onewire
import utime
#import urtc
from machine import Pin, SPI
from matrix7seg import Matrix7seg
import max7219
from machine import Timer


#NETWORK 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect('#######', '######')
    while not wlan.isconnected():
        pass
print('network config:', wlan.ifconfig())
ipadd=wlan.ifconfig()

app = picoweb.WebApp(__name__)

#I2C
#i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
#rtc = urtc.DS3231(i2c)

# 7-segment led
spi = SPI( miso=Pin(12), mosi=Pin(13), sck=Pin(14))
b1 = machine.Pin(0, Pin.OUT, value=1)
#display = Matrix7seg(spi, b1)
display = max7219.Matrix8x8(spi, b1, 4)
display.brightness(0)


# the device is on GPIO3
dat = machine.Pin(3)


# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))
# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)
#temper = 0;

class Temper:
    def __init__(self):
        self.temper = 0

    def setTemper(self, value):
        self.temper = value

    def getTemper(self):
        return self.temper


def readTempAndTime(timer):
    ds.convert_temp()
    for rom in roms:
        temper = ds.read_temp(rom)
        Temper.temper = temper
        #print(temper)
        display.fill(0)
        display.text(str(temper),0,0,1)
        display.show()
    #print(rtc.datetime())

tim = Timer(1)
tim.init(period=1000, mode=Timer.PERIODIC, callback = readTempAndTime)

@app.route("/temp")
def html(req, resp):
    print('hello')
    yield from picoweb.start_response(resp)
    yield from resp.awrite('Overboard temperature: ' + str(Temper.temper))

app.run(debug=True, host =ipadd[0])



    