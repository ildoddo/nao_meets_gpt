"""
Configurazioni Audio Ottimizzate per Diversi Scenari
Risolve il problema delle frasi tagliate prematuramente
"""

# ============================================================
# PROBLEMA: Frasi tagliate prematuramente
# 
# CAUSA PRINCIPALE: pause_threshold troppo basso (1.2s)
# La persona fa pause naturali > 1.2s durante la frase
# 
# SOLUZIONE: Aumentare pause_threshold a 1.5-2.0s
# ============================================================


class AudioConfig:
    """Classe base per configurazioni audio"""
    pass


# ============================================================
# CONFIG 1: AMBIENTE SILENZIOSO (Casa, Ufficio privato)
# ============================================================

class QuietEnvironmentConfig(AudioConfig):
    """
    Ottimizzato per: Casa, ufficio silenzioso
    Problema risolto: Frasi tagliate durante pause naturali
    """
    
    # PARAMETRI VAD - OTTIMIZZATI
    PAUSE_THRESHOLD = 1.8        # ⬆️ Aumentato da 1.2s - CHIAVE!
    PHRASE_THRESHOLD = 0.3       # Minimo per considerare inizio frase
    NON_SPEAKING_DURATION = 0.3  # Tempo per rilevare fine parola
    PHRASE_TIME_LIMIT = 20       # ⬆️ Max durata frase (era 15s)
    
    # ENERGIA
    ENERGY_THRESHOLD = 3000      # ⬇️ Ridotto (ambiente silenzioso)
    DYNAMIC_ENERGY = True
    DYNAMIC_ENERGY_RATIO = 1.3   # ⬇️ Meno aggressivo (era 1.5)
    DYNAMIC_ENERGY_DAMPING = 0.10
    
    # CALIBRAZIONE
    CALIBRATION_DURATION = 2.0
    NOISE_LEVEL = 'quiet'
    
    # FEEDBACK
    VISUAL_FEEDBACK = True
    QUALITY_ANALYSIS = True


# ============================================================
# CONFIG 2: AMBIENTE NORMALE (Ufficio aperto, Laboratorio)
# ============================================================

class NormalEnvironmentConfig(AudioConfig):
    """
    Ottimizzato per: Ufficio con colleghi, laboratorio
    Bilanciamento tra sensibilità e resistenza al rumore
    """
    
    # PARAMETRI VAD
    PAUSE_THRESHOLD = 2.0        # ⬆️ AUMENTATO - evita tagli!
    PHRASE_THRESHOLD = 0.3
    NON_SPEAKING_DURATION = 0.3
    PHRASE_TIME_LIMIT = 20
    
    # ENERGIA
    ENERGY_THRESHOLD = 4000      # Threshold medio
    DYNAMIC_ENERGY = True
    DYNAMIC_ENERGY_RATIO = 1.3
    DYNAMIC_ENERGY_DAMPING = 0.10
    
    # CALIBRAZIONE
    CALIBRATION_DURATION = 2.5   # ⬆️ Più lunga per analizzare rumore
    NOISE_LEVEL = 'normal'
    
    # FEEDBACK
    VISUAL_FEEDBACK = True
    QUALITY_ANALYSIS = True


# ============================================================
# CONFIG 3: AMBIENTE RUMOROSO (Fiera, Open space affollato)
# ============================================================

class NoisyEnvironmentConfig(AudioConfig):
    """
    Ottimizzato per: Fiere, eventi, open space molto rumorosi
    Push-to-talk FORTEMENTE consigliato
    """
    
    # PARAMETRI VAD
    PAUSE_THRESHOLD = 2.5        # ⬆️⬆️ Molto alto - evita falsi positivi
    PHRASE_THRESHOLD = 0.4       # ⬆️ Più stringente
    NON_SPEAKING_DURATION = 0.4
    PHRASE_TIME_LIMIT = 20
    
    # ENERGIA
    ENERGY_THRESHOLD = 6000      # ⬆️ Alto per filtare rumore
    DYNAMIC_ENERGY = False       # ❌ Meglio statico in ambienti rumorosi
    DYNAMIC_ENERGY_RATIO = 1.5
    DYNAMIC_ENERGY_DAMPING = 0.05
    
    # CALIBRAZIONE
    CALIBRATION_DURATION = 3.0   # ⬆️⬆️ Calibrazione lunga
    NOISE_LEVEL = 'noisy'
    
    # FEEDBACK
    VISUAL_FEEDBACK = True
    QUALITY_ANALYSIS = True
    
    # RACCOMANDAZIONE
    USE_PUSH_TO_TALK = True  # ⚠️ FORTEMENTE raccomandato


