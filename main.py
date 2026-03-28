# Importing the libraries, we are going to use
import time
from smbus2 import SMBus, i2c_msg
from bmp280 import BMP280
import paho.mqtt.client as mqtt                        # MQTT library for ThingSpeak
import wiringpi as wp

# Initial target values
desired_lux = 50
desired_temp = 20

# wpi pin numbers for switchs
switch_1_Lux = 3
switch_2_Temp = 4
# Setting up Led pin (PWM)
led_pin = 2
# wpi pin number for fan
fan_pin = 5

wp.wiringPiSetup()                 # Setting up GPIO Pins

# Setting the switch pin mode as input
wp.pinMode(switch_1_Lux, 0)
wp.pinMode(switch_2_Temp, 0)
# Setting the fan pin as output 
wp.pinMode(fan_pin, 1)

#start pmw
wp.softPwmCreate(led_pin, 0, 100)
# Setting pause time
pause_time=0.02

# Set up I2C bus
bus = SMBus(0)

# BH1750 address and setup
bh1750_address = 0x23
bus.write_byte(bh1750_address, 0x10)

# BMP280 address and setup
bmp280_address = 0x77
bmp280 = BMP280(i2c_addr=bmp280_address, i2c_dev=bus)

# MQTT settings for ThingSpeak
MQTT_HOST ="mqtt3.thingspeak.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL =60
MQTT_CLIENT_ID = "your_id"
MQTT_USER = "Your_user"
MQTT_PWD = "your_password"

# MQTT setup
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to ThingSpeak MQTT")
    else:
        print("MQTT connection failed. Code:", rc)

def on_disconnect(client, userdata, flags, rc=0, properties=None):
    print("Disconnected from MQTT. Code:", rc)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, MQTT_CLIENT_ID)
client.username_pw_set(MQTT_USER, MQTT_PWD)
client.on_connect = on_connect
client.on_disconnect = on_disconnect

print("Connecting to ThingSpeak MQTT...")
client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.loop_start()


def get_lux(bus, address):                    # # Function to read BH1750 light intensity (Lux)
    write = i2c_msg.write(address, [0x10])  # set measurement mode
    read = i2c_msg.read(address, 2)         # read two bytes data
    bus.i2c_rdwr(write, read)
    bytes_read = list(read)
    lux = (((bytes_read[0] & 3) << 8) + bytes_read[1]) / 1.2
    return lux

def increase_light_intensity(led,cnt,wait):   # Function to gradually increase the light intensity form 0 to 100 (PWM Duty Cycle).
        n=1
        wp.softPwmWrite(led, cnt)
        time.sleep(wait)  # Wait for smooth transition
       
def decrease_light_intensity(led, cnt, wait): # Function to gradually decrease the light instensity from 100 to 0 (PWM Duty Cycle)
    wp.softPwmWrite(led, cnt)
    time.sleep(wait)

current_intensity = 0  # Variable to track current intensity

try:
    while True:     # Endless loop to periodically read and display values
        try:
        
            if wp.digitalRead(switch_1_Lux)==1:
                print(f"\n==> Button Triggered for changing the desired lux")
                desired_lux = desired_lux + 10
                if desired_lux <= 100 and desired_lux >= 10:
                    print(f"Desired Lux: {desired_lux}")
                    time.sleep(1)
                    continue
            if desired_lux > 100:
                desired_lux = 10
                print(f"Desired Lux {desired_lux}")
                time.sleep(1)
                continue
            
            if wp.digitalRead(switch_2_Temp)==1:
                print(f"\n==> Button Triggered for changing the desired temp")
                desired_temp = desired_temp + 1
                if desired_temp <= 40 and desired_temp >=20:
                    print(f"Desired Temp: {desired_temp}") 
                    time.sleep(1)
                    continue
            if desired_temp > 40:
                desired_temp = 20
                print(f"Desired Temp: {desired_temp}")
                time.sleep(1)
                continue
            
            # Printing the desired lux and desired temp in the terminal
            print("\nDesired Light Intensity: {:.2f} Lux".format(desired_lux))
            degree_sign = u"\N{DEGREE SIGN}"
            print('Desired Temperature: {:.2f}{}C\n'.format(desired_temp, degree_sign))

            # Read BH1750 sensor data and printing it in terminal (lux)
            lux = get_lux(bus, bh1750_address)
            print("Light Intensity: {:.2f} Lux".format(lux))
            # Read BMP280 sensor data and printing it in terminal(temperature)
            temperature = bmp280.get_temperature()
            print('Temperature: {:.2f}{}C\n'.format(temperature, degree_sign))

            # Comparing and taking actions based on the values
            # When increasing the intensity
            if lux < desired_lux:
                wp.softPwmWrite(led_pin, current_intensity)
                if current_intensity == 100:
                    pass
                else:
                    for i in range(current_intensity, 100):
                        current_intensity = i
                        increase_light_intensity(led_pin, current_intensity, pause_time)

            # When decreasing the intensity
            if lux > desired_lux:
                wp.softPwmWrite(led_pin, current_intensity)
                if current_intensity == 0:
                    pass
                else:
                    for i in range(current_intensity, 0, -1):
                        current_intensity = i
                        decrease_light_intensity(led_pin, current_intensity, pause_time)

            if temperature > desired_temp:
                wp.digitalWrite(fan_pin, 1)
            
            if temperature < desired_temp:
                wp.digitalWrite(fan_pin, 0)
        
            # Prepare MQTT payload
            mqtt_payload = (
                f"&field1={lux:.2f}"
                f"&field2={temperature:.2f}"
                f"&field3={desired_lux:.2f}"
                f"&field4={desired_temp:.2f}"
                f"&status=MQTTPUBLISH"
            )

            # Publish to ThingSpeak
            client.publish(MQTT_TOPIC, mqtt_payload)
            print("Published to ThingSpeak:", mqtt_payload)
        

        except Exception as e:
            print("Error:", e)
            client.reconnect()
        
        # Wait before next reading
        else:
            time.sleep(8)

except KeyboardInterrupt:
    print("\nProagram has been stopped by the end user")