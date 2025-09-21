# Smart Persona Builder

A flexible, block-based system for creating and managing AI personas that adapt to different contexts.

## Quick Start

Smart Persona Builder (SPB) allows you to create rich, multi-faceted personas using personality trait blocks that can be mixed, matched, and activated based on context.

### Core Concept

Instead of static system prompts, personas are composed of trait blocks:
- **Demographics**: Age, location, background
- **Professional**: Occupation, skills, experience
- **Personality**: Temperament, social style
- **Communication Style**: Tone, formality, approach
- **Values & Beliefs**: Priorities, philosophy
- **Behavioral Traits**: Problem-solving, habits
- And more...

### Simple Example

```python
# Create a persona
teacher_persona = {
    "persona_id": "teacher_001",
    "name": "Ms. Johnson",
    "personality_traits": {
        "professional": {
            "role": "High School Teacher",
            "experience": "15 years",
            "subjects": ["Math", "Physics"]
        },
        "communication_style": {
            "tone": "patient and encouraging",
            "explanations": "step-by-step with examples"
        }
    }
}

# Generate context-aware prompts
teaching_prompt = generate_prompt(teacher_persona, context="teaching")
parent_meeting = generate_prompt(teacher_persona, context="parent_conference")
```

## Key Features

✅ **Flexible Structure** - Use any key-value pairs that make sense for your use case
✅ **Context Awareness** - Different traits activate for different situations
✅ **Human-Readable JSON** - Easy to edit and understand
✅ **No Schema Enforcement** - Beyond categories, structure is completely flexible
✅ **Reusable Blocks** - Share trait blocks across multiple personas

## Documentation

See [docs/SPECIFICATION.md](docs/SPECIFICATION.md) for complete technical specification including:
- Architecture overview
- Detailed use cases
- Implementation guide
- API documentation
- Code examples

## Project Structure

```
smart_persona_builder_slim/
├── docs/                 # Documentation
├── spb_core/            # Core functionality
├── spb_api/             # REST API
├── spb_templates/       # Pre-built personas
├── personas/            # JSON storage
└── tests/               # Test suite
```

## Design Philosophy

- **Simplicity First**: Clean, maintainable code without unnecessary complexity
- **Flexibility**: Users can structure personas however feels natural
- **No Magic**: Transparent, predictable behavior
- **Configuration-Driven**: No hardcoded values

## Use Cases

- 🤖 **Customer Service** - Consistent service personas across channels
- 📚 **Education** - Teaching assistants with appropriate pedagogy
- 🔧 **Professional Experts** - Domain experts for consultation
- 🗳️ **Social Simulation** - Realistic persona behaviors for research
- 💼 **Training** - Role-play scenarios with consistent characters

## Status

This is the specification and design phase. Implementation follows the patterns established in Smart Conversation Builder for consistency.

---

*Part of the Smart Builder ecosystem for AI conversation and persona management.*