"""
Environment Variables Loader
Carica variabili d'ambiente da file .env
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_env_file(env_file=".env"):
    """
    Carica variabili d'ambiente da file .env
    
    Args:
        env_file (str): Path al file .env
        
    Returns:
        dict: Variabili caricate
    """
    env_vars = {}
    env_path = Path(env_file)
    
    if not env_path.exists():
        logger.warning("File .env non trovato in {}".format(env_path.absolute()))
        logger.info("Crea un file .env copiando .env.example")
        return env_vars
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Ignora commenti e righe vuote
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE
                if '=' not in line:
                    logger.warning("Riga {} ignorata (formato non valido): {}".format(
                        line_num, line))
                    continue
                
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Rimuovi quotes se presenti
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Imposta variabile d'ambiente
                os.environ[key] = value
                env_vars[key] = value
                
                # Log (nasconde valori sensibili)
                if 'KEY' in key or 'SECRET' in key or 'TOKEN' in key:
                    display_value = value[:8] + "..." if len(value) > 8 else "***"
                else:
                    display_value = value
                
                logger.debug("Caricato: {} = {}".format(key, display_value))
        
        logger.info("✓ Caricate {} variabili da {}".format(len(env_vars), env_file))
        return env_vars
        
    except Exception as e:
        logger.error("Errore caricamento .env: {}".format(e))
        return env_vars


def get_env(key, default=None, required=False):
    """
    Ottieni variabile d'ambiente con validazione
    
    Args:
        key (str): Nome della variabile
        default: Valore di default se non trovata
        required (bool): Se True, solleva errore se non trovata
        
    Returns:
        str: Valore della variabile
        
    Raises:
        ValueError: Se required=True e variabile non trovata
    """
    value = os.environ.get(key, default)
    
    if required and value is None:
        raise ValueError(
            "Variabile d'ambiente richiesta '{}' non trovata. "
            "Aggiungila al file .env".format(key)
        )
    
    return value


def validate_env_vars(required_vars):
    """
    Valida che tutte le variabili richieste siano presenti
    
    Args:
        required_vars (list): Lista di variabili richieste
        
    Returns:
        tuple: (bool, list) - (tutto_ok, variabili_mancanti)
    """
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        logger.error("Variabili d'ambiente mancanti: {}".format(", ".join(missing)))
        return False, missing
    
    logger.info("✓ Tutte le variabili richieste sono presenti")
    return True, []


def setup_environment(env_file=".env", required_vars=None):
    """
    Setup completo environment: carica .env e valida variabili
    
    Args:
        env_file (str): Path al file .env
        required_vars (list): Variabili richieste da validare
        
    Returns:
        bool: True se setup completato con successo
    """
    # Carica .env
    load_env_file(env_file)
    
    # Valida variabili richieste
    if required_vars:
        all_ok, missing = validate_env_vars(required_vars)
        
        if not all_ok:
            logger.error("\n" + "=" * 70)
            logger.error("CONFIGURAZIONE MANCANTE")
            logger.error("=" * 70)
            logger.error("Le seguenti variabili sono richieste ma non trovate:")
            for var in missing:
                logger.error("  - {}".format(var))
            logger.error("\nAggiungi queste variabili al file .env")
            logger.error("Vedi .env.example per un template")
            logger.error("=" * 70)
            return False
    
    return True


# Auto-load se importato
if __name__ != "__main__":
    # Carica automaticamente .env quando il modulo viene importato
    load_env_file()
