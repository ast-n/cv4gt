"""

Script to record SVO file from ZED camera

"""

import sys
import pyzed.sl as sl
from signal import signal, SIGINT
import argparse 
import os 

cam = sl.Camera()

#Handler to deal with CTRL+C properly
def handler(signal_received, frame):
    cam.disable_recording()
    cam.close()
    sys.exit(0)

signal(SIGINT, handler)

def main():

    init = sl.InitParameters()

    recording_param = sl.RecordingParameters(opt.output_svo_file, sl.SVO_COMPRESSION_MODE.LOSSLESS) 

    status = cam.open(init) 
    if status != sl.ERROR_CODE.SUCCESS: 
        print("Camera Open", status, "Exit program.")
        exit(1)

    err = cam.enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Recording ZED: ", err)
        exit(1)

    runtime = sl.RuntimeParameters()
    frames_recorded = 0
    print("Recording begun. CTRL+C to quit.")

    while True:
        if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS:
            frames_recorded += 1
            print(f"Frames recorded: {frames_recorded}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_svo_file', type=str, help='Path to the SVO file that will be written', required= True)
    opt = parser.parse_args()
    if not opt.output_svo_file.endswith(".svo") and not opt.output_svo_file.endswith(".svo2"): 
        print("--output_svo_file parameter should be a .svo file but is not : ",opt.output_svo_file,"Exit program.")
        exit()
    main()