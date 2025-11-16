"""
AI-Powered Content Generator
Generates educational content using AI knowledge
"""

import os
import json
import logging
from typing import Dict, List, Optional
import re

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentGenerator:
    """
    AI-powered educational content generator
    Creates lessons, explanations, examples using AI knowledge
    """
    
    def __init__(self, use_ai: bool = True):
        """
        Initialize content generator
        
        Args:
            use_ai: Whether to use AI for content generation
        """
        self.use_ai = use_ai
        self.ai_model = None
        self._initialize_ai()
        
        # Knowledge base for common topics
        self.knowledge_base = self._load_knowledge_base()
    
    def _initialize_ai(self):
        """Initialize AI model for content generation"""
        if not self.use_ai:
            return
        
        # Try OpenAI first
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                self.ai_model = "openai"
                logger.info("Using OpenAI for content generation")
                return
        
        # Try local models
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use a smaller model for content generation
                self.ai_model = pipeline(
                    "text-generation",
                    model="gpt2",  # Can be upgraded to better models
                    device=-1
                )
                logger.info("Using local transformer model for content generation")
            except Exception as e:
                logger.warning(f"Could not load transformer model: {e}")
                self.ai_model = "template_based"
        else:
            self.ai_model = "template_based"
        
        logger.info(f"Content generator initialized with: {self.ai_model}")
    
    def _load_knowledge_base(self) -> Dict:
        """Load knowledge base for common educational topics"""
        return {
            "math": {
                "संख्या (Numbers)": {
                    "concept": "संख्या गिनती का एक तरीका है।",
                    "examples": ["1, 2, 3, 4, 5", "10, 20, 30"],
                    "explanation": "संख्या हमें वस्तुओं को गिनने में मदद करती है।"
                },
                "जोड़ (Addition)": {
                    "concept": "जोड़ दो या अधिक संख्याओं को मिलाना है।",
                    "examples": ["2 + 3 = 5", "10 + 5 = 15"],
                    "explanation": "जब हम दो संख्याओं को जोड़ते हैं, तो हमें उनका योग मिलता है।"
                },
                "घटाव (Subtraction)": {
                    "concept": "घटाव एक संख्या से दूसरी संख्या को हटाना है।",
                    "examples": ["5 - 2 = 3", "10 - 4 = 6"],
                    "explanation": "घटाव में हम बड़ी संख्या से छोटी संख्या को हटाते हैं।"
                },
                "गुणा (Multiplication)": {
                    "concept": "गुणा एक ही संख्या को कई बार जोड़ना है।",
                    "examples": ["2 × 3 = 6", "5 × 4 = 20"],
                    "explanation": "गुणा तेज़ी से जोड़ने का तरीका है।"
                },
                "भिन्न (Fractions)": {
                    "concept": "भिन्न एक संख्या है जो दो संख्याओं के बीच के अनुपात को दर्शाती है।",
                    "examples": ["1/2, 3/4, 2/5"],
                    "explanation": "भिन्न में ऊपर की संख्या अंश और नीचे की संख्या हर कहलाती है।"
                }
            },
            "science": {
                "पौधे (Plants)": {
                    "concept": "पौधे जीवित प्राणी हैं जो अपना भोजन स्वयं बनाते हैं।",
                    "examples": ["पेड़", "झाड़ियाँ", "फूल"],
                    "explanation": "पौधे सूर्य के प्रकाश में प्रकाश संश्लेषण करके भोजन बनाते हैं।"
                },
                "जानवर (Animals)": {
                    "concept": "जानवर जीवित प्राणी हैं जो चल-फिर सकते हैं।",
                    "examples": ["कुत्ता", "बिल्ली", "गाय"],
                    "explanation": "जानवरों को भोजन के लिए दूसरे जीवों पर निर्भर रहना पड़ता है।"
                }
            }
        }
    
    def generate_lesson_content(self, grade: int, subject: str, topic: str,
                               language: str, learning_style: str) -> str:
        """
        Generate comprehensive lesson content using AI knowledge
        
        Args:
            grade: Student grade (1-8)
            subject: Subject name
            topic: Topic name
            language: Language code
            learning_style: Learning style (visual, auditory, kinesthetic)
        
        Returns:
            Complete lesson content
        """
        logger.info(f"Generating lesson content: Grade {grade}, {subject} - {topic}")
        
        # Get knowledge about the topic
        knowledge = self._get_topic_knowledge(subject, topic, language)
        
        # Generate content using AI
        if self.ai_model == "openai":
            content = self._generate_with_openai(grade, subject, topic, language, learning_style, knowledge)
        elif isinstance(self.ai_model, pipeline):
            content = self._generate_with_transformers(grade, subject, topic, language, learning_style, knowledge)
        else:
            content = self._generate_template_based(grade, subject, topic, language, learning_style, knowledge)
        
        return content
    
    def _get_topic_knowledge(self, subject: str, topic: str, language: str) -> Dict:
        """Get knowledge about a topic"""
        # Check knowledge base
        subject_kb = self.knowledge_base.get(subject, {})
        
        # Try to find matching topic
        for kb_topic, info in subject_kb.items():
            if topic.lower() in kb_topic.lower() or kb_topic.lower() in topic.lower():
                return info
        
        # Return generic knowledge
        return {
            "concept": f"{topic} के बारे में जानना महत्वपूर्ण है।",
            "examples": [],
            "explanation": f"{topic} एक रोचक विषय है जिसे हम विस्तार से समझेंगे।"
        }
    
    def _generate_with_openai(self, grade: int, subject: str, topic: str,
                             language: str, learning_style: str, knowledge: Dict) -> str:
        """Generate content using OpenAI"""
        if not OPENAI_AVAILABLE:
            return self._generate_template_based(grade, subject, topic, language, learning_style, knowledge)
        
        # Build prompt for educational content
        lang_name = {"hi": "Hindi", "en": "English", "te": "Telugu", "ta": "Tamil"}.get(language, "Hindi")
        
        prompt = f"""You are an expert teacher teaching {subject} to a grade {grade} student in {lang_name}.

Topic: {topic}

Generate a comprehensive, engaging lesson that:
1. Explains the concept clearly and simply
2. Uses age-appropriate language for grade {grade}
3. Includes 2-3 real-world examples
4. Uses {learning_style} learning style (visual/auditory/kinesthetic)
5. Is engaging and keeps the student interested
6. Is written entirely in {lang_name}

Knowledge about topic:
- Concept: {knowledge.get('concept', '')}
- Examples: {', '.join(knowledge.get('examples', []))}
- Explanation: {knowledge.get('explanation', '')}

Generate the lesson content now:"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert teacher who creates engaging educational content for students."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            content = response.choices[0].message.content.strip()
            return content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return self._generate_template_based(grade, subject, topic, language, learning_style, knowledge)
    
    def _generate_with_transformers(self, grade: int, subject: str, topic: str,
                                   language: str, learning_style: str, knowledge: Dict) -> str:
        """Generate content using local transformers"""
        # For now, fallback to template-based
        # In production, would use fine-tuned educational models
        return self._generate_template_based(grade, subject, topic, language, learning_style, knowledge)
    
    def _generate_template_based(self, grade: int, subject: str, topic: str,
                                language: str, learning_style: str, knowledge: Dict) -> str:
        """Generate content using templates and knowledge base"""
        concept = knowledge.get("concept", f"{topic} के बारे में सीखते हैं")
        examples = knowledge.get("examples", [])
        explanation = knowledge.get("explanation", f"{topic} एक महत्वपूर्ण विषय है")
        
        if language == "hi":
            content = f"""🌟 {topic} - आज का पाठ 🌟

