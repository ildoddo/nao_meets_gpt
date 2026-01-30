"""
Text processing utilities
Gestisce conversione Markdown e manipolazione testo
"""

import re
import logging

logger = logging.getLogger(__name__)


def markdown_to_speech(text):
    """
    Converte Markdown in testo parlato
    
    Args:
        text (str): Testo con formattazione Markdown
        
    Returns:
        str: Testo pulito per sintesi vocale
    """
    if not text:
        return text
    
    original_length = len(text)
    
    # Blocchi di codice
    text = re.sub(r'```[\w]*\n(.*?)\n```', r'', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Headers
    text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)
    
    # Grassetto/Italico
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    
    # Link e URL
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'https?://[^\s]+', '', text)
    
    # Liste
    text = re.sub(r'^[\-\*\+]\s+(.+)$', r'\1', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\.\s+(.+)$', r'\1, \2', text, flags=re.MULTILINE)
    
    # Blockquote
    text = re.sub(r'^>\s+(.+)$', r'\1', text, flags=re.MULTILINE)
    
    # Tabelle
    text = re.sub(r'\|[\-\s\|]+\|', '', text)
    text = re.sub(r'\|', ',', text)
    
    # Emoji comuni
    emoji_map = {
        '✅': 'sì', '❌': 'no', '⚠️': 'attenzione',
        '💡': '', '🎯': '', '🔧': '', '📝': '', '🚀': '', '⭐': '',
    }
    for emoji, word in emoji_map.items():
        text = text.replace(emoji, word)
    
    # Pulizia
    text = re.sub(r'^[\-\*_]{3,}$', '', text, flags=re.MULTILINE)
    text = re.sub(r'[*_~`#]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    text = re.sub(r'\n\s*\n+', '. ', text)
    text = text.strip()
    
    # Abbreviazioni
    abbreviations = {
        'es.': 'esempio', 'ecc.': 'eccetera', 'etc.': 'eccetera',
        'vs.': 'contro', 'vs': 'contro',
    }
    for abbr, full in abbreviations.items():
        text = re.sub(r'\b' + re.escape(abbr) + r'\b', full, text, flags=re.IGNORECASE)
    
    if len(text) < original_length - 10:
        logger.debug("Markdown rimosso: {} -> {} caratteri".format(original_length, len(text)))
    
    return text


def parse_actions(text):
    """
    Estrae azioni dal testo GPT
    
    Args:
        text (str): Testo da GPT
        
    Returns:
        tuple: (actions_list, clean_text)
    """
    action_pattern = r'\[ACTION:(\w+)(?:\|([^\]]+))?\]'
    actions = re.findall(action_pattern, text)
    
    parsed_actions = []
    for action_name, params_str in actions:
        params = {}
        if params_str:
            for param in params_str.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    # Type conversion
                    try:
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        elif value.replace('.', '').isdigit():
                            value = float(value) if '.' in value else int(value)
                    except:
                        pass
                    params[key.strip()] = value.strip()
        
        parsed_actions.append((action_name, params))
    
    # Remove action tags from text
    clean_text = re.sub(action_pattern, '', text).strip()
    
    return parsed_actions, clean_text


def trim_context(context, max_tokens=4096, max_response_tokens=250):
    """
    Trim conversation context to fit token limits
    
    Args:
        context (list): Conversation history
        max_tokens (int): Maximum token limit
        max_response_tokens (int): Tokens reserved for response
        
    Returns:
        list: Trimmed context
    """
    import tiktoken
    
    def count_tokens(messages):
        try:
            encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        num_tokens = 0
        for message in messages:
            num_tokens += 3  # Every message has overhead
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += 1
        num_tokens += 3  # Reply priming
        return num_tokens
    
    total_tokens = count_tokens(context)
    
    while total_tokens + max_response_tokens >= max_tokens:
        if len(context) <= 1:  # Keep system prompt
            logger.warning("Context too long even with only system prompt!")
            break
        
        del context[1]  # Remove oldest message after system
        total_tokens = count_tokens(context)
        logger.debug("Context trimmed to {} tokens".format(total_tokens))
    
    return context
