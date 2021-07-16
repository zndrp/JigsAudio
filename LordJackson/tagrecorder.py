from rfidkeyboard import RfidReader
from audio import Audio
import os
import os.path
import time
import datetime

# Options
PLAYBACK_EXISTING = True        # ...if True: Scans will play back an existing recording, or record if none exists (only ever one recording, unless REPEAT_SCAN_RECORDS=True); otherwise
                                # ...if False: all scans will record and will never play back (except if REPEAT_SCAN_RECORDS=False a repeated scan will just stop a recording; playback is only possible immediately after recording if AUTO_PLAYBACK=True)
RECORDING_TIMEOUT = 60          # Maximum recording duration (seconds)
AUTO_PLAYBACK = False           # Automatically play back the audio after a recording finishes
REPEAT_SCAN_RECORDS = False     # A repeated scan of the same card that is currently playing will start a new recording for that card (otherwise, it will just stop the playback)
RENAME_NOT_OVERWRITE = True     # New recordings rename any existing files (otherwise, will overwrite them)
INPUT_DEVICES = [
    "Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader",
    #"RPI Wired Keyboard 1",
]

# Open the tag reader (keyboard device)
with RfidReader(INPUT_DEVICES, verbose=False) as rfid:

    # The recording/playback process handler
    audio = Audio(verbose=True)

    # Last scanned card
    last_card = None
    last_recording = None
    
    # Main loop, runs forever
    while True:

        # Hacky brief pause to not busy-wait too much
        time.sleep(0.050)

        # Check whether a card has been read
        card = rfid.read()

        # Initial playing/recording status
        was_playing = audio.is_playing()
        was_recording = audio.is_recording()
        
        # If we are recording/playing and a card was scanned...
        if (was_playing or was_recording) and card is not None:
            # ...if this card was used to initiate the action, scanning again will just stop that action
            if card == last_card:
                print("STOPPED BY SAME CARD: " + card)
                # If we're stopping a recording, or stopping anything and we're not treating repeat scans during play as a record...
                if was_recording or not REPEAT_SCAN_RECORDS:
                    # ...do not use the card for a new action
                    card = None
            else:
                print("STOPPED BY ANOTHER CARD: " + card)
            # ...stop the recording/playing
            audio.stop()

        # If a recording has stopped...
        if last_recording and not audio.is_recording():
            print("RECORDING-COMPLETE: " + last_recording)
            # ...if auto-playback, start playing (might immediately get interrupted anyway if scanning a different card)
            if AUTO_PLAYBACK:
                print("AUTO-PLAYBACK: " + last_recording)
                audio.play(last_recording)
            last_recording = None

        # If a new card has been scanned...
        if card is not None:
            print("SCANNED: " + card)

            # Determine the filename
            filename = card + ".wav"

            # Check if the recording already exists
            existing_recording = os.path.isfile(filename)

            # Assume we shouldn't record
            should_record = False

            # If there's no existing recording, we should record
            if not existing_recording: should_record = True

            # If we were just playing this card and repeat scans record, we should record
            if was_playing and REPEAT_SCAN_RECORDS and card == last_card: should_record = True

            # If scans do not playback (all scans record), we should record
            if not PLAYBACK_EXISTING: should_record = True

            # If recording...
            if should_record:
                # If we're preserving old recordings...
                if existing_recording and RENAME_NOT_OVERWRITE:
                    created = os.stat(filename).st_ctime
                    timestamp = datetime.datetime.fromtimestamp(created).strftime("%Y%m%d%H%M%S%f")[:-3]
                    rename = card + "-" + timestamp + ".wav"
                    print("RENAME: " + filename + " " + rename)
                    os.rename(filename, rename)

                # Start the new recording
                print("RECORDING: " + filename)
                last_card = card
                audio.record(filename, timeout = RECORDING_TIMEOUT)
                last_recording = filename
            elif existing_recording:
                # Play back the existing recording
                print("PLAYING: " + filename)
                last_card = card
                audio.play(filename)
            else:
                print("IMPOSSIBLE STATE!: " + card + " / " + filename)