📚 मुख्य अवधारणा (Main Concept):
{concept}

💡 समझाइए (Explanation):
{explanation}

📝 उदाहरण (Examples):"""
            
            if examples:
                for i, example in enumerate(examples[:3], 1):
                    content += f"\n{i}. {example}"
            else:
                content += f"\n1. {topic} का एक उदाहरण यह है कि..."
            
            content += f"""

🎯 अभ्यास के लिए (For Practice):
- {topic} के बारे में सोचें
- अपने आस-पास {topic} के उदाहरण खोजें
- {topic} को समझाने की कोशिश करें

💪 याद रखें (Remember):
{topic} को समझने के लिए नियमित अभ्यास जरूरी है। अगर कोई संदेह है, तो पूछने में संकोच न करें!

🌟 बहुत बढ़िया! आपने {topic} सीख लिया है! 🌟"""
        
        else:  # English
            content = f"""🌟 {topic} - Today's Lesson 🌟

📚 Main Concept:
{concept}

💡 Explanation:
{explanation}

📝 Examples:"""
            
            if examples:
                for i, example in enumerate(examples[:3], 1):
                    content += f"\n{i}. {example}"
            else:
                content += f"\n1. An example of {topic} is..."
            
            content += f"""

🎯 For Practice:
- Think about {topic}
- Find examples of {topic} around you
- Try to explain {topic} to someone

💪 Remember:
Regular practice is important to understand {topic}. Don't hesitate to ask if you have doubts!

