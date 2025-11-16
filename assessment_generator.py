"""
Assessment Generator
Creates daily assessments with adaptive questions
"""

import os
import logging
from typing import Dict, List, Optional
import json
import random

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class AssessmentGenerator:
    """
    Generates adaptive assessments for daily lessons
    Creates engaging questions appropriate for grade level
    """
    
    def __init__(self, grade_range: tuple = (1, 8),
                 question_types: List[str] = None):
        """
        Initialize assessment generator
        
        Args:
            grade_range: Tuple of (min_grade, max_grade)
            question_types: List of question types to use
        """
        self.grade_range = grade_range
        self.question_types = question_types or ["mcq", "short", "interactive"]
        
        # Question templates by grade
        self.question_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load question templates"""
        return {
            "mcq": {
                "hi": {
                    "easy": "{question}\n(a) {option1}\n(b) {option2}\n(c) {option3}\n(d) {option4}",
                    "medium": "निम्नलिखित में से सही उत्तर चुनें:\n{question}\n(a) {option1}\n(b) {option2}\n(c) {option3}\n(d) {option4}",
                    "hard": "सावधानी से सोचकर उत्तर दें:\n{question}\n(a) {option1}\n(b) {option2}\n(c) {option3}\n(d) {option4}"
                },
                "en": {
                    "easy": "{question}\n(a) {option1}\n(b) {option2}\n(c) {option3}\n(d) {option4}",
                    "medium": "Choose the correct answer:\n{question}\n(a) {option1}\n(b) {option2}\n(c) {option3}\n(d) {option4}",
                    "hard": "Think carefully and answer:\n{question}\n(a) {option1}\n(b) {option2}\n(c) {option3}\n(d) {option4}"
                }
            },
            "short": {
                "hi": {
                    "easy": "संक्षेप में उत्तर दें: {question}",
                    "medium": "विस्तार से उत्तर दें: {question}",
                    "hard": "विस्तृत उत्तर लिखें: {question}"
                },
                "en": {
                    "easy": "Answer briefly: {question}",
                    "medium": "Answer in detail: {question}",
                    "hard": "Write a detailed answer: {question}"
                }
            }
        }
    
    def generate_assessment(self, lesson_content: str, topic: str, grade: int,
                           language: str, num_questions: int = 5) -> Dict:
        """
        Generate assessment questions
        
        Args:
            lesson_content: Content of the lesson
            topic: Lesson topic
            grade: Student grade
            language: Language code
            num_questions: Number of questions to generate
        
        Returns:
            Assessment dictionary with questions
        """
        logger.info(f"Generating assessment for grade {grade}, topic: {topic}")
        
        # Determine difficulty distribution
        difficulty_dist = self._get_difficulty_distribution(grade, num_questions)
        
        questions = []
        question_ids = []
        
        for i, (q_type, difficulty) in enumerate(difficulty_dist):
            question = self._generate_question(
                lesson_content=lesson_content,
                topic=topic,
                grade=grade,
                language=language,
                question_type=q_type,
                difficulty=difficulty,
                question_num=i + 1
            )
            
            if question:
                q_id = f"Q{i+1}"
                question["question_id"] = q_id
                question["question_number"] = i + 1
                questions.append(question)
                question_ids.append(q_id)
        
        assessment = {
            "topic": topic,
            "grade": grade,
            "language": language,
            "questions": questions,
            "total_questions": len(questions),
            "question_ids": question_ids,
            "time_limit_minutes": self._calculate_time_limit(grade, len(questions))
        }
        
        return assessment
    
    def _get_difficulty_distribution(self, grade: int, num_questions: int) -> List[tuple]:
        """Get distribution of question types and difficulties"""
        # For lower grades, more easy questions
        if grade <= 3:
            easy_ratio = 0.6
            medium_ratio = 0.3
            hard_ratio = 0.1
        elif grade <= 5:
            easy_ratio = 0.4
            medium_ratio = 0.4
            hard_ratio = 0.2
        else:
            easy_ratio = 0.3
            medium_ratio = 0.4
            hard_ratio = 0.3
        
        num_easy = max(1, int(num_questions * easy_ratio))
        num_medium = max(1, int(num_questions * medium_ratio))
        num_hard = num_questions - num_easy - num_medium
        
        distribution = []
        
        # Add easy questions
        for _ in range(num_easy):
            q_type = random.choice(["mcq", "short"])
            distribution.append((q_type, "easy"))
        
        # Add medium questions
        for _ in range(num_medium):
            q_type = random.choice(["mcq", "short"])
            distribution.append((q_type, "medium"))
        
        # Add hard questions
        for _ in range(num_hard):
            q_type = random.choice(["mcq", "short"])
            distribution.append((q_type, "hard"))
        
        random.shuffle(distribution)
        return distribution
    
    def _generate_question(self, lesson_content: str, topic: str, grade: int,
                          language: str, question_type: str, difficulty: str,
                          question_num: int) -> Optional[Dict]:
        """Generate a single question"""
        try:
            if question_type == "mcq":
                return self._generate_mcq(lesson_content, topic, grade, language, difficulty, question_num)
            elif question_type == "short":
                return self._generate_short_answer(lesson_content, topic, grade, language, difficulty, question_num)
            elif question_type == "interactive":
                return self._generate_interactive(lesson_content, topic, grade, language, difficulty, question_num)
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            return None
    
    def _generate_mcq(self, content: str, topic: str, grade: int, language: str,
                      difficulty: str, question_num: int) -> Dict:
        """Generate multiple choice question"""
        # Extract key concepts from content
        key_concepts = self._extract_key_concepts(content, topic)
        
        if not key_concepts:
            # Fallback question
            question_text = self._get_fallback_question(topic, language, difficulty)
            options = self._generate_options(question_text, topic, language, difficulty)
        else:
            # Generate question based on key concept
            concept = random.choice(key_concepts)
            question_text = self._create_mcq_question(concept, topic, language, difficulty, grade)
            options = self._generate_options_for_concept(concept, topic, language, difficulty)
        
        correct_answer = options[0]  # First option is correct
        
        # Shuffle options
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return {
            "type": "mcq",
            "question": question_text,
            "options": options,
            "correct_answer": chr(97 + correct_index),  # a, b, c, d
            "correct_answer_text": correct_answer,
            "difficulty": difficulty,
            "points": self._get_points(difficulty)
        }
    
    def _generate_short_answer(self, content: str, topic: str, grade: int,
                               language: str, difficulty: str, question_num: int) -> Dict:
        """Generate short answer question"""
        key_concepts = self._extract_key_concepts(content, topic)
        
        if key_concepts:
            concept = random.choice(key_concepts)
            question_text = self._create_short_question(concept, topic, language, difficulty, grade)
        else:
            question_text = self._get_fallback_question(topic, language, difficulty, "short")
        
        # Generate sample answer
        sample_answer = self._generate_sample_answer(question_text, content, language, difficulty, grade)
        
        return {
            "type": "short",
            "question": question_text,
            "sample_answer": sample_answer,
            "difficulty": difficulty,
            "points": self._get_points(difficulty),
            "keywords": self._extract_keywords(sample_answer)
        }
    
    def _generate_interactive(self, content: str, topic: str, grade: int,
                             language: str, difficulty: str, question_num: int) -> Dict:
        """Generate interactive question (drag-drop, matching, etc.)"""
        # Simplified interactive question
        return {
            "type": "interactive",
            "question": f"Match the following related to {topic}",
            "difficulty": difficulty,
            "points": self._get_points(difficulty)
        }
    
    def _extract_key_concepts(self, content: str, topic: str) -> List[str]:
        """Extract key concepts from lesson content"""
        # Simple keyword extraction
        sentences = content.split('.')[:10]  # First 10 sentences
        concepts = []
        
        for sentence in sentences:
            if topic.lower() in sentence.lower():
                # Extract important phrases
                words = sentence.split()[:5]
                if words:
                    concepts.append(' '.join(words))
        
        return concepts[:5] if concepts else [topic]
    
    def _create_mcq_question(self, concept: str, topic: str, language: str,
                            difficulty: str, grade: int) -> str:
        """Create MCQ question text"""
        templates = {
            "hi": {
                "easy": f"{topic} से संबंधित {concept} क्या है?",
                "medium": f"{topic} में {concept} का क्या महत्व है?",
                "hard": f"{topic} के संदर्भ में {concept} कैसे काम करता है?"
            },
            "en": {
                "easy": f"What is {concept} related to {topic}?",
                "medium": f"What is the importance of {concept} in {topic}?",
                "hard": f"How does {concept} work in the context of {topic}?"
            }
        }
        
        return templates.get(language, templates["en"]).get(difficulty, templates["en"]["medium"])
    
    def _create_short_question(self, concept: str, topic: str, language: str,
                              difficulty: str, grade: int) -> str:
        """Create short answer question text"""
        templates = {
            "hi": {
                "easy": f"{topic} के बारे में बताएं।",
                "medium": f"{topic} में {concept} को समझाएं।",
                "hard": f"{topic} में {concept} का विस्तृत विवरण दें।"
            },
            "en": {
                "easy": f"Tell me about {topic}.",
                "medium": f"Explain {concept} in {topic}.",
                "hard": f"Provide a detailed description of {concept} in {topic}."
            }
        }
        
        return templates.get(language, templates["en"]).get(difficulty, templates["en"]["medium"])
    
    def _generate_options(self, question: str, topic: str, language: str,
                         difficulty: str) -> List[str]:
        """Generate options for MCQ"""
        # Generate plausible options
        correct = self._get_correct_option(topic, language)
        incorrect = self._get_incorrect_options(topic, language, 3)
        
        options = [correct] + incorrect
        return options
    
    def _generate_options_for_concept(self, concept: str, topic: str,
                                      language: str, difficulty: str) -> List[str]:
        """Generate options for a specific concept"""
        correct = f"{concept} {topic} से संबंधित है" if language == "hi" else f"{concept} is related to {topic}"
        incorrect = [
            f"{concept} {topic} से अलग है" if language == "hi" else f"{concept} is different from {topic}",
            f"{concept} का कोई संबंध नहीं है" if language == "hi" else f"{concept} has no relation",
            f"{concept} गलत है" if language == "hi" else f"{concept} is incorrect"
        ]
        
        return [correct] + incorrect
    
    def _get_correct_option(self, topic: str, language: str) -> str:
        """Get correct answer option"""
        if language == "hi":
            return f"{topic} का सही उत्तर"
        return f"Correct answer about {topic}"
    
    def _get_incorrect_options(self, topic: str, language: str, count: int) -> List[str]:
        """Generate incorrect distractors"""
        if language == "hi":
            return [
                f"{topic} का गलत उत्तर 1",
                f"{topic} का गलत उत्तर 2",
                f"{topic} का गलत उत्तर 3"
            ][:count]
        return [
            f"Incorrect option 1 about {topic}",
            f"Incorrect option 2 about {topic}",
            f"Incorrect option 3 about {topic}"
        ][:count]
    
    def _get_fallback_question(self, topic: str, language: str,
                              difficulty: str, q_type: str = "mcq") -> str:
        """Get fallback question when content analysis fails"""
        if q_type == "mcq":
            if language == "hi":
                return f"{topic} के बारे में आप क्या जानते हैं?"
            return f"What do you know about {topic}?"
        else:
            if language == "hi":
                return f"{topic} को समझाएं।"
            return f"Explain {topic}."
    
    def _generate_sample_answer(self, question: str, content: str,
                               language: str, difficulty: str, grade: int) -> str:
        """Generate sample answer for short answer questions"""
        # Extract relevant sentences from content
        sentences = content.split('.')[:3]
        answer = '. '.join(sentences)
        
        if len(answer) > 200:
            answer = answer[:200] + "..."
        
        return answer
    
    def _extract_keywords(self, answer: str) -> List[str]:
        """Extract keywords from answer for evaluation"""
        # Simple keyword extraction
        words = answer.lower().split()
        # Filter out common words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "but"}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return keywords[:5]
    
    def _get_points(self, difficulty: str) -> int:
        """Get points for question based on difficulty"""
        return {"easy": 1, "medium": 2, "hard": 3}[difficulty]
    
    def _calculate_time_limit(self, grade: int, num_questions: int) -> int:
        """Calculate time limit for assessment"""
        base_time = {1: 2, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 5}.get(grade, 3)
        return base_time * num_questions
    
    def evaluate_answers(self, assessment: Dict, answers: Dict[str, str],
                        language: str) -> Dict:
        """
        Evaluate student answers
        
        Args:
            assessment: Assessment dictionary
            answers: Dictionary of question_id -> answer
            language: Language code
        
        Returns:
            Evaluation results
        """
        total_points = 0
        earned_points = 0
        correct_answers = 0
        total_questions = len(assessment["questions"])
        
        detailed_results = []
        
        for question in assessment["questions"]:
            q_id = question["question_id"]
            student_answer = answers.get(q_id, "").strip().lower()
            points = question["points"]
            total_points += points
            
            is_correct = False
            feedback = ""
            
            if question["type"] == "mcq":
                correct_option = question["correct_answer"]
                if student_answer == correct_option.lower():
                    is_correct = True
                    earned_points += points
                    correct_answers += 1
                    feedback = "सही उत्तर!" if language == "hi" else "Correct!"
                else:
                    feedback = f"सही उत्तर है: {correct_option}" if language == "hi" else f"Correct answer is: {correct_option}"
            
            elif question["type"] == "short":
                # Keyword-based evaluation
                keywords = question.get("keywords", [])
                student_words = student_answer.split()
                matches = sum(1 for kw in keywords if kw.lower() in student_answer)
                
                if matches >= len(keywords) * 0.5:  # At least 50% keywords match
                    is_correct = True
                    earned_points += points
                    correct_answers += 1
                    feedback = "अच्छा उत्तर!" if language == "hi" else "Good answer!"
                else:
                    feedback = "आपको और अध्ययन करना चाहिए" if language == "hi" else "You should study more"
            
            detailed_results.append({
                "question_id": q_id,
                "question": question["question"],
                "student_answer": answers.get(q_id, ""),
                "correct": is_correct,
                "points_earned": points if is_correct else 0,
                "feedback": feedback
            })
        
        score = earned_points / total_points if total_points > 0 else 0
        percentage = score * 100
        
        # Generate overall feedback
        if percentage >= 80:
            overall_feedback = "बहुत बढ़िया! आपने बहुत अच्छा किया!" if language == "hi" else "Excellent! You did very well!"
        elif percentage >= 60:
            overall_feedback = "अच्छा काम! थोड़ा और अभ्यास करें।" if language == "hi" else "Good work! Practice a bit more."
        else:
            overall_feedback = "कोशिश जारी रखें! आप बेहतर कर सकते हैं।" if language == "hi" else "Keep trying! You can do better."
        
        return {
            "score": score,
            "percentage": percentage,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "total_points": total_points,
            "earned_points": earned_points,
            "overall_feedback": overall_feedback,
            "detailed_results": detailed_results
        }
