"""Audio Alerts Module.

This module provides audio feedback for bin gripper alignment. It generates
beep alerts when bins are misaligned and tracks individual bins to prevent
repetitive alerts for the same bin.

The system uses state management to track bin pickups, handle timeouts, and
suppress alerts appropriately based on gripper state and bin position.
"""

import simpleaudio as sa
import numpy as np
import time
from enum import Enum


class GripperState(Enum):
    """Enumeration of gripper alignment states.

    Attributes:
        NEUTRAL: Bin visible but not aligned with gripper guides.
        GOOD: Bin properly aligned within gripper guides.
        BAD: Bin partially aligned (one corner in, one corner out).
        NONE: No bin detected in frame.
    """
    NEUTRAL = 0
    GOOD = 1
    BAD = 2
    NONE = 3


class AudioHandler:
    """Manages audio feedback for bin gripper alignment.

    Generates beep alerts when bins are misaligned (BAD state) and tracks
    individual bins to prevent duplicate alerts. Implements timeout and
    suppression logic to handle pickup sequences intelligently.

    Attributes:
        beep_wave_obj (sa.WaveObject): Pre-generated beep sound for playback.
        last_beep_time (float): Timestamp of last beep played.
        beep_interval (float): Minimum time between beeps in seconds.
        current_play_obj (sa.PlayObject): Currently playing sound object.
        target_bin_id (int): ID of currently targeted bin.
        target_picked_up (bool): Whether target bin has been picked up.
        handled_bins (set[int]): Set of bin IDs that have been handled.
        pickup_time (float): Timestamp when bin was picked up.
        pickup_timeout (float): Seconds before pickup times out.
        suppress_after_handle (float): Seconds to suppress after handling.
        bin_coming_down (bool): Whether bin is being lowered.
        global_suppress_until_next_pickup (bool): Global suppression flag.
    """
    def __init__(self, frequency=880, duration_ms=75, pickup_timeout=10, suppress_after_handle=2.0):
        """Initialise audio handler.

        Args:
            frequency (int, optional): Beep frequency in Hz. Defaults to 880 (A5 note).
            duration_ms (int, optional): Beep duration in milliseconds. Defaults to 75.
            pickup_timeout (int, optional): Seconds before pickup times out. Defaults to 10.
            suppress_after_handle (float, optional): Seconds to suppress after handling.
                Defaults to 2.0.
        """
        # Sound generation
        self._audio_disabled = False

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
        self.global_suppress_until_next_pickup = False

    def update(self, current_state: GripperState, bin_in_frame: bool, bin_is_above_cutoff: bool, bin_id=None):
        """Update audio handler state and play alerts as needed.

        Processes the current frame's bin detection state and triggers audio
        alerts for misaligned bins. Manages state transitions for pickup,
        lowering, and suppression logic.

        Args:
            current_state (GripperState): Current gripper alignment state.
            bin_in_frame (bool): Whether any bin is visible in the frame.
            bin_is_above_cutoff (bool): Whether bin is above the audio cutoff line.
            bin_id (int, optional): Track ID of the bin, or None if no bin.
        """
        now = time.time()

        # --- Global suppression check ---
        if self.global_suppress_until_next_pickup:
            if self.current_play_obj and self.current_play_obj.is_playing():
                self.current_play_obj.stop()

            if current_state == GripperState.GOOD and bin_id is not None:
                self.reset_state()
                self.target_picked_up = True
                self.target_bin_id = bin_id
                self.pickup_time = now
                self.global_suppress_until_next_pickup = False

        # Stop audio if bin is coming down
        if self.bin_coming_down:
            if self.current_play_obj and self.current_play_obj.is_playing():
                self.current_play_obj.stop()
            if not bin_in_frame:
                if self.target_bin_id is not None:
                    self.handled_bins.add(self.target_bin_id)
                self.reset_state()
                self.global_suppress_until_next_pickup = True
            return

        # Pickup timeout handling
        if self.target_picked_up and self.pickup_time and now - self.pickup_time > self.pickup_timeout:
            self.reset_state()
            self.global_suppress_until_next_pickup = True
            return

        # Detect new pickup
        if current_state == GripperState.GOOD and bin_id is not None and not self.target_picked_up:
            self.target_picked_up = True
            self.target_bin_id = bin_id
            self.pickup_time = now
            return

        # If picked up but gripper no longer GOOD → bin coming down
        if self.target_picked_up and current_state != GripperState.GOOD:
            self.bin_coming_down = True
            if self.current_play_obj and self.current_play_obj.is_playing():
                self.current_play_obj.stop()
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
                # Conditional for Jetson, when headless no audio
                if not self._audio_disabled:
                    try:
                        self.current_play_obj = self.beep_wave_obj.play()
                    except Exception as e:
                        print(f"[AudioHandler] audio play failed: {e}; disabling audio.")
                        self._audio_disabled = True
                        self.current_play_obj = None 
        else:
            if self.current_play_obj and self.current_play_obj.is_playing():
                self.current_play_obj.stop()

    def is_target_picked_up(self):
        """Check if a target bin is currently picked up.

        Returns:
            bool: True if a bin is currently picked up, False otherwise.
        """
        return self.target_picked_up

    def reset_state(self):
        """Reset all tracking state to defaults.

        Clears target bin information, pickup status, and coming down flag.
        Does not clear the handled bins set.
        """
        self.target_picked_up = False
        self.target_bin_id = None
        self.pickup_time = None
        self.bin_coming_down = False
