"""
Curriculum Manager
Manages curriculum for grades 1-8 across subjects
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class CurriculumManager:
    """
    Manages curriculum content for grades 1-8
    Provides structured learning paths
    """
    
    def __init__(self):
        """Initialize curriculum manager"""
        self.curriculum_dir = Path("curriculum")
        self.curriculum_dir.mkdir(exist_ok=True)
        
        # Load curriculum structure
        self.curriculum = self._load_curriculum()
    
    def _load_curriculum(self) -> Dict:
        """Load curriculum structure"""
        curriculum_file = self.curriculum_dir / "curriculum.json"
        
        if curriculum_file.exists():
            with open(curriculum_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Create default curriculum
        curriculum = self._create_default_curriculum()
        with open(curriculum_file, 'w', encoding='utf-8') as f:
            json.dump(curriculum, f, indent=2, ensure_ascii=False)
        
        return curriculum
    
    def _create_default_curriculum(self) -> Dict:
        """Create default curriculum structure"""
        subjects = {
            "math": "गणित",
            "science": "विज्ञान",
            "hindi": "हिंदी",
            "english": "अंग्रेजी",
            "evs": "पर्यावरण अध्ययन"
        }
        
        curriculum = {}
        
        for grade in range(1, 9):
            curriculum[grade] = {}
            for subject, subject_name in subjects.items():
                curriculum[grade][subject] = {
                    "name": subject_name,
                    "topics": self._get_topics_for_subject(grade, subject),
                    "learning_objectives": []
                }
        
        return curriculum
    
    def _get_topics_for_subject(self, grade: int, subject: str) -> List[Dict]:
        """Get topics for a subject and grade - Uses NCERT Syllabus"""
        try:
            from syllabus_knowledge import get_topics_for_subject as get_ncert_topics
            ncert_topics = get_ncert_topics(grade, subject)
            if ncert_topics:
                # Convert NCERT format to our format
                return [{"name": t.get("name", ""), "completed": False, "english": t.get("english", ""), 
                        "description": t.get("description", "")} for t in ncert_topics]
        except ImportError:
            logger.warning("syllabus_knowledge not available, using fallback")
        
        # Fallback to basic topics if NCERT syllabus not available
        topics_map = {
            "math": {
                1: ["संख्या 1-100", "जोड़", "घटाव", "आकार", "माप"],
                2: ["संख्या 1-1000", "जोड़-घटाव", "गुणा", "भाग", "समय"],
                3: ["बड़ी संख्याएं", "गुणा-भाग", "भिन्न", "दशमलव", "माप"],
                4: ["बड़ी संख्याएं", "गुणा-भाग", "भिन्न", "दशमलव", "क्षेत्रफल"],
                5: ["संख्या प्रणाली", "गुणा-भाग", "भिन्न", "दशमलव", "प्रतिशत"],
                6: ["पूर्ण संख्याएं", "भिन्न", "दशमलव", "बीजगणित", "ज्यामिति"],
                7: ["पूर्णांक", "भिन्न", "बीजगणित", "ज्यामिति", "आंकड़े"],
                8: ["परिमेय संख्याएं", "बीजगणित", "ज्यामिति", "मेंसुरेशन", "आंकड़े"]
            },
            "science": {
                1: ["पौधे", "जानवर", "शरीर", "खाना", "पानी"],
                2: ["पौधे", "जानवर", "शरीर", "खाना", "हवा"],
                3: ["पौधे", "जानवर", "शरीर", "खाना", "पदार्थ"],
                4: ["पौधे", "जानवर", "शरीर", "खाना", "ऊर्जा"],
                5: ["पौधे", "जानवर", "शरीर", "खाना", "बल"],
                6: ["खाद्य पदार्थ", "सामग्री", "पौधे", "शरीर", "गति"],
                7: ["पोषण", "श्वसन", "परिवहन", "प्रजनन", "प्रकाश"],
                8: ["फसल उत्पादन", "सूक्ष्मजीव", "सामग्री", "दबाव", "ध्वनि"]
            },
            "hindi": {
                1: ["वर्णमाला", "शब्द", "वाक्य", "कहानी", "कविता"],
                2: ["वर्णमाला", "शब्द", "वाक्य", "कहानी", "कविता"],
                3: ["व्याकरण", "शब्द", "वाक्य", "कहानी", "निबंध"],
                4: ["व्याकरण", "शब्द", "वाक्य", "कहानी", "निबंध"],
                5: ["व्याकरण", "शब्द", "वाक्य", "कहानी", "निबंध"],
                6: ["व्याकरण", "शब्द", "वाक्य", "कहानी", "निबंध"],
                7: ["व्याकरण", "शब्द", "वाक्य", "कहानी", "निबंध"],
                8: ["व्याकरण", "शब्द", "वाक्य", "कहानी", "निबंध"]
            },
            "english": {
                1: ["Alphabet", "Words", "Sentences", "Stories", "Poems"],
                2: ["Alphabet", "Words", "Sentences", "Stories", "Poems"],
                3: ["Grammar", "Words", "Sentences", "Stories", "Essays"],
                4: ["Grammar", "Words", "Sentences", "Stories", "Essays"],
                5: ["Grammar", "Words", "Sentences", "Stories", "Essays"],
                6: ["Grammar", "Words", "Sentences", "Stories", "Essays"],
                7: ["Grammar", "Words", "Sentences", "Stories", "Essays"],
                8: ["Grammar", "Words", "Sentences", "Stories", "Essays"]
            },
            "evs": {
                1: ["परिवार", "स्कूल", "खेल", "खाना", "पानी"],
                2: ["परिवार", "स्कूल", "खेल", "खाना", "पानी"],
                3: ["परिवार", "समुदाय", "पर्यावरण", "खाना", "पानी"],
                4: ["परिवार", "समुदाय", "पर्यावरण", "खाना", "पानी"],
                5: ["परिवार", "समुदाय", "पर्यावरण", "खाना", "पानी"]
            }
        }
        
        topics_list = topics_map.get(subject, {}).get(grade, [])
        return [{"name": topic, "completed": False} for topic in topics_list]
    
    def get_next_subject(self, student_profile) -> str:
        """Get next subject to teach based on student progress"""
        grade = student_profile.grade
        progress = student_profile.progress
        
        # Find subject with least progress
        subjects = list(self.curriculum.get(grade, {}).keys())
        
        if not subjects:
            return "math"  # Default
        
        subject_progress = {
            subj: progress.get(subj, 0.0) for subj in subjects
        }
        
        # Return subject with minimum progress
        return min(subject_progress, key=subject_progress.get)
    
    def get_next_topic(self, grade: int, subject: str, 
                       current_progress: float) -> str:
        """Get next topic based on progress"""
        topics = self.curriculum.get(grade, {}).get(subject, {}).get("topics", [])
        
        if not topics:
            return "Introduction"
        
        # Calculate which topic based on progress
        topic_index = int(current_progress * len(topics))
        topic_index = min(topic_index, len(topics) - 1)
        
        return topics[topic_index]["name"]
    
    def generate_lesson_content(self, grade: int, subject: str, topic: str,
                               language: str, learning_style: str) -> str:
        """
        Generate lesson content
        
        Args:
            grade: Student grade
            subject: Subject name
            topic: Topic name
            language: Language code
            learning_style: Learning style (visual, auditory, kinesthetic)
        
        Returns:
            Lesson content text
        """
        logger.info(f"Generating lesson content for grade {grade}, {subject}: {topic}")
        
        # Use AI-powered content generator if available
        try:
            from content_generator import ContentGenerator
            generator = ContentGenerator(use_ai=True)
            content = generator.generate_lesson_content(
                grade=grade,
                subject=subject,
                topic=topic,
                language=language,
                learning_style=learning_style
            )
            return content
        except ImportError:
            logger.warning("ContentGenerator not available, using template-based generation")
        
        # Fallback to template-based content
        content = self._build_lesson_content(grade, subject, topic, language, learning_style)
        return content
    
    def _build_lesson_content(self, grade: int, subject: str, topic: str,
                              language: str, learning_style: str) -> str:
        """Build lesson content"""
        # Simple template-based content generation
        # In production, this would use AI to generate personalized content
        
        if language == "hi":
            content = f"""
{topic} के बारे में सीखते हैं!

