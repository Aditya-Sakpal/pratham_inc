"""
Topics router - handles topic listing and retrieval
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import TopicResponse

router = APIRouter()

# NCERT Science Topics for Classes 8-10
# This is a simplified list - you can expand based on actual syllabus
NCERT_TOPICS = {
    "Class VIII": [
        {"id": "viii_crop_production", "name": "Crop Production and Management", "chapter": "Chapter 1"},  # Found in NCERT list :contentReference[oaicite:1]{index=1}
        {"id": "viii_microorganisms", "name": "Microorganisms: Friend and Foe", "chapter": "Chapter 2"},
        {"id": "viii_materials_metals", "name": "Materials: Metals and Non-Metals", "chapter": "Chapter 4"},
        {"id": "viii_coal_petroleum", "name": "Coal and Petroleum", "chapter": "Chapter 5"},
        {"id": "viii_force_pressure", "name": "Force and Pressure", "chapter": "Chapter 11"},
        {"id": "viii_friction", "name": "Friction", "chapter": "Chapter 12"},
        {"id": "viii_sound", "name": "Sound", "chapter": "Chapter 13"},
        {"id": "viii_light", "name": "Light", "chapter": "Chapter 16"},
        {"id": "viii_pollution", "name": "Pollution of Air and Water", "chapter": "Chapter 18"},
    ],
    "Class IX": [
        {"id": "ix_matter_nature", "name": "Matter in Our Surroundings", "chapter": "Chapter 1"},  # :contentReference[oaicite:2]{index=2}
        {"id": "ix_pure_substance", "name": "Is Matter Around Us Pure?", "chapter": "Chapter 2"},
        {"id": "ix_atoms_molecules", "name": "Atoms and Molecules", "chapter": "Chapter 3"},
        {"id": "ix_structure_atom", "name": "Structure of the Atom", "chapter": "Chapter 4"},
        {"id": "ix_motion", "name": "Motion", "chapter": "Chapter 8"},
        {"id": "ix_force_laws", "name": "Force and Laws of Motion", "chapter": "Chapter 9"},
        {"id": "ix_work_energy", "name": "Work and Energy", "chapter": "Chapter 11"},
        {"id": "ix_sound", "name": "Sound", "chapter": "Chapter 12"},
        {"id": "ix_natural_resources", "name": "Natural Resources", "chapter": "Chapter 14"},
    ],
    "Class X": [
        {"id": "x_chemical_reactions", "name": "Chemical Reactions and Equations", "chapter": "Chapter 1"},  # :contentReference[oaicite:3]{index=3}
        {"id": "x_acids_bases", "name": "Acids, Bases and Salts", "chapter": "Chapter 2"},
        {"id": "x_metals_nonmetals", "name": "Metals and Non-metals", "chapter": "Chapter 3"},
        {"id": "x_carbon_compounds", "name": "Carbon and its Compounds", "chapter": "Chapter 4"},
        {"id": "x_life_processes", "name": "Life Processes", "chapter": "Chapter 5"},
        {"id": "x_control_coordination", "name": "Control and Coordination", "chapter": "Chapter 6"},
        {"id": "x_heredity_evolution", "name": "Heredity and Evolution", "chapter": "Chapter 8"},
        {"id": "x_light_reflection", "name": "Light – Reflection and Refraction", "chapter": "Chapter 9"},
        {"id": "x_electricity", "name": "Electricity", "chapter": "Chapter 11"},
    ],
}



@router.get("/", response_model=List[TopicResponse])
async def list_topics(class_level: str = None):
    """
    List all available topics
    
    Args:
        class_level: Optional filter by class (Class VIII, Class IX, Class X)
        
    Returns:
        List of topics
    """
    topics = []
    
    if class_level:
        if class_level not in NCERT_TOPICS:
            raise HTTPException(status_code=404, detail=f"Class level {class_level} not found")
        class_topics = NCERT_TOPICS[class_level]
    else:
        # Return all topics
        class_topics = []
        for cls, topic_list in NCERT_TOPICS.items():
            class_topics.extend(topic_list)
    
    for topic in class_topics:
        topics.append(TopicResponse(
            topic_id=topic["id"],
            topic_name=topic["name"],
            class_level=class_level or next(
                cls for cls, topics in NCERT_TOPICS.items() 
                if any(t["id"] == topic["id"] for t in topics)
            ),
            chapter=topic.get("chapter"),
            description=f"NCERT Science topic: {topic['name']}"
        ))
    
    return topics


@router.get("/classes", response_model=List[str])
async def list_classes():
    """List all available class levels"""
    return list(NCERT_TOPICS.keys())


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: str):
    """
    Get specific topic by ID
    
    Args:
        topic_id: Topic identifier
        
    Returns:
        Topic information
    """
    for class_level, topics in NCERT_TOPICS.items():
        for topic in topics:
            if topic["id"] == topic_id:
                return TopicResponse(
                    topic_id=topic["id"],
                    topic_name=topic["name"],
                    class_level=class_level,
                    chapter=topic.get("chapter"),
                    description=f"NCERT Science topic: {topic['name']}"
                )
    
    raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")