# Seminar MicroPython

#### Beschreibung:
Das hier vorgestellte kleine Projekt soll die Verwendung von MicroPython auf handelsüblicher Hardware demonstrieren. Dabei ist mit relativ kleinem Aufwand bereits viel zu erreichen.

#### Verwendete Software:
- PyCharm 2021.3.3 (Community Edition)
- MicroPython Plugin for PyCharm
- Anleitung: https://blog.jetbrains.com/pycharm/2018/01/micropython-plugin-for-pycharm/

#### Verwendete Hardware:
- Node MCU ESP8266 WiFi Modul 
- Pmod OLEDrgb: 96 x 64 RGB OLED mit 16 Bit-Farbauflösung
- Arduino - Grove Schiebepotentiometer
- diverse Kabel und Stecker aus Electronics Fun Kit (elegoo)

#### PIN Zugehörigkeit:
ESP8266		PmodOLEDrgb
VCC-3.3 V ---   VCC (6)
	  ---	VCCEN (9)
	  ---	PMODEN (10)
GND	  ---	GND (5)
	  ---	CS (1)
D5 (SCK)  ---	SCK (4)
D8 (MOSI) ---	MOSI (2)
D1 (GPIO) ---   D/C (7)
D2 (GPIO) ---   RES (8)