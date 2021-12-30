### Project to use GPIOs of Pi4 ###

Planning to connect LCD display to display date/time.
LDR sensor to dim computer screen based on room illumination
Temperature sensor to monitor room temperature. Daikin AC doesnt show room temperature.
Then, IR sensor to be used as remote for TV and Daikin AC.


LCD (4bit mode)  winstar wh1602b-yyc-jt#000

1  Ground   
2  Vcc
3  Contrast     variable resistor -- GND
4  RS		GPIO20	38
5  R/W          GND
6  Enable	GPIO26  37
7  -
8  -
9  -
10 -
11 LCD D4	GPIO16	36	
12 LCD D5	GPIO19	35
13 LCD D6	GPIO13  33
14 LCD D7	GPIO12	32
15 LCD +	variable resistor (or 1k) (backlight)
16 LCD -	GND


Temperature sensor (DHT11)
1 3V   
2 out	GPIO6 31  
3 Gnd

LDR sensor
1 5V
2 out	GPIO21 40
3 Gnd

IR sensor
1 5V      
2 signal  GPIO5 29
3 Gnd

----------------------

Reference: 

https://www.youtube.com/watch?v=cVdSc8VYVBM

