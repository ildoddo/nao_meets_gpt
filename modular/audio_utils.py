"""
Audio utilities for NAO robot
Gestisce cattura audio, stream e configurazione
"""

import requests
import numpy as np
import speech_recognition as sr
import logging

logger = logging.getLogger(__name__)


class NaoStream:
    """Wrapper for audio generator"""
    
    def __init__(self, audio_generator):
        self.audio_generator = audio_generator

    def read(self, size=-1):
        try:
            return next(self.audio_generator)
        except StopIteration:
            return b''


class NaoAudioSource(sr.AudioSource):
    """Custom audio source for NAO robot"""

    def __init__(self, server_url, time_between_chunks):
        self.server_url = server_url
        self.time_between_chunks = time_between_chunks
        self.stream = None
        self.is_listening = False
        self.CHUNK = 1365
        self.SAMPLE_RATE = 16000
        self.SAMPLE_WIDTH = 2

    def __enter__(self):
        """Start listening"""
        try:
            response = requests.post(
                "{}/start_listening".format(self.server_url),
                timeout=5
            )
            response.raise_for_status()
            self.is_listening = True
            self.stream = NaoStream(self.audio_generator())
            logger.info("✓ NAO audio stream started")
            return self
        except Exception as e:
            logger.error("✗ Failed to start NAO listening: {}".format(e))
            raise

    def audio_generator(self):
        """Generator that fetches audio chunks from NAO"""
        import time
        
        while self.is_listening:
            try:
                response = requests.get(
                    "{}/get_audio_chunk".format(self.server_url),
                    timeout=10
                )
                response.raise_for_status()
                yield response.content
                
                buffer_response = requests.get(
                    "{}/get_server_buffer_length".format(self.server_url),
                    timeout=5
                )
                current_buffer_length = buffer_response.json()["length"]
                
                # Adaptive timing
                correcting_factor = 1.0 / (1.0 + np.exp(current_buffer_length - np.pi))
                corrected_time = self.time_between_chunks * correcting_factor
                time.sleep(corrected_time)
                
            except requests.exceptions.Timeout:
                logger.warning("Audio chunk request timed out")
                time.sleep(0.1)
            except Exception as e:
                logger.error("Error in audio generator: {}".format(e))
                time.sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop listening"""
        self.is_listening = False
        try:
            requests.post("{}/stop_listening".format(self.server_url), timeout=5)
            logger.info("✓ NAO audio stream stopped")
        except Exception as e:
            logger.error("✗ Failed to stop NAO listening: {}".format(e))


def configure_recognizer(energy_threshold=4000, dynamic_energy=True):
    """
    Configure speech recognizer with optimal parameters
    
    Args:
        energy_threshold (int): Energy threshold for voice detection
        dynamic_energy (bool): Use dynamic energy adjustment
        
    Returns:
        sr.Recognizer: Configured recognizer
    """
    recognizer = sr.Recognizer()
    
    recognizer.pause_threshold = 1.2
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.5
    
    if dynamic_energy:
        recognizer.dynamic_energy_threshold = True
        recognizer.dynamic_energy_adjustment_damping = 0.15
        recognizer.dynamic_energy_ratio = 1.5
    else:
        recognizer.energy_threshold = energy_threshold
    
    return recognizer
