# Guida Rapida: Usare Google Gemini

## 🚀 Setup Veloce (3 Passi)

### Passo 1: Ottieni API Key Gemini

1. Vai su https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copia la chiave (inizia con `AIza...`)

### Passo 2: Configura `.env`

Apri (o crea) il file `.env` e aggiungi:

```bash
# Google Gemini Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza_la_tua_chiave_qui
LLM_MODEL=gemini/gemini-1.5-flash
LLM_API_BASE=https://generativelanguage.googleapis.com

# NAO Configuration
NAO_SERVER_URL=http://192.168.1.100:5004

# Transcription (opzionale)
TRANSCRIPTION_METHOD=google
TRANSCRIPTION_LANGUAGE=it-IT
```

### Passo 3: Avvia!

```bash
python brain.py
```

Fatto! ✨

## 📋 Modelli Gemini Disponibili

| Modello | Velocità | Qualità | Costo | Note |
|---------|----------|---------|-------|------|
| **gemini/gemini-1.5-flash** | ⚡⚡⚡ | ⭐⭐⭐ | GRATIS | Consigliato |
| gemini/gemini-1.5-pro | ⚡⚡ | ⭐⭐⭐⭐⭐ | GRATIS | Più intelligente |
| gemini/gemini-2.0-flash-exp | ⚡⚡⚡ | ⭐⭐⭐⭐ | GRATIS | Sperimentale |

### Come Cambiare Modello

Nel tuo `.env`, cambia:

```bash
# Per modello veloce (consigliato)
LLM_MODEL=gemini/gemini-1.5-flash

# Per modello più intelligente
LLM_MODEL=gemini/gemini-1.5-pro

# Per modello sperimentale
LLM_MODEL=gemini/gemini-2.0-flash-exp
```

## 🆚 Gemini vs GitHub Models

| Caratteristica | Gemini Flash | GitHub GPT-4o-mini |
|----------------|--------------|-------------------|
| Velocità | ⚡⚡⚡ Molto veloce | ⚡⚡ Veloce |
| Qualità IT | ⭐⭐⭐⭐ Ottimo | ⭐⭐⭐ Buono |
| Rate Limits | 15 req/min (gratis) | Generosi |
| Contesto | 1M token | 128K token |
| Costo | GRATIS | GRATIS |

**Consiglio:** Prova entrambi e scegli quello che preferisci!

## 🔧 Troubleshooting

### Errore: "API key not found"

**Soluzione:**
```bash
# Verifica che .env contenga:
GEMINI_API_KEY=AIza_tua_chiave

# Niente virgolette, niente spazi prima/dopo =
```

### Errore: "quota exceeded"

**Causa:** Superato il rate limit gratuito (15 req/min)

**Soluzioni:**
1. Aspetta 1 minuto
2. Usa un'altra API key
3. Passa a GitHub Models temporaneamente

### Le risposte sono troppo lunghe

Riduci GPT_MAX_TOKENS nel `.env`:
```bash
GPT_MAX_TOKENS=150  # Default: 250
```

### Voglio risposte più creative

Aumenta GPT_TEMPERATURE nel `.env`:
```bash
GPT_TEMPERATURE=0.9  # Default: 0.7
```

## 🎯 Configurazione Completa Gemini

Esempio `.env` ottimizzato per Gemini:

```bash
# ===== LLM: Google Gemini =====
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza_your_key_here
LLM_MODEL=gemini/gemini-1.5-flash
LLM_API_BASE=https://generativelanguage.googleapis.com

# ===== NAO =====
NAO_SERVER_URL=http://192.168.1.100:5004

# ===== TRANSCRIPTION =====
TRANSCRIPTION_METHOD=google
TRANSCRIPTION_LANGUAGE=it-IT

# ===== AUDIO =====
USE_NAO_MICROPHONE=true
USE_PUSH_TO_TALK=false
ENERGY_THRESHOLD=4000
DYNAMIC_ENERGY=true

# ===== GPT SETTINGS =====
GPT_MAX_TOKENS=250
GPT_TEMPERATURE=0.7
TOKEN_LIMIT=4096
```

## 🌟 Vantaggi Gemini

1. **GRATIS** con limiti generosi
2. **Velocissimo** (quasi quanto GPT-4o-mini)
3. **Ottimo per italiano** (addestrato su molti dati IT)
4. **Contesto enorme** (1M token vs 128K)
5. **Multimodale** (anche se non usato qui)

## ⚠️ Limitazioni

1. Rate limit: 15 request/min (tier gratuito)
2. Slightly meno consistente di GPT-4 per task complessi
3. A volte più verboso (risolvi con GPT_MAX_TOKENS basso)

## 📚 Link Utili

- **Ottieni API Key**: https://aistudio.google.com/app/apikey
- **Documentazione**: https://ai.google.dev/docs
- **Pricing**: https://ai.google.dev/pricing (spoiler: è gratis!)
- **Rate Limits**: https://ai.google.dev/gemini-api/docs/quota

## 🔄 Switching tra Provider

Puoi switchare facilmente tra provider:

**Usa Gemini:**
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
LLM_MODEL=gemini/gemini-1.5-flash
```

**Torna a GitHub:**
```bash
LLM_PROVIDER=github
GITHUB_API_KEY=ghp_...
LLM_MODEL=gpt-4o-mini
```

**Prova Groq (velocissimo!):**
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
LLM_MODEL=llama-3.1-70b-versatile
```

Basta modificare `.env` e riavviare `brain.py`!

---

**Fatto!** Ora NAO usa Google Gemini! 🎉
