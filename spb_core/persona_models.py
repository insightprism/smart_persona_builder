"""Core data structures and operations for Smart Persona Builder"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid

# Valid trait categories - these are validated but contents are flexible
VALID_CATEGORIES = [
    "demographics",
    "professional", 
    "personality",
    "communication_style",
    "values_beliefs",
    "behavioral_traits",
    "capabilities",
    "background",
    "relationships",
    "preferences"
]

def create_empty_persona(persona_id: str, name: str, description: str = "", category: str = "general") -> Dict:
    """Create a new empty persona with basic structure
    
    Args:
        persona_id: Unique identifier for the persona
        name: Display name for the persona
        description: Brief description of the persona
        category: Category type (professional, social, educational, etc)
        
    Returns:
        Dictionary representing the persona structure
    """
    return {
        "persona_id": persona_id,
        "name": name,
        "description": description,
        "category": category,
        "personality_traits": {},
        "llm_config": {
            "provider": "openai",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "metadata": {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "modified_at": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0"
        }
    }

def add_trait_block(persona: Dict, category: str, traits: Dict) -> Dict:
    """Add a trait block to persona
    
    Args:
        persona: The persona dictionary to modify
        category: The trait category (must be in VALID_CATEGORIES)
        traits: Dictionary of traits (any key-value pairs)
        
    Returns:
        Updated persona dictionary
        
    Raises:
        ValueError: If category is not valid
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Must be one of {VALID_CATEGORIES}")
    
    # Create personality_traits if it doesn't exist
    if "personality_traits" not in persona:
        persona["personality_traits"] = {}
    
    # Add the trait block
    persona["personality_traits"][category] = traits
    
    # Update modified timestamp
    if "metadata" in persona:
        persona["metadata"]["modified_at"] = datetime.utcnow().isoformat() + "Z"
    
    return persona

def remove_trait_block(persona: Dict, category: str) -> Dict:
    """Remove a trait block from persona
    
    Args:
        persona: The persona dictionary to modify
        category: The trait category to remove
        
    Returns:
        Updated persona dictionary
    """
    if "personality_traits" in persona and category in persona["personality_traits"]:
        del persona["personality_traits"][category]
        
        # Update modified timestamp
        if "metadata" in persona:
            persona["metadata"]["modified_at"] = datetime.utcnow().isoformat() + "Z"
    
    return persona

def validate_categories(persona: Dict) -> Tuple[bool, List[str]]:
    """Validate that all trait categories in persona are valid
    
    Args:
        persona: The persona dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_invalid_categories)
    """
    invalid_categories = []
    
    if "personality_traits" in persona:
        for category in persona["personality_traits"].keys():
            if category not in VALID_CATEGORIES:
                invalid_categories.append(category)
    
    is_valid = len(invalid_categories) == 0
    return is_valid, invalid_categories

def merge_personas(base_persona: Dict, overlay_persona: Dict) -> Dict:
    """Merge two personas, with overlay taking precedence
    
    Args:
        base_persona: The base persona
        overlay_persona: The persona to overlay on top
        
    Returns:
        New merged persona
    """
    import copy
    merged = copy.deepcopy(base_persona)
    
    # Merge personality traits
    if "personality_traits" in overlay_persona:
        if "personality_traits" not in merged:
            merged["personality_traits"] = {}
        
        for category, traits in overlay_persona["personality_traits"].items():
            if category in merged["personality_traits"]:
                # Merge traits within category
                merged["personality_traits"][category].update(traits)
            else:
                merged["personality_traits"][category] = traits
    
    # Update metadata
    merged["metadata"]["modified_at"] = datetime.utcnow().isoformat() + "Z"
    
    return merged

def clone_persona(persona: Dict, new_id: str, new_name: str) -> Dict:
    """Create a copy of a persona with a new ID and name
    
    Args:
        persona: The persona to clone
        new_id: New unique identifier
        new_name: New display name
        
    Returns:
        Cloned persona with new identity
    """
    import copy
    cloned = copy.deepcopy(persona)
    cloned["persona_id"] = new_id
    cloned["name"] = new_name
    cloned["metadata"]["created_at"] = datetime.utcnow().isoformat() + "Z"
    cloned["metadata"]["modified_at"] = datetime.utcnow().isoformat() + "Z"
    
    return cloned