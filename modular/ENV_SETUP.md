# Guida Setup Variabili d'Ambiente

## 🔐 Perché Usare File .env?

**Vantaggi:**
- ✅ **Sicurezza**: API keys non nel codice
- ✅ **Comodità**: Non serve `export` ogni volta
- ✅ **Portabilità**: Stesso codice, diverse configurazioni
- ✅ **Team**: Ogni sviluppatore ha il suo `.env`
- ✅ **Git-safe**: `.env` è in `.gitignore`

## 🚀 Setup Veloce (3 Passi)

### Passo 1: Crea File .env

```bash
# Nella directory del progetto
touch .env

# Oppure copia dal template
cp .env.example .env
```

### Passo 2: Aggiungi la Tua API Key

Apri `.env` con un editor e aggiungi:

```bash
# .env
GITHUB_API_KEY=ghp_tuaChiaveQuiSenzaVirgolette123456789
```

**⚠️ IMPORTANTE:** 
- Nessuno spazio prima/dopo `=`
- Nessun apice o virgolette (a meno che non facciano parte della key)
- Una variabile per riga

### Passo 3: Avvia Brain.py

```bash
python brain.py
```

Il sistema carica automaticamente `.env`! ✨

## 📝 Template File .env

Ecco un template completo:

```bash
# ===== API KEYS =====

# GitHub Models (RICHIESTA)
GITHUB_API_KEY=ghp_your_token_here

# OpenAI (opzionale)
# OPENAI_API_KEY=sk-your_key_here

# Groq (opzionale)
# GROQ_API_KEY=gsk_your_key_here

# Anthropic Claude (opzionale)
# ANTHROPIC_API_KEY=sk-ant-your_key_here


# ===== NAO CONFIGURATION =====

# URL del server NAO
NAO_SERVER_URL=http://192.168.1.100:5004


# ===== OPTIONAL SETTINGS =====

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Conversation file
CONVERSATION_FILE=conversation_context.txt
```

## 🔑 Come Ottenere le API Keys

### GitHub Models (Consigliata)

1. Vai su https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Seleziona scope: `read:packages`
4. Click "Generate token"
5. Copia il token (inizia con `ghp_`)
6. Incollalo in `.env`:
   ```bash
   GITHUB_API_KEY=ghp_il_tuo_token_qui
   ```

**GRATIS** con limiti generosi!

### OpenAI (Alternativa)

1. Vai su https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copia la chiave (inizia con `sk-`)
4. Incollala in `.env`:
   ```bash
   OPENAI_API_KEY=sk-la_tua_chiave_qui
   ```

**A PAGAMENTO** (~$0.002 per 1K token)

### Groq (Alternativa Veloce)

1. Vai su https://console.groq.com/keys
2. Crea account gratuito
3. Genera API key
4. Incollala in `.env`:
   ```bash
   GROQ_API_KEY=gsk_la_tua_chiave_qui
   ```

**GRATIS** con limiti generosi!

## 🛠️ Uso Avanzato

### Multiple Environments

Puoi avere diversi file .env:

```bash
.env              # Development
.env.production   # Production
.env.test         # Testing
```

Carica quello specifico:

```python
from env_loader import load_env_file

load_env_file(".env.production")
```

### Override da Codice

```python
# In brain.py
class Config:
    # .env ha priorità, poi fallback
    NAO_SERVER_URL = os.getenv("NAO_SERVER_URL", "http://localhost:5004")
    API_KEY = os.getenv("GITHUB_API_KEY", "default_key")
```

### Validazione Variabili

Il sistema valida automaticamente le variabili richieste:

```python
# In main()
setup_environment(
    env_file=".env",
    required_vars=["GITHUB_API_KEY", "NAO_SERVER_URL"]
)
```

Se mancano, mostra errore chiaro:

```
ERROR: CONFIGURAZIONE MANCANTE
Le seguenti variabili sono richieste ma non trovate:
  - GITHUB_API_KEY
  - NAO_SERVER_URL

Aggiungi queste variabili al file .env
```

## 🔒 Sicurezza

### ✅ DO (Fai):

1. **Aggiungi .env al .gitignore**
   ```bash
   # .gitignore
   .env
   .env.*
   ```

