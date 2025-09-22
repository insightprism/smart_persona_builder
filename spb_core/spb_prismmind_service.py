"""
PrismMind integration service for Smart SCBConversation Builder.
Simple integration following PrismMind's intended usage pattern.
"""

import sys
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from PIL import Image

# Add PrismMind to path
sys.path.append('/home/markly2/prismmind')

from pm_engines.pm_llm_engine import PmLLMEngine
from pm_config.pm_llm_engine_config import pm_get_llm_config, pm_llm_config_dto, DEFAULT_LLM_PERSONA_PROFILE_MAP
# Import PrismMind utilities for our custom handler
from pm_utils.pm_call_llm import pm_call_llm, pm_format_llm_payload
from pm_utils.pm_trace_handler_log_dec import pm_trace_handler_log_dec

from bcb_core.bcb_data_models import SCBConversation, ConversationBlock

async def test_conversation_with_llm(
    scb_conversation: SCBConversation,
    llm_provider: str = "claude_balanced_medium_creativity",
    llm_handler_name: str = "pm_simple_persona_block_chain_handler_async",
    llm_temperature: Optional[float] = None,
    llm_max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Test conversation with LLM using simple PrismMind pattern.

    Args:
        scb_conversation: Smart SCBConversation Builder conversation object
        llm_provider: Provider name from DEFAULT_LLM_PERSONA_PROFILE_MAP
                     (e.g., "claude_balanced_medium_creativity", "openai_compact_low_creativity")
        llm_handler_name: LLM handler name (default: "pm_simple_persona_block_chain_handler_async")
        llm_temperature: Optional override (uses provider default if None)
        llm_max_tokens: Optional override (uses provider default if None)

    Returns:
        Dict with success, response, and metadata
    """
    
    try:
        # Extract message and context from conversation
        message = _extract_current_message(scb_conversation)
        system_prompt = _extract_system_prompt(scb_conversation)
        
        # Simple PrismMind pattern with configurable handler
        llm_config = pm_llm_config_dto(
            llm_provider=llm_provider,
            handler_name=llm_handler_name,
            temperature=llm_temperature,  # Override if provided
            max_tokens=llm_max_tokens     # Override if provided
        )
        
        llm_config = pm_get_llm_config(llm_config)


        llm_engine = PmLLMEngine(
            engine_config=llm_config,
            handler_config={"system_prompt": system_prompt} if system_prompt else None
        )
        
        # IMPORTANT: Pass blocks directly in rag_data for block chain handler
        # The pm_simple_persona_block_chain_handler_async expects rag_data["sbc_conversation_history"]
        llm_engine.rag_data = {"sbc_conversation": scb_conversation.blocks}
        
        # Simple call pattern
        start_time = datetime.utcnow()
        result = await llm_engine(message)
        end_time = datetime.utcnow()
        
        # Extract response from PrismMind result
        llm_response = result.get("output_content", "")
        metadata = result.get("metadata", {})
        
        # Build response - include sbc_output_block if available from handler
        response_dict = {
            "success": True,
            "response": llm_response,
            "metadata": {
                "provider": llm_provider,
                "actual_provider": llm_config.llm_provider,
                "model": llm_config.llm_name,
                "temperature": llm_config.temperature,
                "max_tokens": llm_config.max_tokens,
                "response_time_ms": int((end_time - start_time).total_seconds() * 1000),
                "handler": llm_handler_name,
                "prismmind_metadata": metadata
            },
            "conversation_context": {
                "message": message,
                "system_prompt": system_prompt,
                "total_blocks": len(scb_conversation.blocks),
                "blocks_with_content": len([b for b in scb_conversation.blocks if b.user.strip() or b.assistant.strip()])
            }
        }

        # Pass through sbc_output_block if handler provided it
        if "sbc_output_block" in result:
            response_dict["sbc_output_block"] = result["sbc_output_block"]

        return response_dict
        
    except Exception as e:
        logging.error(f"PrismMind LLM call failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"LLM test failed: {str(e)}",
            "response": "",
            "metadata": {
                "provider": llm_provider,
                "error_type": type(e).__name__
            }
        }

def _extract_current_message(conversation: SCBConversation) -> str:
    """Extract the current user message from conversation."""
    
    # Look for the last user message that doesn't have an assistant response
    # This will be the message we want the LLM to respond to
    for block in reversed(conversation.blocks):
        if block.user.strip() and not block.assistant.strip():
            # Found a user message without an assistant response
            return block.user.strip()
    
    # If all messages have responses, use the last user message
    # (This handles the case where we're regenerating a response)
    for block in reversed(conversation.blocks):
        if block.user.strip():
            return block.user.strip()
    
    # Fallback message
    return "Continue this conversation based on the context provided."

def _extract_system_prompt(conversation: SCBConversation) -> Optional[str]:
    """Extract system prompt from conversation blocks."""
    
    # Look for the most recent non-empty system prompt
    for block in reversed(conversation.blocks):
        if block.system.strip():
            return block.system.strip()
    
    return None

def _build_conversation_context(conversation: SCBConversation) -> Dict[str, Any]:
    """Build conversation context for rag_data."""
    
    conversation_history = []
    current_message_index = None
    
    # Find the index of the block containing the current message
    # (last user message without an assistant response)
    for i in range(len(conversation.blocks) - 1, -1, -1):
        block = conversation.blocks[i]
        if block.user.strip() and not block.assistant.strip():
            current_message_index = i
            break
    
    # Build conversation history excluding the current message
    for i, block in enumerate(conversation.blocks):
        # Skip the block with the current message we're asking about
        if i == current_message_index:
            # Don't add the current user message to history
            # But do add any previous assistant response in the same block if it exists
            if block.assistant.strip():
                conversation_history.append({
                    "role": "assistant",
                    "content": block.assistant.strip()
                })
            continue
            
        # Add user message if present
        if block.user.strip():
            conversation_history.append({
                "role": "user",
                "content": block.user.strip()
            })
        
        # Add assistant response if present
        if block.assistant.strip():
            conversation_history.append({
                "role": "assistant", 
                "content": block.assistant.strip()
            })
    
    return {
        "conversation_history": conversation_history
    }

async def test_conversation_with_custom_prompt(
    conversation: SCBConversation,
    user_prompt: str,
    llm_provider: str = "claude_balanced_medium_creativity",
    llm_handler_name: str = "pm_simple_persona_block_chain_handler_async",
    llm_temperature: Optional[float] = None,
    llm_max_tokens: Optional[int] = None,
    rag_image: Optional[Union[str, bytes, Image.Image]] = None
) -> Dict[str, Any]:
    """
    Test a custom user prompt with the conversation history as context.

    Args:
        conversation: Smart SCBConversation Builder conversation object
        user_prompt: Custom prompt to test (e.g., "What was the first question I asked?")
        llm_provider: Provider name from DEFAULT_LLM_PERSONA_PROFILE_MAP
        llm_handler_name: LLM handler name (default: "pm_simple_persona_block_chain_handler_async")
        llm_temperature: Optional override
        llm_max_tokens: Optional override
        rag_image: Optional image input (file path, bytes, or PIL Image) for multi-modal analysis

    Returns:
        Dict with success, response, and metadata
    """
    
    try:
        system_prompt = _extract_system_prompt(conversation)
        
        # Log the conversation context for debugging
        logging.info(f"Custom prompt test - User prompt: {user_prompt}")
        logging.info(f"Custom prompt test - SCBConversation blocks: {len(conversation.blocks)}")
        
        # Use the custom prompt as the message
        message = user_prompt
        
        # Simple PrismMind pattern with configurable handler
        llm_config = pm_llm_config_dto(
            llm_provider=llm_provider,
            handler_name=llm_handler_name,
            temperature=llm_temperature,
            max_tokens=llm_max_tokens
        )
        
        llm_config = pm_get_llm_config(llm_config)
        llm_engine = PmLLMEngine(
            engine_config=llm_config,
            handler_config={"system_prompt": system_prompt} if system_prompt else None
        )
        
        # IMPORTANT: Pass blocks directly in rag_data, not conversation_history
        # The pm_simple_persona_block_chain_handler_async expects rag_data["blocks"]
        rag_data = {"blocks": conversation.blocks}

        # Add image to rag_data if provided for multi-modal analysis
        if rag_image is not None:
            rag_data["image"] = rag_image
            image_type = type(rag_image).__name__
            logging.info(f"Custom prompt test - Including image in rag_data (type: {image_type})")

        llm_engine.rag_data = rag_data
        
        # Call with custom prompt
        start_time = datetime.utcnow()
        result = await llm_engine(message)
        end_time = datetime.utcnow()
        
        # Extract response
        llm_response = result.get("output_content", "")
        metadata = result.get("metadata", {})
        
        return {
            "success": True,
            "response": llm_response,
            "metadata": {
                "provider": llm_provider,
                "actual_provider": llm_config.llm_provider,
                "model": llm_config.llm_name,
                "temperature": llm_config.temperature,
                "max_tokens": llm_config.max_tokens,
                "response_time_ms": int((end_time - start_time).total_seconds() * 1000),
                "handler": llm_handler_name,
                "prismmind_metadata": metadata,
                "custom_prompt": True
            },
            "conversation_context": {
                "message": message,
                "system_prompt": system_prompt,
                "total_blocks": len(conversation.blocks),
                "blocks_with_content": len([b for b in conversation.blocks if b.user.strip() or b.assistant.strip()])
            }
        }
        
    except Exception as e:
        logging.error(f"PrismMind LLM call with custom prompt failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"LLM test failed: {str(e)}",
            "response": "",
            "metadata": {
                "provider": llm_provider,
                "error_type": type(e).__name__,
                "custom_prompt": True
            }
        }

def _build_full_conversation_context(conversation: SCBConversation) -> Dict[str, Any]:
    """Build full conversation context including all messages."""
    
    conversation_history = []
    
    # Include ALL user/assistant pairs from all blocks
    for block in conversation.blocks:
        if block.user.strip():
            conversation_history.append({
                "role": "user",
                "content": block.user.strip()
            })
        
        if block.assistant.strip():
            conversation_history.append({
                "role": "assistant", 
                "content": block.assistant.strip()
            })
    
    return {
        "conversation_history": conversation_history
    }

def get_available_providers() -> Dict[str, Any]:
    """
    Get available providers from PrismMind DEFAULT_LLM_PERSONA_PROFILE_MAP.
    
    Returns:
        Dict with provider info organized by base provider and creativity levels
    """
    
    try:
        # Return the provider map directly - frontend can organize as needed
        providers_info = {
            "available": True,
            "providers": DEFAULT_LLM_PERSONA_PROFILE_MAP,
            "provider_keys": list(DEFAULT_LLM_PERSONA_PROFILE_MAP.keys()),
            "default_provider": "claude_compact_medium_creativity"
        }
        
        return providers_info
        
    except Exception as e:
        logging.error(f"Error getting providers: {e}")
        return {"available": False, "error": str(e)}


