# Smart Environment Control System
An Orange Pi-based IoT system that monitors and controls light intensity and temperature using sensors (BH1750 &amp; BMP280), with automated LED and fan control and real-time cloud monitoring via MQTT (ThingSpeak).

Features:- 
- Real-time light (Lux) monitoring using BH1750 sensor
- Temperature monitoring using BMP280 sensor
- Automatic LED brightness control using PWM
- Fan control based on temperature threshold
- Adjustable target values via physical buttons
- Cloud data logging using MQTT (ThingSpeak)

How It Works:- 
- The system continuously reads light and temperature data
- Compares values with user-defined targets
- Adjusts LED brightness and fan accordingly
- Sends data to ThingSpeak via MQTT for remote monitoring

Hardware Used:- 
- Orange Pi
- BH1750 Light Sensor
- BMP280 Temperature Sensor
- LED (PWM controlled)
- Cooling Fan
- Push Buttons
- Breadboard & Jumper Wires

Project Setup:-

![Setup](setup.jpg)

Circuit Diagram:-

![Schematic](schematic.png)

How to run:- 
1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt
3. Configure MQTT credentials in the code
4. Connect hardware components:
   - BH1750 (Light Sensor)
   - BMP280 (Temperature Sensor)
   - LED (PWM control)
   - Fan (GPIO output)
   - Push buttons
5. Run the program:
   python3 main.py
6. Monitor output:
   - Real-time sensor data in terminal
   - Data published to ThingSpeak via MQTT
