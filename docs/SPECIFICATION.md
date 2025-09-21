# Smart Persona Builder - Technical Specification

## Executive Summary

Smart Persona Builder (SPB) is a flexible, block-based system for creating and managing AI personas. Similar to how Smart Conversation Builder uses blocks to construct conversations, SPB uses "personality trait blocks" to compose rich, contextual personas that can adapt their behavior based on different situations.

## Purpose and Motivation

### The Problem
Current AI systems often use static, monolithic system prompts that:
- Treat personas as fixed entities rather than multi-faceted personalities
- Require complete rewriting for minor persona adjustments
- Cannot easily adapt to different contexts (professional vs. social vs. emergency)
- Lack reusability across different applications
- Make it difficult to maintain consistency across multiple conversations

### The Solution
A modular, trait-based persona system where:
- Personas are composed of reusable personality trait blocks
- Each block represents a specific aspect of identity (demographics, professional, values, etc.)
- Blocks can be mixed, matched, and activated based on context
- System prompts are generated dynamically from active trait blocks
- Personas are stored as simple JSON for easy editing and sharing

## Core Benefits

1. **Flexibility**: Users can define personas using any terminology that feels natural
2. **Reusability**: Trait blocks can be shared across multiple personas
3. **Context Awareness**: Different traits activate for different situations
4. **Maintainability**: Changes to one trait don't affect others
5. **Simplicity**: JSON structure is human-readable and editable
6. **Scalability**: Easy to add new trait categories or customize existing ones

## Architecture Overview

### Design Principles
1. **No Schema Enforcement**: Beyond category validation, users can use any keys/values
2. **Function-First**: Use simple functions, not complex class hierarchies
3. **Configuration-Driven**: No hardcoded values in the implementation
4. **Single Responsibility**: Each function does one thing well
5. **No Fallback Logic**: Keep code clean and predictable

### Core Components

#### 1. Persona Structure
```json
{
  "persona_id": "unique_identifier",
  "name": "Display Name",
  "description": "Brief description",
  "category": "professional|social|educational|etc",
  "personality_traits": {
    "demographics": { /* any key-value pairs */ },
    "professional": { /* any key-value pairs */ },
    "personality": { /* any key-value pairs */ },
    "communication_style": { /* any key-value pairs */ },
    "values_beliefs": { /* any key-value pairs */ },
    "behavioral_traits": { /* any key-value pairs */ },
    "capabilities": { /* any key-value pairs */ },
    "background": { /* any key-value pairs */ },
    "relationships": { /* any key-value pairs */ },
    "preferences": { /* any key-value pairs */ }
  },
  "llm_config": {
    "provider": "openai",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

#### 2. Trait Categories (Validated)
- `demographics`: Age, location, gender, family status
- `professional`: Occupation, experience, skills, education
- `personality`: Temperament, social style, energy level
- `communication_style`: Tone, formality, verbosity, humor
- `values_beliefs`: Politics, religion, priorities, philosophy
- `behavioral_traits`: Decision-making, problem-solving, habits
- `capabilities`: Skills, knowledge, expertise areas
- `background`: History, experiences, cultural context
- `relationships`: Family, friends, social connections
- `preferences`: Likes, dislikes, hobbies, interests

#### 3. System Prompt Generation
- Loop through active trait blocks
- Format each category and its traits
- Support context-based filtering
- Generate natural language output

## Use Cases

### Use Case 1: Professional Expert Consultation
```python
# Create a plumber persona
plumber_joe = {
    "persona_id": "plumber_joe_001",
    "name": "Joe Martinez",
    "personality_traits": {
        "professional": {
            "occupation": "Master Plumber",
            "years_experience": 25,
            "specialties": ["residential", "commercial"],
            "license": "AZ-MP-12345"
        },
        "communication_style": {
            "approach": "friendly and direct",
            "explains": "in simple terms",
            "always_mentions": "safety first"
        },
        "behavioral_traits": {
            "problem_solving": "systematic diagnosis",
            "cost_estimates": "always provides",
            "teaching": "explains while fixing"
        }
    }
}

# Context: Emergency call
prompt = generate_prompt(plumber_joe, context="emergency")
# Emphasizes: Quick assessment, safety, immediate actions

# Context: Teaching DIY
prompt = generate_prompt(plumber_joe, context="teaching")
# Emphasizes: Step-by-step, tool explanations, safety warnings
```

### Use Case 2: Multi-Context Social Simulation
```python
# Sarah - changes based on context
sarah = {
    "persona_id": "sarah_mitchell",
    "name": "Sarah Mitchell",
    "personality_traits": {
        "demographics": {
            "age": 35,
            "location": "Chicago",
            "children": "2 boys, ages 8 and 11"
        },
        "professional": {
            "role": "Marketing Manager",
            "company": "Tech startup",
            "work_style": "data-driven"
        },
        "personality": {
            "social": "extrovert at work, needs quiet time at home",
            "stress_response": "exercise and meditation"
        },
        "values_beliefs": {
            "political": "moderate, focuses on education",
            "priorities": ["family", "career growth", "health"]
        }
    }
}

