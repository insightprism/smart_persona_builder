"""Tests for system prompt generation"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spb_core.persona_models import create_empty_persona, add_trait_block
from spb_core.prompt_generator import (
    generate_system_prompt,
    filter_traits_by_context,
    format_trait_block,
    generate_conversation_starter,
    extract_key_traits
)

def test_generate_system_prompt_empty():
    """Test prompt generation for empty persona"""
    prompt = generate_system_prompt({})
    assert prompt == "You are a helpful assistant."
    
    prompt2 = generate_system_prompt(None)
    assert prompt2 == "You are a helpful assistant."

def test_generate_system_prompt_basic():
    """Test basic system prompt generation"""
    persona = create_empty_persona("test", "Test Person", "A test persona")
    persona = add_trait_block(persona, "professional", {"role": "Teacher", "experience": "10 years"})
    
    prompt = generate_system_prompt(persona)
    
    assert "You are Test Person" in prompt
    assert "A test persona" in prompt
    assert "Professional:" in prompt
    assert "Role: Teacher" in prompt
    assert "Experience: 10 years" in prompt
    assert "Maintain these characteristics consistently" in prompt

def test_generate_system_prompt_with_context():
    """Test context-filtered prompt generation"""
    persona = create_empty_persona("test", "Dr. Smith")
    persona = add_trait_block(persona, "professional", {"role": "Doctor"})
    persona = add_trait_block(persona, "demographics", {"age": 45})
    persona = add_trait_block(persona, "personality", {"temperament": "calm"})
    
    # Professional context should filter traits
    prompt = generate_system_prompt(persona, "professional")
    
    assert "Professional:" in prompt
    assert "Role: Doctor" in prompt
    # Demographics shouldn't be in professional context
    assert "Age:" not in prompt

def test_filter_traits_by_context():
    """Test trait filtering by context"""
    traits = {
        "professional": {"role": "Engineer"},
        "demographics": {"age": 30},
        "personality": {"temperament": "friendly"},
        "communication_style": {"tone": "casual"}
    }
    
    # Test professional context
    filtered = filter_traits_by_context(traits, "professional")
    assert "professional" in filtered
    assert "communication_style" in filtered
    assert "demographics" not in filtered
    
    # Test social context  
    filtered = filter_traits_by_context(traits, "social")
    assert "personality" in filtered
    assert "professional" not in filtered
    
    # Test unknown context (returns all)
    filtered = filter_traits_by_context(traits, "unknown")
    assert filtered == traits

def test_format_trait_block():
    """Test trait block formatting"""
    # Simple traits
    traits = {"role": "Teacher", "experience": 10}
    formatted = format_trait_block("professional", traits)
    
    assert "Professional:" in formatted
    assert "- Role: Teacher" in formatted
    assert "- Experience: 10" in formatted
    
    # List values
    traits_list = {"skills": ["Python", "JavaScript", "SQL"]}
    formatted = format_trait_block("capabilities", traits_list)
    
    assert "Capabilities:" in formatted
    assert "- Skills: Python, JavaScript, SQL" in formatted
    
    # Nested dict
    traits_nested = {
        "education": {
            "degree": "Ph.D.",
            "field": "Computer Science"
        }
    }
    formatted = format_trait_block("background", traits_nested)
    
    assert "Background:" in formatted
    assert "- Education:" in formatted
    assert "  - Degree: Ph.D." in formatted
    assert "  - Field: Computer Science" in formatted
    
    # Empty traits
    formatted = format_trait_block("empty", {})
    assert formatted == ""

def test_generate_conversation_starter():
    """Test conversation starter generation"""
    persona = create_empty_persona("test", "Jane Doe")
    
    # Basic starter
    starter = generate_conversation_starter(persona)
    assert "Hello! I'm Jane Doe." in starter
    assert "How can I help you today?" in starter
    
    # Professional context
    persona = add_trait_block(persona, "professional", {"role": "Consultant"})
    starter = generate_conversation_starter(persona, "professional")
    assert "As a Consultant" in starter
    
    # Teaching context
    starter = generate_conversation_starter(persona, "teaching")
    assert "help you learn" in starter or "How can I help" in starter
    
    # Customer service context
    starter = generate_conversation_starter(persona, "customer_service")
    assert "How may I assist you today?" in starter

def test_extract_key_traits():
    """Test key trait extraction"""
    persona = create_empty_persona("test", "Test")
    persona = add_trait_block(persona, "professional", {
        "role": "Engineer",
        "experience": "5 years",
        "company": "TechCorp"
    })
    persona = add_trait_block(persona, "personality", {
        "temperament": "analytical",
        "social_style": "introverted"
    })
    
    traits = extract_key_traits(persona, max_traits=3)
    
    assert len(traits) <= 3
    assert any("role: Engineer" in t for t in traits)
    assert any("experience: 5 years" in t for t in traits)
    
    # Test with no traits
    empty_persona = create_empty_persona("empty", "Empty")
    traits = extract_key_traits(empty_persona)
    assert traits == []

def test_complex_prompt_generation():
    """Test prompt generation with complex persona"""
    persona = create_empty_persona("complex", "Dr. Sarah Johnson", "Experienced physician and educator")
    
    persona = add_trait_block(persona, "professional", {
        "role": "Emergency Room Physician",
        "experience": "15 years",
        "specialties": ["Trauma", "Critical Care"],
        "hospital": "City General"
    })
    
    persona = add_trait_block(persona, "communication_style", {
        "bedside_manner": "compassionate but direct",
        "explanations": "uses simple terms",
        "urgency_response": "calm under pressure"
    })
    
    persona = add_trait_block(persona, "values_beliefs", {
        "medical_ethics": "first do no harm",
        "patient_advocacy": "strong advocate",
        "continuous_learning": "evidence-based practice"
    })
    
    # Generate for medical context
    prompt = generate_system_prompt(persona, "medical")
    
    # Should have name and description
    assert "Dr. Sarah Johnson" in prompt
    assert "Experienced physician and educator" in prompt
    
    # Check that it's properly formatted
    lines = prompt.split("\n")
    assert any("You are" in line for line in lines)
    assert any("Maintain these characteristics" in line for line in lines)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])