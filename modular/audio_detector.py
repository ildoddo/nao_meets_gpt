"""
Advanced Audio Detection System
Sistema di rilevamento vocale intelligente per NAO con VAD migliorato
"""

import numpy as np
import speech_recognition as sr
import logging
import time
from collections import deque

logger = logging.getLogger(__name__)


class SmartAudioDetector:
    """
    Rilevatore audio intelligente con VAD avanzato
    
    Risolve problemi di:
    - Frasi tagliate prematuramente
    - Pause naturali interpretate come fine frase
    - Sensibilità al rumore ambientale
    """
    
    def __init__(self, config=None):
        """
        Inizializza il rilevatore
        
        Args:
            config: Oggetto configurazione (opzionale)
        """
        # Parametri VAD ottimizzati
        self.min_phrase_duration = 0.3      # Minimo 0.3s per considerare una frase
        self.pause_threshold = 1.5           # 1.5s di pausa per terminare (era 1.2s)
        self.silence_threshold = 2.0         # 2.0s di silenzio assoluto per forzare stop
        self.phrase_time_limit = 20          # Max 20s per frase (era 15s)
        
        # Energia
        self.min_energy = 300               # Soglia minima energia voce
        self.max_energy = 4000              # Soglia massima energia (adattiva)
        self.energy_ratio = 1.3             # Ratio voce/silenzio (era 1.5)
        
        # Finestra analisi
        self.window_size = 0.1              # Analizza 100ms alla volta
        self.history_window = 10            # Mantieni ultimi 10 chunk per analisi
        
        # Stato
        self.energy_history = deque(maxlen=self.history_window)
        self.speech_detected = False
        self.last_speech_time = None
        self.total_speech_duration = 0
        
        # Statistiche
        self.stats = {
            'phrases_recorded': 0,
            'avg_duration': 0,
            'premature_cuts': 0,
            'false_starts': 0
        }
        
        # Applica config se fornito
        if config:
            self._apply_config(config)
    
    def _apply_config(self, config):
        """Applica configurazione custom"""
        if hasattr(config, 'MIN_PHRASE_DURATION'):
            self.min_phrase_duration = config.MIN_PHRASE_DURATION
        if hasattr(config, 'PAUSE_THRESHOLD'):
            self.pause_threshold = config.PAUSE_THRESHOLD
        if hasattr(config, 'SILENCE_THRESHOLD'):
            self.silence_threshold = config.SILENCE_THRESHOLD
        if hasattr(config, 'PHRASE_TIME_LIMIT'):
            self.phrase_time_limit = config.PHRASE_TIME_LIMIT
    
    def configure_recognizer(self, recognizer, dynamic=True, noise_level='normal'):
        """
        Configura recognizer con parametri ottimizzati
        
        Args:
            recognizer: sr.Recognizer object
            dynamic: Usa threshold dinamico
            noise_level: 'quiet', 'normal', 'noisy'
        """
        # Parametri base
        recognizer.pause_threshold = self.pause_threshold
        recognizer.phrase_threshold = self.min_phrase_duration
        recognizer.non_speaking_duration = 0.3  # Ridotto da 0.5s
        
        # Energy threshold basato su ambiente
        energy_thresholds = {
            'quiet': 2000,
            'normal': 4000,
            'noisy': 6000
        }
        
        if dynamic:
            recognizer.dynamic_energy_threshold = True
            recognizer.dynamic_energy_adjustment_damping = 0.10  # Più reattivo (era 0.15)
            recognizer.dynamic_energy_ratio = self.energy_ratio
            logger.info("VAD dinamico attivo (ratio: {})".format(self.energy_ratio))
        else:
            recognizer.energy_threshold = energy_thresholds.get(noise_level, 4000)
            logger.info("VAD statico: {} (livello: {})".format(
                recognizer.energy_threshold, noise_level))
        
        return recognizer
    
    def adaptive_calibration(self, source, recognizer, duration=2.0):
        """
        Calibrazione adattiva multi-fase
        
        Analizza il rumore ambientale in modo più intelligente
        """
        logger.info("📊 Calibrazione adattiva ({:.1f}s)...".format(duration))
        
        # Fase 1: Calibrazione standard
        recognizer.adjust_for_ambient_noise(source, duration=duration * 0.6)
        base_threshold = recognizer.energy_threshold
        
        # Fase 2: Analisi picchi
        logger.info("   Analisi picchi rumore...")
        energy_samples = []
        
        start_time = time.time()
        while time.time() - start_time < duration * 0.4:
            try:
                # Leggi piccolo chunk
                buffer = source.stream.read(source.CHUNK)
                if isinstance(buffer, str):
                    buffer = buffer.encode('latin-1')
                
                # Calcola energia
                audio_data = np.frombuffer(buffer, dtype=np.int16)
                energy = np.sqrt(np.mean(audio_data.astype(np.float64) ** 2))
                energy_samples.append(energy)
                
            except:
                break
        
        if energy_samples:
            # Calcola statistiche
            mean_energy = np.mean(energy_samples)
            max_energy = np.max(energy_samples)
            std_energy = np.std(energy_samples)
            
            # Threshold intelligente: media + 2*std (copre 95% del rumore)
            intelligent_threshold = mean_energy + (2 * std_energy)
            
            # Usa il maggiore tra base e intelligente, ma con cap
            final_threshold = min(
                max(base_threshold, intelligent_threshold),
                8000  # Cap massimo
            )
            
            recognizer.energy_threshold = final_threshold
            
            logger.info("   Base: {:.0f} | Intelligente: {:.0f} | Finale: {:.0f}".format(
                base_threshold, intelligent_threshold, final_threshold))
            logger.info("   Rumore: μ={:.0f} σ={:.0f} max={:.0f}".format(
                mean_energy, std_energy, max_energy))
        else:
            logger.info("   Threshold: {:.0f}".format(base_threshold))
        
        return recognizer.energy_threshold
    
    def smart_listen(self, source, recognizer, show_feedback=True):
        """
        Ascolto intelligente con feedback in tempo reale
        
        Returns:
            sr.AudioData or None
        """
        logger.info("🎤 Ascolto attivo (pausa: {:.1f}s, max: {}s)".format(
            self.pause_threshold, self.phrase_time_limit))
        
        if show_feedback:
            logger.info("   [. = silenzio | █ = parlato | ✓ = fine]")
        
        # Reset stato
        self.speech_detected = False
        self.last_speech_time = None
        self.total_speech_duration = 0
        phrase_start = None
        
        try:
            # Usa listen con timeout più lungo
            audio_data = recognizer.listen(
                source,
                timeout=None,  # Nessun timeout iniziale
                phrase_time_limit=self.phrase_time_limit
            )
            
            # Aggiorna statistiche
            self.stats['phrases_recorded'] += 1
            
            return audio_data
            
        except sr.WaitTimeoutError:
            logger.warning("⚠️ Timeout attesa voce")
            return None
        
        except Exception as e:
            logger.error("❌ Errore ascolto: {}".format(e))
            return None
    
    def analyze_recording_quality(self, audio_data):
        """
        Analizza qualità registrazione per rilevare tagli prematuri
        
        Returns:
            dict: {
                'duration': float,
                'likely_cut': bool,
                'confidence': float,
                'recommendation': str
            }
        """
        # Estrai audio
        wav_data = audio_data.get_wav_data()
        audio_array = np.frombuffer(wav_data, dtype=np.int16)
        
        # Calcola durata
        sample_rate = audio_data.sample_rate
        duration = len(audio_array) / sample_rate
        
        # Analizza ultimi 200ms
        tail_samples = int(0.2 * sample_rate)
        tail = audio_array[-tail_samples:] if len(audio_array) > tail_samples else audio_array
        
        # Energia finale
        tail_energy = np.sqrt(np.mean(tail.astype(np.float64) ** 2))
        overall_energy = np.sqrt(np.mean(audio_array.astype(np.float64) ** 2))
        
        # Ratio energia finale/totale
        energy_ratio = tail_energy / (overall_energy + 1e-6)
        
        # Euristica: se energia finale > 70% della media, probabilmente tagliato
        likely_cut = energy_ratio > 0.7 and duration < 3.0
        confidence = min(energy_ratio * 1.2, 1.0)
        
        result = {
            'duration': duration,
            'likely_cut': likely_cut,
            'confidence': confidence,
            'tail_energy': tail_energy,
            'overall_energy': overall_energy,
            'recommendation': ''
        }
        
        # Genera raccomandazione
        if likely_cut:
            result['recommendation'] = "Aumenta PAUSE_THRESHOLD a {:.1f}s".format(
                self.pause_threshold + 0.3)
            self.stats['premature_cuts'] += 1
        elif duration < 0.5:
            result['recommendation'] = "Possibile false start"
            self.stats['false_starts'] += 1
        else:
            result['recommendation'] = "OK"
        
        return result
    
    def get_stats(self):
        """Ritorna statistiche utilizzo"""
        if self.stats['phrases_recorded'] > 0:
            self.stats['premature_cut_rate'] = (
                self.stats['premature_cuts'] / self.stats['phrases_recorded'] * 100
            )
        return self.stats