# Different contexts activate different traits
work_prompt = generate_prompt(sarah, "professional")    # Professional traits
voting_prompt = generate_prompt(sarah, "voting")        # Values + demographics
parent_prompt = generate_prompt(sarah, "parenting")     # Family + values
```

### Use Case 3: Customer Service Training
```python
# Template for consistent service personas
cs_template = {
    "personality_traits": {
        "communication_style": {
            "tone": "warm and professional",
            "active_listening": "reflects understanding",
            "empathy": "acknowledges frustration"
        },
        "behavioral_traits": {
            "problem_resolution": "solution-focused",
            "de_escalation": "remain calm",
            "follow_up": "always confirm resolution"
        }
    }
}

# Create specific representatives
tech_support = merge(cs_template, {"professional": {"specialty": "software"}})
billing_support = merge(cs_template, {"professional": {"specialty": "accounts"}})
```

### Use Case 4: Educational Personas
```python
teacher_betty = {
    "persona_id": "teacher_betty",
    "name": "Betty Rodriguez",
    "personality_traits": {
        "professional": {
            "role": "Retired Teacher",
            "experience": "35 years",
            "subjects": ["Math", "Science"],
            "grade_levels": "High School"
        },
        "personality": {
            "patience": "infinite with students",
            "enthusiasm": "contagious love of learning"
        },
        "communication_style": {
            "explanations": "breaks down complex topics",
            "encouragement": "celebrates small victories",
            "questions": "Socratic method"
        },
        "behavioral_traits": {
            "teaching_philosophy": "every child can learn",
            "adapts_to": "different learning styles"
        }
    }
}
```

### Use Case 5: Political/Voter Simulation
```python
midwest_voter = {
    "persona_id": "midwest_voter_001",
    "name": "Robert Johnson",
    "personality_traits": {
        "demographics": {
            "age": 52,
            "location": "suburban Detroit",
            "occupation": "auto worker",
            "union_member": True
        },
        "values_beliefs": {
            "economic_views": "supports manufacturing jobs",
            "social_views": "moderate",
            "key_issues": ["jobs", "healthcare", "retirement security"],
            "voting_history": "swing voter"
        },
        "background": {
            "family_job_loss": "2008 recession",
            "union_involvement": "20 years",
            "community_ties": "strong"
        }
    }
}

# Generate for different scenarios
election_prompt = generate_prompt(midwest_voter, "voting")
policy_prompt = generate_prompt(midwest_voter, "policy_discussion")
```

## Implementation Guide

### File Structure
```
smart_persona_builder_slim/
├── docs/
│   └── SPECIFICATION.md          # This document
├── spb_core/
│   ├── __init__.py
│   ├── persona_models.py        # Core data structures
│   ├── prompt_generator.py      # System prompt generation
│   ├── persona_manager.py       # File I/O operations
│   └── persona_validator.py     # Simple validation
├── spb_api/
│   ├── __init__.py
│   └── persona_endpoints.py     # REST API
├── spb_templates/
│   ├── __init__.py
│   └── common_personas.py       # Pre-built templates
├── personas/                     # JSON storage
│   └── *.json
└── tests/
    └── test_*.py
```

### Key Functions

#### persona_models.py
```python
def create_empty_persona(persona_id: str, name: str) -> Dict
def add_trait_block(persona: Dict, category: str, traits: Dict) -> Dict
def remove_trait_block(persona: Dict, category: str) -> Dict
def validate_categories(persona: Dict) -> tuple[bool, List[str]]
```

#### prompt_generator.py
```python
def generate_system_prompt(persona: Dict, context: str = None) -> str
def filter_traits_by_context(traits: Dict, context: str) -> Dict
def format_trait_block(category: str, traits: Dict) -> str
```

#### persona_manager.py
```python
def save_persona(persona: Dict, directory: str) -> str
def load_persona(persona_id: str, directory: str) -> Dict
def list_personas(directory: str) -> List[Dict]
def delete_persona(persona_id: str, directory: str) -> bool
```

### API Endpoints
```
GET    /personas                 # List all personas
GET    /personas/{id}            # Get specific persona
POST   /personas                 # Create new persona
PUT    /personas/{id}            # Update persona
DELETE /personas/{id}            # Delete persona
POST   /personas/{id}/generate   # Generate system prompt
GET    /personas/categories      # Get valid categories
POST   /personas/validate        # Validate persona structure
```

## Context-Based Trait Filtering

Different contexts activate different personality traits:

### Context Mappings
```python
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
```

## Implementation Notes

### DO:
- Keep trait blocks completely flexible (any key-value pairs)
- Validate only category names, not content
- Use simple loops for prompt generation
- Store as human-readable JSON
- Allow custom categories via configuration
- Support context-based trait filtering
- Make all configurations passable as parameters

### DON'T:
- Don't enforce schemas on trait content
- Don't add fallback values or defaults
- Don't create complex class hierarchies
- Don't validate trait values
- Don't hardcode category names in functions
- Don't overcomplicate the prompt generation
- Don't add error recovery or retry logic

### Code Style Example
```python
# GOOD: Simple, clear, single purpose
def add_trait_block(persona: Dict, category: str, traits: Dict) -> Dict:
    """Add a trait block to persona"""
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}")
    persona["personality_traits"][category] = traits
    return persona

