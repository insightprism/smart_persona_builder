"""Tests for persona validation functions"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spb_core.persona_validator import (
    validate_persona_structure,
    validate_trait_block,
    validate_llm_config,
    check_persona_completeness,
    suggest_missing_traits
)
from spb_core.persona_models import create_empty_persona, add_trait_block

def test_validate_persona_structure_valid():
    """Test validation of valid persona structure"""
    persona = {
        "persona_id": "valid_001",
        "name": "Valid Person",
        "description": "A valid persona",
        "category": "professional",
        "personality_traits": {
            "demographics": {"age": 30}
        },
        "llm_config": {
            "provider": "openai",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "metadata": {}
    }
    
    is_valid, errors = validate_persona_structure(persona)
    assert is_valid
    assert errors == []

def test_validate_persona_structure_missing_required():
    """Test validation with missing required fields"""
    # Missing persona_id
    persona = {"name": "No ID"}
    is_valid, errors = validate_persona_structure(persona)
    assert not is_valid
    assert "Missing required field: persona_id" in errors
    
    # Missing name
    persona = {"persona_id": "test"}
    is_valid, errors = validate_persona_structure(persona)
    assert not is_valid
    assert "Missing required field: name" in errors
    
    # Empty strings
    persona = {"persona_id": "", "name": ""}
    is_valid, errors = validate_persona_structure(persona)
    assert not is_valid
    assert any("non-empty string" in e for e in errors)

def test_validate_persona_structure_wrong_types():
    """Test validation with wrong field types"""
    persona = {
        "persona_id": "test",
        "name": "Test",
        "description": 123,  # Should be string
        "category": ["wrong"],  # Should be string
        "personality_traits": "not a dict",  # Should be dict
        "llm_config": ["not", "a", "dict"],  # Should be dict
        "metadata": "not a dict"  # Should be dict
    }
    
    is_valid, errors = validate_persona_structure(persona)
    assert not is_valid
    assert "description must be a string" in errors
    assert "category must be a string" in errors
    assert "personality_traits must be a dictionary" in errors
    assert "llm_config must be a dictionary" in errors
    assert "metadata must be a dictionary" in errors

def test_validate_persona_structure_invalid_categories():
    """Test validation with invalid trait categories"""
    persona = {
        "persona_id": "test",
        "name": "Test",
        "personality_traits": {
            "demographics": {},  # Valid
            "invalid_category": {},  # Invalid
            "another_invalid": {}  # Invalid
        }
    }
    
    is_valid, errors = validate_persona_structure(persona)
    assert not is_valid
    assert "Invalid trait category: invalid_category" in errors
    assert "Invalid trait category: another_invalid" in errors

def test_validate_trait_block():
    """Test validation of individual trait blocks"""
    # Valid trait block
    is_valid, errors = validate_trait_block("demographics", {"age": 30, "location": "NYC"})
    assert is_valid
    assert errors == []
    
    # Invalid category
    is_valid, errors = validate_trait_block("invalid_cat", {"key": "value"})
    assert not is_valid
    assert "Invalid category: invalid_cat" in errors
    
    # Not a dictionary
    is_valid, errors = validate_trait_block("demographics", "not a dict")
    assert not is_valid
    assert "Traits must be a dictionary" in errors
    
    # Empty dictionary
    is_valid, errors = validate_trait_block("demographics", {})
    assert not is_valid
    assert "Trait block cannot be empty" in errors
    
    # Invalid key type
    is_valid, errors = validate_trait_block("demographics", {123: "value"})
    assert not is_valid
    assert any("Trait key must be a string" in e for e in errors)
    
    # Empty key
    is_valid, errors = validate_trait_block("demographics", {"": "value"})
    assert not is_valid
    assert "Trait key cannot be empty" in errors
    
    # Unsupported value type
    class CustomClass:
        pass
    is_valid, errors = validate_trait_block("demographics", {"key": CustomClass()})
    assert not is_valid
    assert any("unsupported type" in e for e in errors)

def test_validate_trait_block_complex_values():
    """Test validation with complex but valid values"""
    traits = {
        "string": "text",
        "integer": 42,
        "float": 3.14,
        "boolean": True,
        "list": [1, 2, "three"],
        "nested_dict": {
            "sub_key": "sub_value"
        }
    }
    
    is_valid, errors = validate_trait_block("professional", traits)
    assert is_valid
    assert errors == []

def test_validate_llm_config():
    """Test LLM configuration validation"""
    # Valid config
    errors = validate_llm_config({
        "provider": "openai",
        "temperature": 0.7,
        "max_tokens": 2000
    })
    assert errors == []
    
    # Invalid provider
    errors = validate_llm_config({"provider": "invalid_provider"})
    assert "Invalid LLM provider: invalid_provider" in errors
    
    # Invalid temperature
    errors = validate_llm_config({"temperature": "not a number"})
    assert "Temperature must be a number" in errors
    
    errors = validate_llm_config({"temperature": -1})
    assert "Temperature must be between 0 and 2" in errors
    
    errors = validate_llm_config({"temperature": 3})
    assert "Temperature must be between 0 and 2" in errors
    
    # Invalid max_tokens
    errors = validate_llm_config({"max_tokens": "not an int"})
    assert "max_tokens must be an integer" in errors
    
    errors = validate_llm_config({"max_tokens": 0})
    assert "max_tokens must be between 1 and 100000" in errors
    
    errors = validate_llm_config({"max_tokens": 200000})
    assert "max_tokens must be between 1 and 100000" in errors

def test_check_persona_completeness():
    """Test checking persona completeness"""
    # Empty persona
    persona = create_empty_persona("test", "Test")
    metrics = check_persona_completeness(persona)
    
    assert metrics["total_categories"] == 10  # Number of valid categories
    assert metrics["filled_categories"] == 0
    assert len(metrics["missing_categories"]) == 10
    assert metrics["total_traits"] == 0
    assert metrics["completeness_score"] == 0.0
    
    # Partially complete persona
    persona = add_trait_block(persona, "demographics", {"age": 30, "location": "NYC"})
    persona = add_trait_block(persona, "professional", {"role": "Engineer"})
    metrics = check_persona_completeness(persona)
    
    assert metrics["filled_categories"] == 2
    assert len(metrics["missing_categories"]) == 8
    assert metrics["total_traits"] == 3
    assert metrics["completeness_score"] > 0
    
    # More complete persona
    for category in ["personality", "communication_style", "values_beliefs"]:
        persona = add_trait_block(persona, category, {f"{category}_trait": "value"})
    
    metrics = check_persona_completeness(persona)
    assert metrics["filled_categories"] == 5
    assert metrics["total_traits"] == 6
    assert metrics["completeness_score"] > 25  # At least 25% complete

def test_suggest_missing_traits():
    """Test trait suggestions"""
    # Empty persona
    persona = create_empty_persona("test", "Test")
    suggestions = suggest_missing_traits(persona)
    # Just check that suggestions exist - content may vary
    assert len(suggestions) > 0
    
    # Professional persona without professional traits
    persona = {"category": "professional", "personality_traits": {}}
    suggestions = suggest_missing_traits(persona)
    assert any("professional" in s for s in suggestions)
    
    # Any persona without common traits
    persona = {"personality_traits": {"demographics": {}}}
    suggestions = suggest_missing_traits(persona)
    assert any("communication_style" in s for s in suggestions)
    assert any("personality" in s for s in suggestions)
    
    # Political persona
    persona = {"category": "political", "personality_traits": {}}
    suggestions = suggest_missing_traits(persona)
    assert any("values_beliefs" in s for s in suggestions)
    
    # Well-populated persona
    persona = create_empty_persona("complete", "Complete")
    for cat in ["professional", "communication_style", "personality", "values_beliefs", "demographics"]:
        persona = add_trait_block(persona, cat, {"test": "value"})
    
    suggestions = suggest_missing_traits(persona)
    # Should have fewer suggestions
    assert len(suggestions) < 3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])