#!/usr/bin/env python3
"""
Test script for the enhanced pm_sbc_conversation_handler_async with image processing support.

This script tests:
1. Handler works without images (backward compatibility)
2. Handler processes images correctly when provided
3. Error handling for invalid images
"""

import sys
import asyncio
from pathlib import Path

# Add paths for imports
sys.path.append('/home/markly2/prismmind')
sys.path.append('/home/markly2/claude_code/smart_persona_builder_slim')
sys.path.append('/home/markly2/claude_code/smart_conversation_builder_slim')  # Add conversation builder to path

try:
    from pm_engines.pm_llm_engine import pm_sbc_conversation_handler_async
    from pm_config.pm_llm_engine_config import pm_get_llm_config, pm_llm_config_dto
    from bcb_core.bcb_data_models import ConversationBlock, BlockMetadata
    from PIL import Image
    import io
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def create_test_conversation_block():
    """Create a sample ConversationBlock for testing."""
    from datetime import datetime
    import uuid

    current_time = datetime.utcnow().isoformat() + "Z"

    metadata = BlockMetadata(
        block_id=str(uuid.uuid4()),
        timestamp=current_time,
        tokens=50,
        model="test-model",
        modified_at=current_time
    )

    return ConversationBlock(
        system="You are a helpful DIY assistant specializing in home repairs.",
        user="I have a plumbing issue that needs fixing.",
        assistant="I'd be happy to help you with your plumbing problem. Can you describe what's happening?",
        context="Home repair context for pipe issues",
        metadata=metadata,
        context_injections=[],
        search_metadata=None
    )

def create_test_image():
    """Create a simple test image."""
    # Create a small test image (100x100 red square)
    img = Image.new('RGB', (100, 100), color='red')
    return img

def get_pipe_leak_image_path():
    """Get path to the real pipe leak image for testing."""
    # Path to the actual pipe leak image provided by user
    image_path = "/home/markly2/claude_code/smart_conversation_builder_slim/test_images/pipe_leak.jpg"
    return image_path

async def test_without_image():
    """Test handler without image (backward compatibility)."""
    print("\n🧪 Testing without image (backward compatibility)...")

    try:
        # Create test data
        test_block = create_test_conversation_block()
        input_data = "What tools do I need to fix this pipe?"
        rag_data = {
            "sbc_conversation": [test_block]
        }

        # Get LLM config using proper pattern from test_conversation_with_llm
        base_config = pm_llm_config_dto(
            llm_provider="claude_balanced_medium_creativity",
            handler_name="pm_sbc_conversation_handler_async",
            temperature=0.7,
            max_tokens=2048
        )
        llm_config = pm_get_llm_config(base_config)

        # Call the handler
        result = await pm_sbc_conversation_handler_async(
            input_data=input_data,
            llm_config=llm_config,
            handler_config=None,
            rag_data=rag_data
        )

        # Verify result structure
        assert result.get("success") is True, "Handler should return success=True"
        assert "output_content" in result, "Result should contain output_content"
        assert "sbc_output_block" in result, "Result should contain sbc_output_block"
        assert "metadata" in result, "Result should contain metadata"

        print("✅ Test without image: PASSED")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Output length: {len(result.get('output_content', ''))}")
        print(f"   - Has sbc_output_block: {result.get('sbc_output_block') is not None}")

        return True

    except Exception as e:
        print(f"❌ Test without image: FAILED - {e}")
        return False

async def test_with_image():
    """Test handler with image."""
    print("\n🧪 Testing with image...")

    try:
        # Create test data
        test_block = create_test_conversation_block()
        test_image = create_test_image()
        input_data = "What do you see in this image? Can you help me identify the problem?"
        rag_data = {
            "sbc_conversation": [test_block],
            "image": test_image  # Pass PIL Image directly
        }

        # Get LLM config using proper pattern from test_conversation_with_llm
        base_config = pm_llm_config_dto(
            llm_provider="claude_balanced_medium_creativity",
            handler_name="pm_sbc_conversation_handler_async",
            temperature=0.7,
            max_tokens=2048
        )
        llm_config = pm_get_llm_config(base_config)

        # Call the handler
        result = await pm_sbc_conversation_handler_async(
            input_data=input_data,
            llm_config=llm_config,
            handler_config=None,
            rag_data=rag_data
        )

        # Verify result structure
        assert result.get("success") is True, "Handler should return success=True"
        assert "output_content" in result, "Result should contain output_content"
        assert "sbc_output_block" in result, "Result should contain sbc_output_block"
        assert "metadata" in result, "Result should contain metadata"

        print("✅ Test with image: PASSED")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Output length: {len(result.get('output_content', ''))}")
        print(f"   - Has sbc_output_block: {result.get('sbc_output_block') is not None}")

        return True

    except Exception as e:
        print(f"❌ Test with image: FAILED - {e}")
        return False

