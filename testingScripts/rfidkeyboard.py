from __future__ import print_function   # Python 2 support for:  print(..., end=...)
import sys                              # Python 2 doesn't support print(..., flush=True)
import time
import os
import fcntl

class RfidReader:
    """
        Non-blocking raw-input reader for enter-terminated time-batched numeric input
        (e.g. M301 Mifare Card RF ID Reader)
        Dan Jackson, 2020-2021
    """

    def __init__(self, deviceName = None, verbose = False, deviceIndex = None):
        # Ensure device name is a list of allowed devices
        if deviceName is None or deviceName == "":
            self.deviceName = []
        elif isinstance(deviceName, list):
            self.deviceName = deviceName
        else:
            self.deviceName = [deviceName]
        self.verbose = verbose          # Noisy output to stdout for debugging
        self.deviceIndex = deviceIndex  # None/0=(Default) last matching device name found, 1=1st matching, ...
        self.file = None
        self.card = ""
        self.input = ""
        self.last = None
    
    def __del__(self):
        self.close()
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, type, value, tb):
        self.close()
    
    def open(self):
        print("RfidReader: Opening..." + str(self.deviceName))
        inputDeviceBase = "/sys/class/input/"
        inputPathBase = "/dev/input/"
        inputDevice = None
        matchIndex = 0
        for device in os.listdir(inputDeviceBase):
            if not device.startswith("event"):
                continue
            nameFile = inputDeviceBase + device + "/device/name"
            with open(nameFile, 'r') as nf:
                name = nf.read().strip()
            print("RfidReader: Checking input [" + device + "]: '" + name + "'")
            if len(self.deviceName) > 0 and name not in self.deviceName:
                continue
            matchIndex += 1
            print("RfidReader: ...match " + str(matchIndex) + ", looking for " + str(self.deviceIndex) + "")
            if self.deviceIndex is not None and self.deviceIndex > 0 and matchIndex != self.deviceIndex:
                continue
            inputDevice = inputPathBase + device
        if inputDevice == None:
            print("RfidReader: Cannot find a matching input device: " + str(self.deviceName))
            raise Exception("Cannot find matching input device")
        print("RfidReader: Found input device: " + inputDevice)
        self.file = open(inputDevice, "rb", buffering=0)
        # Non-blocking mode
        fd = self.file.fileno()
        fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)
    
    def close(self):
        if self.file == None:
            return
        #print("RfidReader: Closing...")
        self.file.close()
        self.file = None
    
    def read(self):
        #print("RfidReader: Read...")
        self.card = ""
        now = time.time()
        if (self.input != "" and self.last != None and now - self.last > 2):
            print("RfidReader: Input timeout")
            self.input = ""
            self.last = None
        while True:
            eventData = None
            try:
                eventData = self.file.read(24)
            except IOError as e:
                if e.errno == 11: # Python 2 gets [Errno 11] Resource temporarily unavailable
                    if self.verbose:
                        print("!", end="") # flush=True (can't with Python 2 __future__ print)
                        sys.stdout.flush()
                    break
                raise

            if eventData is None: # Python 3 get no event
                if self.verbose:
                    print(".", end="") # flush=True (can't with Python 2 __future__ print)
                    sys.stdout.flush()
                #raise TypeError("No data read")
                break

            self.last = now 

            #timeS: eventData.readUInt32LE(0),
            #timeUS: eventData.readUInt32LE(4),
            #type: eventData.readUInt16LE(8),
            #code: eventData.readUInt16LE(10),
            #value: eventData.readInt32LE(12),

            # 28=Enter, 2='1', 3='2', ..., 10='9', 11='0'
            code = eventData[10]
            # 0=release, 1=press, 2=repeat
            value = eventData[12]

            # Compatibility with Python 2
            if isinstance(code, str):
                code = ord(code)
            if isinstance(value, str):
                value = ord(value)

            # Map scan code to character
            char = None
            # Main keyboard numeric input
            if code == 28: char = "\n" # 28=Main keyboard Enter key
            elif code >= 2 and code <= 11: char = str((code - 1) % 10) # Main keyboard numeric keys: 2='1', 3='2', ..., 10='9', 11='0'
            # Num-pad
            elif code == 96: char = "\n" # 96=Numpad Enter
            elif code == 82: char = "0" # 82=0 numpad
            elif code >= 79 and code <= 81: char = str(code - 79 + 1) # 79/80/81=1/2/3 numpad
            elif code >= 75 and code <= 77: char = str(code - 75 + 4) # 75/76/77=4/5/6 numpad
            elif code >= 71 and code <= 73: char = str(code - 71 + 7) # 71/72/73=7/8/9 numpad
            # Limited alpha support for hex digits (not tracking shift/caps status, so lower-case only)
            elif code == 30: char = "a"
            elif code == 48: char = "b"
            elif code == 46: char = "c"
            elif code == 32: char = "d"
            elif code == 18: char = "e"
            elif code == 33: char = "f"

            if value == 1: # pressed
                if char is not None and self.verbose:
                    print("<" +  str(code) + "=" + str(ord(char)) + "=" + char.replace("\n", "\\n") + ">", end="") # flush=True (can't with Python 2 __future__ print)
                    sys.stdout.flush()
                if (char == "\n"):                    # Keycode for enter
                    self.card = self.input
                    self.input = ""
                elif char is not None:      # Keycode for decimal digit: 2='1', 3='2', ..., 10='9', 11='0'
                    self.input = self.input + char
                else:
                    # Unhandled scan code
                    if self.verbose:
                        print("[?" + str(code) + "]", end="") # flush=True (can't with Python 2 __future__ print)
                        sys.stdout.flush()
                    pass
        
        # No card found / cards exist
        if self.card == "":
            return None
        return self.card
        
# Example code if run from command-line
if __name__ == "__main__":
    # Default device name (None=last to enumerate), override as first command-line parameter
    deviceName = None
    #deviceName = "RPI Wired Keyboard 1"
    if len(sys.argv) > 1: deviceName = sys.argv[1]
    print("Example using device: " + str(deviceName))
    
    with RfidReader(deviceName, verbose=True) as rfid:
        while True:
            card = rfid.read()
            if card is not None:
                print("CARD: " + card)
            time.sleep(0.050)
        
#except Exception as e:
#    print('Exception ' + e.__doc__ + ' -- ' + e.message)

