"""
Daily Tuition Agent for Village Students (Grades 1-8)
An intelligent educational agent with voice, video, assessments, and interactive Q&A
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tuition_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from voice_synthesizer import VoiceSynthesizer
    from video_generator import VideoGenerator
    from qa_system import QASystem
    from assessment_generator import AssessmentGenerator
    from engagement_tracker import EngagementTracker
    from curriculum_manager import CurriculumManager
except ImportError as e:
    logger.warning(f"Some modules not available: {e}")
    # Create placeholder classes for graceful degradation
    class VoiceSynthesizer:
        def synthesize(self, *args, **kwargs): return "audio.mp3"
    class VideoGenerator:
        def create_lesson_video(self, *args, **kwargs): return "video.mp4"
    class QASystem:
        def answer_question(self, *args, **kwargs): return "Answer not available"
    class AssessmentGenerator:
        def generate_assessment(self, *args, **kwargs): return {"questions": []}
        def evaluate_answers(self, *args, **kwargs): return {"score": 0.0}
    class EngagementTracker:
        def record_interaction(self, *args, **kwargs): pass
        def get_engagement_score(self, *args, **kwargs): return 0.0
        def get_engagement_stats(self, *args, **kwargs): return {}
        def update_engagement_score(self, *args, **kwargs): pass
        badges = {}
    class CurriculumManager:
        def get_next_subject(self, *args, **kwargs): return "math"
        def get_next_topic(self, *args, **kwargs): return "Introduction"
        def generate_lesson_content(self, *args, **kwargs): return "Lesson content"
        def get_learning_objectives(self, *args, **kwargs): return []


@dataclass
class StudentProfile:
    """Student profile data structure"""
    student_id: str
    name: str
    grade: int
    language: str
    progress: Dict[str, float]  # subject -> completion percentage
    last_lesson_date: Optional[str]
    engagement_score: float
    learning_style: str  # visual, auditory, kinesthetic
    strengths: List[str]
    areas_for_improvement: List[str]


@dataclass
class Lesson:
    """Lesson data structure"""
    lesson_id: str
    grade: int
    subject: str
    topic: str
    content: str
    duration_minutes: int
    video_path: Optional[str]
    audio_path: Optional[str]
    learning_objectives: List[str]
    difficulty_level: str  # easy, medium, hard


class TuitionAgent:
    """
    Main Tuition Agent orchestrator
    Coordinates all components to deliver personalized education
    """
    
    def __init__(self, config_path: str = "tuition_config.json"):
        """Initialize the tuition agent with all components"""
        self.config = self._load_config(config_path)
        self.students_dir = Path("students")
        self.lessons_dir = Path("lessons")
        self.assessments_dir = Path("assessments")
        
        # Create necessary directories
        self.students_dir.mkdir(exist_ok=True)
        self.lessons_dir.mkdir(exist_ok=True)
        self.assessments_dir.mkdir(exist_ok=True)
        
        # Initialize components
        logger.info("Initializing Tuition Agent components...")
        self.voice_synthesizer = VoiceSynthesizer(
            language=self.config.get("default_language", "hi"),
            voice_style=self.config.get("voice_style", "friendly")
        )
        self.video_generator = VideoGenerator(
            animation_style=self.config.get("animation_style", "cartoon"),
            quality=self.config.get("video_quality", "medium")
        )
        self.qa_system = QASystem(
            language=self.config.get("default_language", "hi"),
            model_name=self.config.get("qa_model", "gpt-3.5-turbo")
        )
        self.assessment_generator = AssessmentGenerator(
            grade_range=(1, 8),
            question_types=self.config.get("question_types", ["mcq", "short", "interactive"])
        )
        self.engagement_tracker = EngagementTracker()
        self.curriculum_manager = CurriculumManager()
        
        logger.info("Tuition Agent initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "default_language": "hi",  # Hindi
            "supported_languages": ["hi", "en", "te", "ta", "mr", "gu", "bn", "kn", "ml", "or"],
            "voice_style": "friendly",
            "animation_style": "cartoon",
            "video_quality": "medium",
            "qa_model": "gpt-3.5-turbo",
            "question_types": ["mcq", "short", "interactive"],
            "daily_lesson_duration": 30,  # minutes
            "assessment_questions": 5,
            "engagement_threshold": 0.7
        }
    
    def register_student(self, name: str, grade: int, language: str, 
                        learning_style: str = "visual") -> str:
        """Register a new student"""
        student_id = f"STU_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        student_profile = StudentProfile(
            student_id=student_id,
            name=name,
            grade=grade,
            language=language,
            progress={},
            last_lesson_date=None,
            engagement_score=0.0,
            learning_style=learning_style,
            strengths=[],
            areas_for_improvement=[]
        )
        
        # Save student profile
        profile_path = self.students_dir / f"{student_id}.json"
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(student_profile), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Registered new student: {name} (ID: {student_id})")
        return student_id
    
    def load_student(self, student_id: str) -> Optional[StudentProfile]:
        """Load student profile"""
        profile_path = self.students_dir / f"{student_id}.json"
        if not profile_path.exists():
            return None
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return StudentProfile(**data)
    
    def save_student(self, student: StudentProfile):
        """Save student profile"""
        profile_path = self.students_dir / f"{student.student_id}.json"
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(student), f, indent=2, ensure_ascii=False)
    
    def create_daily_lesson(self, student_id: str, subject: str = None) -> Lesson:
        """Create a personalized daily lesson for a student"""
        student = self.load_student(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Get appropriate lesson from curriculum
        if subject is None:
            subject = self.curriculum_manager.get_next_subject(student)
        
        lesson_topic = self.curriculum_manager.get_next_topic(
            student.grade, subject, student.progress.get(subject, 0.0)
        )
        
        # Generate lesson content
        lesson_content = self.curriculum_manager.generate_lesson_content(
            grade=student.grade,
            subject=subject,
            topic=lesson_topic,
            language=student.language,
            learning_style=student.learning_style
        )
        
        # Create lesson
        lesson_id = f"LESSON_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        lesson = Lesson(
            lesson_id=lesson_id,
            grade=student.grade,
            subject=subject,
            topic=lesson_topic,
            content=lesson_content,
            duration_minutes=self.config["daily_lesson_duration"],
            video_path=None,
            audio_path=None,
            learning_objectives=self.curriculum_manager.get_learning_objectives(
                student.grade, subject, lesson_topic
            ),
            difficulty_level=self._determine_difficulty(student, subject)
        )
        
        # Generate audio narration
        logger.info(f"Generating voice narration for lesson {lesson_id}...")
        audio_path = self.voice_synthesizer.synthesize(
            text=lesson_content,
            language=student.language,
            output_path=str(self.lessons_dir / f"{lesson_id}_audio.mp3")
        )
        lesson.audio_path = audio_path
        
        # Generate animated video
        logger.info(f"Generating animated video for lesson {lesson_id}...")
        video_path = self.video_generator.create_lesson_video(
            lesson_content=lesson_content,
            topic=lesson_topic,
            grade=student.grade,
            language=student.language,
            output_path=str(self.lessons_dir / f"{lesson_id}_video.mp4")
        )
        lesson.video_path = video_path
        
        # Save lesson
        lesson_path = self.lessons_dir / f"{lesson_id}.json"
        with open(lesson_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(lesson), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created lesson {lesson_id} for student {student_id}")
        return lesson
    
    def _determine_difficulty(self, student: StudentProfile, subject: str) -> str:
        """Determine appropriate difficulty level for student"""
        progress = student.progress.get(subject, 0.0)
        if progress < 0.3:
            return "easy"
        elif progress < 0.7:
            return "medium"
        else:
            return "hard"
    
    def answer_doubt(self, student_id: str, question: str) -> str:
        """Answer student's doubt in their language"""
        student = self.load_student(student_id)
        if not student:
            return "Student not found"
        
        logger.info(f"Student {student_id} asked: {question}")
        
        # Get contextual answer from Q&A system
        answer = self.qa_system.answer_question(
            question=question,
            language=student.language,
            grade=student.grade,
            context=self._get_recent_lesson_context(student_id)
        )
        
        # Track engagement
        self.engagement_tracker.record_interaction(student_id, "doubt_asked")
        
        return answer
    
    def _get_recent_lesson_context(self, student_id: str) -> str:
        """Get context from recent lessons"""
        # Find most recent lesson for this student
        lesson_files = sorted(
            self.lessons_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if lesson_files:
            with open(lesson_files[0], 'r', encoding='utf-8') as f:
                lesson_data = json.load(f)
                return lesson_data.get("content", "")
        return ""
    
    def conduct_assessment(self, student_id: str, lesson_id: str) -> Dict:
        """Conduct daily assessment on taught lesson"""
        student = self.load_student(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Load lesson
        lesson_path = self.lessons_dir / f"{lesson_id}.json"
        if not lesson_path.exists():
            raise ValueError(f"Lesson {lesson_id} not found")
        
        with open(lesson_path, 'r', encoding='utf-8') as f:
            lesson_data = json.load(f)
        
        # Generate assessment questions
        logger.info(f"Generating assessment for lesson {lesson_id}...")
        assessment = self.assessment_generator.generate_assessment(
            lesson_content=lesson_data["content"],
            topic=lesson_data["topic"],
            grade=student.grade,
            language=student.language,
            num_questions=self.config["assessment_questions"]
        )
        
        # Save assessment
        assessment_id = f"ASSESS_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        assessment_path = self.assessments_dir / f"{assessment_id}.json"
        assessment["assessment_id"] = assessment_id
        assessment["student_id"] = student_id
        assessment["lesson_id"] = lesson_id
        
        with open(assessment_path, 'w', encoding='utf-8') as f:
            json.dump(assessment, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created assessment {assessment_id} for student {student_id}")
        return assessment
    
    def submit_assessment(self, student_id: str, assessment_id: str, 
                         answers: Dict[str, str]) -> Dict:
        """Submit assessment answers and get results"""
        # Load assessment
        assessment_path = self.assessments_dir / f"{assessment_id}.json"
        if not assessment_path.exists():
            raise ValueError(f"Assessment {assessment_id} not found")
        
        with open(assessment_path, 'r', encoding='utf-8') as f:
            assessment = json.load(f)
        
        # Evaluate answers
        results = self.assessment_generator.evaluate_answers(
            assessment=assessment,
            answers=answers,
            language=self.load_student(student_id).language
        )
        
        # Update student progress
        student = self.load_student(student_id)
        subject = assessment.get("subject", "general")
        if subject not in student.progress:
            student.progress[subject] = 0.0
        
        # Update progress based on score
        score = results["score"]
        if score >= 0.8:
            student.progress[subject] = min(1.0, student.progress[subject] + 0.1)
        elif score >= 0.6:
            student.progress[subject] = min(1.0, student.progress[subject] + 0.05)
        
        student.last_lesson_date = datetime.now().isoformat()
        self.save_student(student)
        
        # Track engagement
        self.engagement_tracker.record_interaction(student_id, "assessment_completed")
        self.engagement_tracker.update_engagement_score(
            student_id, 
            score * 0.3  # Assessment contributes to engagement
        )
        
        results["student_id"] = student_id
        results["assessment_id"] = assessment_id
        
        # Save results
        results_path = self.assessments_dir / f"{assessment_id}_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
    
    def get_engagement_suggestions(self, student_id: str) -> List[str]:
        """Get suggestions to improve student engagement"""
        student = self.load_student(student_id)
        if not student:
            return []
        
        engagement_score = self.engagement_tracker.get_engagement_score(student_id)
        
        suggestions = []
        if engagement_score < 0.5:
            suggestions.append("Try shorter lessons with more interactive elements")
            suggestions.append("Add more visual content and animations")
            suggestions.append("Include gamification elements like badges and rewards")
        elif engagement_score < 0.7:
            suggestions.append("Mix different types of activities")
            suggestions.append("Add more real-world examples")
            suggestions.append("Include storytelling elements")
        else:
            suggestions.append("Maintain current engagement level")
            suggestions.append("Consider advanced topics")
        
        return suggestions
    
    def run_daily_session(self, student_id: str) -> Dict:
        """Run complete daily tuition session"""
        logger.info(f"Starting daily session for student {student_id}")
        
        student = self.load_student(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        session_results = {
            "student_id": student_id,
            "date": datetime.now().isoformat(),
            "lesson": None,
            "assessment": None,
            "engagement_score": 0.0
        }
        
        # Create and deliver lesson
        lesson = self.create_daily_lesson(student_id)
        session_results["lesson"] = {
            "lesson_id": lesson.lesson_id,
            "subject": lesson.subject,
            "topic": lesson.topic,
            "video_path": lesson.video_path,
            "audio_path": lesson.audio_path
        }
        
        # Conduct assessment
        assessment = self.conduct_assessment(student_id, lesson.lesson_id)
        session_results["assessment"] = {
            "assessment_id": assessment["assessment_id"],
            "questions": len(assessment["questions"])
        }
        
        # Update engagement
        engagement_score = self.engagement_tracker.get_engagement_score(student_id)
        session_results["engagement_score"] = engagement_score
        
        logger.info(f"Daily session completed for student {student_id}")
        return session_results


def main():
    """Main entry point for the tuition agent"""
    agent = TuitionAgent()
    
    # Example usage
    print("=== Daily Tuition Agent for Village Students ===\n")
    
    # Register a sample student
    student_id = agent.register_student(
        name="Rahul",
        grade=5,
        language="hi",
        learning_style="visual"
    )
    
    # Run daily session
    session = agent.run_daily_session(student_id)
    print(f"\nDaily session completed!")
    print(f"Lesson: {session['lesson']['topic']}")
    print(f"Assessment: {session['assessment']['questions']} questions")
    print(f"Engagement Score: {session['engagement_score']:.2f}")
    
    # Example doubt answering
    doubt = "गणित में भिन्न क्या होती है?"
    answer = agent.answer_doubt(student_id, doubt)
    print(f"\nStudent asked: {doubt}")
    print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
