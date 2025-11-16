"""
Student Interface for Daily Tuition Agent
Simple CLI interface for village students
"""

import os
import sys
from typing import Optional
from tuition_agent import TuitionAgent, StudentProfile

class StudentInterface:
    """Simple CLI interface for students"""
    
    def __init__(self):
        """Initialize interface"""
        self.agent = TuitionAgent()
        self.current_student_id: Optional[str] = None
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print("  🌟 दैनिक ट्यूशन एजेंट - Village Students के लिए 🌟")
        print("  Daily Tuition Agent for Village Students")
        print("="*60)
        print("\nयह एजेंट आपको:")
        print("  ✓ आवाज़ और एनिमेटेड वीडियो के साथ पढ़ाएगा")
        print("  ✓ आपके सवालों के जवाब देगा")
        print("  ✓ रोजाना मूल्यांकन करेगा")
        print("  ✓ आपको बोर नहीं होने देगा!")
        print("\n" + "-"*60)
    
    def register_or_login(self):
        """Register new student or login"""
        print("\nक्या आप नए छात्र हैं? (Are you a new student?)")
        print("1. हाँ, मैं नया हूँ (Yes, I'm new)")
        print("2. नहीं, मैं पहले से पंजीकृत हूँ (No, I'm already registered)")
        
        choice = input("\nअपना विकल्प चुनें (Enter your choice): ").strip()
        
        if choice == "1":
            return self.register_student()
        elif choice == "2":
            return self.login_student()
        else:
            print("गलत विकल्प! (Invalid choice!)")
            return self.register_or_login()
    
    def register_student(self) -> str:
        """Register a new student"""
        print("\n--- नया छात्र पंजीकरण (New Student Registration) ---")
        
        name = input("अपना नाम दर्ज करें (Enter your name): ").strip()
        if not name:
            print("नाम आवश्यक है! (Name is required!)")
            return self.register_student()
        
        print("\nकक्षा चुनें (Select your grade):")
        for grade in range(1, 9):
            print(f"  {grade}. कक्षा {grade} (Grade {grade})")
        
        try:
            grade = int(input("\nकक्षा (Grade): ").strip())
            if grade < 1 or grade > 8:
                raise ValueError
        except ValueError:
            print("कृपया 1-8 के बीच एक वैध कक्षा चुनें!")
            return self.register_student()
        
        print("\nभाषा चुनें (Select language):")
        languages = {
            "1": ("hi", "हिंदी"),
            "2": ("en", "English"),
            "3": ("te", "తెలుగు"),
            "4": ("ta", "தமிழ்"),
            "5": ("mr", "मराठी")
        }
        
        for key, (code, name) in languages.items():
            print(f"  {key}. {name}")
        
        lang_choice = input("\nभाषा (Language): ").strip()
        language = languages.get(lang_choice, ("hi", "हिंदी"))[0]
        
        print("\nसीखने की शैली (Learning style):")
        print("  1. दृश्य (Visual)")
        print("  2. श्रवण (Auditory)")
        print("  3. गतिशील (Kinesthetic)")
        
        style_choice = input("\nशैली (Style): ").strip()
        style_map = {"1": "visual", "2": "auditory", "3": "kinesthetic"}
        learning_style = style_map.get(style_choice, "visual")
        
        student_id = self.agent.register_student(name, grade, language, learning_style)
        
        print(f"\n✅ सफलतापूर्वक पंजीकृत! (Successfully registered!)")
        print(f"आपका छात्र ID: {student_id}")
        
        return student_id
    
    def login_student(self) -> Optional[str]:
        """Login existing student"""
        print("\n--- छात्र लॉगिन (Student Login) ---")
        student_id = input("अपना छात्र ID दर्ज करें (Enter your student ID): ").strip()
        
        student = self.agent.load_student(student_id)
        if student:
            print(f"\n✅ स्वागत है, {student.name}! (Welcome, {student.name}!)")
            return student_id
        else:
            print("❌ छात्र नहीं मिला! (Student not found!)")
            return None
    
    def display_main_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("  मुख्य मेनू (Main Menu)")
        print("="*60)
        print("\n1. 📚 आज का पाठ शुरू करें (Start Today's Lesson)")
        print("2. ❓ कोई संदेह पूछें (Ask a Doubt)")
        print("3. 📝 मूल्यांकन करें (Take Assessment)")
        print("4. 📊 मेरी प्रगति देखें (View My Progress)")
        print("5. 🏆 मेरे बैज देखें (View My Badges)")
        print("6. 🎯 सुझाव प्राप्त करें (Get Suggestions)")
        print("7. 🚪 बाहर निकलें (Exit)")
        print("\n" + "-"*60)
    
    def start_lesson(self):
        """Start today's lesson"""
        if not self.current_student_id:
            print("कृपया पहले लॉगिन करें! (Please login first!)")
            return
        
        print("\n📚 आज का पाठ शुरू कर रहे हैं... (Starting today's lesson...)")
        
        try:
            # Ask for subject preference
            print("\nविषय चुनें (Select subject):")
            subjects = {
                "1": "math",
                "2": "science",
                "3": "hindi",
                "4": "english",
                "5": "evs"
            }
            
            for key, subject in subjects.items():
                print(f"  {key}. {subject}")
            
            subject_choice = input("\nविषय (Subject) [Enter for auto]: ").strip()
            subject = subjects.get(subject_choice) if subject_choice else None
            
            lesson = self.agent.create_daily_lesson(self.current_student_id, subject)
            
            print(f"\n✅ पाठ तैयार है! (Lesson ready!)")
            print(f"\nविषय (Subject): {lesson.subject}")
            print(f"विषय (Topic): {lesson.topic}")
            print(f"अवधि (Duration): {lesson.duration_minutes} मिनट")
            
            if lesson.video_path:
                print(f"\n📹 वीडियो: {lesson.video_path}")
            if lesson.audio_path:
                print(f"🔊 ऑडियो: {lesson.audio_path}")
            
            print("\nपाठ सामग्री (Lesson Content):")
            print("-" * 60)
            print(lesson.content[:500] + "..." if len(lesson.content) > 500 else lesson.content)
            print("-" * 60)
            
            # Record lesson completion
            self.agent.engagement_tracker.record_interaction(
                self.current_student_id, 
                "lesson_completed",
                {"lesson_id": lesson.lesson_id}
            )
            
            # Ask if they want to take assessment
            assess = input("\nक्या आप मूल्यांकन करना चाहते हैं? (y/n): ").strip().lower()
            if assess == "y":
                self.take_assessment(lesson.lesson_id)
        
        except Exception as e:
            print(f"❌ त्रुटि: {e}")
    
    def ask_doubt(self):
        """Ask a doubt"""
        if not self.current_student_id:
            print("कृपया पहले लॉगिन करें! (Please login first!)")
            return
        
        print("\n❓ अपना सवाल पूछें (Ask your question)")
        print("-" * 60)
        question = input("सवाल (Question): ").strip()
        
        if not question:
            print("कृपया एक सवाल दर्ज करें!")
            return
        
        print("\n🤔 सोच रहे हैं... (Thinking...)")
        
        try:
            answer = self.agent.answer_doubt(self.current_student_id, question)
            
            print("\n" + "="*60)
            print("  उत्तर (Answer)")
            print("="*60)
            print(answer)
            print("="*60)
        
        except Exception as e:
            print(f"❌ त्रुटि: {e}")
    
    def take_assessment(self, lesson_id: Optional[str] = None):
        """Take assessment"""
        if not self.current_student_id:
            print("कृपया पहले लॉगिन करें!")
            return
        
        if not lesson_id:
            # Get recent lesson
            print("कृपया पाठ ID दर्ज करें (Enter lesson ID):")
            lesson_id = input("पाठ ID (Lesson ID): ").strip()
        
        if not lesson_id:
            print("पाठ ID आवश्यक है!")
            return
        
        print("\n📝 मूल्यांकन तैयार कर रहे हैं... (Preparing assessment...)")
        
        try:
            assessment = self.agent.conduct_assessment(self.current_student_id, lesson_id)
            
            print(f"\n✅ मूल्यांकन तैयार है! (Assessment ready!)")
            print(f"कुल प्रश्न (Total questions): {assessment['total_questions']}")
            print(f"समय सीमा (Time limit): {assessment['time_limit_minutes']} मिनट")
            
            # Collect answers
            answers = {}
            print("\n" + "="*60)
            print("  मूल्यांकन प्रश्न (Assessment Questions)")
            print("="*60)
            
            for i, question in enumerate(assessment['questions'], 1):
                print(f"\nप्रश्न {i}: {question['question']}")
                
                if question['type'] == 'mcq':
                    for j, option in enumerate(question['options'], 1):
                        print(f"  {chr(96+j)}) {option}")
                    answer = input("\nउत्तर (Answer a/b/c/d): ").strip().lower()
                else:
                    answer = input("\nउत्तर (Answer): ").strip()
                
                answers[question['question_id']] = answer
            
            # Submit and get results
            print("\n📊 मूल्यांकन जांच रहे हैं... (Evaluating assessment...)")
            results = self.agent.submit_assessment(
                self.current_student_id,
                assessment['assessment_id'],
                answers
            )
            
            print("\n" + "="*60)
            print("  मूल्यांकन परिणाम (Assessment Results)")
            print("="*60)
            print(f"स्कोर (Score): {results['percentage']:.1f}%")
            print(f"सही उत्तर (Correct): {results['correct_answers']}/{results['total_questions']}")
            print(f"\n{results['overall_feedback']}")
            print("="*60)
        
        except Exception as e:
            print(f"❌ त्रुटि: {e}")
    
    def view_progress(self):
        """View student progress"""
        if not self.current_student_id:
            print("कृपया पहले लॉगिन करें!")
            return
        
        student = self.agent.load_student(self.current_student_id)
        if not student:
            print("छात्र नहीं मिला!")
            return
        
        print("\n" + "="*60)
        print(f"  {student.name} की प्रगति (Progress)")
        print("="*60)
        
        print(f"\nकक्षा (Grade): {student.grade}")
        print(f"भाषा (Language): {student.language}")
        print(f"सीखने की शैली (Learning Style): {student.learning_style}")
        
        if student.progress:
            print("\nविषय-वार प्रगति (Subject-wise Progress):")
            for subject, progress in student.progress.items():
                bar_length = int(progress * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                print(f"  {subject}: {bar} {progress*100:.1f}%")
        else:
            print("\nअभी तक कोई प्रगति नहीं है।")
        
        # Engagement stats
        stats = self.agent.engagement_tracker.get_engagement_stats(self.current_student_id)
        print(f"\nसग्रहण स्कोर (Engagement Score): {stats['engagement_score']:.2f}")
        print(f"कुल पाठ (Total Lessons): {stats['total_lessons']}")
        print(f"वर्तमान स्ट्रीक (Current Streak): {stats['current_streak']} दिन")
        
        print("="*60)
    
    def view_badges(self):
        """View earned badges"""
        if not self.current_student_id:
            print("कृपया पहले लॉगिन करें!")
            return
        
        stats = self.agent.engagement_tracker.get_engagement_stats(self.current_student_id)
        badges = stats.get('badges_earned', [])
        
        print("\n" + "="*60)
        print("  🏆 आपके बैज (Your Badges)")
        print("="*60)
        
        if badges:
            for badge_id in badges:
                badge_info = self.agent.engagement_tracker.badges.get(badge_id, {})
                badge_name = badge_info.get("name", badge_id)
                print(f"  🏅 {badge_name}")
        else:
            print("  अभी तक कोई बैज नहीं मिला है। पढ़ाई जारी रखें!")
        
        print("="*60)
    
    def get_suggestions(self):
        """Get learning suggestions"""
        if not self.current_student_id:
            print("कृपया पहले लॉगिन करें!")
            return
        
        suggestions = self.agent.get_engagement_suggestions(self.current_student_id)
        motivational = self.agent.engagement_tracker.get_motivational_message(
            self.current_student_id,
            self.agent.load_student(self.current_student_id).language
        )
        
        print("\n" + "="*60)
        print("  💡 सुझाव (Suggestions)")
        print("="*60)
        print(f"\n{motivational}\n")
        
        if suggestions:
            print("सीखने के सुझाव (Learning Suggestions):")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("बहुत अच्छा काम कर रहे हैं! जारी रखें!")
        
        print("="*60)
    
    def run(self):
        """Run the interface"""
        self.display_welcome()
        
        # Register or login
        student_id = self.register_or_login()
        if not student_id:
            print("लॉगिन असफल! (Login failed!)")
            return
        
        self.current_student_id = student_id
        
        # Main loop
        while True:
            self.display_main_menu()
            choice = input("\nविकल्प चुनें (Enter choice): ").strip()
            
            if choice == "1":
                self.start_lesson()
            elif choice == "2":
                self.ask_doubt()
            elif choice == "3":
                self.take_assessment()
            elif choice == "4":
                self.view_progress()
            elif choice == "5":
                self.view_badges()
            elif choice == "6":
                self.get_suggestions()
            elif choice == "7":
                print("\n👋 धन्यवाद! फिर मिलेंगे! (Thank you! See you again!)")
                break
            else:
                print("❌ गलत विकल्प! (Invalid choice!)")
            
            input("\nजारी रखने के लिए Enter दबाएं... (Press Enter to continue...)")


def main():
    """Main entry point"""
    try:
        interface = StudentInterface()
        interface.run()
    except KeyboardInterrupt:
        print("\n\n👋 धन्यवाद! (Thank you!)")
    except Exception as e:
        print(f"\n❌ त्रुटि: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
