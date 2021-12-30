#!/usr/bin/env python3

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import RPi.GPIO as GPIO
import time
import datetime
import threading
import board
import adafruit_dht
import psutil


# Define GPIO to LCD mapping
LCD_RS = 20
LCD_E  = 26
LCD_D4 = 16
LCD_D5 = 19
LCD_D6 = 13
LCD_D7 = 12


# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

lcd_line1 = ''
lcd_line2 = ''

## to configure DHT11
dhtDevice = adafruit_dht.DHT11(board.D6)

celcius = 0.0
humid = 0.0


def main():
  # Main program block
  
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers

  # Initialise display
  lcd_init()

  t_lcd = threading.Thread(target=lcd_display_time)
  t_dht = threading.Thread(target=dht_monitor)

  t_lcd.start()
  t_dht.start()

  t_lcd.join()
  t_dht.join()


def dht_monitor():
	global humid
	global celcius

	while True:
		try:
			humid, celcius = dhtDevice.humidity, dhtDevice.temperature
			time.sleep(60)
			#print (' HERE: {:>7.1f} {:>7.1f}'.format(humid, celcius))
		except RuntimeError as error:
			print(error.args[0])
			## retry after 2 sec
			time.sleep(2)
		except Exception as error:
			dhtDevice.exit()
			raise error


def lcd_display_time():
	global celcius

	while True:
		## get current date/time
		now = datetime.datetime.now()

		## format temp_str
		## 12:11:30 Fri 11Feb1990
		temp_str = now.strftime("%H:%M:%S %a %d%b%Y")

		led_line_1 = temp_str[:8] + '{:>7.1f}C'.format(celcius)
		led_line_2 = temp_str[9:]

		## display in the LCD
		lcd_string(led_line_1,LCD_LINE_1)
		lcd_string(led_line_2,LCD_LINE_2)

		time.sleep(0.8)


def lcd_init():
  ## setup ports
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7

  # Initialise display
  init_cmds = [ 
  		0x33, # 110011 Initialise
  		0x32, # 110010 Initialise
  		0x06, # 000110 Cursor move direction
  		0x0C, # 001100 Display On,Cursor Off, Blink Off
  		0x28, # 101000 Data length, number of lines, font size
  		0x01  # 000001 Clear display
  ]

  ## For some reason, during initialization,
  ## it needs extra delay
  for cmd in init_cmds:
    time.sleep(10*E_DELAY)
    lcd_byte(cmd,LCD_CMD)
  time.sleep(10*E_DELAY)


def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)


if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    dhtDevice.exit()
    GPIO.cleanup()
