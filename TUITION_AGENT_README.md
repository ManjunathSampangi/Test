# Daily Tuition Agent for Village Students (Grades 1-8)

An intelligent, multilingual educational agent designed specifically for village students in India. The agent provides personalized daily tuition with voice narration, animated videos, interactive assessments, and doubt-solving capabilities in local languages.

## 🌟 Features

### Core Capabilities
- **Voice-Based Teaching**: Natural text-to-speech in multiple Indian languages (Hindi, English, Telugu, Tamil, Marathi, Gujarati, Bengali, Kannada, Malayalam, Odia)
- **Animated Video Lessons**: Engaging cartoon-style animated videos for visual learning
- **Daily Assessments**: Adaptive assessments with MCQ and short-answer questions
- **Interactive Q&A**: Human-like doubt solving in student's native language
- **Progress Tracking**: Comprehensive progress monitoring across subjects
- **Gamification**: Badge system, streaks, and engagement tracking to keep students motivated

### Key Highlights
- ✅ **Multilingual Support**: Teaches in 10+ Indian languages
- ✅ **Grade-Appropriate Content**: Curriculum for grades 1-8
- ✅ **Adaptive Learning**: Adjusts difficulty based on student progress
- ✅ **Engagement Focus**: Prevents boredom with interactive elements
- ✅ **Offline Capable**: Can work with limited internet connectivity
- ✅ **Village-Friendly**: Simple interface, low resource requirements

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- Internet connection (for AI features, optional for basic mode)
- Audio output device (speakers/headphones)
- Video player (for watching lesson videos)

### Python Dependencies
Install all dependencies:
```bash
pip install -r tuition_requirements.txt
```

### Optional Dependencies
- **OpenAI API Key** (for advanced Q&A): Set `OPENAI_API_KEY` environment variable
- **GPU** (optional): For faster video generation and AI processing

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd /workspace

# Install dependencies
pip install -r tuition_requirements.txt
```

### 2. Configuration

Edit `tuition_config.json` to customize:
- Default language
- Voice style
- Animation style
- Assessment settings
- Subject preferences

### 3. Run the Agent

#### Option A: Using Student Interface (Recommended)
```bash
python student_interface.py
```

This provides an interactive CLI interface where students can:
- Register/Login
- Start daily lessons
- Ask doubts
- Take assessments
- View progress and badges

#### Option B: Using Python API
```python
from tuition_agent import TuitionAgent

# Initialize agent
agent = TuitionAgent()

# Register a student
student_id = agent.register_student(
    name="Rahul",
    grade=5,
    language="hi",
    learning_style="visual"
)

# Run daily session
session = agent.run_daily_session(student_id)
print(f"Lesson: {session['lesson']['topic']}")
print(f"Assessment: {session['assessment']['questions']} questions")
```

## 📚 Usage Guide

### For Students

1. **First Time Setup**
   - Run `python student_interface.py`
   - Choose "नया छात्र" (New Student)
   - Enter name, grade (1-8), language, and learning style
   - Save your Student ID

2. **Daily Learning**
   - Login with your Student ID
   - Select "आज का पाठ शुरू करें" (Start Today's Lesson)
   - Watch video and listen to audio
   - Complete the assessment
   - Ask any doubts using "कोई संदेह पूछें"

3. **Track Progress**
   - View progress: "मेरी प्रगति देखें"
   - Check badges: "मेरे बैज देखें"
   - Get suggestions: "सुझाव प्राप्त करें"

### For Teachers/Administrators

#### Register Multiple Students
```python
from tuition_agent import TuitionAgent

agent = TuitionAgent()

students = [
    {"name": "Rahul", "grade": 5, "language": "hi"},
    {"name": "Priya", "grade": 3, "language": "te"},
    {"name": "Amit", "grade": 7, "language": "en"}
]

for student in students:
    student_id = agent.register_student(**student)
    print(f"Registered: {student['name']} - ID: {student_id}")
```

#### Generate Lesson for Specific Topic
```python
lesson = agent.create_daily_lesson(
    student_id="STU_20240101120000",
    subject="math"
)
print(f"Video: {lesson.video_path}")
print(f"Audio: {lesson.audio_path}")
```

#### Answer Student Doubt
```python
answer = agent.answer_doubt(
    student_id="STU_20240101120000",
    question="गणित में भिन्न क्या होती है?"
)
print(answer)
```

## 🏗️ Architecture

### Core Modules

1. **tuition_agent.py**: Main orchestrator
   - Manages student profiles
   - Coordinates all components
   - Handles daily sessions

2. **voice_synthesizer.py**: Text-to-Speech
   - Multi-language TTS
   - Supports gTTS, pyttsx3, Coqui TTS
   - Emotional voice synthesis

3. **video_generator.py**: Animated Video Creation
   - Creates educational videos
   - Scene-based animation
   - Grade-appropriate visuals

4. **qa_system.py**: Question Answering
   - Doubt resolution
   - Context-aware answers
   - Multilingual support

5. **assessment_generator.py**: Assessment Creation
   - Adaptive question generation
   - Multiple question types
   - Automatic evaluation

6. **engagement_tracker.py**: Engagement Monitoring
   - Tracks student engagement
   - Badge system
   - Streak tracking
   - Motivational messages

7. **curriculum_manager.py**: Curriculum Management
   - Grade-wise curriculum
   - Subject-wise topics
   - Learning objectives

### Data Structure

```
/workspace/
├── students/              # Student profiles
│   └── STU_*.json
├── lessons/               # Generated lessons
│   ├── LESSON_*.json
│   ├── LESSON_*_audio.mp3
│   └── LESSON_*_video.mp4
├── assessments/           # Assessments and results
│   ├── ASSESS_*.json
│   └── ASSESS_*_results.json
├── engagement_data/       # Engagement tracking
│   └── STU_*.json
└── curriculum/            # Curriculum data
    └── curriculum.json
