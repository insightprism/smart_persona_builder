"""Validation functions for persona structures"""

from typing import Dict, List, Tuple, Any, Optional
from .persona_models import VALID_CATEGORIES

def validate_persona_structure(persona: Dict) -> Tuple[bool, List[str]]:
    """Validate the overall structure of a persona
    
    Args:
        persona: The persona dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    if "persona_id" not in persona:
        errors.append("Missing required field: persona_id")
    elif not isinstance(persona["persona_id"], str) or not persona["persona_id"]:
        errors.append("persona_id must be a non-empty string")
    
    if "name" not in persona:
        errors.append("Missing required field: name")
    elif not isinstance(persona["name"], str) or not persona["name"]:
        errors.append("name must be a non-empty string")
    
    # Check optional fields have correct types
    if "description" in persona and not isinstance(persona["description"], str):
        errors.append("description must be a string")
    
    if "category" in persona and not isinstance(persona["category"], str):
        errors.append("category must be a string")
    
    # Validate personality_traits structure
    if "personality_traits" in persona:
        if not isinstance(persona["personality_traits"], dict):
            errors.append("personality_traits must be a dictionary")
        else:
            # Check that all categories are valid
            for category in persona["personality_traits"].keys():
                if category not in VALID_CATEGORIES:
                    errors.append(f"Invalid trait category: {category}")
                elif not isinstance(persona["personality_traits"][category], dict):
                    errors.append(f"Trait category '{category}' must contain a dictionary")
    
    # Validate llm_config if present
    if "llm_config" in persona:
        if not isinstance(persona["llm_config"], dict):
            errors.append("llm_config must be a dictionary")
        else:
            llm_errors = validate_llm_config(persona["llm_config"])
            errors.extend(llm_errors)
    
    # Validate metadata if present
    if "metadata" in persona:
        if not isinstance(persona["metadata"], dict):
            errors.append("metadata must be a dictionary")
    
    is_valid = len(errors) == 0
    return is_valid, errors

def validate_trait_block(category: str, traits: Dict) -> Tuple[bool, List[str]]:
    """Validate a single trait block
    
    Args:
        category: The trait category
        traits: The traits dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check category is valid
    if category not in VALID_CATEGORIES:
        errors.append(f"Invalid category: {category}")
    
    # Check traits is a dictionary
    if not isinstance(traits, dict):
        errors.append("Traits must be a dictionary")
    elif len(traits) == 0:
        errors.append("Trait block cannot be empty")
    else:
        # Validate trait values (basic type checking)
        for key, value in traits.items():
            if not isinstance(key, str):
                errors.append(f"Trait key must be a string, got {type(key).__name__}")
            elif not key:
                errors.append("Trait key cannot be empty")
            
            # Values can be strings, numbers, lists, or nested dicts
            if not isinstance(value, (str, int, float, bool, list, dict)):
                errors.append(f"Trait value for '{key}' has unsupported type: {type(value).__name__}")
    
    is_valid = len(errors) == 0
    return is_valid, errors

def validate_llm_config(llm_config: Dict) -> List[str]:
    """Validate LLM configuration
    
    Args:
        llm_config: The LLM configuration dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Check provider
    if "provider" in llm_config:
        valid_providers = ["openai", "anthropic", "google", "azure", "local"]
        if llm_config["provider"] not in valid_providers:
            errors.append(f"Invalid LLM provider: {llm_config['provider']}")
    
    # Check temperature
    if "temperature" in llm_config:
        temp = llm_config["temperature"]
        if not isinstance(temp, (int, float)):
            errors.append("Temperature must be a number")
        elif temp < 0 or temp > 2:
            errors.append("Temperature must be between 0 and 2")
    
    # Check max_tokens
    if "max_tokens" in llm_config:
        tokens = llm_config["max_tokens"]
        if not isinstance(tokens, int):
            errors.append("max_tokens must be an integer")
        elif tokens < 1 or tokens > 100000:
            errors.append("max_tokens must be between 1 and 100000")
    
    return errors

def check_persona_completeness(persona: Dict) -> Dict[str, Any]:
    """Check how complete a persona is
    
    Args:
        persona: The persona to check
        
    Returns:
        Dictionary with completeness metrics
    """
    metrics = {
        "total_categories": len(VALID_CATEGORIES),
        "filled_categories": 0,
        "missing_categories": [],
        "total_traits": 0,
        "completeness_score": 0.0
    }
    
    if "personality_traits" in persona:
        filled = set(persona["personality_traits"].keys())
        metrics["filled_categories"] = len(filled)
        metrics["missing_categories"] = [c for c in VALID_CATEGORIES if c not in filled]
        
        # Count total traits
        for traits in persona["personality_traits"].values():
            if isinstance(traits, dict):
                metrics["total_traits"] += len(traits)
    else:
        metrics["missing_categories"] = VALID_CATEGORIES.copy()
    
    # Calculate completeness score (0-100)
    category_score = (metrics["filled_categories"] / metrics["total_categories"]) * 50
    trait_score = min(metrics["total_traits"] / 20, 1.0) * 50  # Assume 20 traits is "complete"
    metrics["completeness_score"] = round(category_score + trait_score, 1)
    
    return metrics

def suggest_missing_traits(persona: Dict) -> List[str]:
    """Suggest trait categories that might be added to a persona
    
    Args:
        persona: The persona to analyze
        
    Returns:
        List of suggestions
    """
    suggestions = []
    
    if "personality_traits" not in persona:
        suggestions.append("Add personality_traits to define the persona's characteristics")
        return suggestions
    
    traits = persona["personality_traits"]
    
    # Check for commonly important categories
    if "professional" not in traits and persona.get("category") == "professional":
        suggestions.append("Add 'professional' traits to define occupation and skills")
    
    if "communication_style" not in traits:
        suggestions.append("Add 'communication_style' to define how the persona speaks")
    
    if "personality" not in traits:
        suggestions.append("Add 'personality' traits to define temperament and social style")
    
    if "values_beliefs" not in traits and persona.get("category") in ["political", "social"]:
        suggestions.append("Add 'values_beliefs' for political or social personas")
    
    if "demographics" not in traits:
        suggestions.append("Consider adding 'demographics' for age, location, etc.")
    
    return suggestions