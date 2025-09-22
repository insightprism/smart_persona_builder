"""REST API endpoints for Smart Persona Builder"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, PlainTextResponse
from typing import Dict, List, Any, Optional
import os
import json
import uuid
from datetime import datetime

from spb_core import (
    create_empty_persona,
    add_trait_block,
    remove_trait_block,
    validate_categories,
    generate_system_prompt,
    filter_traits_by_context,
    save_persona,
    load_persona,
    list_personas,
    delete_persona,
    validate_persona_structure,
    validate_trait_block
)
from spb_core.persona_manager import search_personas, export_persona, import_persona
from spb_core.persona_validator import check_persona_completeness, suggest_missing_traits
from spb_core.persona_models import VALID_CATEGORIES, CATEGORY_DESCRIPTIONS, merge_personas, clone_persona

router = APIRouter(prefix="/api/personas", tags=["personas"])

# Configuration
PERSONAS_DIR = os.environ.get("SPB_PERSONAS_DIR", "personas")

@router.get("/")
async def get_personas() -> List[Dict]:
    """List all personas"""
    try:
        return list_personas(PERSONAS_DIR)
    except Exception as e:
        raise HTTPException(500, f"Error listing personas: {str(e)}")

@router.get("/categories")
async def get_valid_categories() -> Dict[str, Any]:
    """Get list of valid trait categories"""
    return {
        "categories": VALID_CATEGORIES,
        "descriptions": CATEGORY_DESCRIPTIONS
    }

@router.get("/{persona_id}")
async def get_persona(persona_id: str) -> Dict:
    """Get a specific persona"""
    try:
        return load_persona(persona_id, PERSONAS_DIR)
    except FileNotFoundError:
        raise HTTPException(404, f"Persona {persona_id} not found")
    except Exception as e:
        raise HTTPException(500, f"Error loading persona: {str(e)}")

@router.post("/")
async def create_persona(persona_data: Dict[str, Any]) -> Dict[str, str]:
    """Create a new persona"""
    try:
        # Generate ID if not provided
        if "persona_id" not in persona_data:
            persona_data["persona_id"] = f"persona_{uuid.uuid4().hex[:8]}"
        
        # Validate structure
        is_valid, errors = validate_persona_structure(persona_data)
        if not is_valid:
            raise HTTPException(400, f"Invalid persona structure: {', '.join(errors)}")
        
        # Add metadata if not present
        if "metadata" not in persona_data:
            persona_data["metadata"] = {}
        persona_data["metadata"]["created_at"] = datetime.utcnow().isoformat() + "Z"
        persona_data["metadata"]["modified_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Save persona
        filepath = save_persona(persona_data, PERSONAS_DIR)
        
        return {
            "status": "created",
            "persona_id": persona_data["persona_id"],
            "filepath": filepath
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error creating persona: {str(e)}")

@router.put("/{persona_id}")
async def update_persona(persona_id: str, persona_data: Dict[str, Any]) -> Dict[str, str]:
    """Update an existing persona"""
    try:
        # Ensure ID matches
        persona_data["persona_id"] = persona_id
        
        # Validate structure
        is_valid, errors = validate_persona_structure(persona_data)
        if not is_valid:
            raise HTTPException(400, f"Invalid persona structure: {', '.join(errors)}")
        
        # Update metadata
        if "metadata" not in persona_data:
            persona_data["metadata"] = {}
        persona_data["metadata"]["modified_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Save persona
        filepath = save_persona(persona_data, PERSONAS_DIR)
        
        return {
            "status": "updated",
            "persona_id": persona_id,
            "filepath": filepath
        }
    except Exception as e:
        raise HTTPException(500, f"Error updating persona: {str(e)}")

@router.delete("/{persona_id}")
async def remove_persona(persona_id: str) -> Dict[str, str]:
    """Delete a persona"""
    try:
        deleted = delete_persona(persona_id, PERSONAS_DIR)
        if deleted:
            return {"status": "deleted", "persona_id": persona_id}
        else:
            raise HTTPException(404, f"Persona {persona_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error deleting persona: {str(e)}")

@router.post("/{persona_id}/traits")
async def add_traits(persona_id: str, trait_data: Dict[str, Any]) -> Dict:
    """Add a trait block to a persona"""
    try:
        # Load existing persona
        persona = load_persona(persona_id, PERSONAS_DIR)
        
        # Extract category and traits
        category = trait_data.get("category")
        traits = trait_data.get("traits", {})
        
        if not category:
            raise HTTPException(400, "Category is required")
        
        # Validate trait block
        is_valid, errors = validate_trait_block(category, traits)
        if not is_valid:
            raise HTTPException(400, f"Invalid trait block: {', '.join(errors)}")
        
        # Add trait block
        updated_persona = add_trait_block(persona, category, traits)
        
        # Save updated persona
        save_persona(updated_persona, PERSONAS_DIR)
        
        return updated_persona
    except FileNotFoundError:
        raise HTTPException(404, f"Persona {persona_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error adding traits: {str(e)}")

@router.delete("/{persona_id}/traits/{category}")
async def remove_traits(persona_id: str, category: str) -> Dict:
    """Remove a trait block from a persona"""
    try:
        # Load existing persona
        persona = load_persona(persona_id, PERSONAS_DIR)
        
        # Remove trait block
        updated_persona = remove_trait_block(persona, category)
        
        # Save updated persona
        save_persona(updated_persona, PERSONAS_DIR)
        
        return updated_persona
    except FileNotFoundError:
        raise HTTPException(404, f"Persona {persona_id} not found")
    except Exception as e:
        raise HTTPException(500, f"Error removing traits: {str(e)}")

@router.post("/{persona_id}/generate")
async def generate_prompt(persona_id: str, context_data: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Generate a system prompt for a persona"""
    try:
        # Load persona
        persona = load_persona(persona_id, PERSONAS_DIR)
        
        # Extract context
        context = context_data.get("context") if context_data else None
        
        # Generate prompt
        system_prompt = generate_system_prompt(persona, context)
        
        return {
            "persona_id": persona_id,
            "context": context or "general",
            "system_prompt": system_prompt
        }
    except FileNotFoundError:
        raise HTTPException(404, f"Persona {persona_id} not found")
    except Exception as e:
        raise HTTPException(500, f"Error generating prompt: {str(e)}")