2. **Non committare API keys**
   ```bash
   git status  # Verifica .env non sia tracciato
   ```

3. **Usa .env.example come template**
   ```bash
   # .env.example (commit questo)
   GITHUB_API_KEY=your_key_here
   
   # .env (NON committare)
   GITHUB_API_KEY=ghp_reale123456789
   ```

4. **Ruota le keys periodicamente**
   - Ogni 3-6 mesi
   - Subito se esposte

### ❌ DON'T (Non fare):

1. **Non committare .env su Git**
   ```bash
   # SBAGLIATO!
   git add .env
   ```

2. **Non condividere screenshots con keys**
   
3. **Non hardcodare keys nel codice**
   ```python
   # SBAGLIATO!
   API_KEY = "ghp_123456789"
   
   # GIUSTO!
   API_KEY = os.getenv("GITHUB_API_KEY")
   ```

4. **Non loggare keys**
   ```python
   # SBAGLIATO!
   logger.info("API Key: {}".format(api_key))
   
   # GIUSTO! (env_loader nasconde automaticamente)
   logger.debug("Loaded API Key: {}".format(api_key[:8] + "..."))
   ```

## 🐛 Troubleshooting

### Problema: "API Key non trovata"

**Causa:** `.env` non caricato o variabile scritta male

**Soluzione:**
```bash
# Verifica che .env esista
ls -la .env

# Verifica contenuto
cat .env

# Verifica formato (nessuno spazio!)
# SBAGLIATO:
GITHUB_API_KEY = ghp_123  # Spazi intorno a =
GITHUB_API_KEY="ghp_123"  # Virgolette non necessarie

# GIUSTO:
GITHUB_API_KEY=ghp_123
```

### Problema: "Module 'env_loader' not found"

**Soluzione:**
Assicurati che `env_loader.py` sia nella stessa directory di `brain.py`

```bash
ls -la
# Dovresti vedere:
# brain.py
# env_loader.py
# .env
```

### Problema: Keys funzionano con export ma non con .env

**Causa:** Formato errato in `.env`

**Soluzione:**
```bash
# .env DEVE essere così:
GITHUB_API_KEY=ghp_valore_senza_virgolette

# NON così:
export GITHUB_API_KEY=...  # export non serve in .env
GITHUB_API_KEY = ...        # niente spazi
GITHUB_API_KEY="..."        # niente virgolette (a meno che parte del valore)
```

### Problema: Git tracked .env per errore

**Soluzione:**
```bash
# Rimuovi da Git (ma mantieni file locale)
git rm --cached .env

# Aggiungi a .gitignore se non c'è già
echo ".env" >> .gitignore

# Commit
git commit -m "Remove .env from git"
```

## 📚 Documentazione env_loader

### Funzioni Disponibili

```python
from env_loader import load_env_file, get_env, validate_env_vars, setup_environment

# Carica .env manualmente
load_env_file(".env")

# Ottieni variabile con default
api_key = get_env("GITHUB_API_KEY", default="fallback_value")

# Ottieni variabile richiesta (errore se manca)
api_key = get_env("GITHUB_API_KEY", required=True)

# Valida multiple variabili
ok, missing = validate_env_vars(["API_KEY", "SERVER_URL"])
if not ok:
    print("Mancano:", missing)

# Setup completo (raccomandato)
setup_environment(
    env_file=".env",
    required_vars=["GITHUB_API_KEY"]
)
```

## 🎯 Best Practices

1. **Usa .env.example** come template condiviso
2. **Documenta ogni variabile** con commenti in .env.example
3. **Valida variabili richieste** all'avvio
4. **Non loggare valori sensibili**
5. **Ruota keys periodicamente**
6. **Usa chiavi diverse** per dev/staging/production

## ✅ Checklist Setup

- [ ] File `.env` creato
- [ ] API key aggiunta a `.env`
- [ ] `.env` in `.gitignore`
- [ ] `.env.example` committato (senza keys reali)
- [ ] Testato: `python brain.py` funziona
- [ ] Verificato: `git status` non mostra `.env`

---

**Fatto!** Ora le tue API keys sono al sicuro e non devi più fare `export` ogni volta! 🎉
