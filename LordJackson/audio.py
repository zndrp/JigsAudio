import subprocess
import time

class Audio:
    """
        Non-blocking audio recorder/player
        Dan Jackson, 2021
    """

    def __init__(self, verbose = True):
        self.verbose = verbose          # Noisy output to stdout for debugging
        self.process = None             # Process handle
        self.command = None             # Current process tag/label
        self.started = None             # Process start time
        
    def run(self, tag, args):
        self.stop()  # stop any existing
        if self.verbose: print("AUDIO: " + tag + ": " + str(args))
        self.process = subprocess.Popen(args, shell=False) # , preexec_fn=os.setsid
        self.start = time.time()
        if self.verbose: print("AUDIO: ...(pid=" + str(self.process.pid) + ")")
        self.command = tag

    def record(self, filename, timeout = 60):
        self.run('record', ['arecord', '-c1', '-r' , '44100', '-f', 'S16_LE', '-t', 'wav', '-d', str(timeout), filename])

    def play(self, filename):
        self.run('play', ['aplay', filename])

    def is_running(self):
        if self.process is None:
            self.command = None
            return False
        if self.process.poll() is not None:
            self.process = None
            if self.verbose: print("AUDIO: (stopped)")
            return False
        return True

    def duration(self):
        if not self.is_running():
            return None
        duration = time.time() - self.start
        return duration

    def is_recording(self):
        if not self.is_running():
            return False
        return self.command == "record"

    def is_playing(self):
        if not self.is_running():
            return False
        return self.command == "play"

    def stop(self):
        if not self.is_running():
            return

        # Kill the process
        if self.verbose: print("AUDIO: Killing existing process: pid=" + str(self.process.pid) + "")

        self.process.terminate()

        # Kill process group
        #os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

        # As our processes handle hardware, let's wait (at most a few seconds) until it is actually stopped
        start = time.time()
        while time.time() - start < 5:
            if not self.is_running():
                if self.verbose: print("AUDIO: ...terminated")
                break
            time.sleep(0.050)

        # Kill if still running
        if self.process is not None:
            if self.verbose: print("AUDIO: ...killing")
            self.process.kill()

        self.process = None
        self.command = None



# Example code if run from command-line
if __name__ == "__main__":
    audio = Audio(verbose = True)

    audio.record("test.wav")
    time.sleep(5)
    audio.stop()

    audio.play("test.wav")
    time.sleep(4)
    audio.stop()
