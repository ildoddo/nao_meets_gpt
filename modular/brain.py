#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAO Conversational System - Main Brain
Sistema conversazionale per robot NAO con Whisper e GPT
"""

import os
import time
import logging
from pathlib import Path
import speech_recognition as sr

# Carica variabili d'ambiente da .env
from env_loader import setup_environment

# Import moduli locali
from audio_utils import NaoAudioSource, configure_recognizer
from speech_transcriber import create_transcriber
from text_utils import markdown_to_speech, parse_actions, trim_context
from nao_client import NaoClient
from gpt_client import GPTClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== CONFIGURAZIONE ==========

class Config:
    """Configurazione centralizzata del sistema"""
    
    # NAO Server (può essere sovrascritto da .env)
    NAO_SERVER_URL = os.getenv("NAO_SERVER_URL", "http://192.168.151.121:5004")
    
    # Trascrizione
    TRANSCRIPTION_METHOD = "google"  # "google" (veloce) o "whisper" (offline)
    TRANSCRIPTION_LANGUAGE = "it-IT"  # "it-IT" per Google, "it" per Whisper
    
    # Whisper (solo se TRANSCRIPTION_METHOD = "whisper")
    WHISPER_MODEL = "small"  # tiny, base, small, medium, large
    WHISPER_DEVICE = "cpu"
    
    # Audio
    USE_NAO_MICROPHONE = True   # False = usa microfono computer
    USE_PUSH_TO_TALK = False    # True = premi INVIO per parlare
    ENERGY_THRESHOLD = 4000
    DYNAMIC_ENERGY = True
    VAD_THRESHOLD = 0.5
    
    # GPT
    GPT_MODEL = "github/gpt-4o-mini"
    GPT_API_BASE = "https://models.inference.ai.azure.com"
    GPT_MAX_TOKENS = 250
    GPT_TEMPERATURE = 0.7
    
    # Token limits
    TOKEN_LIMIT = 4096
    
    # Files
    SYSTEM_PROMPT_FILE = "system_prompt.txt"
    CONVERSATION_FILE = "conversation_context.txt"
    
    # Audio parameters (calculated)
    SAMPLING_RATE = 16000
    SAMPLES_PER_CHUNK = 1365
    TIME_BETWEEN_CHUNKS = SAMPLES_PER_CHUNK / SAMPLING_RATE


# ========== INIZIALIZZAZIONE ==========

def initialize_system(config):
    """
    Inizializza tutti i componenti del sistema
    
    Returns:
        tuple: (transcriber, nao_client, gpt_client, system_prompt)
    """
    logger.info("\n" + "=" * 70)
    logger.info("INIZIALIZZAZIONE SISTEMA NAO")
    logger.info("=" * 70)
    
    # 1. Carica system prompt
    system_prompt = load_system_prompt(config.SYSTEM_PROMPT_FILE)
    
    # 2. Inizializza Transcriber (Google o Whisper)
    logger.info("Metodo trascrizione: {}".format(config.TRANSCRIPTION_METHOD))
    
    if config.TRANSCRIPTION_METHOD == "google":
        transcriber = create_transcriber("google")
    else:
        transcriber = create_transcriber(
            "whisper",
            model=config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE
        )
    
    # 3. Inizializza client NAO
    nao_client = NaoClient(config.NAO_SERVER_URL)
    
    if config.USE_NAO_MICROPHONE:
        if not nao_client.test_connection():
            logger.error("Impossibile connettersi a NAO. Uscita.")
            return None
    
    # 4. Inizializza client GPT
    # API key viene caricata da .env automaticamente
    if not os.getenv("GITHUB_API_KEY"):
        logger.warning("GITHUB_API_KEY non trovata in .env")
        logger.warning("Usando valore di default (probabilmente non funzionerà)")
    
    gpt_client = GPTClient(
        model=config.GPT_MODEL,
        api_base=config.GPT_API_BASE
    )
    
    logger.info("=" * 70)
    logger.info("Configurazione:")
    logger.info("  Trascrizione: {}".format(config.TRANSCRIPTION_METHOD))
    if config.TRANSCRIPTION_METHOD == "whisper":
        logger.info("  Whisper model: {}".format(config.WHISPER_MODEL))
    logger.info("  Microfono: {}".format("NAO" if config.USE_NAO_MICROPHONE else "Computer"))
    logger.info("  GPT: {}".format(config.GPT_MODEL))
    logger.info("=" * 70 + "\n")
    
    return transcriber, nao_client, gpt_client, system_prompt


def load_system_prompt(filename):
    """Carica system prompt da file"""
    try:
        if Path(filename).exists():
            with open(filename, "r", encoding="utf-8") as f:
                prompt = f.read()
            logger.info("✓ System prompt caricato da {}".format(filename))
            return prompt
        else:
            logger.warning("System prompt non trovato, uso default")
            return """Sei NAO, un assistente robotico amichevole.

