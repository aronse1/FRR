import sys
import os
import asyncio
from helper_keyboard_input import KeyboardHelper

key_helper = KeyboardHelper()
current_key_code = -1
loop = asyncio.get_event_loop()

command = [0,0,0,0]

def keycode_callback(keycode):
    global current_key_code
    global command
    current_key_code = keycode
    
    match current_key_code:
        case 119:
            command = [1,0,0,0]
        case 97:
            command = [0,0,1,0]
        case 115:
            command = [0,1,0,0]
        case 100:
            command = [0,0,0,1]
            
    #print("Key code updated: ", str(command))

MAX_SPEED = 255


X = 0
speed = 0
heading = 0
flags = 0

def calculate_speed(X):
    if (X >= 0 and X < MAX_SPEED):
        temp2 = X / 255;
        temp = 0.8 * temp2 + 0.2 * pow(temp2, 3);
        return temp * 255;


def main():
    global current_key_code
    global speed
    global heading
    global flags
    global X
    
    while True:
        if command[0] == 1:
            speed = calculate_speed(X+10)
        elif command[1] == 1:
            speed = calculate_speed(speed-10)
        elif command[2] == 1:
            heading -= 10        
        elif command[3] == 1:
            heading += 10
        
        print(str(command), " ", speed, " ", heading)
    
    
    
def run_loop():
    global loop
    global key_helper
    key_helper.set_callback(keycode_callback)
    loop.run_until_complete(
        asyncio.gather(
            main()
        )
    )

if __name__ == "__main__":
    loop.run_in_executor(None, key_helper.get_key_continuous)
    run_loop()
