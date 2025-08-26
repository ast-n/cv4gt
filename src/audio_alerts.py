import simpleaudio as sa
import numpy as np
import time
from enum import Enum


class GripperState(Enum):
    """
    He lives here now
    """
    NEUTRAL = 0
    GOOD = 1
    BAD = 2
    NONE = 3


class AudioHandler:
    def __init__(self, frequency=880, duration_ms=75):
        """
        Init audio handler by generation of reuable beep sound.
        """

        # Sound gen - standard sine wave
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
        self.target_picked_up = False
        self.target_bin_id = None

        print("Audio Handler UP")

    def update(self, current_state: GripperState, bin_in_frame: bool, bin_is_above_cutoff: bool, bin_id=None):
        """
        Updates the handler with current frame state, play audio if needed
        ONLY METHOD THAT NEEDS TO BE CALLED
        """
        # If a target has been picked up, check if it has disappeared, reset
        if self.target_picked_up:
            is_different_bin = bin_id is not None and bin_id != self.target_bin_id
            if not bin_in_frame or is_different_bin:
                self.reset_state()
            return
        
        if current_state == GripperState.GOOD:
            self.target_picked_up = True
            self.target_bin_id = bin_id
            return

        # Determine if beep is needed
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

    def is_target_picked_up(self):
        """
        Public method to query state
        """
        return self.target_picked_up
    
    def reset_state(self):
        """
        Internal method to reset the state.
        """
        self.target_picked_up = False
        self.target_bin_id = None