# BAD: Too much logic, fallbacks, defaults
def add_trait_block(persona, category=None, traits=None):
    """Don't write code like this"""
    category = category or "general"  # NO: Don't add defaults
    traits = traits or {}             # NO: Don't add fallbacks
    if not validate_traits(traits):   # NO: Don't validate content
        traits = sanitize(traits)     # NO: Don't transform data
    # ... etc
```

## Example Generated System Prompts

### Professional Context
```
You are Joe Martinez

Master plumber with 25 years of experience

Professional:
- Occupation: Master Plumber
- Years Experience: 25
- Specialties: residential, commercial
- License: AZ-MP-12345

Communication Style:
- Approach: friendly and direct
- Explains: in simple terms
- Always Mentions: safety first

Capabilities:
- Pipe Repair: expert level
- Leak Detection: advanced
- Code Compliance: certified

Maintain these characteristics consistently in all your responses.
```

### Social Context
```
You are Sarah Mitchell

Marketing manager and mother of two

Personality:
- Social: extrovert at work, needs quiet time at home
- Stress Response: exercise and meditation
- Energy: high in morning, lower by evening

Preferences:
- Activities: hiking, reading, cooking
- Music: indie rock and classical
- Weekend: family time priority

Relationships:
- Children: 2 boys, ages 8 and 11
- Friends: small close circle
- Community: active in school PTA

Maintain these characteristics consistently in all your responses.
```

## Testing Approach

### Core Tests
1. Create persona with all trait categories
2. Generate prompts for different contexts
3. Save/load from JSON
4. Validate category names only
5. Handle missing/empty traits gracefully
6. Context filtering produces correct subsets

### Integration Tests
1. API endpoint functionality
2. File system operations
3. Prompt generation with real personas
4. Context filtering with multiple personas
5. Template creation and application

### Edge Cases
1. Empty personality_traits object
2. Unknown categories (should reject)
3. Very large trait blocks
4. Special characters in values
5. Nested objects in traits
6. Array values in traits

## Configuration

### Default Configuration
```python
SPB_CONFIG = {
    "valid_categories": [
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
    ],
    "personas_directory": "personas",
    "max_trait_size": 10000,  # characters per trait block
    "default_llm_config": {
        "provider": "openai",
        "temperature": 0.7,
        "max_tokens": 2000
    }
}
```

## Success Metrics

1. **Simplicity**: < 500 lines of core code
2. **Flexibility**: Any JSON structure accepted within categories
3. **Performance**: < 100ms prompt generation
4. **Reliability**: No runtime errors from unexpected data
5. **Usability**: Non-technical users can create personas
6. **Maintainability**: New developers understand code in < 30 minutes

## Migration from Existing Systems

For users with existing persona definitions:

1. Map existing fields to trait categories
2. No need to change field names - SPB accepts any keys
3. Add persona_id and name at top level
4. Move all traits under personality_traits object
5. Separate LLM configuration from traits

### Example Migration
```python
# Old format
old_persona = {
    "name": "Betty",
    "age": 65,
    "occupation": "Teacher",
    "personality": "warm"
}

# New SPB format
new_persona = {
    "persona_id": "betty_001",
    "name": "Betty",
    "personality_traits": {
        "demographics": {
            "age": 65
        },
        "professional": {
            "occupation": "Teacher"
        },
        "personality": {
            "temperament": "warm"
        }
    },
    "llm_config": {
        "provider": "openai",
        "temperature": 0.7
    }
}
```

## Future Enhancements (Not in V1)

These are possibilities for future versions, NOT to be implemented initially:

- Persona inheritance (base + variations)
- Trait block versioning
- Analytics on trait usage
- Persona consistency scoring
- Multi-language support
- Integration with Smart Conversation Builder
- Trait block library/marketplace
- A/B testing framework for personas
- Automatic persona generation from conversations
- Persona evolution over time

## Conclusion

Smart Persona Builder provides a flexible, maintainable system for creating rich AI personas. By using a block-based approach with no schema enforcement, it allows users to describe personas naturally while maintaining enough structure for consistent system prompt generation. The focus on simplicity and flexibility ensures the system can adapt to any use case without modification.

The system's power comes from its simplicity - by not overengineering the solution, we create something that is both powerful and maintainable. Users can create personas that behave differently in different contexts, just like real people do, without complex configuration or programming.

---

*This specification provides complete context for implementing Smart Persona Builder. The system should remain simple, flexible, and focused on its core purpose: turning personality trait blocks into effective system prompts.*