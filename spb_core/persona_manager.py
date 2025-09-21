"""File I/O operations for persona management"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import glob

def save_persona(persona: Dict, directory: str = "personas") -> str:
    """Save persona to JSON file
    
    Args:
        persona: The persona dictionary to save
        directory: Directory to save personas in
        
    Returns:
        Path to the saved file
        
    Raises:
        ValueError: If persona_id is missing
        IOError: If file cannot be written
    """
    if "persona_id" not in persona:
        raise ValueError("Persona must have a persona_id")
    
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Update modified timestamp
    if "metadata" not in persona:
        persona["metadata"] = {}
    persona["metadata"]["modified_at"] = datetime.utcnow().isoformat() + "Z"
    
    # Save to file
    filename = f"{persona['persona_id']}.json"
    filepath = os.path.join(directory, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(persona, f, indent=2, ensure_ascii=False)
        return filepath
    except IOError as e:
        raise IOError(f"Failed to save persona to {filepath}: {e}")

def load_persona(persona_id: str, directory: str = "personas") -> Dict:
    """Load persona from JSON file
    
    Args:
        persona_id: The ID of the persona to load
        directory: Directory containing personas
        
    Returns:
        The loaded persona dictionary
        
    Raises:
        FileNotFoundError: If persona file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    filename = f"{persona_id}.json"
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Persona file not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            persona = json.load(f)
        return persona
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in persona file {filepath}", e.doc, e.pos)

def list_personas(directory: str = "personas") -> List[Dict]:
    """List all personas in directory
    
    Args:
        directory: Directory containing personas
        
    Returns:
        List of persona summaries (id, name, description, category)
    """
    personas = []
    
    if not os.path.exists(directory):
        return personas
    
    # Find all JSON files
    pattern = os.path.join(directory, "*.json")
    for filepath in glob.glob(pattern):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                persona = json.load(f)
                
            # Extract summary information
            summary = {
                "persona_id": persona.get("persona_id", "unknown"),
                "name": persona.get("name", "Unnamed"),
                "description": persona.get("description", ""),
                "category": persona.get("category", "general"),
                "trait_count": len(persona.get("personality_traits", {})),
                "modified_at": persona.get("metadata", {}).get("modified_at", "")
            }
            personas.append(summary)
        except (json.JSONDecodeError, KeyError):
            # Skip invalid files
            continue
    
    # Sort by modified date (newest first)
    personas.sort(key=lambda x: x.get("modified_at", ""), reverse=True)
    
    return personas

def delete_persona(persona_id: str, directory: str = "personas") -> bool:
    """Delete a persona file
    
    Args:
        persona_id: The ID of the persona to delete
        directory: Directory containing personas
        
    Returns:
        True if deleted, False if file didn't exist
    """
    filename = f"{persona_id}.json"
    filepath = os.path.join(directory, filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False
    
    return False

def search_personas(query: str, directory: str = "personas") -> List[Dict]:
    """Search for personas by name or description
    
    Args:
        query: Search query string
        directory: Directory containing personas
        
    Returns:
        List of matching persona summaries
    """
    query_lower = query.lower()
    all_personas = list_personas(directory)
    
    matches = []
    for persona_summary in all_personas:
        # Search in name and description
        if (query_lower in persona_summary.get("name", "").lower() or
            query_lower in persona_summary.get("description", "").lower()):
            matches.append(persona_summary)
    
    return matches

def export_persona(persona: Dict, format: str = "json") -> str:
    """Export persona to different formats
    
    Args:
        persona: The persona to export
        format: Export format (json, yaml, markdown)
        
    Returns:
        Exported string representation
    """
    if format == "json":
        return json.dumps(persona, indent=2, ensure_ascii=False)
    
    elif format == "markdown":
        lines = []
        lines.append(f"# {persona.get('name', 'Unnamed Persona')}")
        lines.append("")
        
        if persona.get("description"):
            lines.append(f"**Description:** {persona['description']}")
            lines.append("")
        
        if persona.get("category"):
            lines.append(f"**Category:** {persona['category']}")
            lines.append("")
        
        # Export personality traits
        if "personality_traits" in persona:
            lines.append("## Personality Traits")
            lines.append("")
            
            for category, traits in persona["personality_traits"].items():
                lines.append(f"### {category.replace('_', ' ').title()}")
                for key, value in traits.items():
                    if isinstance(value, list):
                        value_str = ", ".join(str(v) for v in value)
                    else:
                        value_str = str(value)
                    lines.append(f"- **{key}:** {value_str}")
                lines.append("")
        
        return "\n".join(lines)
    
    elif format == "yaml":
        # Simple YAML export (without dependency)
        lines = []
        lines.append(f"persona_id: {persona.get('persona_id', '')}")
        lines.append(f"name: {persona.get('name', '')}")
        lines.append(f"description: {persona.get('description', '')}")
        lines.append(f"category: {persona.get('category', 'general')}")
        lines.append("personality_traits:")
        
        for category, traits in persona.get("personality_traits", {}).items():
            lines.append(f"  {category}:")
            for key, value in traits.items():
                if isinstance(value, list):
                    lines.append(f"    {key}:")
                    for item in value:
                        lines.append(f"      - {item}")
                else:
                    lines.append(f"    {key}: {value}")
        
        return "\n".join(lines)
    
    else:
        raise ValueError(f"Unsupported export format: {format}")

def import_persona(content: str, format: str = "json") -> Dict:
    """Import persona from different formats
    
    Args:
        content: The content to import
        format: Import format (json)
        
    Returns:
        Imported persona dictionary
    """
    if format == "json":
        return json.loads(content)
    else:
        raise ValueError(f"Unsupported import format: {format}")