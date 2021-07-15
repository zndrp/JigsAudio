import time
import os
import fcntl

class RfidReader:
    """
        M301 Mifare Card RF ID Reader
        Dan Jackson, 2020
    """

    def __init__(self, deviceName = "Barcode Reader"):
        self.deviceName = deviceName
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
        print("RfidReader: Opening..." + self.deviceName)
        inputDeviceBase = "/sys/class/input/"
        inputPathBase = "/dev/input/"        
        inputDevice = None
        for device in os.listdir(inputDeviceBase):
            if not device.startswith("event"):
                continue
            nameFile = inputDeviceBase + device + "/device/name"
            with open(nameFile, 'r') as nf:
                name = nf.read().strip()
            print("RfidReader: Checking input [" + device + "]: '" + name + "'")
            if name != self.deviceName:
                continue
            inputDevice = inputPathBase + device
        if inputDevice == None:
            print("RfidReader: Cannot find input device: " + self.deviceName)
            raise Exception("Cannot find input device")
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
                # [Errno 11] Resource temporarily unavailable
                if e.errno == 11:
                    break
                raise

            self.last = now 

            #timeS: eventData.readUInt32LE(0),
            #timeUS: eventData.readUInt32LE(4),
            #type: eventData.readUInt16LE(8),
            #code: eventData.readUInt16LE(10),
            #value: eventData.readInt32LE(12),

            # 28=Enter, 2='1', 3='2', ..., 10='9', 11='0'
            code = ord(eventData[10])
            # 0=release, 1=press, 2=repeat
            value = ord(eventData[12])

            if value == 1:
                #print(">" + str(code) + " -- " + self.input)
                if (code == 28):                    # Keycode for enter
                    self.card = self.input
                    self.input = ""
                elif code >= 2 and code <= 11:      # Keycode for decimal digit: 2='1', 3='2', ..., 10='9', 11='0'
                    self.input = self.input + str((code - 1) % 10)
                else:
                    # Ignore other characters
                    pass
        
        # No card found / cards exist
        if self.card == "":
            return None
        return self.card
        
# Example code if run from command-line
if __name__ == "__main__":
    with RfidReader("") as rfid:
        while True:
            card = rfid.read()
            if card is not None:
                print("CARD: " + card)
            time.sleep(0.050)
        
#except Exception as e:
#    print('Exception ' + e.__doc__ + ' -- ' + e.message)
