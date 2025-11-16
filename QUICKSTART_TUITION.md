# Quick Start Guide - Daily Tuition Agent

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Install basic dependencies
pip install python-dotenv requests

# For voice features (choose one or more)
pip install gtts          # Google TTS (requires internet)
pip install pyttsx3       # Offline TTS (limited languages)

# For video generation
pip install moviepy pillow matplotlib numpy

# For AI features (optional)
pip install openai        # For advanced Q&A
pip install transformers  # For local AI models
```

### Step 2: Run Demo

```bash
python demo_tuition_agent.py
```

This will:
- Initialize the agent
- Register a sample student
- Create a lesson
- Show Q&A example
- Generate assessment
- Display engagement stats

### Step 3: Use Student Interface

```bash
python student_interface.py
```

Follow the prompts to:
1. Register as a new student
2. Start learning
3. Ask doubts
4. Take assessments

## 📝 Basic Usage

### Register a Student

```python
from tuition_agent import TuitionAgent

agent = TuitionAgent()
student_id = agent.register_student(
    name="Rahul",
    grade=5,
    language="hi",  # Hindi
    learning_style="visual"
)
```

### Create Daily Lesson

```python
lesson = agent.create_daily_lesson(student_id, subject="math")
print(f"Topic: {lesson.topic}")
print(f"Video: {lesson.video_path}")
print(f"Audio: {lesson.audio_path}")
```

### Answer Student Doubt

```python
answer = agent.answer_doubt(
    student_id,
    "गणित में भिन्न क्या होती है?"
)
print(answer)
```

### Conduct Assessment

```python
assessment = agent.conduct_assessment(student_id, lesson.lesson_id)
print(f"Questions: {assessment['total_questions']}")

# Student answers
answers = {"Q1": "a", "Q2": "भिन्न एक संख्या है..."}

# Evaluate
results = agent.submit_assessment(
    student_id,
    assessment['assessment_id'],
    answers
)
print(f"Score: {results['percentage']:.1f}%")
```

## ⚙️ Configuration

Edit `tuition_config.json`:

```json
{
  "default_language": "hi",
  "daily_lesson_duration": 30,
  "assessment_questions": 5
}
```

## 🌐 Supported Languages

- Hindi (hi)
- English (en)
- Telugu (te)
- Tamil (ta)
- Marathi (mr)
- Gujarati (gu)
- Bengali (bn)
- Kannada (kn)
- Malayalam (ml)
- Odia (or)

## 🎯 Features

✅ Voice narration in local languages
✅ Animated educational videos
✅ Daily assessments
✅ Interactive Q&A
✅ Progress tracking
✅ Gamification (badges, streaks)

## 📚 Next Steps

1. Read `TUITION_AGENT_README.md` for detailed documentation
2. Customize curriculum in `curriculum/curriculum.json`
3. Configure voice/video settings in `tuition_config.json`
4. Set up OpenAI API key for advanced Q&A (optional)

## 🆘 Troubleshooting

**Voice not working?**
- Install: `pip install gtts` or `pip install pyttsx3`
- Check audio device

**Video not generating?**
- Install: `pip install moviepy pillow`
- Check disk space

**Q&A not responding?**
- Set `OPENAI_API_KEY` environment variable (optional)
- System will use fallback answers

## 💡 Tips

- Start with demo to understand the system
- Use student interface for best experience
- Configure language based on student needs
- Track progress regularly
- Encourage daily learning for streaks

---

**Happy Learning! 📚✨**