# ============================================================
# CONFIG 4: CONVERSAZIONE NATURALE (Massima tolleranza pause)
# ============================================================

class NaturalConversationConfig(AudioConfig):
    """
    Ottimizzato per: Conversazioni naturali con molte pause
    Es: persona che pensa mentre parla, anziani, bambini
    
    RISOLVE: Il problema principale delle frasi tagliate!
    """
    
    # PARAMETRI VAD - MASSIMA TOLLERANZA
    PAUSE_THRESHOLD = 2.5        # ⬆️⬆️⬆️ Molto tollerante!
    PHRASE_THRESHOLD = 0.2       # ⬇️ Più sensibile all'inizio
    NON_SPEAKING_DURATION = 0.2  # ⬇️ Reattivo su singole parole
    PHRASE_TIME_LIMIT = 30       # ⬆️⬆️ Frasi molto lunghe OK
    
    # ENERGIA
    ENERGY_THRESHOLD = 3500
    DYNAMIC_ENERGY = True
    DYNAMIC_ENERGY_RATIO = 1.2   # ⬇️⬇️ Molto meno aggressivo
    DYNAMIC_ENERGY_DAMPING = 0.08
    
    # CALIBRAZIONE
    CALIBRATION_DURATION = 2.5
    NOISE_LEVEL = 'normal'
    
    # FEEDBACK
    VISUAL_FEEDBACK = True
    QUALITY_ANALYSIS = True


# ============================================================
# CONFIG 5: VELOCE (Testing, sviluppo)
# ============================================================

class FastTestConfig(AudioConfig):
    """
    Per test rapidi durante sviluppo
    """
    
    # PARAMETRI VAD
    PAUSE_THRESHOLD = 1.0        # Corto per test veloci
    PHRASE_THRESHOLD = 0.2
    NON_SPEAKING_DURATION = 0.3
    PHRASE_TIME_LIMIT = 10
    
    # ENERGIA
    ENERGY_THRESHOLD = 3000
    DYNAMIC_ENERGY = True
    DYNAMIC_ENERGY_RATIO = 1.3
    DYNAMIC_ENERGY_DAMPING = 0.15
    
    # CALIBRAZIONE
    CALIBRATION_DURATION = 1.0   # Veloce
    NOISE_LEVEL = 'normal'
    
    # FEEDBACK
    VISUAL_FEEDBACK = False      # Meno output
    QUALITY_ANALYSIS = False


# ============================================================
# CONFIG 6: CUSTOM (Template per tuning manuale)
# ============================================================

class CustomAudioConfig(AudioConfig):
    """
    Template per creare la tua configurazione personalizzata
    
    Guida al tuning:
    
    1. PAUSE_THRESHOLD (più importante!)
       - Troppo basso (< 1.5s) → Frasi tagliate ❌
       - Ideale (1.8-2.5s) → Conversazione naturale ✅
       - Troppo alto (> 3s) → Lentezza eccessiva ⚠️
    
    2. ENERGY_THRESHOLD
       - Troppo basso → False starts, rumore ❌
       - Ideale → Rileva voce, ignora rumore ✅
       - Troppo alto → Non rileva voce ❌
    
    3. DYNAMIC_ENERGY
       - True → Si adatta al rumore ✅ (raccomandato)
       - False → Consistente ma meno flessibile
    
    4. PHRASE_TIME_LIMIT
       - Troppo corto → Taglia frasi lunghe ❌
       - 15-20s → Standard ✅
       - 30s+ → Conversazioni complesse ✅
    """
    
    # VAD - INIZIA DA QUI E TWEAKA
    PAUSE_THRESHOLD = 2.0        # ⬅️ SE FRASI TAGLIATE: AUMENTA A 2.5
    PHRASE_THRESHOLD = 0.3       # Lascia invariato
    NON_SPEAKING_DURATION = 0.3  # Lascia invariato
    PHRASE_TIME_LIMIT = 20       # ⬅️ SE FRASI LUNGHE: AUMENTA A 30
    
    # ENERGIA
    ENERGY_THRESHOLD = 4000      # ⬅️ REGOLA in base a calibrazione
    DYNAMIC_ENERGY = True        # ⬅️ True raccomandato
    DYNAMIC_ENERGY_RATIO = 1.3
    DYNAMIC_ENERGY_DAMPING = 0.10
    
    # CALIBRAZIONE
    CALIBRATION_DURATION = 2.0
    NOISE_LEVEL = 'normal'       # quiet/normal/noisy
    
    # FEEDBACK
    VISUAL_FEEDBACK = True
    QUALITY_ANALYSIS = True


