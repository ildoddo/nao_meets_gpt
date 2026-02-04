# 🎯 Modifiche: Supporto Multi-Provider LLM

## 📋 Riepilogo

Il sistema NAO ora supporta **configurazione flessibile** di API keys e endpoints tramite file `.env`, permettendo di switchare facilmente tra diversi provider LLM (GitHub, Gemini, OpenAI, Groq, Anthropic) senza modificare il codice.

## ✅ Cosa È Stato Modificato

### 1. **File Creati/Modificati**

#### Nuovi File:
- `.env.example` - Template configurazione con tutti i provider
- `.env.gemini` - Esempio specifico per Google Gemini
- `GEMINI_GUIDE.md` - Guida completa per usare Gemini
- `MULTI_PROVIDER_CHANGES.md` - Questo documento

#### File Modificati:
- `gpt_client.py` - Auto-detect API key basato sul provider
- `brain.py` - Config caricata da variabili env
- `README.md` - Documentazione aggiornata
- `ENV_SETUP.md` - Aggiunta sezione Gemini

### 2. **Funzionalità Aggiunte**

#### Auto-Detection API Key
```python
# gpt_client.py ora rileva automaticamente l'API key giusta
env_key_map = {
    'github': 'GITHUB_API_KEY',
    'gemini': 'GEMINI_API_KEY',
    'openai': 'OPENAI_API_KEY',
    'groq': 'GROQ_API_KEY',
    'anthropic': 'ANTHROPIC_API_KEY'
}
```

#### Configurazione via Environment
```bash
# .env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
LLM_MODEL=gemini/gemini-1.5-flash
LLM_API_BASE=https://generativelanguage.googleapis.com
```

#### Supporto Multi-Provider
- ✅ GitHub Models (GPT-4o-mini)
- ✅ Google Gemini (Flash/Pro) ⭐ NUOVO
- ✅ Groq (Llama 3.1)
- ✅ OpenAI (GPT-4)
- ✅ Anthropic (Claude 3.5)

## 🚀 Come Usare

### Setup Gemini (Esempio)

**1. Crea `.env`:**
```bash
cp .env.gemini .env
```

**2. Aggiungi API Key:**
```bash
# Ottieni key da: https://aistudio.google.com/app/apikey
nano .env

# Modifica:
GEMINI_API_KEY=AIza_your_real_key_here
```

**3. Avvia:**
```bash
python brain.py
```

### Switching tra Provider

Basta modificare `.env`:

```bash
# Usa Gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
LLM_MODEL=gemini/gemini-1.5-flash

# Oppure GitHub
LLM_PROVIDER=github  
GITHUB_API_KEY=ghp_...
LLM_MODEL=gpt-4o-mini

# Oppure Groq (velocissimo!)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
LLM_MODEL=llama-3.1-70b-versatile
```

## 📊 Confronto Provider

| Provider | Modello | Velocità | Qualità IT | Costo | Rate Limits |
|----------|---------|----------|------------|-------|-------------|
| **Gemini** | flash | ⚡⚡⚡ | ⭐⭐⭐⭐ | GRATIS | 15/min |
| GitHub | gpt-4o-mini | ⚡⚡ | ⭐⭐⭐ | GRATIS | Generosi |
| Groq | llama-3.1 | ⚡⚡⚡⚡ | ⭐⭐⭐ | GRATIS | 30/min |
| OpenAI | gpt-4o | ⚡⚡ | ⭐⭐⭐⭐⭐ | €€€ | Alti |
| Anthropic | claude-3.5 | ⚡⚡ | ⭐⭐⭐⭐⭐ | €€€ | Alti |

**Raccomandazione:** Prova **Gemini Flash** per velocità + qualità gratis!

## 🔧 Dettagli Tecnici

### Modifiche `gpt_client.py`

**Prima:**
```python
class GPTClient:
    def __init__(self, model, api_base):
        self.model = model
        self.api_base = api_base
        # API key hardcoded per GitHub
```

**Dopo:**
```python
class GPTClient:
    def __init__(self, model=None, api_base=None, api_key=None):
        # Auto-detect da environment
        self.model = model or os.getenv("LLM_MODEL")
        self.api_base = api_base or os.getenv("LLM_API_BASE")
        self._setup_api_key(api_key)  # Auto rileva provider
        
    def _setup_api_key(self, api_key=None):
        # Rileva provider dal model name
        provider = self.model.split('/')[0]
        # Carica API key corretta
        env_var = env_key_map[provider]
        self.api_key = os.getenv(env_var)
```

### Modifiche `brain.py`

**Prima:**
```python
class Config:
    GPT_MODEL = "github/gpt-4o-mini"
    GPT_API_BASE = "https://models.inference.ai.azure.com"
```

