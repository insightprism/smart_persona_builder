#!/usr/bin/env python3
"""Example usage of Smart Persona Builder"""

from spb_core import (
    create_empty_persona,
    add_trait_block,
    generate_system_prompt,
    save_persona,
    load_persona
)
from spb_templates import get_teacher_template, apply_template
import json

def main():
    print("=" * 60)
    print("Smart Persona Builder - Usage Examples")
    print("=" * 60)
    
    # Example 1: Create a persona from scratch
    print("\n1. Creating a custom persona from scratch:")
    print("-" * 40)
    
    # Create empty persona
    sarah = create_empty_persona(
        persona_id="sarah_mitchell",
        name="Sarah Mitchell",
        description="Marketing manager and mother of two",
        category="professional"
    )
    
    # Add demographic traits
    sarah = add_trait_block(sarah, "demographics", {
        "age": 35,
        "location": "Chicago, IL",
        "family": "Married with 2 children (ages 8 and 11)"
    })
    
    # Add professional traits
    sarah = add_trait_block(sarah, "professional", {
        "role": "Marketing Manager",
        "company": "Tech startup",
        "experience": "12 years",
        "skills": ["Digital marketing", "Data analytics", "Team leadership"],
        "work_style": "data-driven and collaborative"
    })
    
    # Add personality traits
    sarah = add_trait_block(sarah, "personality", {
        "temperament": "optimistic and energetic",
        "social_style": "extrovert at work, needs quiet time at home",
        "stress_response": "exercise and meditation"
    })
    
    # Add communication style
    sarah = add_trait_block(sarah, "communication_style", {
        "tone": "friendly and professional",
        "meetings": "prepared with data and visuals",
        "emails": "concise and action-oriented",
        "feedback": "constructive and specific"
    })
    
    # Generate system prompt
    prompt = generate_system_prompt(sarah)
    print(f"Generated prompt for {sarah['name']}:")
    print(prompt[:300] + "...")
    
    # Save persona
    filepath = save_persona(sarah, "personas")
    print(f"\nSaved to: {filepath}")
    
    # Example 2: Use a template
    print("\n\n2. Using a pre-built template:")
    print("-" * 40)
    
    # Get teacher template
    teacher = get_teacher_template()
    print(f"Template: {teacher['name']} - {teacher['description']}")
    
    # Customize the template
    customized_teacher = apply_template("teacher", {
        "persona_id": "mr_wilson",
        "name": "Mr. Wilson",
        "personality_traits": {
            "professional": {
                "subjects": ["History", "Geography"],
                "experience": "20 years",
                "teaching_style": "storytelling and interactive discussions"
            }
        }
    })
    
    print(f"\nCustomized: {customized_teacher['name']}")
    print(f"Subjects: {customized_teacher['personality_traits']['professional']['subjects']}")
    
    # Example 3: Context-aware prompts
    print("\n\n3. Context-aware system prompts:")
    print("-" * 40)
    
    # Generate prompts for different contexts
    contexts = ["professional", "social", "parenting"]
    
    for context in contexts:
        prompt = generate_system_prompt(sarah, context)
        lines = prompt.split('\n')
        print(f"\nContext: {context}")
        print(f"Active traits: {len(lines)} lines")
        print(f"Preview: {lines[0][:100]}...")
    
    # Example 4: Load and display a persona
    print("\n\n4. Loading a saved persona:")
    print("-" * 40)
    
    loaded_sarah = load_persona("sarah_mitchell", "personas")
    print(f"Loaded: {loaded_sarah['name']}")
    print(f"Categories: {list(loaded_sarah['personality_traits'].keys())}")
    
    # Count total traits
    total_traits = sum(
        len(traits) for traits in loaded_sarah['personality_traits'].values()
    )
    print(f"Total traits defined: {total_traits}")
    
    # Example 5: Display persona as JSON
    print("\n\n5. Persona JSON structure:")
    print("-" * 40)
    
    # Show compact version
    compact = {
        "persona_id": loaded_sarah["persona_id"],
        "name": loaded_sarah["name"],
        "trait_categories": list(loaded_sarah["personality_traits"].keys()),
        "llm_config": loaded_sarah["llm_config"]
    }
    print(json.dumps(compact, indent=2))
    
    print("\n" + "=" * 60)
    print("Examples complete! Check 'personas' directory for saved files.")
    print("=" * 60)

if __name__ == "__main__":
    main()