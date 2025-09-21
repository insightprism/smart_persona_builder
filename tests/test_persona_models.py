"""Tests for persona models and operations"""

import pytest
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spb_core.persona_models import (
    create_empty_persona,
    add_trait_block,
    remove_trait_block,
    validate_categories,
    merge_personas,
    clone_persona,
    VALID_CATEGORIES
)

def test_create_empty_persona():
    """Test creating an empty persona"""
    persona = create_empty_persona(
        persona_id="test_001",
        name="Test Person",
        description="A test persona",
        category="professional"
    )
    
    assert persona["persona_id"] == "test_001"
    assert persona["name"] == "Test Person"
    assert persona["description"] == "A test persona"
    assert persona["category"] == "professional"
    assert persona["personality_traits"] == {}
    assert "llm_config" in persona
    assert "metadata" in persona
    assert "created_at" in persona["metadata"]

def test_add_trait_block():
    """Test adding trait blocks to persona"""
    persona = create_empty_persona("test_002", "Test")
    
    # Add valid trait block
    traits = {"age": 30, "location": "New York"}
    updated = add_trait_block(persona, "demographics", traits)
    
    assert "demographics" in updated["personality_traits"]
    assert updated["personality_traits"]["demographics"] == traits
    
    # Test invalid category
    with pytest.raises(ValueError, match="Invalid category"):
        add_trait_block(persona, "invalid_category", traits)

def test_remove_trait_block():
    """Test removing trait blocks from persona"""
    persona = create_empty_persona("test_003", "Test")
    
    # Add then remove
    traits = {"role": "Engineer"}
    persona = add_trait_block(persona, "professional", traits)
    assert "professional" in persona["personality_traits"]
    
    updated = remove_trait_block(persona, "professional")
    assert "professional" not in updated["personality_traits"]
    
    # Remove non-existent category (should not error)
    updated2 = remove_trait_block(updated, "nonexistent")
    assert updated2 == updated

def test_validate_categories():
    """Test category validation"""
    # Valid categories
    persona = {
        "personality_traits": {
            "demographics": {},
            "professional": {}
        }
    }
    is_valid, errors = validate_categories(persona)
    assert is_valid
    assert errors == []
    
    # Invalid categories
    persona2 = {
        "personality_traits": {
            "invalid_cat": {},
            "another_invalid": {}
        }
    }
    is_valid, errors = validate_categories(persona2)
    assert not is_valid
    assert "invalid_cat" in errors
    assert "another_invalid" in errors

def test_merge_personas():
    """Test merging two personas"""
    base = create_empty_persona("base", "Base Person")
    base = add_trait_block(base, "demographics", {"age": 30})
    base = add_trait_block(base, "professional", {"role": "Teacher"})
    
    overlay = create_empty_persona("overlay", "Overlay Person")
    overlay = add_trait_block(overlay, "demographics", {"age": 35, "location": "Boston"})
    overlay = add_trait_block(overlay, "personality", {"temperament": "calm"})
    
    merged = merge_personas(base, overlay)
    
    # Check merged traits
    assert merged["personality_traits"]["demographics"]["age"] == 35  # Overlay wins
    assert merged["personality_traits"]["demographics"]["location"] == "Boston"  # From overlay
    assert merged["personality_traits"]["professional"]["role"] == "Teacher"  # From base
    assert merged["personality_traits"]["personality"]["temperament"] == "calm"  # From overlay

def test_clone_persona():
    """Test cloning a persona"""
    original = create_empty_persona("original", "Original Person")
    original = add_trait_block(original, "demographics", {"age": 40})
    
    cloned = clone_persona(original, "cloned_001", "Cloned Person")
    
    assert cloned["persona_id"] == "cloned_001"
    assert cloned["name"] == "Cloned Person"
    assert cloned["personality_traits"] == original["personality_traits"]
    assert cloned["metadata"]["created_at"] != original["metadata"]["created_at"]

def test_trait_block_flexibility():
    """Test that trait blocks accept any key-value pairs"""
    persona = create_empty_persona("flex_test", "Flexible")
    
    # Test various data types
    complex_traits = {
        "string_value": "text",
        "number_value": 42,
        "float_value": 3.14,
        "boolean_value": True,
        "list_value": ["item1", "item2"],
        "nested_dict": {
            "sub_key": "sub_value"
        },
        "custom_field_xyz": "anything goes"
    }
    
    updated = add_trait_block(persona, "professional", complex_traits)
    
    assert updated["personality_traits"]["professional"] == complex_traits

def test_all_valid_categories():
    """Test that all documented categories are valid"""
    persona = create_empty_persona("cat_test", "Category Test")
    
    # Test each valid category
    for category in VALID_CATEGORIES:
        traits = {f"test_{category}": "value"}
        persona = add_trait_block(persona, category, traits)
        assert category in persona["personality_traits"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])