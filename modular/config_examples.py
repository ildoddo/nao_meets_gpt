"""
Esempi di configurazione per diversi scenari d'uso
Copia una di queste configurazioni in brain.py
"""

# ============================================================
# CONFIGURAZIONE 1: PRODUCTION (CONSIGLIATA)
# Usa Google per velocità massima e precisione
# ============================================================

class ProductionConfig:
    """Configurazione ottimizzata per produzione/demo"""
    
    # NAO
    NAO_SERVER_URL = "http://192.168.1.100:5004"
    
    # Trascrizione: Google (veloce e preciso)
    TRANSCRIPTION_METHOD = "google"
    TRANSCRIPTION_LANGUAGE = "it-IT"
    
    # Audio: NAO microphone
    USE_NAO_MICROPHONE = True
    USE_PUSH_TO_TALK = False
    ENERGY_THRESHOLD = 4000
    DYNAMIC_ENERGY = True
    
    # GPT: GitHub Models
    GPT_MODEL = "github/gpt-4o-mini"
    GPT_API_BASE = "https://models.inference.ai.azure.com"
    GPT_MAX_TOKENS = 250
    GPT_TEMPERATURE = 0.7
    
    # Limiti
    TOKEN_LIMIT = 4096
    
    # File
    SYSTEM_PROMPT_FILE = "system_prompt.txt"
    CONVERSATION_FILE = "conversation_context.txt"


# ============================================================
# CONFIGURAZIONE 2: OFFLINE MODE
# Usa Whisper per funzionare senza internet
# ============================================================

class OfflineConfig:
    """Configurazione per uso offline (senza internet)"""
    
    NAO_SERVER_URL = "http://192.168.1.100:5004"
    
    # Trascrizione: Whisper (offline)
    TRANSCRIPTION_METHOD = "whisper"
    TRANSCRIPTION_LANGUAGE = "it"
    WHISPER_MODEL = "small"  # Compromesso velocità/accuratezza
    WHISPER_DEVICE = "cpu"   # o "cuda" se hai GPU
    
    # Audio
    USE_NAO_MICROPHONE = True
    USE_PUSH_TO_TALK = False
    ENERGY_THRESHOLD = 4000
    DYNAMIC_ENERGY = True
    VAD_THRESHOLD = 0.5
    
    # GPT: Locale (es. Ollama)
    GPT_MODEL = "ollama/llama2"  # Modello locale
    GPT_API_BASE = "http://localhost:11434"
    GPT_MAX_TOKENS = 250
    GPT_TEMPERATURE = 0.7
    
    TOKEN_LIMIT = 4096
    SYSTEM_PROMPT_FILE = "system_prompt.txt"
    CONVERSATION_FILE = "conversation_context.txt"


# ============================================================
# CONFIGURAZIONE 3: DEVELOPMENT
# Usa microfono computer per sviluppo più veloce
# ============================================================

class DevelopmentConfig:
    """Configurazione per sviluppo (microfono laptop)"""
    
    NAO_SERVER_URL = "http://192.168.1.100:5004"
    
    # Trascrizione: Google (veloce)
    TRANSCRIPTION_METHOD = "google"
    TRANSCRIPTION_LANGUAGE = "it-IT"
    
    # Audio: Computer microphone (migliore qualità)
    USE_NAO_MICROPHONE = False  # ← Usa laptop!
    USE_PUSH_TO_TALK = True     # ← Premi INVIO per parlare
    ENERGY_THRESHOLD = 3000
    DYNAMIC_ENERGY = True
    
    # GPT
    GPT_MODEL = "github/gpt-4o-mini"
    GPT_API_BASE = "https://models.inference.ai.azure.com"
    GPT_MAX_TOKENS = 250
    GPT_TEMPERATURE = 0.7
    
    TOKEN_LIMIT = 4096
    SYSTEM_PROMPT_FILE = "system_prompt.txt"
    CONVERSATION_FILE = "conversation_context.txt"


# ============================================================
# CONFIGURAZIONE 4: HIGH ACCURACY
# Massima precisione (più lento)
# ============================================================

class HighAccuracyConfig:
    """Configurazione per massima accuratezza"""
    
    NAO_SERVER_URL = "http://192.168.1.100:5004"
    
    # Trascrizione: Whisper medium (molto preciso)
    TRANSCRIPTION_METHOD = "whisper"
    TRANSCRIPTION_LANGUAGE = "it"
    WHISPER_MODEL = "medium"  # Più preciso
    WHISPER_DEVICE = "cpu"
    
    # Audio: Laptop (miglior qualità)
    USE_NAO_MICROPHONE = False
    USE_PUSH_TO_TALK = True
    ENERGY_THRESHOLD = 3000
    DYNAMIC_ENERGY = True
    VAD_THRESHOLD = 0.4  # Più sensibile
    
    # GPT: Modello più potente
    GPT_MODEL = "github/gpt-4o"  # Non mini
    GPT_API_BASE = "https://models.inference.ai.azure.com"
    GPT_MAX_TOKENS = 500  # Risposte più lunghe
    GPT_TEMPERATURE = 0.6  # Più conservativo
    
    TOKEN_LIMIT = 8192  # Più contesto
    SYSTEM_PROMPT_FILE = "system_prompt.txt"
    CONVERSATION_FILE = "conversation_context.txt"