🌟 Excellent! You've learned about {topic}! 🌟"""
        
        # Add learning style specific content
        if learning_style == "visual":
            content += "\n\n👁️ Visual Learners: Watch the video carefully and observe the examples!"
        elif learning_style == "auditory":
            content += "\n\n👂 Auditory Learners: Listen to the audio narration carefully!"
        elif learning_style == "kinesthetic":
            content += "\n\n✋ Kinesthetic Learners: Try to practice this yourself!"
        
        return content
    
    def generate_explanation(self, question: str, topic: str, grade: int,
                            language: str, context: Optional[str] = None) -> str:
        """
        Generate explanation for a student's question
        
        Args:
            question: Student's question
            topic: Related topic
            grade: Student grade
            language: Language code
            context: Additional context
        
        Returns:
            Detailed explanation
        """
        logger.info(f"Generating explanation for: {question[:50]}...")
        
        # Get knowledge about topic
        subject = self._infer_subject(topic)
        knowledge = self._get_topic_knowledge(subject, topic, language)
        
        if self.ai_model == "openai":
            return self._explain_with_openai(question, topic, grade, language, knowledge, context)
        else:
            return self._explain_template_based(question, topic, grade, language, knowledge, context)
    
    def _explain_with_openai(self, question: str, topic: str, grade: int,
                            language: str, knowledge: Dict, context: Optional[str]) -> str:
        """Generate explanation using OpenAI"""
        if not OPENAI_AVAILABLE:
            return self._explain_template_based(question, topic, grade, language, knowledge, context)
        
        lang_name = {"hi": "Hindi", "en": "English"}.get(language, "Hindi")
        
        prompt = f"""You are a patient teacher explaining to a grade {grade} student in {lang_name}.

Student's question: {question}
Topic: {topic}

Context: {context or 'No specific context'}

Knowledge: {knowledge.get('explanation', '')}

Provide a clear, simple, encouraging explanation in {lang_name} that:
1. Directly answers the question
2. Uses simple language appropriate for grade {grade}
3. Includes an example if helpful
4. Is encouraging and positive
5. Helps the student understand

Explanation:"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a kind and patient teacher who explains concepts clearly to students."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI explanation failed: {e}")
            return self._explain_template_based(question, topic, grade, language, knowledge, context)
    
    def _explain_template_based(self, question: str, topic: str, grade: int,
                               language: str, knowledge: Dict, context: Optional[str]) -> str:
        """Generate explanation using templates"""
        explanation = knowledge.get("explanation", f"{topic} के बारे में यह एक अच्छा सवाल है।")
        examples = knowledge.get("examples", [])
        
        if language == "hi":
            answer = f"""बहुत अच्छा सवाल! आइए समझते हैं:

{explanation}"""
            
            if examples:
                answer += f"\n\nउदाहरण के लिए:\n"
                for i, example in enumerate(examples[:2], 1):
                    answer += f"{i}. {example}\n"
            
            answer += "\nअगर अभी भी कोई संदेह है, तो बताएं!"
        
        else:  # English
            answer = f"""Great question! Let's understand:

{explanation}"""
            
            if examples:
                answer += f"\n\nFor example:\n"
                for i, example in enumerate(examples[:2], 1):
                    answer += f"{i}. {example}\n"
            
            answer += "\nIf you still have doubts, please ask!"
        
        return answer
    
    def _infer_subject(self, topic: str) -> str:
        """Infer subject from topic"""
        topic_lower = topic.lower()
        
        math_keywords = ["संख्या", "जोड़", "घटाव", "गुणा", "भाग", "भिन्न", "number", "add", "subtract", "multiply", "divide"]
        science_keywords = ["पौधे", "जानवर", "शरीर", "plant", "animal", "body"]
        
        if any(kw in topic_lower for kw in math_keywords):
            return "math"
        elif any(kw in topic_lower for kw in science_keywords):
            return "science"
        else:
            return "general"
    
    def generate_examples(self, topic: str, subject: str, grade: int,
                         language: str, count: int = 3) -> List[str]:
        """Generate examples for a topic"""
        knowledge = self._get_topic_knowledge(subject, topic, language)
        examples = knowledge.get("examples", [])
        
        if len(examples) >= count:
            return examples[:count]
        
        # Generate additional examples if needed
        if language == "hi":
            additional = [
                f"{topic} का एक उदाहरण है...",
                f"हम {topic} को रोजमर्रा की जिंदगी में देख सकते हैं...",
                f"{topic} के बारे में सोचें तो..."
            ]
        else:
            additional = [
                f"An example of {topic} is...",
                f"We can see {topic} in daily life...",
                f"Think about {topic}..."
            ]
        
        return (examples + additional)[:count]
    
    def expand_knowledge_base(self, subject: str, topic: str, knowledge: Dict):
        """Add new knowledge to the knowledge base"""
        if subject not in self.knowledge_base:
            self.knowledge_base[subject] = {}
        
        self.knowledge_base[subject][topic] = knowledge
        logger.info(f"Added knowledge for {subject} - {topic}")
