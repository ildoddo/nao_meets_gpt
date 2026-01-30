"""
GPT Client
Gestisce comunicazione con LLM via LiteLLM
"""

import logging
from litellm import completion

logger = logging.getLogger(__name__)


class GPTClient:
    """Client for GPT/LLM communication"""
    
    def __init__(self, model="github/gpt-4o-mini", api_base=None, timeout=30):
        """
        Initialize GPT client
        
        Args:
            model (str): Model identifier
            api_base (str): API base URL
            timeout (int): Request timeout
        """
        self.model = model
        self.api_base = api_base or "https://models.inference.ai.azure.com"
        self.timeout = timeout
    
    def generate_response(self, conversation_context, max_tokens=250, temperature=0.7):
        """
        Generate response from GPT
        
        Args:
            conversation_context (list): List of message dicts
            max_tokens (int): Maximum tokens for response
            temperature (float): Temperature for generation
            
        Returns:
            str or None: Generated text or None on failure
        """
        try:
            logger.info("🤖 Generating response with {}...".format(self.model))
            
            import time
            start_time = time.time()
            
            response = completion(
                model=self.model,
                messages=conversation_context,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                api_base=self.api_base,
                timeout=self.timeout
            )
            
            elapsed = time.time() - start_time
            logger.info("✓ Response generated in {:.2f}s".format(elapsed))
            
            # Extract message
            gpt_message = response.choices[0].message.content.strip()
            
            # Log token usage
            if hasattr(response, 'usage'):
                logger.info("  Tokens: {} (prompt: {}, completion: {})".format(
                    response.usage.total_tokens,
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                ))
            
            logger.info("🤖 GPT: {}".format(gpt_message[:100] + "..." if len(gpt_message) > 100 else gpt_message))
            
            return gpt_message
            
        except Exception as e:
            logger.error("❌ GPT API error: {}".format(e))
            return None
    
    def generate_with_fallback(self, conversation_context, fallback_message=None, **kwargs):
        """
        Generate response with automatic fallback
        
        Args:
            conversation_context (list): Conversation history
            fallback_message (str): Message to return on failure
            **kwargs: Additional arguments for generate_response
            
        Returns:
            str: Generated text or fallback message
        """
        response = self.generate_response(conversation_context, **kwargs)
        
        if response:
            return response
        
        # Fallback
        if fallback_message is None:
            fallback_message = "Mi dispiace, ho avuto un problema. Puoi ripetere?"
        
        logger.warning("Using fallback: {}".format(fallback_message))
        return fallback_message