# ============================================================
# CONFIGURAZIONE 5: FAST TESTING
# Per test veloci durante sviluppo
# ============================================================

class FastTestConfig:
    """Configurazione per test rapidi"""
    
    NAO_SERVER_URL = "http://192.168.1.100:5004"
    
    # Trascrizione: Google (velocissimo)
    TRANSCRIPTION_METHOD = "google"
    TRANSCRIPTION_LANGUAGE = "it-IT"
    
    # Audio: Push-to-talk per controllo
    USE_NAO_MICROPHONE = False
    USE_PUSH_TO_TALK = True  # Controllo totale
    ENERGY_THRESHOLD = 2000
    DYNAMIC_ENERGY = False
    
    # GPT: Risposte brevi
    GPT_MODEL = "github/gpt-4o-mini"
    GPT_API_BASE = "https://models.inference.ai.azure.com"
    GPT_MAX_TOKENS = 100  # Risposte corte
    GPT_TEMPERATURE = 0.5
    
    TOKEN_LIMIT = 2048
    SYSTEM_PROMPT_FILE = "system_prompt.txt"
    CONVERSATION_FILE = "conversation_context.txt"


# ============================================================
# CONFIGURAZIONE 6: NOISY ENVIRONMENT
# Per ambienti rumorosi (uffici, fiere)
# ============================================================

class NoisyEnvironmentConfig:
    """Configurazione per ambienti rumorosi"""
    
    NAO_SERVER_URL = "http://192.168.1.100:5004"
    
    # Trascrizione: Google
    TRANSCRIPTION_METHOD = "google"
    TRANSCRIPTION_LANGUAGE = "it-IT"
    
    # Audio: Configurazione anti-rumore
    USE_NAO_MICROPHONE = True
    USE_PUSH_TO_TALK = True  # IMPORTANTE: evita attivazioni false
    ENERGY_THRESHOLD = 6000  # Molto alto
    DYNAMIC_ENERGY = False   # Fisso per consistenza
    
    # GPT
    GPT_MODEL = "github/gpt-4o-mini"
    GPT_API_BASE = "https://models.inference.ai.azure.com"
    GPT_MAX_TOKENS = 200
    GPT_TEMPERATURE = 0.7
    
    TOKEN_LIMIT = 4096
    SYSTEM_PROMPT_FILE = "system_prompt.txt"
    CONVERSATION_FILE = "conversation_context.txt"


# ============================================================
# COME USARE QUESTE CONFIGURAZIONI
# ============================================================

"""
In brain.py, sostituisci la classe Config con una di queste:

# Esempio 1: Usa production config
from config_examples import ProductionConfig as Config

# Esempio 2: Usa development config
from config_examples import DevelopmentConfig as Config

# Esempio 3: Copia manualmente
class Config:
    # Copia i parametri da ProductionConfig
    NAO_SERVER_URL = "http://..."
    TRANSCRIPTION_METHOD = "google"
    # ...

Oppure crea la tua config personalizzata!
"""

# ============================================================
# PARAMETRI SPIEGATI
# ============================================================

"""
NAO_SERVER_URL: 
  URL del server body.py su NAO
  Esempio: "http://nao.local:5004"

TRANSCRIPTION_METHOD:
  "google" = Veloce, preciso, richiede internet
  "whisper" = Offline, più lento

TRANSCRIPTION_LANGUAGE:
  "it-IT" per Google
  "it" per Whisper

USE_NAO_MICROPHONE:
  True = Usa microfoni NAO (più robotico)
  False = Usa microfono computer (migliore qualità)

USE_PUSH_TO_TALK:
  True = Premi INVIO per parlare (controllo totale)
  False = Sempre in ascolto (più naturale)

ENERGY_THRESHOLD:
  2000-3000 = Ambiente silenzioso
  4000-5000 = Ambiente normale
  6000+ = Ambiente rumoroso

DYNAMIC_ENERGY:
  True = Si adatta automaticamente al rumore
  False = Usa ENERGY_THRESHOLD fisso

GPT_MODEL:
  "github/gpt-4o-mini" = Veloce, economico
  "github/gpt-4o" = Più intelligente, lento
  "anthropic/claude-3-sonnet" = Alternativa

GPT_MAX_TOKENS:
  100-200 = Risposte brevi
  250-300 = Risposte normali
  400+ = Risposte dettagliate

GPT_TEMPERATURE:
  0.5 = Più conservativo, ripetitivo
  0.7 = Bilanciato (consigliato)
  0.9+ = Più creativo, meno prevedibile
"""