**Dopo:**
```python
class Config:
    # Tutto caricato da .env con fallback
    GPT_MODEL = os.getenv("LLM_MODEL", "github/gpt-4o-mini")
    GPT_API_BASE = os.getenv("LLM_API_BASE", None)
    TRANSCRIPTION_METHOD = os.getenv("TRANSCRIPTION_METHOD", "google")
    # etc...
```

## 📝 Variabili Environment Supportate

### LLM Configuration
- `LLM_PROVIDER` - Provider name (info, non usato dal codice)
- `LLM_MODEL` - Model identifier (es. `gemini/gemini-1.5-flash`)
- `LLM_API_BASE` - API endpoint URL
- `GEMINI_API_KEY` - Gemini API key
- `GITHUB_API_KEY` - GitHub Models token
- `OPENAI_API_KEY` - OpenAI API key
- `GROQ_API_KEY` - Groq API key
- `ANTHROPIC_API_KEY` - Anthropic API key

### NAO Configuration
- `NAO_SERVER_URL` - NAO server endpoint

### Transcription
- `TRANSCRIPTION_METHOD` - google|whisper
- `TRANSCRIPTION_LANGUAGE` - it-IT|it
- `WHISPER_MODEL` - tiny|base|small|medium|large

### Audio
- `USE_NAO_MICROPHONE` - true|false
- `USE_PUSH_TO_TALK` - true|false
- `ENERGY_THRESHOLD` - 2000-6000
- `DYNAMIC_ENERGY` - true|false

### GPT Settings
- `GPT_MAX_TOKENS` - 100-500
- `GPT_TEMPERATURE` - 0.0-1.0
- `TOKEN_LIMIT` - 2048-8192

## 🎓 Best Practices

1. **Usa `.env`** per tutte le configurazioni
2. **Non committare** `.env` su Git (già in .gitignore)
3. **Usa `.env.example`** come template
4. **Commenta** i provider non usati in `.env`
5. **Testa** diversi provider per trovare il migliore

## 🔍 Troubleshooting

### Errore: "API key not found"

**Causa:** Provider non configurato in `.env`

**Soluzione:**
```bash
# Verifica provider nel model name
LLM_MODEL=gemini/gemini-1.5-flash  # provider = "gemini"

# Assicurati che la key corretta esista
GEMINI_API_KEY=your_key_here
```

### Modello non supportato

**Errore:** `Model 'xyz' not found`

**Soluzione:** Usa un modello valido dal provider:
```bash
# Gemini
LLM_MODEL=gemini/gemini-1.5-flash
LLM_MODEL=gemini/gemini-1.5-pro

# GitHub  
LLM_MODEL=gpt-4o-mini
LLM_MODEL=gpt-4o

# Groq
LLM_MODEL=llama-3.1-70b-versatile
LLM_MODEL=mixtral-8x7b-32768
```

### Rate limit exceeded

**Soluzione:** Passa a provider con limiti più alti:
```bash
# Gemini: 15 req/min (gratis)
# Groq: 30 req/min (gratis)
# OpenAI: molto alti (pagamento)
```

## 📚 Documentazione

- **Setup .env**: [ENV_SETUP.md](ENV_SETUP.md)
- **Guida Gemini**: [GEMINI_GUIDE.md](GEMINI_GUIDE.md)
- **README**: [README.md](README.md)
- **Esempi config**: [config_examples.py](config_examples.py)

## ✅ Testing

### Test 1: Verifica Auto-Detection

```bash
# Crea .env con Gemini
echo "LLM_MODEL=gemini/gemini-1.5-flash" > .env
echo "GEMINI_API_KEY=test" >> .env

# Avvia brain.py e verifica log:
# GPT Client initialized:
#   Model: gemini/gemini-1.5-flash
#   API Base: https://generativelanguage.googleapis.com
```

### Test 2: Switching Provider

```bash
# Test GitHub
LLM_MODEL=gpt-4o-mini
GITHUB_API_KEY=your_key

# Test Gemini
LLM_MODEL=gemini/gemini-1.5-flash
GEMINI_API_KEY=your_key

# Verifica che funzionino entrambi
```

## 🎉 Vantaggi

1. ✅ **Flessibilità**: Cambia provider senza modificare codice
2. ✅ **Sicurezza**: API keys non nel codice
3. ✅ **Semplicità**: Un file `.env` per tutto
4. ✅ **Portabilità**: Stesso codice, diverse configurazioni
5. ✅ **Multi-provider**: Prova tutti i provider facilmente

## 🚀 Prossimi Passi

Ora puoi:

1. Provare **Google Gemini** (vedi [GEMINI_GUIDE.md](GEMINI_GUIDE.md))
2. Testare **Groq** per velocità massima
3. Confrontare qualità tra provider
4. Ottimizzare `GPT_MAX_TOKENS` e `GPT_TEMPERATURE`
5. Creare configurazioni custom in `.env`

---

**Versione:** 2.1
**Data:** 2024-01-15
**Autore:** Sistema NAO Conversazionale
