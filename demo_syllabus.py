"""
Demo: How the System Knows the Syllabus
"""

from syllabus_knowledge import (
    get_syllabus_for_grade,
    get_topics_for_subject,
    get_learning_objectives,
    validate_topic,
    get_next_topic_in_syllabus,
    get_syllabus_progress,
    get_textbook_reference
)

def demo_syllabus_knowledge():
    """Demonstrate syllabus knowledge"""
    print("="*70)
    print("  How the System Knows the Syllabus - Demo")
    print("="*70)
    
    # Example 1: Get syllabus for Grade 5 Math
    print("\n1. Getting NCERT Syllabus for Grade 5 Math:")
    print("-" * 70)
    syllabus = get_syllabus_for_grade(5, "math")
    print(f"Subject: {syllabus.get('name', 'Mathematics')}")
    print("\nTopics:")
    for i, topic in enumerate(syllabus.get('topics', [])[:5], 1):
        print(f"  {i}. {topic.get('name')} ({topic.get('english')})")
        if topic.get('description'):
            print(f"     → {topic.get('description')}")
    
    # Example 2: Get all topics for a subject
    print("\n\n2. All Topics for Grade 5 Math:")
    print("-" * 70)
    topics = get_topics_for_subject(5, "math")
    for topic in topics:
        print(f"  • {topic.get('name')} - {topic.get('english')}")
    
    # Example 3: Validate if a topic is in syllabus
    print("\n\n3. Validating Topics:")
    print("-" * 70)
    test_topics = ["भिन्न", "Fractions", "Algebra", "कलन"]
    for topic in test_topics:
        is_valid = validate_topic(5, "math", topic)
        status = "✅ IN SYLLABUS" if is_valid else "❌ NOT IN SYLLABUS"
        print(f"  '{topic}' for Grade 5 Math: {status}")
    
    # Example 4: Get next topic
    print("\n\n4. Getting Next Topic in Sequence:")
    print("-" * 70)
    current = "गुणा और भाग"
    next_topic = get_next_topic_in_syllabus(5, "math", current)
    if next_topic:
        print(f"  Current: {current}")
        print(f"  Next: {next_topic.get('name')} ({next_topic.get('english')})")
    else:
        print(f"  Current: {current}")
        print("  Next: (Last topic or not found)")
    
    # Example 5: Learning Objectives
    print("\n\n5. Learning Objectives for Grade 5 Math:")
    print("-" * 70)
    objectives = get_learning_objectives(5, "math")
    for obj in objectives:
        print(f"  • {obj}")
    
    # Example 6: Textbook Reference
    print("\n\n6. NCERT Textbook Reference:")
    print("-" * 70)
    textbook = get_textbook_reference(5, "math")
    print(f"  Grade 5 Math: {textbook}")
    
    # Example 7: Syllabus Progress
    print("\n\n7. Syllabus Progress Tracking:")
    print("-" * 70)
    completed = ["संख्या प्रणाली", "गुणा और भाग"]
    progress = get_syllabus_progress(5, "math", completed)
    print(f"  Total Topics: {progress['total_topics']}")
    print(f"  Completed: {progress['completed_topics']}")
    print(f"  Remaining: {progress['remaining_topics']}")
    print(f"  Progress: {progress['progress_percentage']:.1f}%")
    print(f"\n  Completed Topics:")
    for topic in completed:
        print(f"    ✓ {topic}")
    print(f"\n  Remaining Topics:")
    for topic in progress['all_topics']:
        if topic not in completed:
            print(f"    ○ {topic}")
    
    # Example 8: Different Grades
    print("\n\n8. Syllabus Across Different Grades:")
    print("-" * 70)
    for grade in [1, 3, 5, 8]:
        topics = get_topics_for_subject(grade, "math")
        print(f"\n  Grade {grade} Math ({len(topics)} topics):")
        for topic in topics[:3]:  # Show first 3
            print(f"    • {topic.get('name')}")
        if len(topics) > 3:
            print(f"    ... and {len(topics) - 3} more")
    
    print("\n" + "="*70)
    print("  ✅ The System KNOWS the Syllabus!")
    print("="*70)
    print("\nKey Points:")
    print("  • Syllabus based on NCERT/CBSE curriculum")
    print("  • Complete coverage for Grades 1-8")
    print("  • Topics, objectives, and sequences defined")
    print("  • Validates topics before teaching")
    print("  • Tracks progress against syllabus")
    print("="*70)


if __name__ == "__main__":
    demo_syllabus_knowledge()