NON USARE FORMATTAZIONE MARKDOWN (asterischi, backtick, ecc.).
Scrivi in testo semplice naturale.

Quando esegui azioni fisiche, usa: [ACTION:nome_azione|parametri]
Esempio: "Certo, mi alzo! [ACTION:stand|speed=0.5]"

Rispondi sempre in italiano in modo conciso (2-3 frasi max)."""
    
    except Exception as e:
        logger.error("Errore caricamento prompt: {}".format(e))
        return "Sei un assistente robotico amichevole."


# ========== FUNZIONI PRINCIPALI ==========

def get_user_input(config, recognizer, transcriber):
    """
    Cattura e trascrivi input utente
    
    Returns:
        str or None: Testo trascritto o None
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Registra audio
            audio_data = record_audio(config, recognizer)
            
            if audio_data is None:
                continue
            
            # Salva per debug
            with open("input_raw.wav", "wb") as f:
                f.write(audio_data.get_wav_data())
            
            # Trascrivi (Google è semplice, senza info aggiuntive)
            if config.TRANSCRIPTION_METHOD == "google":
                text = transcriber.transcribe_with_retry(
                    audio_data,
                    language=config.TRANSCRIPTION_LANGUAGE
                )
                
                if text:
                    return text
                
            else:  # Whisper
                text, info = transcriber.transcribe_with_retry(
                    audio_data,
                    language=config.TRANSCRIPTION_LANGUAGE.split('-')[0]
                )
                
                if text and len(text.strip()) > 0:
                    # Controlla confidenza per Whisper
                    if 'avg_logprob' in info and info['avg_logprob'] < -0.8:
                        logger.warning("⚠️ Bassa confidenza: {:.2f}".format(info['avg_logprob']))
                        confirm = input("Trascrizione: '{}'. OK? (s/n): ".format(text))
                        if confirm.lower() != 's':
                            continue
                    
                    return text
            
            logger.warning("Trascrizione vuota, riprovo...")
            
        except Exception as e:
            logger.error("Errore: {}".format(e))
    
    logger.error("Impossibile ottenere input dopo {} tentativi".format(max_retries))
    return None


def record_audio(config, recognizer):
    """Registra audio da NAO o microfono"""
    try:
        if config.USE_PUSH_TO_TALK:
            input("Premi INVIO e poi parla... ")
        
        logger.info("🎤 Registrazione...")
        
        if config.USE_NAO_MICROPHONE:
            source = NaoAudioSource(config.NAO_SERVER_URL, config.TIME_BETWEEN_CHUNKS)
        else:
            source = sr.Microphone(sample_rate=16000)
        
        with source as src:
            # Calibra rumore
            logger.info("📊 Calibrazione (1 sec)...")
            recognizer.adjust_for_ambient_noise(src, duration=1.0)
            logger.info("   Threshold: {}".format(recognizer.energy_threshold))
            
            # Registra
            logger.info("🎤 Parla ora!")
            audio_data = recognizer.listen(
                src,
                phrase_time_limit=15,
                timeout=None
            )
            
            logger.info("✓ Registrazione completata")
            return audio_data
    
    except Exception as e:
        logger.error("Errore registrazione: {}".format(e))
        return None