@router.post("/validate")
async def validate_persona(persona_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a persona structure"""
    try:
        is_valid, errors = validate_persona_structure(persona_data)
        
        # Check categories
        cat_valid, cat_errors = validate_categories(persona_data)
        if not cat_valid:
            errors.extend([f"Invalid category: {cat}" for cat in cat_errors])
        
        # Get completeness metrics
        completeness = check_persona_completeness(persona_data)
        suggestions = suggest_missing_traits(persona_data)
        
        return {
            "valid": is_valid and cat_valid,
            "errors": errors,
            "completeness": completeness,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(500, f"Error validating persona: {str(e)}")

@router.get("/{persona_id}/completeness")
async def get_completeness(persona_id: str) -> Dict[str, Any]:
    """Check how complete a persona is"""
    try:
        persona = load_persona(persona_id, PERSONAS_DIR)
        completeness = check_persona_completeness(persona)
        suggestions = suggest_missing_traits(persona)
        
        return {
            "persona_id": persona_id,
            "completeness": completeness,
            "suggestions": suggestions
        }
    except FileNotFoundError:
        raise HTTPException(404, f"Persona {persona_id} not found")
    except Exception as e:
        raise HTTPException(500, f"Error checking completeness: {str(e)}")

@router.post("/search")
async def search(query_data: Dict[str, str]) -> List[Dict]:
    """Search for personas"""
    try:
        query = query_data.get("query", "")
        if not query:
            raise HTTPException(400, "Search query is required")
        
        results = search_personas(query, PERSONAS_DIR)
        return results
    except Exception as e:
        raise HTTPException(500, f"Error searching personas: {str(e)}")

@router.post("/{persona_id}/export")
async def export(persona_id: str, format_data: Optional[Dict[str, str]] = None) -> Any:
    """Export a persona in different formats"""
    try:
        persona = load_persona(persona_id, PERSONAS_DIR)
        format = format_data.get("format", "json") if format_data else "json"
        
        if format == "json":
            return persona
        elif format == "markdown":
            content = export_persona(persona, "markdown")
            return PlainTextResponse(content, media_type="text/markdown")
        elif format == "yaml":
            content = export_persona(persona, "yaml")
            return PlainTextResponse(content, media_type="text/yaml")
        else:
            raise HTTPException(400, f"Unsupported export format: {format}")
    except FileNotFoundError:
        raise HTTPException(404, f"Persona {persona_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error exporting persona: {str(e)}")

@router.post("/import")
async def import_persona_file(file: UploadFile = File(...)) -> Dict[str, str]:
    """Import a persona from a file"""
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Determine format from filename
        if file.filename.endswith('.json'):
            persona = import_persona(content_str, "json")
        else:
            raise HTTPException(400, "Only JSON format is currently supported")
        
        # Generate ID if not present
        if "persona_id" not in persona:
            persona["persona_id"] = f"imported_{uuid.uuid4().hex[:8]}"
        
        # Validate
        is_valid, errors = validate_persona_structure(persona)
        if not is_valid:
            raise HTTPException(400, f"Invalid persona structure: {', '.join(errors)}")
        
        # Save
        filepath = save_persona(persona, PERSONAS_DIR)
        
        return {
            "status": "imported",
            "persona_id": persona["persona_id"],
            "filepath": filepath
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error importing persona: {str(e)}")

@router.post("/merge")
async def merge_two_personas(merge_data: Dict[str, Any]) -> Dict:
    """Merge two personas"""
    try:
        base_id = merge_data.get("base_persona_id")
        overlay_id = merge_data.get("overlay_persona_id")
        new_id = merge_data.get("new_persona_id")
        new_name = merge_data.get("new_name")
        
        if not all([base_id, overlay_id, new_id, new_name]):
            raise HTTPException(400, "base_persona_id, overlay_persona_id, new_persona_id, and new_name are required")
        
        # Load personas
        base = load_persona(base_id, PERSONAS_DIR)
        overlay = load_persona(overlay_id, PERSONAS_DIR)
        
        # Merge
        merged = merge_personas(base, overlay)
        merged["persona_id"] = new_id
        merged["name"] = new_name
        
        # Save
        filepath = save_persona(merged, PERSONAS_DIR)
        
        return merged
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error merging personas: {str(e)}")

@router.post("/{persona_id}/clone")
async def clone_persona_endpoint(persona_id: str, clone_data: Dict[str, str]) -> Dict:
    """Clone a persona with a new ID and name"""
    try:
        new_id = clone_data.get("new_persona_id")
        new_name = clone_data.get("new_name")
        
        if not all([new_id, new_name]):
            raise HTTPException(400, "new_persona_id and new_name are required")
        
        # Load original
        original = load_persona(persona_id, PERSONAS_DIR)
        
        # Clone
        cloned = clone_persona(original, new_id, new_name)
        
        # Save
        filepath = save_persona(cloned, PERSONAS_DIR)
        
        return cloned
    except FileNotFoundError:
        raise HTTPException(404, f"Persona {persona_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error cloning persona: {str(e)}")