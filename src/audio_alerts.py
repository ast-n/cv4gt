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
    def __init__(self, frequency=880, duration_ms=75, pickup_timeout=10, suppress_after_handle=2.0):
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
        self.handled_bins = set()      # Bins already picked up and returned
        self.pickup_time = None        # Timestamp of pickup
        self.pickup_timeout = pickup_timeout
        self.suppress_after_handle = suppress_after_handle
        self.suppress_until = 0  # timestamp until which beeps are suppressed
        self.bin_coming_down = False

        print("Audio Handler UP")

   
    def update(self, current_state: GripperState, bin_in_frame: bool, bin_is_above_cutoff: bool, bin_id=None):
        now = time.time()

        # --- Global suppression for pickup/return ---
        if self.bin_coming_down or now < self.suppress_until:
            if self.current_play_obj and self.current_play_obj.is_playing():
                self.current_play_obj.stop()
                print("[DEBUG] Beep stopped due to global suppression.")
            if self.bin_coming_down:
                self.suppress_until = now + 0.5  # refresh suppression while coming down
                if not bin_in_frame:
                    self.bin_coming_down = False
                    if self.target_bin_id is not None:
                        self.handled_bins.add(self.target_bin_id)
                        print(f"[DEBUG] Bin {self.target_bin_id} fully out of frame. Marked as handled.")
                    self.reset_state()
                print("[DEBUG] Bin is coming down. Global suppression active.")
            return

        # --- Pickup timeout ---
        if self.target_picked_up and self.pickup_time and now - self.pickup_time > self.pickup_timeout:
            print(f"[WARN] Pickup timeout exceeded for bin {self.target_bin_id}. Resetting state.")
            self.reset_state()

        # --- Handle active pickup ---
        if self.target_picked_up:
            if current_state != GripperState.GOOD:
                self.bin_coming_down = True
                self.suppress_until = now + self.suppress_after_handle
                print(f"[DEBUG] Bin {self.target_bin_id} is coming down. Suppression active.")
            else:
                self.suppress_until = now + self.suppress_after_handle
                print(f"[DEBUG] Bin {self.target_bin_id} still picked up. Suppression active.")
            return

        # --- Detect new pickup ---
        if current_state == GripperState.GOOD and bin_id is not None:
            self.target_picked_up = True
            self.target_bin_id = bin_id
            self.pickup_time = now
            self.suppress_until = now + self.suppress_after_handle
            print(f"[DEBUG] Bin {bin_id} picked up. Tracking as target. Global suppression active.")
            return

        # --- Suppress beeps for already handled bins ---
        if bin_id in self.handled_bins:
            print(f"[DEBUG] Bin {bin_id} already handled. No beep played.")
            return

        # --- Only beep if no global suppression and bin is in alignment ---
        should_beep = (
            current_state == GripperState.BAD and
            bin_in_frame and
            not bin_is_above_cutoff
        )

        if should_beep:
            if (now - self.last_beep_time > self.beep_interval and
                (self.current_play_obj is None or not self.current_play_obj.is_playing())):
                self.last_beep_time = now
                self.current_play_obj = self.beep_wave_obj.play()
                print(f"[DEBUG] Beep played for bin {bin_id}.")
        else:
            if self.current_play_obj and self.current_play_obj.is_playing():
                self.current_play_obj.stop()
                print(f"[DEBUG] Beep stopped (no longer needed).")



    def is_target_picked_up(self):
        return self.target_picked_up

    def reset_state(self):
        self.target_picked_up = False
        self.target_bin_id = None
        self.pickup_time = None
