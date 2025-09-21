"""System prompt generation from persona traits"""

from typing import Dict, Optional, List, Any

# Context to trait mappings - which traits are relevant for different contexts
CONTEXT_TRAITS = {
    "professional": ["professional", "communication_style", "capabilities"],
    "medical": ["demographics", "background", "preferences"],
    "emergency": ["behavioral_traits", "capabilities", "communication_style"],
    "social": ["personality", "preferences", "relationships"],
    "voting": ["demographics", "values_beliefs", "background"],
    "parenting": ["values_beliefs", "behavioral_traits", "background"],
    "teaching": ["communication_style", "behavioral_traits", "capabilities"],
    "customer_service": ["communication_style", "behavioral_traits", "professional"]
}

def generate_system_prompt(persona: Dict, context: Optional[str] = None) -> str:
    """Generate a system prompt from persona traits
    
    Args:
        persona: The persona dictionary
        context: Optional context to filter relevant traits
        
    Returns:
        Generated system prompt as string
    """
    if not persona:
        return "You are a helpful assistant."
    
    # Start with persona name and description
    prompt_parts = []
    
    if "name" in persona:
        prompt_parts.append(f"You are {persona['name']}")
    
    if "description" in persona and persona["description"]:
        prompt_parts.append(f"\n{persona['description']}")
    
    # Get traits to include based on context
    traits_to_include = persona.get("personality_traits", {})
    
    if context:
        traits_to_include = filter_traits_by_context(traits_to_include, context)
    
    # Format each trait block
    if traits_to_include:
        prompt_parts.append("\n")
        for category, traits in traits_to_include.items():
            formatted_block = format_trait_block(category, traits)
            if formatted_block:
                prompt_parts.append(formatted_block)
    
    # Add consistency reminder
    if prompt_parts:
        prompt_parts.append("\nMaintain these characteristics consistently in all your responses.")
    
    return "\n".join(prompt_parts) if prompt_parts else "You are a helpful assistant."

def filter_traits_by_context(traits: Dict, context: str) -> Dict:
    """Filter traits based on context relevance
    
    Args:
        traits: Dictionary of all personality traits
        context: The context to filter for
        
    Returns:
        Filtered dictionary containing only relevant traits
    """
    if context not in CONTEXT_TRAITS:
        # If context unknown, return all traits
        return traits
    
    relevant_categories = CONTEXT_TRAITS[context]
    filtered_traits = {}
    
    for category in relevant_categories:
        if category in traits:
            filtered_traits[category] = traits[category]
    
    return filtered_traits

def format_trait_block(category: str, traits: Dict) -> str:
    """Format a single trait block for the prompt
    
    Args:
        category: The trait category name
        traits: Dictionary of traits in this category
        
    Returns:
        Formatted string representation of the trait block
    """
    if not traits:
        return ""
    
    # Format category name
    category_title = category.replace("_", " ").title()
    lines = [f"\n{category_title}:"]
    
    # Format each trait
    for key, value in traits.items():
        formatted_key = key.replace("_", " ").title()
        
        # Handle different value types
        if isinstance(value, list):
            value_str = ", ".join(str(v) for v in value)
            lines.append(f"- {formatted_key}: {value_str}")
        elif isinstance(value, dict):
            lines.append(f"- {formatted_key}:")
            for sub_key, sub_value in value.items():
                formatted_sub_key = sub_key.replace("_", " ").title()
                lines.append(f"  - {formatted_sub_key}: {sub_value}")
        else:
            lines.append(f"- {formatted_key}: {value}")
    
    return "\n".join(lines)

def generate_conversation_starter(persona: Dict, context: Optional[str] = None) -> str:
    """Generate an appropriate conversation starter based on persona
    
    Args:
        persona: The persona dictionary
        context: Optional context for the conversation
        
    Returns:
        A conversation starter string
    """
    starters = []
    
    if "name" in persona:
        starters.append(f"Hello! I'm {persona['name']}.")
    
    # Add context-specific starters
    if context == "professional" and "professional" in persona.get("personality_traits", {}):
        prof_traits = persona["personality_traits"]["professional"]
        if "role" in prof_traits:
            starters.append(f"As a {prof_traits['role']}, I'm here to help.")
    elif context == "teaching" and "communication_style" in persona.get("personality_traits", {}):
        starters.append("I'm here to help you learn. What would you like to know?")
    elif context == "customer_service":
        starters.append("How may I assist you today?")
    else:
        starters.append("How can I help you today?")
    
    return " ".join(starters)

def extract_key_traits(persona: Dict, max_traits: int = 5) -> List[str]:
    """Extract the most important traits from a persona
    
    Args:
        persona: The persona dictionary
        max_traits: Maximum number of traits to extract
        
    Returns:
        List of key trait descriptions
    """
    key_traits = []
    
    # Priority order for trait extraction
    priority_categories = ["professional", "personality", "communication_style", "values_beliefs"]
    
    for category in priority_categories:
        if category in persona.get("personality_traits", {}):
            traits = persona["personality_traits"][category]
            
            # Extract first few traits from each category
            for key, value in list(traits.items())[:2]:
                if isinstance(value, (str, int, float)):
                    trait_desc = f"{key.replace('_', ' ')}: {value}"
                    key_traits.append(trait_desc)
                    
                    if len(key_traits) >= max_traits:
                        return key_traits
    
    return key_traits