async def test_invalid_image():
    """Test handler with invalid image."""
    print("\n🧪 Testing with invalid image...")

    try:
        # Create test data with invalid image (not string, bytes, or PIL)
        test_block = create_test_conversation_block()
        input_data = "What do you see in this image?"
        rag_data = {
            "sbc_conversation": [test_block],
            "image": 12345  # This should cause a ValueError - invalid type
        }

        # Get LLM config using proper pattern from test_conversation_with_llm
        base_config = pm_llm_config_dto(
            llm_provider="claude_balanced_medium_creativity",
            handler_name="pm_sbc_conversation_handler_async",
            temperature=0.7,
            max_tokens=2048
        )
        llm_config = pm_get_llm_config(base_config)

        # Call the handler - should raise an exception
        try:
            result = await pm_sbc_conversation_handler_async(
                input_data=input_data,
                llm_config=llm_config,
                handler_config=None,
                rag_data=rag_data
            )
            print("❌ Test with invalid image: FAILED - Should have raised an exception")
            return False
        except ValueError as e:
            if "image_input must be a file path, bytes, or PIL.Image" in str(e):
                print("✅ Test with invalid image: PASSED - Correctly rejected invalid image")
                return True
            else:
                print(f"❌ Test with invalid image: FAILED - Wrong error: {e}")
                return False

    except Exception as e:
        print(f"❌ Test with invalid image: FAILED - Unexpected error: {e}")
        return False

async def test_with_pipe_leak_image():
    """Test handler with real pipe leak image."""
    print("\n🧪 Testing with pipe leak image...")

    try:
        # Create test data with pipe repair context
        test_block = create_test_conversation_block()
        pipe_image_path = get_pipe_leak_image_path()
        input_data = "I'm seeing water spraying from this pipe connection. What type of fitting is this and how should I fix it?"
        rag_data = {
            "sbc_conversation": [test_block],
            "image": pipe_image_path  # Pass image file path
        }

        # Get LLM config using proper pattern from test_conversation_with_llm
        base_config = pm_llm_config_dto(
            llm_provider="claude_balanced_medium_creativity",
            handler_name="pm_sbc_conversation_handler_async",
            temperature=0.7,
            max_tokens=2048
        )
        llm_config = pm_get_llm_config(base_config)

        # Call the handler
        result = await pm_sbc_conversation_handler_async(
            input_data=input_data,
            llm_config=llm_config,
            handler_config=None,
            rag_data=rag_data
        )

        # Verify result structure
        assert result.get("success") is True, "Handler should return success=True"
        assert "output_content" in result, "Result should contain output_content"
        assert "sbc_output_block" in result, "Result should contain sbc_output_block"
        assert "metadata" in result, "Result should contain metadata"

        print("✅ Test with pipe leak image: PASSED")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Output length: {len(result.get('output_content', ''))}")
        print(f"   - Has sbc_output_block: {result.get('sbc_output_block') is not None}")
        print(f"   - Image path used: {pipe_image_path}")

        # Show a snippet of the response for context
        response = result.get('output_content', '')
        if len(response) > 200:
            print(f"   - Response preview: {response[:200]}...")
        else:
            print(f"   - Full response: {response}")

        return True

    except Exception as e:
        print(f"❌ Test with pipe leak image: FAILED - {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Testing enhanced pm_sbc_conversation_handler_async with image processing")
    print("=" * 70)

    results = []

    # Test without image (backward compatibility)
    results.append(await test_without_image())

    # Test with image
    results.append(await test_with_image())

    # Test with real pipe leak image - commented out as file is placeholder
    # results.append(await test_with_pipe_leak_image())

    # Test invalid image
    results.append(await test_invalid_image())

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)

    print(f"   Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests PASSED! The enhanced handler is working correctly.")
    else:
        print("❌ Some tests FAILED. Please check the implementation.")

    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)