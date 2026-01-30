"""
Speech Transcription Module
Supporta Google Speech Recognition (veloce) e Whisper (offline)
"""

import tempfile
import os
import time
import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)

# Import opzionale di Whisper
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Faster-Whisper non disponibile. Solo Google Speech disponibile.")


class SpeechTranscriber:
    """
    Transcriber universale con supporto Google e Whisper
    """
    
    def __init__(self, method="google", whisper_model="small", whisper_device="cpu"):
        """
        Initialize transcriber
        
        Args:
            method (str): "google" o "whisper"
            whisper_model (str): Modello Whisper (se method="whisper")
            whisper_device (str): Device per Whisper (cpu/cuda)
        """
        self.method = method.lower()
        self.whisper_model_name = whisper_model
        self.whisper_device = whisper_device
        self.whisper_model = None
        
        if self.method == "whisper":
            self._init_whisper()
        else:
            logger.info("Trascrizione: Google Speech Recognition")
    
    def _init_whisper(self):
        """Inizializza Whisper (solo se richiesto)"""
        if not WHISPER_AVAILABLE:
            logger.error("Whisper richiesto ma non disponibile!")
            raise ImportError("faster-whisper non installato")
        
        logger.info("Loading Whisper model: {}...".format(self.whisper_model_name))
        try:
            self.whisper_model = WhisperModel(
                self.whisper_model_name,
                device=self.whisper_device,
                compute_type="int8" if self.whisper_device == "cpu" else "float16",
                num_workers=1
            )
            logger.info("✓ Whisper {} loaded successfully!".format(self.whisper_model_name))
        except Exception as e:
            logger.error("✗ Failed to load Whisper: {}".format(e))
            raise
    
    def transcribe(self, audio_data, language="it-IT"):
        """
        Trascrivi audio con il metodo selezionato
        
        Args:
            audio_data: AudioData from speech_recognition
            language (str): Codice lingua ("it-IT" per Google, "it" per Whisper)
            
        Returns:
            tuple: (text, info_dict)
        """
        if self.method == "google":
            return self._transcribe_google(audio_data, language)
        elif self.method == "whisper":
            # Converti language code se necessario
            lang = language.split('-')[0] if '-' in language else language
            return self._transcribe_whisper(audio_data, lang)
        else:
            raise ValueError("Metodo non valido: {}".format(self.method))
    
    def _transcribe_google(self, audio_data, language="it-IT"):
        """
        Trascrivi usando Google Speech Recognition (veloce e preciso)
        
        Args:
            audio_data: AudioData oggetto
            language (str): Codice lingua (es. "it-IT")
            
        Returns:
            tuple: (text, info_dict)
        """
        try:
            logger.info("📝 Trascrizione con Google Speech Recognition...")
            start_time = time.time()
            
            # Trascrivi
            text = sr.Recognizer().recognize_google(audio_data, language=language)
            
            elapsed = time.time() - start_time
            
            logger.info("✓ Trascrizione completata in {:.2f}s".format(elapsed))
            logger.info("💬 Trascritto: '{}'".format(text))
            
            info = {
                'text': text,
                'language': language,
                'method': 'google',
                'duration': elapsed,
                'confidence': 'high'  # Google non fornisce score ma è affidabile
            }
            
            return text, info
            
        except sr.UnknownValueError:
            logger.warning("❌ Google non ha capito l'audio")
            return "", {'error': 'unknown_value', 'method': 'google'}
            
        except sr.RequestError as e:
            logger.error("❌ Errore richiesta Google: {}".format(e))
            return "", {'error': str(e), 'method': 'google'}
        
        except Exception as e:
            logger.error("❌ Errore generico: {}".format(e))
            return "", {'error': str(e), 'method': 'google'}
    
    def _transcribe_whisper(self, audio_data, language="it"):
        """
        Trascrivi usando Whisper (offline ma più lento)
        
        Args:
            audio_data: AudioData oggetto
            language (str): Codice lingua (es. "it")
            
        Returns:
            tuple: (text, info_dict)
        """
        temp_file = None
        
        try:
            # Salva audio temporaneo
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, mode='wb') as f:
                f.write(audio_data.get_wav_data())
                temp_file = f.name
            
            logger.info("📝 Trascrizione con Whisper...")
            start_time = time.time()
            
            # Trascrivi
            segments, info = self.whisper_model.transcribe(
                temp_file,
                language=language,
                beam_size=5,
                temperature=0.0,
                vad_filter=True,
                vad_parameters=dict(
                    threshold=0.5,
                    min_speech_duration_ms=250,
                    min_silence_duration_ms=800
                )
            )
            
            # Estrai testo
            segments_list = list(segments)
            text = " ".join([seg.text for seg in segments_list]).strip()
            
            elapsed = time.time() - start_time
            
            logger.info("✓ Trascrizione completata in {:.2f}s".format(elapsed))
            logger.info("  Lingua: {} (conf: {:.2%})".format(info.language, info.language_probability))
            logger.info("💬 Trascritto: '{}'".format(text))
            
            # Calcola confidenza media
            avg_logprob = sum([s.avg_logprob for s in segments_list]) / len(segments_list) if segments_list else -1
            
            info_dict = {
                'text': text,
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': info.duration,
                'method': 'whisper',
                'avg_logprob': avg_logprob
            }
            
            return text, info_dict
            
        finally:
            # Cleanup
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    def transcribe_with_retry(self, audio_data, language="it-IT", max_retries=2):
        """
        Trascrivi con retry automatico
        
        Args:
            audio_data: AudioData oggetto
            language (str): Codice lingua
            max_retries (int): Numero massimo tentativi
            
        Returns:
            tuple: (text, info_dict)
        """
        for attempt in range(max_retries):
            text, info = self.transcribe(audio_data, language)
            
            # Se Google ha successo, ritorna subito
            if self.method == "google" and text:
                return text, info
            
            # Se Whisper ha successo, ritorna
            if self.method == "whisper" and text:
                return text, info
            
            # Se fallito, riprova
            if attempt < max_retries - 1:
                logger.warning("Tentativo {} fallito, riprovo...".format(attempt + 1))
                time.sleep(0.5)
        
        # Tutti i tentativi falliti
        logger.error("Trascrizione fallita dopo {} tentativi".format(max_retries))
        return "", {'error': 'max_retries_exceeded', 'method': self.method}