def process_turn(config, user_message, conversation_context, nao_client, gpt_client):
    """
    Processa un turno di conversazione completo
    
    Returns:
        bool: True se successo
    """
    # 1. Aggiungi messaggio utente
    conversation_context.append({
        "role": "user",
        "content": user_message
    })
    
    # 2. Trim context
    conversation_context = trim_context(
        conversation_context,
        max_tokens=config.TOKEN_LIMIT,
        max_response_tokens=config.GPT_MAX_TOKENS
    )
    
    # 3. Genera risposta GPT
    gpt_message = gpt_client.generate_with_fallback(
        conversation_context,
        max_tokens=config.GPT_MAX_TOKENS,
        temperature=config.GPT_TEMPERATURE
    )
    
    if not gpt_message:
        return False
    
    # 4. Estrai azioni
    actions, clean_text = parse_actions(gpt_message)
    
    # 5. Esegui azioni
    if actions:
        logger.info("🎬 Esecuzione {} azione/i".format(len(actions)))
        for action_name, params in actions:
            nao_client.execute_action(action_name, params)
    
    # 6. Pulisci markdown e fai parlare NAO
    speech_text = markdown_to_speech(clean_text)
    if speech_text:
        nao_client.speak(speech_text)
    
    # 7. Aggiungi risposta al contesto
    conversation_context.append({
        "role": "assistant",
        "content": gpt_message
    })
    
    # 8. Salva conversazione
    save_conversation(conversation_context, config.CONVERSATION_FILE)
    
    return True


def save_conversation(context, filename):
    """Salva conversazione su file"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write("CONVERSAZIONE\n")
            f.write("=" * 50 + "\n\n")
            
            for entry in context:
                role = entry['role'].upper()
                content = entry['content']
                f.write("[{}]\n{}\n\n".format(role, content))
                f.write("-" * 50 + "\n\n")
    
    except Exception as e:
        logger.error("Impossibile salvare: {}".format(e))


# ========== MAIN LOOP ==========

def main():
    """Main conversation loop"""
    
    # Setup environment: carica .env e valida API keys
    if not setup_environment(
        env_file=".env",
        required_vars=["GITHUB_API_KEY"]  # Lista variabili richieste
    ):
        logger.error("Setup environment fallito. Controlla il file .env")
        return
    
    config = Config()
    
    # Inizializza sistema
    result = initialize_system(config)
    if result is None:
        return
    
    transcriber, nao_client, gpt_client, system_prompt = result
    
    # Inizializza conversazione
    conversation_context = [{"role": "system", "content": system_prompt}]
    
    # Configura recognizer
    recognizer = configure_recognizer(
        energy_threshold=config.ENERGY_THRESHOLD,
        dynamic_energy=config.DYNAMIC_ENERGY
    )
    
    # Loop
    logger.info("\n" + "=" * 70)
    logger.info("SISTEMA PRONTO - Premi Ctrl+C per uscire")
    logger.info("=" * 70 + "\n")
    
    turn_count = 0
    running = True
    
    while running:
        try:
            turn_count += 1
            logger.info("\n--- Turno {} ---".format(turn_count))
            
            # Input utente
            user_message = get_user_input(config, recognizer, transcriber)
            
            if not user_message:
                logger.warning("Input non valido, riprovo...")
                continue
            
            # Processa turno
            success = process_turn(
                config,
                user_message,
                conversation_context,
                nao_client,
                gpt_client
            )
            
            if success:
                logger.info("✓ Turno {} completato".format(turn_count))
            
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Interruzione utente")
            running = False
        
        except Exception as e:
            logger.error("❌ Errore: {}".format(e))
            logger.info("Continuo...")
    
    # Cleanup
    logger.info("\n" + "=" * 70)
    logger.info("Sessione terminata dopo {} turni".format(turn_count))
    logger.info("Conversazione salvata in {}".format(config.CONVERSATION_FILE))
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
