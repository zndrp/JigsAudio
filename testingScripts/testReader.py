with RfidReader("Barcode Reader") as rfid:
    while True:
        card = rfid.read()
        if card is not None:
            print("SCANNED: " + card)
        time.sleep(0.050) # HACK: Don’t busy-wait the CPU too much