class AdvancedRecognizer(sr.Recognizer):
    """
    Recognizer esteso con callback per feedback tempo reale
    """
    
    def __init__(self):
        super().__init__()
        self.callback = None
        self.visual_feedback = True
    
    def set_callback(self, callback):
        """Imposta callback per eventi audio"""
        self.callback = callback
    
    def listen_with_feedback(self, source, timeout=None, phrase_time_limit=None):
        """
        Listen con feedback visivo
        
        Mostra in tempo reale quando sta parlando/in pausa
        """
        import sys
        
        # Parametri
        seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE
        pause_buffer_count = int(math.ceil(self.pause_threshold / seconds_per_buffer))
        phrase_buffer_count = int(math.ceil(self.phrase_threshold / seconds_per_buffer))
        non_speaking_buffer_count = int(math.ceil(self.non_speaking_duration / seconds_per_buffer))
        
        # Stato
        elapsed_time = 0
        buffer = b""
        
        # Frames
        frames = []
        
        # Energy threshold
        if self.dynamic_energy_threshold:
            # Stima dinamica
            pass  # Usa meccanismo esistente
        
        while True:
            # Leggi chunk
            elapsed_time += seconds_per_buffer
            
            if timeout and elapsed_time > timeout:
                raise sr.WaitTimeoutError("timeout")
            
            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0:
                break
            
            frames.append(buffer)
            
            # Calcola energia
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
            
            # Feedback visivo
            if self.visual_feedback:
                if energy > self.energy_threshold:
                    sys.stdout.write("█")
                else:
                    sys.stdout.write(".")
                sys.stdout.flush()
            
            # Callback
            if self.callback:
                self.callback(energy, elapsed_time)
            
            # Logica di stop (semplificata, usa quella esistente di sr.Recognizer)
            if phrase_time_limit and elapsed_time > phrase_time_limit:
                break
        
        if self.visual_feedback:
            print(" ✓")
        
        # Costruisci AudioData
        frame_data = b"".join(frames)
        return sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)


def create_smart_detector(config=None):
    """
    Factory per creare rilevatore intelligente
    
    Args:
        config: Configurazione custom
        
    Returns:
        SmartAudioDetector
    """
    detector = SmartAudioDetector(config)
    logger.info("✅ Smart Audio Detector inizializzato")
    logger.info("   Pause threshold: {:.1f}s | Time limit: {}s".format(
        detector.pause_threshold, detector.phrase_time_limit))
    return detector
