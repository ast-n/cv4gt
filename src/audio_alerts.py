import simpleaudio as sa
import numpy as np
import time
from enum import Enum


class GripperState(Enum):
    NEUTRAL = 0
    GOOD = 1
    BAD = 2
    NONE = 3


class AudioHandler:
    def __init__(self, frequency=880, duration_ms=75):
        # Sound generation
        sample_rate = 44100
        duration_s = duration_ms / 1000.0
        t = np.linspace(0, duration_s, int(sample_rate * duration_s), False)
        audio_data = np.sin(frequency * t * 2 * np.pi)
        audio_data = (audio_data * 32767 / np.max(np.abs(audio_data))).astype(np.int16)
        self.beep_wave_obj = sa.WaveObject(audio_data, 1, 2, sample_rate)

        # State management
        self.last_beep_time = 0
        self.beep_interval = 0.3
        self.current_play_obj = None
        self.target_bin_id = None      # Currently lifted bin
        self.target_picked_up = False
        self.handled_bins = set()      # Bins that have been picked up and returned

        print("Audio Handler UP")

    def update(self, current_state: GripperState, bin_in_frame: bool, bin_is_above_cutoff: bool, bin_id=None):
        """
        Updates the handler with current frame state and plays audio if needed
        """

        # Check if bin has already been handled
        if bin_id in self.handled_bins:
            if self.current_play_obj is not None and self.current_play_obj.is_playing():
                self.current_play_obj.stop()
                print(f"[DEBUG] Bin {bin_id} already handled. Stopping audio.")
            else:
                print(f"[DEBUG] Bin {bin_id} already handled. No beep played.")
            return

        # If a bin is currently picked up
        if self.target_picked_up:
            # Detect when the gripper is bringing the bin down (i.e., current_state != GOOD)
            if current_state != GripperState.GOOD:
                if self.current_play_obj is not None and self.current_play_obj.is_playing():
                    self.current_play_obj.stop()
                    print(f"[DEBUG] Bin {self.target_bin_id} coming down. Stopping audio.")
                if self.target_bin_id is not None:
                    self.handled_bins.add(self.target_bin_id)
                    print(f"[DEBUG] Bin {self.target_bin_id} marked as handled.")
                self.reset_state()
                return
            # Still lifting; do not beep for this bin
            print(f"[DEBUG] Bin {self.target_bin_id} is currently picked up. Beep suppressed.")
            return

        # Pick up new bin
        # Inside update() where bin is picked up
        if current_state == GripperState.GOOD and bin_id is not None:
            # Mark as picked up
            self.target_picked_up = True
            self.target_bin_id = bin_id

            # Stop any ongoing beep immediately
            if self.current_play_obj is not None and self.current_play_obj.is_playing():
                self.current_play_obj.stop()
                print(f"[DEBUG] Bin {bin_id} picked up. Stopping any ongoing beep immediately.")

            print(f"[DEBUG] Bin {bin_id} picked up. Tracking as target.")
            return


        # Determine if beep is needed for other bins
        should_beep = (
            current_state == GripperState.BAD and
            bin_in_frame and
            not bin_is_above_cutoff
        )

        if should_beep:
            current_time = time.time()
            time_check = (current_time - self.last_beep_time > self.beep_interval)
            playing_check = (self.current_play_obj is None or not self.current_play_obj.is_playing())
            if time_check and playing_check:
                self.last_beep_time = current_time
                self.current_play_obj = self.beep_wave_obj.play()
                print(f"[DEBUG] Beep played for bin {bin_id}.")

    def is_target_picked_up(self):
        return self.target_picked_up

    def reset_state(self):
        self.target_picked_up = False
        self.target_bin_id = None
