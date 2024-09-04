import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import asyncio

from helper_keyboard_input import KeyboardHelper
from sphero_sdk import SerialAsyncDal
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import RvrStreamingServices
from sphero_sdk import BatteryVoltageStatesEnum as VoltageStates

# initialize global variables
key_helper = KeyboardHelper()
current_key_code = -1
driving_keys = [119, 97, 115, 100, 32]
speed = 0
heading = 0
flags = 0

loop = asyncio.get_event_loop()
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

def keycode_callback(keycode):
    global current_key_code
    current_key_code = keycode
    print("Key code updated: ", str(current_key_code))

async def accelerometer_handler(accelerometer_data):
    print('Accelerometer data response: ', accelerometer_data)
    

async def imu_handler(imu_data):
    print('IMU data response: ', imu_data)

async def motor_stall_handler(response):
    print('Motor stall response:', response)
async def main():
    """
    Runs the main control loop for this demo.  Uses the KeyboardHelper class to read a keypress from the terminal.

    W - Go forward.  Press multiple times to increase speed.
    A - Decrease heading by -10 degrees with each key press.
    S - Go reverse. Press multiple times to increase speed.
    D - Increase heading by +10 degrees with each key press.
    Spacebar - Reset speed and flags to 0. RVR will coast to a stop

    """
    global current_key_code
    global speed
    global heading
    global flags

    
    await rvr.wake()

    await rvr.reset_yaw()
    
        # Give RVR time to wake up
    await asyncio.sleep(2)
    
    await rvr.sensor_control.add_sensor_data_handler(
        service=RvrStreamingServices.accelerometer,
        handler=accelerometer_handler
    )
    
    await rvr.sensor_control.add_sensor_data_handler(
        service=RvrStreamingServices.imu,
        handler=imu_handler
    )
    
    await rvr.enable_motor_stall_notify(is_enabled=True)

    await rvr.on_motor_stall_notify(handler=motor_stall_handler)
    
    battery_percentage = await rvr.get_battery_percentage()
    print('Battery percentage: ', battery_percentage)

    battery_voltage_state = await rvr.get_battery_voltage_state()
    print('Voltage state: ', battery_voltage_state)
    
    state_info = '[{}, {}, {}, {}]'.format(
        '{}: {}'.format(VoltageStates.unknown.name, VoltageStates.unknown.value),
        '{}: {}'.format(VoltageStates.ok.name, VoltageStates.ok.value),
        '{}: {}'.format(VoltageStates.low.name, VoltageStates.low.value),
        '{}: {}'.format(VoltageStates.critical.name, VoltageStates.critical.value)
    )
    print('Voltage states: ', state_info)
    
    await rvr.sensor_control.start(interval=250)

    while True:

        if current_key_code == 119:  # W
            # if previously going reverse, reset speed back to 64
            if flags == 1:
                speed = 64
            else:
                # else increase speed
                speed += 64
            # go forward
            flags = 0
        elif current_key_code == 97:  # A
            heading -= 10
        elif current_key_code == 115:  # S
            # if previously going forward, reset speed back to 64
            if flags == 0:
                speed = 64
            else:
                # else increase speed
                speed += 64
            # go reverse
            flags = 1
        elif current_key_code == 100:  # D
            heading += 10
        elif current_key_code == 32:  # SPACE
            # reset speed and flags, but don't modify heading.
            speed = 0
            flags = 0

        # check the speed value, and wrap as necessary.
        if speed > 255:
            speed = 255
        elif speed < -255:
            speed = -255

        # check the heading value, and wrap as necessary.
        if heading > 359:
            heading = heading - 359
        elif heading < 0:
            heading = 359 + heading

        # reset the key code every loop
        current_key_code = -1

        # issue the driving command
        await rvr.drive_with_heading(speed, heading, flags)

        # sleep the infinite loop for a 10th of a second to avoid flooding the serial port.
        await asyncio.sleep(0.1)


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
    try:
        run_loop()
    except KeyboardInterrupt:
        print("Keyboard Interrupt...")
        key_helper.end_get_key_continuous()
        loop.run_until_complete(
            asyncio.gather(
                rvr.sensor_control.clear(),
                rvr.close()
            )
        )
    finally:
        if loop.is_running():
            loop.close()
        print("Press any key to exit.")
        exit(1)
        