class GoogleTranscriber:
    """
    Transcriber semplificato solo per Google (più leggero)
    """
    
    def __init__(self):
        """Inizializza Google transcriber"""
        self.recognizer = sr.Recognizer()
        logger.info("✓ Google Speech Recognition ready")
    
    def transcribe(self, audio_data, language="it-IT"):
        """
        Trascrivi audio con Google
        
        Args:
            audio_data: AudioData from speech_recognition
            language (str): Codice lingua (default: "it-IT")
            
        Returns:
            str or None: Testo trascritto o None se fallito
        """
        try:
            logger.info("📝 Trascrizione con Google...")
            start_time = time.time()
            
            text = self.recognizer.recognize_google(audio_data, language=language)
            
            elapsed = time.time() - start_time
            logger.info("✓ Trascritto in {:.2f}s: '{}'".format(elapsed, text))
            
            return text
            
        except sr.UnknownValueError:
            logger.warning("❌ Audio non comprensibile")
            return None
            
        except sr.RequestError as e:
            logger.error("❌ Errore Google API: {}".format(e))
            return None
            
        except Exception as e:
            logger.error("❌ Errore: {}".format(e))
            return None
    
    def transcribe_with_retry(self, audio_data, language="it-IT", max_retries=3):
        """
        Trascrivi con retry automatico
        
        Returns:
            str or None: Testo trascritto
        """
        for attempt in range(max_retries):
            text = self.transcribe(audio_data, language)
            
            if text:
                return text
            
            if attempt < max_retries - 1:
                logger.warning("Tentativo {} fallito, riprovo...".format(attempt + 1))
                time.sleep(0.3)
        
        logger.error("Trascrizione fallita dopo {} tentativi".format(max_retries))
        return None


# Factory function per creare il transcriber appropriato
def create_transcriber(method="google", **kwargs):
    """
    Factory per creare il transcriber appropriato
    
    Args:
        method (str): "google" o "whisper"
        **kwargs: Argomenti aggiuntivi per il transcriber
        
    Returns:
        Transcriber appropriato
    """
    if method == "google":
        return GoogleTranscriber()
    elif method == "whisper":
        return SpeechTranscriber(
            method="whisper",
            whisper_model=kwargs.get('model', 'small'),
            whisper_device=kwargs.get('device', 'cpu')
        )
    else:
        raise ValueError("Metodo non supportato: {}. Usa 'google' o 'whisper'".format(method))