आज हम {topic} के बारे में जानेंगे। यह बहुत रोचक और महत्वपूर्ण है।

मुख्य बिंदु:
1. {topic} क्या है?
2. {topic} क्यों महत्वपूर्ण है?
3. {topic} के उदाहरण
4. {topic} का उपयोग

आइए विस्तार से समझते हैं...

{topic} हमारे दैनिक जीवन में बहुत उपयोगी है। हम इसे कई जगह देख सकते हैं।

उदाहरण के लिए, जब हम {topic} के बारे में सोचते हैं, तो हमें कई चीजें याद आती हैं।

अब आप {topic} को अच्छी तरह समझ गए होंगे। अगर कोई सवाल है, तो पूछ सकते हैं!
"""
        else:
            content = f"""
Let's learn about {topic}!

Today we will learn about {topic}. This is very interesting and important.

Main points:
1. What is {topic}?
2. Why is {topic} important?
3. Examples of {topic}
4. Uses of {topic}

Let's understand in detail...

{topic} is very useful in our daily life. We can see it in many places.

For example, when we think about {topic}, we remember many things.

Now you must have understood {topic} well. If you have any questions, feel free to ask!
"""
        
        # Adjust for learning style
        if learning_style == "visual":
            content += "\n\n[Visual elements and diagrams will be shown in the video]"
        elif learning_style == "auditory":
            content += "\n\n[Listen carefully to the audio explanation]"
        elif learning_style == "kinesthetic":
            content += "\n\n[Try to practice this yourself]"
        
        return content.strip()
    
    def get_learning_objectives(self, grade: int, subject: str, topic: str) -> List[str]:
        """Get learning objectives for a topic - Uses NCERT Syllabus"""
        try:
            from syllabus_knowledge import get_learning_objectives as get_ncert_objectives
            ncert_objectives = get_ncert_objectives(grade, subject)
            if ncert_objectives:
                return ncert_objectives
        except ImportError:
            logger.debug("syllabus_knowledge not available, using fallback")
        
        # Fallback objectives
        objectives = {
            "hi": [
                f"{topic} को समझना",
                f"{topic} के उदाहरण देना",
                f"{topic} का उपयोग करना"
            ],
            "en": [
                f"Understand {topic}",
                f"Give examples of {topic}",
                f"Use {topic}"
            ]
        }
        
        return objectives.get("hi", objectives["en"])