```

## 🎯 Features in Detail

### Voice Synthesis
- **Languages**: Hindi, English, Telugu, Tamil, Marathi, Gujarati, Bengali, Kannada, Malayalam, Odia
- **Engines**: Google TTS (online), pyttsx3 (offline), Coqui TTS (high quality)
- **Features**: Slow speech mode, emotional tones, friendly voice style

### Video Generation
- **Style**: Cartoon animations (engaging for children)
- **Quality**: Adjustable (low/medium/high)
- **Features**: Scene-based content, grade-appropriate visuals, subtitles support

### Q&A System
- **Models**: OpenAI GPT (if API key available), Local transformers, Rule-based fallback
- **Features**: Context-aware answers, conversation history, grade-appropriate language
- **Languages**: All supported Indian languages

### Assessment System
- **Question Types**: MCQ, Short Answer, Interactive
- **Adaptive**: Difficulty adjusts based on grade and progress
- **Evaluation**: Automatic scoring with detailed feedback
- **Feedback**: Encouraging messages in student's language

### Engagement System
- **Badges**: First Lesson, Week Warrior, Perfect Score, Doubt Solver, Consistent Learner
- **Streaks**: Daily learning streak tracking
- **Metrics**: Engagement score based on multiple factors
- **Suggestions**: Personalized learning suggestions

## 🔧 Configuration

### tuition_config.json

```json
{
  "default_language": "hi",
  "supported_languages": ["hi", "en", "te", "ta", "mr", "gu", "bn", "kn", "ml", "or"],
  "voice_style": "friendly",
  "animation_style": "cartoon",
  "video_quality": "medium",
  "daily_lesson_duration": 30,
  "assessment_questions": 5,
  "engagement_threshold": 0.7
}
```

### Environment Variables

```bash
# Optional: For advanced AI features
export OPENAI_API_KEY="your-api-key-here"
```

## 📊 Student Progress Tracking

The system tracks:
- **Subject-wise Progress**: Completion percentage per subject
- **Engagement Score**: 0.0 to 1.0 based on interactions
- **Learning Streak**: Consecutive days of learning
- **Badges Earned**: Achievement badges
- **Assessment Scores**: Performance in assessments
- **Doubt Frequency**: Questions asked

## 🎮 Gamification

### Badges
- **पहला पाठ (First Lesson)**: Complete first lesson
- **सप्ताह योद्धा (Week Warrior)**: 7-day learning streak
- **पूर्ण अंक (Perfect Score)**: Score 100% in assessment
- **संदेह समाधानकर्ता (Doubt Solver)**: Ask 10+ doubts
- **निरंतर शिक्षार्थी (Consistent Learner)**: 14-day streak

### Engagement Features
- Daily streak tracking
- Motivational messages
- Progress visualization
- Learning suggestions

## 🌐 Language Support

### Fully Supported Languages
- Hindi (हिंदी)
- English
- Telugu (తెలుగు)
- Tamil (தமிழ்)
- Marathi (मराठी)
- Gujarati (ગુજરાતી)
- Bengali (বাংলা)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)
- Odia (ଓଡ଼ିଆ)

## 🐛 Troubleshooting

### Voice Not Working
- Check audio output device
- Install TTS dependencies: `pip install gtts pyttsx3`
- For offline: Use pyttsx3 (may have limited language support)

### Video Not Generating
- Install moviepy: `pip install moviepy pillow`
- Check disk space
- Verify video codec support

### Q&A Not Responding
- Check internet connection (for OpenAI)
- Verify API key if using OpenAI
- System will fallback to rule-based answers

### Assessment Issues
- Ensure lesson is completed first
- Check lesson_id is correct
- Verify assessment file exists

## 🔒 Privacy & Data

- All student data stored locally
- No data sent to external servers (except optional OpenAI API)
- Student profiles can be exported/deleted
- Compliant with educational data privacy

## 🚀 Future Enhancements

- [ ] Web interface for better accessibility
- [ ] Mobile app for Android/iOS
- [ ] Offline mode with pre-downloaded content
- [ ] Parent/Teacher dashboard
- [ ] Advanced AI content generation
- [ ] Multi-student classroom mode
- [ ] Integration with school curriculum
- [ ] Performance analytics

## 📝 License

This project is provided as-is for educational purposes, specifically designed to help village students in India access quality education.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional language support
- More video animation styles
- Enhanced assessment types
- Better offline capabilities
- Performance optimizations

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review logs in `tuition_agent.log`
3. Verify configuration in `tuition_config.json`

## 🙏 Acknowledgments

Built with care for village students in India, aiming to bridge the educational gap through technology.

---

**Made with ❤️ for Village Students**