# ============================================================
# COME USARE QUESTE CONFIGURAZIONI
# ============================================================

"""
In brain.py, aggiungi questi parametri alla classe Config:

# Metodo 1: Importa config predefinita
from audio_configs import NaturalConversationConfig

class Config:
    # ... altri parametri ...
    
    # Audio VAD parameters
    PAUSE_THRESHOLD = NaturalConversationConfig.PAUSE_THRESHOLD
    PHRASE_TIME_LIMIT = NaturalConversationConfig.PHRASE_TIME_LIMIT
    ENERGY_THRESHOLD = NaturalConversationConfig.ENERGY_THRESHOLD
    # ...

# Metodo 2: Valori diretti
class Config:
    # ... altri parametri ...
    
    # Audio VAD - OTTIMIZZATO per evitare tagli
    PAUSE_THRESHOLD = 2.0        # ⬆️ Chiave per evitare tagli!
    PHRASE_THRESHOLD = 0.3
    NON_SPEAKING_DURATION = 0.3
    PHRASE_TIME_LIMIT = 20
    
    # Energy
    ENERGY_THRESHOLD = 4000
    DYNAMIC_ENERGY = True
    DYNAMIC_ENERGY_RATIO = 1.3

Poi in audio_utils.py modificare configure_recognizer() per usare questi parametri.
"""


# ============================================================
# TROUBLESHOOTING
# ============================================================

"""
PROBLEMA: Frasi ancora tagliate

SOLUZIONI (in ordine di priorità):

1. ⬆️ Aumenta PAUSE_THRESHOLD
   PAUSE_THRESHOLD = 2.5  # o anche 3.0

2. ⬆️ Aumenta PHRASE_TIME_LIMIT
   PHRASE_TIME_LIMIT = 30  # per frasi molto lunghe

3. ⬇️ Riduci DYNAMIC_ENERGY_RATIO
   DYNAMIC_ENERGY_RATIO = 1.2  # meno aggressivo

4. Usa push-to-talk
   USE_PUSH_TO_TALK = True  # controllo manuale

5. Analizza i log
   Abilita QUALITY_ANALYSIS = True
   Guarda le raccomandazioni nel log


PROBLEMA: False starts (si attiva sul rumore)

SOLUZIONI:

1. ⬆️ Aumenta ENERGY_THRESHOLD
   ENERGY_THRESHOLD = 5000  # o usa 'noisy'

2. ⬆️ Aumenta PHRASE_THRESHOLD
   PHRASE_THRESHOLD = 0.4

3. Disabilita DYNAMIC_ENERGY
   DYNAMIC_ENERGY = False

4. Calibrazione più lunga
   CALIBRATION_DURATION = 3.0


PROBLEMA: Non rileva quando parlo

SOLUZIONI:

1. ⬇️ Riduci ENERGY_THRESHOLD
   ENERGY_THRESHOLD = 3000

2. Verifica calibrazione
   Guarda il log della calibrazione
   Threshold dovrebbe essere 2000-6000

3. Prova microfono computer
   USE_NAO_MICROPHONE = False
"""
