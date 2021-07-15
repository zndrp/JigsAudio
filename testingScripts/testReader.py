from rfidkeyboard import *

with RfidReader("Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader") as rfid:
    while True:
        card = rfid.read()
        if card is not None:
            print("SCANNED: " + card)
        time.sleep(0.050) # HACK Dont busy-wait the CPU too much
