"""Tests for persona file management"""

import pytest
import json
import os
import tempfile
import shutil
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spb_core.persona_models import create_empty_persona, add_trait_block
from spb_core.persona_manager import (
    save_persona,
    load_persona,
    list_personas,
    delete_persona,
    search_personas,
    export_persona,
    import_persona
)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)

def test_save_and_load_persona(temp_dir):
    """Test saving and loading personas"""
    persona = create_empty_persona("test_save", "Test Person")
    persona = add_trait_block(persona, "demographics", {"age": 30})
    
    # Save persona
    filepath = save_persona(persona, temp_dir)
    assert os.path.exists(filepath)
    assert filepath.endswith("test_save.json")
    
    # Load persona
    loaded = load_persona("test_save", temp_dir)
    assert loaded["persona_id"] == "test_save"
    assert loaded["name"] == "Test Person"
    assert loaded["personality_traits"]["demographics"]["age"] == 30

def test_save_persona_without_id(temp_dir):
    """Test that saving without persona_id raises error"""
    persona = {"name": "No ID"}
    
    with pytest.raises(ValueError, match="must have a persona_id"):
        save_persona(persona, temp_dir)

def test_load_nonexistent_persona(temp_dir):
    """Test loading a persona that doesn't exist"""
    with pytest.raises(FileNotFoundError):
        load_persona("nonexistent", temp_dir)

def test_list_personas(temp_dir):
    """Test listing all personas"""
    # Create multiple personas
    persona1 = create_empty_persona("persona1", "Person One")
    persona2 = create_empty_persona("persona2", "Person Two", "Second persona")
    persona2["category"] = "professional"
    persona2 = add_trait_block(persona2, "professional", {"role": "Engineer"})
    
    save_persona(persona1, temp_dir)
    save_persona(persona2, temp_dir)
    
    # List personas
    personas = list_personas(temp_dir)
    
    assert len(personas) == 2
    
    # Check persona summaries
    p1 = next(p for p in personas if p["persona_id"] == "persona1")
    assert p1["name"] == "Person One"
    assert p1["trait_count"] == 0
    
    p2 = next(p for p in personas if p["persona_id"] == "persona2")
    assert p2["name"] == "Person Two"
    assert p2["description"] == "Second persona"
    assert p2["category"] == "professional"
    assert p2["trait_count"] == 1

def test_list_personas_empty_dir(temp_dir):
    """Test listing personas from empty directory"""
    personas = list_personas(temp_dir)
    assert personas == []
    
    # Non-existent directory
    personas = list_personas(os.path.join(temp_dir, "nonexistent"))
    assert personas == []

def test_delete_persona(temp_dir):
    """Test deleting a persona"""
    persona = create_empty_persona("to_delete", "Delete Me")
    save_persona(persona, temp_dir)
    
    # Verify it exists
    assert os.path.exists(os.path.join(temp_dir, "to_delete.json"))
    
    # Delete it
    deleted = delete_persona("to_delete", temp_dir)
    assert deleted == True
    assert not os.path.exists(os.path.join(temp_dir, "to_delete.json"))
    
    # Delete non-existent
    deleted = delete_persona("nonexistent", temp_dir)
    assert deleted == False

def test_search_personas(temp_dir):
    """Test searching for personas"""
    # Create personas with searchable content
    p1 = create_empty_persona("john_doe", "John Doe", "A software engineer")
    p2 = create_empty_persona("jane_smith", "Jane Smith", "A data scientist")
    p3 = create_empty_persona("bob_jones", "Bob Jones", "An engineer")
    
    save_persona(p1, temp_dir)
    save_persona(p2, temp_dir)
    save_persona(p3, temp_dir)
    
    # Search by name
    results = search_personas("john", temp_dir)
    assert len(results) == 1
    assert results[0]["persona_id"] == "john_doe"
    
    # Search by description
    results = search_personas("engineer", temp_dir)
    assert len(results) == 2
    ids = [r["persona_id"] for r in results]
    assert "john_doe" in ids
    assert "bob_jones" in ids
    
    # Case insensitive search
    results = search_personas("JANE", temp_dir)
    assert len(results) == 1
    assert results[0]["persona_id"] == "jane_smith"
    
    # No matches
    results = search_personas("xyz123", temp_dir)
    assert results == []

def test_export_persona_json():
    """Test exporting persona to JSON"""
    persona = create_empty_persona("export_test", "Export Test")
    persona = add_trait_block(persona, "demographics", {"age": 25})
    
    exported = export_persona(persona, "json")
    
    # Should be valid JSON
    parsed = json.loads(exported)
    assert parsed["persona_id"] == "export_test"
    assert parsed["personality_traits"]["demographics"]["age"] == 25

def test_export_persona_markdown():
    """Test exporting persona to Markdown"""
    persona = create_empty_persona("md_test", "Markdown Test", "Test description")
    persona["category"] = "professional"
    persona = add_trait_block(persona, "professional", {
        "role": "Developer",
        "skills": ["Python", "JavaScript"]
    })
    
    exported = export_persona(persona, "markdown")
    
    assert "# Markdown Test" in exported
    assert "**Description:** Test description" in exported
    assert "**Category:** professional" in exported
    assert "### Professional" in exported
    assert "**role:** Developer" in exported
    assert "**skills:** Python, JavaScript" in exported

def test_export_persona_yaml():
    """Test exporting persona to YAML"""
    persona = create_empty_persona("yaml_test", "YAML Test")
    persona = add_trait_block(persona, "demographics", {
        "age": 30,
        "hobbies": ["reading", "hiking"]
    })
    
    exported = export_persona(persona, "yaml")
    
    assert "persona_id: yaml_test" in exported
    assert "name: YAML Test" in exported
    assert "demographics:" in exported
    assert "age: 30" in exported
    assert "hobbies:" in exported
    assert "- reading" in exported
    assert "- hiking" in exported

def test_export_invalid_format():
    """Test exporting with invalid format"""
    persona = create_empty_persona("test", "Test")
    
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_persona(persona, "invalid_format")

def test_import_persona_json():
    """Test importing persona from JSON"""
    original = create_empty_persona("import_test", "Import Test")
    original = add_trait_block(original, "professional", {"role": "Manager"})
    
    json_str = json.dumps(original)
    imported = import_persona(json_str, "json")
    
    assert imported["persona_id"] == "import_test"
    assert imported["name"] == "Import Test"
    assert imported["personality_traits"]["professional"]["role"] == "Manager"

def test_import_invalid_format():
    """Test importing with invalid format"""
    with pytest.raises(ValueError, match="Unsupported import format"):
        import_persona("content", "invalid_format")

def test_file_io_with_special_characters(temp_dir):
    """Test handling personas with special characters"""
    persona = create_empty_persona("special", "Test Person")
    persona = add_trait_block(persona, "demographics", {
        "location": "São Paulo",
        "interests": "café & crêpes",
        "emoji": "😊"
    })
    
    # Save and load
    save_persona(persona, temp_dir)
    loaded = load_persona("special", temp_dir)
    
    # Check special characters preserved
    assert loaded["personality_traits"]["demographics"]["location"] == "São Paulo"
    assert loaded["personality_traits"]["demographics"]["interests"] == "café & crêpes"
    assert loaded["personality_traits"]["demographics"]["emoji"] == "😊"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])