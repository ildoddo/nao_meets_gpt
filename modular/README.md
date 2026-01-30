# NAO Meets GPT - Modular Edition

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: modular](https://img.shields.io/badge/code%20style-modular-brightgreen.svg)](https://github.com/YOUR_USERNAME/nao_meets_gpt)

> 🤖 Enhanced conversational AI system for NAO robot with modular architecture
# NAO Conversational System

Sistema conversazionale modulare per robot NAO con Whisper e GPT.

## 📁 Struttura Progetto

```
nao_meets_gpt/
├── brain.py                    # Main script (300 righe)
├── audio_utils.py              # Gestione audio e stream NAO
├── speech_transcriber.py       # Trascrizione (Google + Whisper)
├── text_utils.py               # Elaborazione testo e markdown
├── nao_client.py               # Client comunicazione NAO
├── gpt_client.py               # Client GPT/LLM
├── env_loader.py               # Caricamento variabili .env ⭐ NEW
├── body.py                     # Server NAO (Python 2)
├── actions.py                  # Gestione azioni fisiche (Python 2)
├── .env                        # Variabili d'ambiente (non committare!)
├── .env.example                # Template .env
├── .gitignore                  # File da non committare
├── system_prompt.txt           # System prompt per GPT
├── requirements.txt            # Dipendenze Python 3
├── README.md                   # Questo file
└── ENV_SETUP.md               # Guida setup .env ⭐ NEW
```

## 🚀 Quick Start

### 1. Installa Dipendenze

**Sul tuo computer (Python 3):**
```bash
pip install -r requirements.txt
```

**Su NAO (Python 2):**
```bash
pip2 install flask
```

### 2. Configura

**Crea file `.env` (raccomandato):**
```bash
# Copia il template
cp .env.example .env

# Modifica .env e aggiungi la tua API key
nano .env
```

Nel file `.env`:
```bash
# GitHub Models API Key
GITHUB_API_KEY=ghp_la_tua_chiave_qui

# NAO Server URL
NAO_SERVER_URL=http://192.168.1.100:5004
```

**Oppure (vecchio metodo):**
```bash
export GITHUB_API_KEY="your_token_here"
```

Modifica `brain.py`:
```python
class Config:
    NAO_SERVER_URL = "http://192.168.1.100:5004"  # IP del tuo NAO
    TRANSCRIPTION_METHOD = "google"  # "google" (veloce) o "whisper" (offline)
    TRANSCRIPTION_LANGUAGE = "it-IT"  # Lingua per trascrizione
    USE_NAO_MICROPHONE = True  # False per microfono computer
```

Imposta GitHub API key:
```bash
export GITHUB_API_KEY="your_token_here"
```

### 3. Avvia

**Terminal 1 (NAO):**
```bash
ssh nao@nao.local
cd /home/nao
python2 body.py
```

**Terminal 2 (Computer):**
```bash
python brain.py
```

## 📋 requirements.txt

```txt
faster-whisper
litellm
tiktoken
SpeechRecognition
numpy
requests
```

## ⚙️ Configurazione Avanzata

### Scegli Metodo Trascrizione

**Google Speech Recognition (default - consigliato):**
```python
class Config:
    TRANSCRIPTION_METHOD = "google"  # Veloce e preciso
    TRANSCRIPTION_LANGUAGE = "it-IT"
```

**Whisper (offline):**
```python
class Config:
    TRANSCRIPTION_METHOD = "whisper"  # Non richiede internet
    TRANSCRIPTION_LANGUAGE = "it"
    WHISPER_MODEL = "small"  # tiny/base/small/medium/large
```

### Usa Microfono Computer

```python
class Config:
    USE_NAO_MICROPHONE = False  # Qualità audio migliore
```

### Push-to-Talk

```python
class Config:
    USE_PUSH_TO_TALK = True  # Premi INVIO per parlare
```

### Cambia Modello GPT

```python
class Config:
    GPT_MODEL = "github/gpt-4o"  # Modello più potente
    # Oppure:
    GPT_MODEL = "openai/gpt-4"
    # GPT_MODEL = "anthropic/claude-3-sonnet"
```

## 🎯 Esempi d'Uso

### Conversazione Base
```
Utente: "Ciao NAO, come stai?"
NAO: "Ciao! Sto benissimo, grazie. Come posso aiutarti?"
```

### Con Azioni Fisiche
```
Utente: "Alzati e salutami"
NAO: "Certo! Mi alzo subito. [ACTION:stand] Ti saluto! [ACTION:wave_hand]"
[NAO si alza e saluta]
```

### Informazioni
```
Utente: "Quanta batteria hai?"
NAO: "Fammi controllare... [ACTION:get_battery_level]"
[NAO: "La mia batteria è al 75%"]
```

## 🔧 Personalizzazione

### Aggiungi Nuove Azioni

In `actions.py` (Python 2):
```python
def my_custom_action(self, param1="default"):
    """Descrizione azione"""
    try:
        # Codice azione
        self.motion.setAngles(...)
        return True, "Azione completata!"
    except Exception as e:
        return False, "Errore: {}".format(e)
```

Aggiorna `system_prompt.txt` con la nuova azione.

### Modifica System Prompt

Modifica `system_prompt.txt` per cambiare personalità e comportamento di NAO.

## 🐛 Troubleshooting

### Audio non rilevato
```python
# Aumenta energia threshold
class Config:
    ENERGY_THRESHOLD = 6000
```

### Trascrizioni sbagliate

**Con Google (default):**
- Google è già molto accurato (~98%)
- Se problemi, verifica connessione internet
- Parla chiaramente verso il microfono

**Con Whisper:**
```python
# Usa modello più grande
class Config:
    WHISPER_MODEL = "medium"
```

### Connessione NAO fallita
```bash
# Verifica IP
ping nao.local

# Verifica server
curl http://192.168.1.100:5004/health
```

## 📊 Performance

### Confronto Metodi Trascrizione

| Metodo | Tempo (3s audio) | Accuratezza IT | Offline | Note |
|--------|------------------|----------------|---------|------|
| **Google** | **~0.5s** | **~98%** | ❌ | ⭐ Veloce e preciso |
| Whisper tiny | ~0.5s | ~85% | ✅ | Poco accurato |
| Whisper base | ~1s | ~92% | ✅ | Accettabile |
| Whisper small | ~2s | ~96% | ✅ | Buono ma lento |
| Whisper medium | ~5s | ~97.5% | ✅ | Molto lento |

**Consiglio:** Usa **Google** per velocità e precisione. Usa **Whisper** solo se non hai internet.

## 🎓 Architettura

### Flusso Dati

```
Utente parla
    ↓
NAO microfoni → body.py (Python 2)
    ↓
HTTP stream → audio_utils.py
    ↓
Google/Whisper → speech_transcriber.py
    ↓
Testo → gpt_client.py
    ↓
Risposta GPT → text_utils.py (pulisce markdown)
    ↓
[ACTION:...] → nao_client.py
    ↓
body.py → NAO parla/si muove
```

### Moduli

- **brain.py**: Orchestratore principale (300 righe)
- **audio_utils.py**: Stream audio NAO, configurazione recognizer
- **speech_transcriber.py**: Google Speech Recognition + Whisper (opzionale)
- **text_utils.py**: Markdown→speech, parsing azioni, trim context
- **nao_client.py**: API client per body.py
- **gpt_client.py**: Wrapper LiteLLM con fallback
- **body.py**: Server Flask per NAO (Python 2)
- **actions.py**: Libreria azioni fisiche (Python 2)

## 📝 Log

Il sistema logga dettagliatamente:
```
2024-01-15 10:30:15 - INFO - 🎤 Registrazione...
2024-01-15 10:30:18 - INFO - ✓ Registrazione completata
2024-01-15 10:30:18 - INFO - 📝 Trascrizione...
2024-01-15 10:30:19 - INFO - ✓ Trascritto: 'ciao come stai'
2024-01-15 10:30:19 - INFO - 🤖 Generating response...
2024-01-15 10:30:21 - INFO - ✓ Response generated
2024-01-15 10:30:21 - INFO - 🔊 Sending text to NAO...
```

## 🔒 Sicurezza

- Non committare API keys nel codice
- Usa variabili d'ambiente: `export GITHUB_API_KEY=...`
- File `.gitignore` dovrebbe includere:
  ```
  *.pyc
  __pycache__/
  .env
  conversation_context.txt
  input_raw.wav
  ```

## 📚 Risorse

- [Whisper Documentation](https://github.com/openai/whisper)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [NAO Documentation](http://doc.aldebaran.com/)
- [GitHub Models](https://github.com/marketplace/models)
- **[ENV Setup Guide](ENV_SETUP.md)** - Guida completa variabili ambiente ⭐

## 🤝 Contributi

Per miglioramenti o bug fixes, crea una issue o pull request.

## 📄 Licenza

MIT License - vedi LICENSE file

---

**Versione**: 2.0 (Modulare)  
**Ultima modifica**: 2024-01-15
