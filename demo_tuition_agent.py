"""
Demo script for Daily Tuition Agent
Shows basic usage examples
"""

from tuition_agent import TuitionAgent
import json

def demo_basic_usage():
    """Demonstrate basic usage of the tuition agent"""
    print("="*70)
    print("  Daily Tuition Agent - Demo")
    print("="*70)
    
    # Initialize agent
    print("\n1. Initializing Tuition Agent...")
    agent = TuitionAgent()
    print("   ✅ Agent initialized")
    
    # Register a student
    print("\n2. Registering a new student...")
    student_id = agent.register_student(
        name="Rahul Kumar",
        grade=5,
        language="hi",
        learning_style="visual"
    )
    print(f"   ✅ Student registered with ID: {student_id}")
    
    # Load student profile
    print("\n3. Loading student profile...")
    student = agent.load_student(student_id)
    print(f"   ✅ Loaded: {student.name}, Grade {student.grade}, Language: {student.language}")
    
    # Create a lesson
    print("\n4. Creating daily lesson...")
    print("   ⏳ This may take a moment (generating audio and video)...")
    try:
        lesson = agent.create_daily_lesson(student_id, subject="math")
        print(f"   ✅ Lesson created!")
        print(f"      Topic: {lesson.topic}")
        print(f"      Subject: {lesson.subject}")
        print(f"      Duration: {lesson.duration_minutes} minutes")
        if lesson.audio_path:
            print(f"      Audio: {lesson.audio_path}")
        if lesson.video_path:
            print(f"      Video: {lesson.video_path}")
    except Exception as e:
        print(f"   ⚠️  Lesson creation had issues: {e}")
        print("   (This is normal if TTS/video libraries are not fully configured)")
        # Create a mock lesson for demo
        from tuition_agent import Lesson
        from datetime import datetime
        lesson = Lesson(
            lesson_id="DEMO_LESSON",
            grade=5,
            subject="math",
            topic="संख्या (Numbers)",
            content="आज हम संख्याओं के बारे में सीखेंगे...",
            duration_minutes=30,
            video_path=None,
            audio_path=None,
            learning_objectives=["संख्या को समझना", "संख्या का उपयोग"],
            difficulty_level="medium"
        )
    
    # Answer a doubt
    print("\n5. Answering student doubt...")
    doubt = "गणित में भिन्न क्या होती है?"
    print(f"   Student asks: {doubt}")
    try:
        answer = agent.answer_doubt(student_id, doubt)
        print(f"   ✅ Answer: {answer[:100]}...")
    except Exception as e:
        print(f"   ⚠️  Q&A had issues: {e}")
        print("   (This is normal if AI models are not configured)")
        answer = "भिन्न एक संख्या है जो दो संख्याओं के बीच के अनुपात को दर्शाती है।"
        print(f"   Answer (fallback): {answer}")
    
    # Generate assessment
    print("\n6. Generating assessment...")
    try:
        assessment = agent.conduct_assessment(student_id, lesson.lesson_id)
        print(f"   ✅ Assessment created!")
        print(f"      Total questions: {assessment['total_questions']}")
        print(f"      Time limit: {assessment['time_limit_minutes']} minutes")
        print(f"\n   Sample question:")
        if assessment['questions']:
            q = assessment['questions'][0]
            print(f"      {q['question']}")
            if q['type'] == 'mcq':
                for i, opt in enumerate(q['options'], 1):
                    print(f"        {chr(96+i)}) {opt}")
    except Exception as e:
        print(f"   ⚠️  Assessment generation had issues: {e}")
        print("   (This is normal if assessment generator needs configuration)")
    
    # View engagement
    print("\n7. Checking engagement...")
    engagement_score = agent.engagement_tracker.get_engagement_score(student_id)
    stats = agent.engagement_tracker.get_engagement_stats(student_id)
    print(f"   ✅ Engagement Score: {engagement_score:.2f}")
    print(f"      Total Lessons: {stats['total_lessons']}")
    print(f"      Current Streak: {stats['current_streak']} days")
    
    # Get suggestions
    print("\n8. Getting learning suggestions...")
    suggestions = agent.get_engagement_suggestions(student_id)
    if suggestions:
        print(f"   ✅ Suggestions:")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"      {i}. {suggestion}")
    else:
        print("   ✅ Keep up the good work!")
    
    print("\n" + "="*70)
    print("  Demo completed!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Run 'python student_interface.py' for interactive interface")
    print("  2. Configure tuition_config.json for customization")
    print("  3. Install optional dependencies for full features:")
    print("     - pip install gtts (for voice)")
    print("     - pip install moviepy (for video)")
    print("     - Set OPENAI_API_KEY for advanced Q&A")
    print("="*70)


if __name__ == "__main__":
    try:
        demo_basic_usage()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
