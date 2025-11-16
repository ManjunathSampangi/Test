"""
Interactive Q&A System
Answers student doubts in their language with human-like responses
"""

import os
import logging
from typing import Optional, Dict, List
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Install with: pip install transformers")

logger = logging.getLogger(__name__)


class QASystem:
    """
    Question-Answering system for educational content
    Provides human-like answers in student's language
    """
    
    def __init__(self, language: str = "hi", model_name: str = "gpt-3.5-turbo"):
        """
        Initialize Q&A system
        
        Args:
            language: Default language code
            model_name: Model to use for Q&A
        """
        self.language = language
        self.model_name = model_name
        self.qa_model = None
        self.translator = None
        self._initialize_models()
        
        # Context storage for better answers
        self.conversation_history = {}
    
    def _initialize_models(self):
        """Initialize Q&A and translation models"""
        # Try to initialize OpenAI if available
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                self.qa_model = "openai"
                logger.info("Using OpenAI for Q&A")
                return
        
        # Try to use local models
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use a multilingual Q&A model
                self.qa_model = pipeline(
                    "question-answering",
                    model="deepset/xlm-roberta-base-squad2",
                    device=-1  # CPU
                )
                logger.info("Using local transformer model for Q&A")
            except Exception as e:
                logger.warning(f"Could not load transformer model: {e}")
                self.qa_model = "rule_based"
        else:
            self.qa_model = "rule_based"
        
        logger.info(f"Q&A system initialized with model: {self.qa_model}")
    
    def answer_question(self, question: str, language: Optional[str] = None,
                       grade: Optional[int] = None, context: Optional[str] = None,
                       student_id: Optional[str] = None) -> str:
        """
        Answer student's question in their language
        
        Args:
            question: Student's question
            language: Language code (defaults to instance language)
            grade: Student's grade level
            context: Recent lesson context
            student_id: Student ID for conversation history
        
        Returns:
            Answer in student's language
        """
        lang = language or self.language
        
        logger.info(f"Answering question in {lang}: {question[:50]}...")
        
        # Get conversation history if available
        history = None
        if student_id and student_id in self.conversation_history:
            history = self.conversation_history[student_id]
        
        # Generate answer based on model type
        if self.qa_model == "openai":
            answer = self._answer_with_openai(question, lang, grade, context, history)
        elif isinstance(self.qa_model, pipeline):
            answer = self._answer_with_transformers(question, lang, grade, context)
        else:
            answer = self._answer_rule_based(question, lang, grade, context)
        
        # Store in conversation history
        if student_id:
            if student_id not in self.conversation_history:
                self.conversation_history[student_id] = []
            self.conversation_history[student_id].append({
                "question": question,
                "answer": answer,
                "language": lang
            })
            # Keep only last 5 exchanges
            if len(self.conversation_history[student_id]) > 5:
                self.conversation_history[student_id] = self.conversation_history[student_id][-5:]
        
        return answer
    
    def _answer_with_openai(self, question: str, language: str, grade: Optional[int],
                           context: Optional[str], history: Optional[List]) -> str:
        """Answer using OpenAI API"""
        if not OPENAI_AVAILABLE:
            return self._answer_rule_based(question, language, grade, context)
        
        # Build prompt with educational context
        system_prompt = self._build_educational_prompt(language, grade)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if history:
            for exchange in history[-3:]:  # Last 3 exchanges
                messages.append({"role": "user", "content": exchange["question"]})
                messages.append({"role": "assistant", "content": exchange["answer"]})
        
        # Add context if available
        user_prompt = question
        if context:
            user_prompt = f"Context from recent lesson: {context}\n\nStudent's question: {question}"
        
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            answer = response.choices[0].message.content.strip()
            
            # Translate if needed (OpenAI usually handles multilingual)
            if language != "en":
                answer = self._ensure_language(answer, language)
            
            return answer
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._answer_rule_based(question, language, grade, context)
    
    def _answer_with_transformers(self, question: str, language: str,
                                 grade: Optional[int], context: Optional[str]) -> str:
        """Answer using local transformer model"""
        if not isinstance(self.qa_model, pipeline):
            return self._answer_rule_based(question, language, grade, context)
        
        # Use context if available
        if context:
            try:
                result = self.qa_model(question=question, context=context)
                answer = result["answer"]
                
                # Translate to target language if needed
                if language != "en":
                    answer = self._translate_text(answer, "en", language)
                
                return self._format_answer_for_grade(answer, grade)
            except Exception as e:
                logger.error(f"Transformer Q&A error: {e}")
        
        return self._answer_rule_based(question, language, grade, context)
    
    def _answer_rule_based(self, question: str, language: str,
                          grade: Optional[int], context: Optional[str]) -> str:
        """Rule-based answer system (fallback)"""
        question_lower = question.lower()
        
        # Common educational questions and answers
        answers = {
            "hi": {
                "क्या": "हाँ, मैं आपकी मदद कर सकता हूँ!",
                "कैसे": "मैं आपको विस्तार से समझाता हूँ...",
                "क्यों": "यह एक बहुत अच्छा सवाल है!",
                "कब": "आइए इसे समझते हैं...",
                "कहाँ": "यह बहुत रोचक है...",
            },
            "en": {
                "what": "Yes, I can help you with that!",
                "how": "Let me explain this to you in detail...",
                "why": "That's a great question!",
                "when": "Let's understand this together...",
                "where": "This is very interesting...",
            }
        }
        
        # Find matching answer pattern
        lang_answers = answers.get(language, answers["en"])
        for key, answer in lang_answers.items():
            if key in question_lower:
                return self._format_answer_for_grade(answer, grade)
        
        # Generic encouraging response
        generic_responses = {
            "hi": "यह एक अच्छा सवाल है! मैं आपको इसके बारे में बताता हूँ।",
            "en": "That's a great question! Let me help you understand this."
        }
        
        response = generic_responses.get(language, generic_responses["en"])
        
        # Add context-based information if available
        if context:
            response += f"\n\n{context[:200]}"
        
        return self._format_answer_for_grade(response, grade)
    
    def _build_educational_prompt(self, language: str, grade: Optional[int]) -> str:
        """Build educational system prompt"""
        grade_info = f"for a grade {grade} student" if grade else "for a student"
        
        prompts = {
            "hi": f"""आप एक दयालु और धैर्यवान शिक्षक हैं जो {grade_info} को पढ़ा रहे हैं।
            - सरल और समझने योग्य भाषा का प्रयोग करें
            - उदाहरणों के साथ समझाएं
            - प्रोत्साहन दें और सकारात्मक रहें
            - हिंदी में जवाब दें""",
            "en": f"""You are a kind and patient teacher teaching {grade_info}.
            - Use simple and understandable language
            - Explain with examples
            - Be encouraging and positive
            - Answer in English"""
        }
        
        return prompts.get(language, prompts["en"])
    
    def _format_answer_for_grade(self, answer: str, grade: Optional[int]) -> str:
        """Format answer appropriately for grade level"""
        if grade is None:
            return answer
        
        # For lower grades, keep answers shorter and simpler
        if grade <= 3:
            # Limit length and use simpler words
            sentences = answer.split('.')[:2]
            answer = '. '.join(sentences)
            if not answer.endswith('.'):
                answer += '.'
        
        return answer
    
    def _ensure_language(self, text: str, target_language: str) -> str:
        """Ensure text is in target language (simplified)"""
        # In a real implementation, use proper translation
        # For now, return as-is (assuming model handles multilingual)
        return text
    
    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text between languages"""
        if source_lang == target_lang:
            return text
        
        # Try to use translation model if available
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use multilingual translation model
                translator = pipeline(
                    "translation",
                    model=f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}",
                    device=-1
                )
                result = translator(text)
                return result[0]["translation_text"]
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
        
        # Fallback: return original text
        return text
    
    def clear_history(self, student_id: str):
        """Clear conversation history for a student"""
        if student_id in self.conversation_history:
            del self.conversation_history[student_id]
    
    def get_suggested_questions(self, topic: str, language: str, grade: int) -> List[str]:
        """Get suggested questions students might ask"""
        suggestions = {
            "hi": [
                f"{topic} क्या है?",
                f"{topic} कैसे काम करता है?",
                f"{topic} का उदाहरण दें",
                f"{topic} क्यों महत्वपूर्ण है?",
            ],
            "en": [
                f"What is {topic}?",
                f"How does {topic} work?",
                f"Give an example of {topic}",
                f"Why is {topic} important?",
            ]
        }
        
        return suggestions.get(language, suggestions["en"])[:3]
