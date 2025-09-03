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
        self.target_bin_id = None
        self.target_picked_up = False
        self.handled_bins = set()
        self.pickup_time = None
        self.pickup_timeout = pickup_timeout
        self.suppress_after_handle = suppress_after_handle
        self.bin_coming_down = False
        self.global_suppress_until_next_pickup = False  # New global suppression

    def update(self, current_state: GripperState, bin_in_frame: bool, bin_is_above_cutoff: bool, bin_id=None):
        now = time.time()

        # --- Global suppression check ---
        if self.global_suppress_until_next_pickup:
            # Stop any current audio
            if self.current_play_obj and self.current_play_obj.is_playing():
                self.current_play_obj.stop()

            # Detect new bin pickup → lift suppression immediately
            if current_state == GripperState.GOOD and bin_id is not None:
                self.reset_state()  # Reset previous bin state
                self.target_picked_up = True
                self.target_bin_id = bin_id
                self.pickup_time = now
                self.global_suppress_until_next_pickup = False
                print(f"[DEBUG] New bin {bin_id} picked up. Global suppression lifted.")

            # Continue to check beep for new bin immediately
            # No return here, we want to allow beep logic below

        # Stop audio if bin is coming down
        if self.bin_coming_down:
            if self.current_play_obj and self.current_play_obj.is_playing():
                self.current_play_obj.stop()
                print(f"[DEBUG] Beep force-stopped (bin coming down, bin {self.target_bin_id}).")
            if not bin_in_frame:
                if self.target_bin_id is not None:
                    self.handled_bins.add(self.target_bin_id)
                    print(f"[DEBUG] Bin {self.target_bin_id} fully out of frame. Marked as handled.")
                self.reset_state()
                self.global_suppress_until_next_pickup = True  # Activate global suppression
                print("[DEBUG] Global suppression activated until next pickup.")
            return  # Exit early

        # Pickup timeout handling
        if self.target_picked_up and self.pickup_time and now - self.pickup_time > self.pickup_timeout:
            print(f"[WARN] Pickup timeout exceeded for bin {self.target_bin_id}. Resetting state.")
            self.reset_state()
            self.global_suppress_until_next_pickup = True
            return

        # Detect new pickup (if not in global suppression)
        if current_state == GripperState.GOOD and bin_id is not None and not self.target_picked_up:
            self.target_picked_up = True
            self.target_bin_id = bin_id
            self.pickup_time = now
            print(f"[DEBUG] Bin {bin_id} picked up. Tracking as target.")
            return

        # If picked up but gripper no longer GOOD → bin coming down
        if self.target_picked_up and current_state != GripperState.GOOD:
            self.bin_coming_down = True
            if self.current_play_obj and self.current_play_obj.is_playing():
                self.current_play_obj.stop()
            print(f"[DEBUG] Bin {self.target_bin_id} released. Beeps stopped, bin coming down.")
            return

        # Suppress beeps for already handled bins
        if bin_id in self.handled_bins:
            return

        # Determine if we should beep
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


    def is_target_picked_up(self):
        return self.target_picked_up

    def reset_state(self):
        self.target_picked_up = False
        self.target_bin_id = None
        self.pickup_time = None
        self.bin_coming_down = False
