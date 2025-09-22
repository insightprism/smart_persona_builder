"""REST API endpoints for LLM interactions"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import asyncio
import sys

# Add paths for imports
sys.path.append('/home/markly2/prismmind')
sys.path.append('/home/markly2/claude_code/smart_conversation_builder_slim')

from spb_core.spb_prismmind_service import test_conversation_with_llm
from bcb_core.bcb_data_models import SCBConversation, ConversationBlock, BlockMetadata
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/llm", tags=["llm"])

@router.post("/generate")
async def generate_llm_response(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate LLM response based on system and user prompts.

    Args:
        request_data: Dictionary containing:
            - system_prompt: System instruction for the AI
            - user_prompt: User's message
            - conversation_history: Optional list of previous conversation blocks
            - llm_provider: Optional LLM provider (default: claude_balanced_medium_creativity)
            - temperature: Optional temperature (0.0-1.0)
            - max_tokens: Optional max tokens

    Returns:
        Dict with success status and generated response
    """
    try:
        # Extract parameters
        system_prompt = request_data.get("system_prompt", "You are a helpful assistant.")
        user_prompt = request_data.get("user_prompt", "")
        conversation_history = request_data.get("conversation_history", [])
        llm_provider = request_data.get("llm_provider", "claude_balanced_medium_creativity")
        temperature = request_data.get("temperature", None)
        max_tokens = request_data.get("max_tokens", None)

        if not user_prompt:
            raise HTTPException(400, "User prompt is required")

        # Create conversation blocks from history
        blocks = []

        # Add system prompt as first block if provided
        if system_prompt:
            current_time = datetime.utcnow().isoformat() + "Z"
            metadata = BlockMetadata(
                block_id=str(uuid.uuid4()),
                timestamp=current_time,
                tokens=0,
                model="system",
                modified_at=current_time
            )
            blocks.append(ConversationBlock(
                system=system_prompt,
                user="",
                assistant="",
                context="",
                metadata=metadata,
                context_injections=[],
                search_metadata=None
            ))

        # Add conversation history blocks
        for hist_block in conversation_history:
            current_time = datetime.utcnow().isoformat() + "Z"
            metadata = BlockMetadata(
                block_id=hist_block.get("id", str(uuid.uuid4())),
                timestamp=hist_block.get("timestamp", current_time),
                tokens=0,
                model="conversation",
                modified_at=current_time
            )
            blocks.append(ConversationBlock(
                system=hist_block.get("system", ""),
                user=hist_block.get("user", ""),
                assistant=hist_block.get("assistant", ""),
                context="",
                metadata=metadata,
                context_injections=[],
                search_metadata=None
            ))

        # Add current user prompt as the last block
        current_time = datetime.utcnow().isoformat() + "Z"
        metadata = BlockMetadata(
            block_id=str(uuid.uuid4()),
            timestamp=current_time,
            tokens=0,
            model="current",
            modified_at=current_time
        )
        blocks.append(ConversationBlock(
            system="",
            user=user_prompt,
            assistant="",  # This will be filled by LLM
            context="",
            metadata=metadata,
            context_injections=[],
            search_metadata=None
        ))

        # Create SCBConversation object
        conversation = SCBConversation(
            blocks=blocks
        )

        # Call LLM service
        result = await test_conversation_with_llm(
            scb_conversation=conversation,
            llm_provider=llm_provider,
            llm_handler_name="pm_simple_persona_block_chain_handler_async",
            llm_temperature=temperature,
            llm_max_tokens=max_tokens
        )

        if result.get("success"):
            return {
                "success": True,
                "response": result.get("response", ""),
                "metadata": result.get("metadata", {}),
                "conversation_context": result.get("conversation_context", {})
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "LLM generation failed"),
                "response": ""
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error generating LLM response: {str(e)}")

@router.get("/providers")
async def get_llm_providers() -> Dict[str, List[str]]:
    """Get available LLM providers"""
    return {
        "providers": [
            "claude_balanced_medium_creativity",
            "claude_creative_high_creativity",
            "claude_precise_low_creativity",
            "openai_balanced_medium_creativity",
            "openai_compact_low_creativity",
            "gpt4_balanced_medium_creativity"
        ]
    }

@router.post("/test")
async def test_llm_connection() -> Dict[str, Any]:
    """Test LLM connection with a simple prompt"""
    try:
        # Create a simple test conversation
        current_time = datetime.utcnow().isoformat() + "Z"
        metadata = BlockMetadata(
            block_id=str(uuid.uuid4()),
            timestamp=current_time,
            tokens=0,
            model="test",
            modified_at=current_time
        )

        test_block = ConversationBlock(
            system="You are a helpful assistant.",
            user="Say 'Hello, LLM is working!' if you can hear me.",
            assistant="",
            context="",
            metadata=metadata,
            context_injections=[],
            search_metadata=None
        )

        conversation = SCBConversation(
            blocks=[test_block]
        )

        result = await test_conversation_with_llm(
            scb_conversation=conversation,
            llm_provider="claude_balanced_medium_creativity",
            llm_temperature=0.3,
            llm_max_tokens=100
        )

        return {
            "success": result.get("success", False),
            "message": "LLM connection test completed",
            "response": result.get("response", ""),
            "provider": result.get("metadata", {}).get("provider", "unknown")
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"LLM connection test failed: {str(e)}",
            "response": "",
            "provider": "unknown"
        }