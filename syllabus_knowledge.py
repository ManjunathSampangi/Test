"""
Indian Curriculum Syllabus Knowledge Base
NCERT/CBSE Syllabus for Grades 1-8
"""

# NCERT/CBSE Syllabus Structure for Grades 1-8
NCERT_SYLLABUS = {
    1: {
        "math": {
            "name": "गणित (Mathematics)",
            "topics": [
                {
                    "name": "संख्या 1 से 100 तक",
                    "english": "Numbers 1 to 100",
                    "description": "संख्या पहचान, गिनती, संख्या लिखना",
                    "chapters": ["संख्या का परिचय", "गिनती", "संख्या लिखना", "संख्या की तुलना"]
                },
                {
                    "name": "जोड़ (Addition)",
                    "english": "Addition",
                    "description": "एक अंकीय संख्याओं का जोड़",
                    "chapters": ["जोड़ का परिचय", "जोड़ के उदाहरण", "जोड़ की समस्याएं"]
                },
                {
                    "name": "घटाव (Subtraction)",
                    "english": "Subtraction",
                    "description": "एक अंकीय संख्याओं का घटाव",
                    "chapters": ["घटाव का परिचय", "घटाव के उदाहरण"]
                },
                {
                    "name": "आकार और पैटर्न",
                    "english": "Shapes and Patterns",
                    "description": "बुनियादी आकारों की पहचान",
                    "chapters": ["वृत्त", "वर्ग", "त्रिभुज", "आयत"]
                },
                {
                    "name": "माप (Measurement)",
                    "english": "Measurement",
                    "description": "लंबाई, वजन, समय का परिचय",
                    "chapters": ["लंबाई", "वजन", "समय"]
                }
            ]
        },
        "hindi": {
            "name": "हिंदी",
            "topics": [
                {
                    "name": "वर्णमाला",
                    "english": "Alphabet",
                    "description": "हिंदी वर्णमाला का परिचय",
                    "chapters": ["स्वर", "व्यंजन", "मात्राएं"]
                },
                {
                    "name": "शब्द निर्माण",
                    "english": "Word Formation",
                    "description": "सरल शब्द बनाना",
                    "chapters": ["दो अक्षर के शब्द", "तीन अक्षर के शब्द"]
                },
                {
                    "name": "वाक्य",
                    "english": "Sentences",
                    "description": "सरल वाक्य बनाना",
                    "chapters": ["सरल वाक्य", "वाक्य पढ़ना"]
                }
            ]
        },
        "evs": {
            "name": "पर्यावरण अध्ययन",
            "topics": [
                {
                    "name": "मेरा परिवार",
                    "english": "My Family",
                    "description": "परिवार के सदस्यों की पहचान",
                    "chapters": ["परिवार", "रिश्ते"]
                },
                {
                    "name": "मेरा स्कूल",
                    "english": "My School",
                    "description": "स्कूल के बारे में जानना",
                    "chapters": ["स्कूल", "कक्षा", "दोस्त"]
                },
                {
                    "name": "खाना",
                    "english": "Food",
                    "description": "भोजन के प्रकार",
                    "chapters": ["खाना", "स्वस्थ खाना"]
                }
            ]
        }
    },
    2: {
        "math": {
            "name": "गणित",
            "topics": [
                {"name": "संख्या 1 से 1000 तक", "english": "Numbers 1 to 1000"},
                {"name": "जोड़ और घटाव", "english": "Addition and Subtraction"},
                {"name": "गुणा का परिचय", "english": "Introduction to Multiplication"},
                {"name": "आकार", "english": "Shapes"},
                {"name": "समय", "english": "Time"}
            ]
        },
        "hindi": {
            "name": "हिंदी",
            "topics": [
                {"name": "वर्णमाला का पुनरावलोकन", "english": "Alphabet Review"},
                {"name": "शब्द और वाक्य", "english": "Words and Sentences"},
                {"name": "कहानी", "english": "Stories"}
            ]
        },
        "evs": {
            "name": "पर्यावरण अध्ययन",
            "topics": [
                {"name": "परिवार और मित्र", "english": "Family and Friends"},
                {"name": "खाना और स्वास्थ्य", "english": "Food and Health"},
                {"name": "पानी", "english": "Water"}
            ]
        }
    },
    3: {
        "math": {
            "name": "गणित",
            "topics": [
                {"name": "बड़ी संख्याएं", "english": "Large Numbers"},
                {"name": "जोड़, घटाव, गुणा", "english": "Addition, Subtraction, Multiplication"},
                {"name": "भाग का परिचय", "english": "Introduction to Division"},
                {"name": "भिन्न का परिचय", "english": "Introduction to Fractions"},
                {"name": "माप", "english": "Measurement"}
            ]
        },
        "science": {
            "name": "विज्ञान",
            "topics": [
                {"name": "पौधे", "english": "Plants"},
                {"name": "जानवर", "english": "Animals"},
                {"name": "हमारा शरीर", "english": "Our Body"},
                {"name": "खाना", "english": "Food"}
            ]
        },
        "hindi": {
            "name": "हिंदी",
            "topics": [
                {"name": "व्याकरण", "english": "Grammar"},
                {"name": "कहानी और कविता", "english": "Stories and Poems"},
                {"name": "निबंध", "english": "Essays"}
            ]
        }
    },
    4: {
        "math": {
            "name": "गणित",
            "topics": [
                {"name": "संख्या प्रणाली", "english": "Number System"},
                {"name": "गुणा और भाग", "english": "Multiplication and Division"},
                {"name": "भिन्न", "english": "Fractions"},
                {"name": "दशमलव का परिचय", "english": "Introduction to Decimals"},
                {"name": "ज्यामिति", "english": "Geometry"}
            ]
        },
        "science": {
            "name": "विज्ञान",
            "topics": [
                {"name": "पौधे और जानवर", "english": "Plants and Animals"},
                {"name": "हमारा शरीर", "english": "Our Body"},
                {"name": "पदार्थ", "english": "Materials"},
                {"name": "प्रकृति", "english": "Nature"}
            ]
        }
    },
    5: {
        "math": {
            "name": "गणित",
            "topics": [
                {"name": "संख्या प्रणाली", "english": "Number System"},
                {"name": "गुणा और भाग", "english": "Multiplication and Division"},
                {"name": "भिन्न", "english": "Fractions"},
                {"name": "दशमलव", "english": "Decimals"},
                {"name": "प्रतिशत का परिचय", "english": "Introduction to Percentage"},
                {"name": "क्षेत्रफल और परिमाप", "english": "Area and Perimeter"}
            ]
        },
        "science": {
            "name": "विज्ञान",
            "topics": [
                {"name": "पौधे", "english": "Plants"},
                {"name": "जानवर", "english": "Animals"},
                {"name": "हमारा शरीर", "english": "Our Body"},
                {"name": "पदार्थ", "english": "Materials"},
                {"name": "बल और ऊर्जा", "english": "Force and Energy"}
            ]
        },
        "hindi": {
            "name": "हिंदी",
            "topics": [
                {"name": "व्याकरण", "english": "Grammar"},
                {"name": "कहानी", "english": "Stories"},
                {"name": "कविता", "english": "Poems"},
                {"name": "निबंध", "english": "Essays"}
            ]
        }
    },
    6: {
        "math": {
            "name": "गणित",
            "topics": [
                {"name": "पूर्ण संख्याएं", "english": "Whole Numbers"},
                {"name": "भिन्न", "english": "Fractions"},
                {"name": "दशमलव", "english": "Decimals"},
                {"name": "बीजगणित का परिचय", "english": "Introduction to Algebra"},
                {"name": "ज्यामिति", "english": "Geometry"},
                {"name": "आंकड़े", "english": "Data Handling"}
            ]
        },
        "science": {
            "name": "विज्ञान",
            "topics": [
                {"name": "खाद्य पदार्थ", "english": "Food"},
                {"name": "सामग्री", "english": "Materials"},
                {"name": "पौधे", "english": "Plants"},
                {"name": "शरीर और गति", "english": "Body and Motion"},
                {"name": "प्रकाश", "english": "Light"}
            ]
        }
    },
    7: {
        "math": {
            "name": "गणित",
            "topics": [
                {"name": "पूर्णांक", "english": "Integers"},
                {"name": "भिन्न और दशमलव", "english": "Fractions and Decimals"},
                {"name": "बीजगणित", "english": "Algebra"},
                {"name": "ज्यामिति", "english": "Geometry"},
                {"name": "आंकड़े", "english": "Data Handling"},
                {"name": "प्रतिशत", "english": "Percentage"}
            ]
        },
        "science": {
            "name": "विज्ञान",
            "topics": [
                {"name": "पोषण", "english": "Nutrition"},
                {"name": "श्वसन", "english": "Respiration"},
                {"name": "परिवहन", "english": "Transportation"},
                {"name": "प्रजनन", "english": "Reproduction"},
                {"name": "प्रकाश", "english": "Light"},
                {"name": "बिजली", "english": "Electricity"}
            ]
        }
    },
    8: {
        "math": {
            "name": "गणित",
            "topics": [
                {"name": "परिमेय संख्याएं", "english": "Rational Numbers"},
                {"name": "बीजगणित", "english": "Algebra"},
                {"name": "ज्यामिति", "english": "Geometry"},
                {"name": "मेंसुरेशन", "english": "Mensuration"},
                {"name": "आंकड़े", "english": "Data Handling"},
                {"name": "वर्ग और वर्गमूल", "english": "Squares and Square Roots"}
            ]
        },
        "science": {
            "name": "विज्ञान",
            "topics": [
                {"name": "फसल उत्पादन", "english": "Crop Production"},
                {"name": "सूक्ष्मजीव", "english": "Microorganisms"},
                {"name": "सामग्री", "english": "Materials"},
                {"name": "दबाव", "english": "Pressure"},
                {"name": "ध्वनि", "english": "Sound"},
                {"name": "प्रकाश", "english": "Light"}
            ]
        }
    }
}

# Learning Objectives by Grade and Subject
LEARNING_OBJECTIVES = {
    "math": {
        1: ["संख्या पहचान", "गिनती", "सरल जोड़-घटाव", "आकार पहचान"],
        2: ["बड़ी संख्याएं", "जोड़-घटाव", "गुणा का परिचय"],
        3: ["गुणा-भाग", "भिन्न का परिचय", "माप"],
        4: ["गुणा-भाग", "भिन्न", "दशमलव"],
        5: ["भिन्न और दशमलव", "क्षेत्रफल", "प्रतिशत"],
        6: ["बीजगणित", "ज्यामिति", "आंकड़े"],
        7: ["पूर्णांक", "बीजगणित", "ज्यामिति"],
        8: ["परिमेय संख्याएं", "बीजगणित", "मेंसुरेशन"]
    },
    "science": {
        3: ["पौधे और जानवर", "शरीर", "खाना"],
        4: ["पौधे", "जानवर", "पदार्थ"],
        5: ["पौधे", "जानवर", "बल और ऊर्जा"],
        6: ["खाद्य पदार्थ", "सामग्री", "प्रकाश"],
        7: ["पोषण", "श्वसन", "प्रकाश"],
        8: ["सूक्ष्मजीव", "दबाव", "ध्वनि"]
    }
}

# NCERT Textbook References
NCERT_TEXTBOOKS = {
    "math": {
        1: "Math-Magic Class 1",
        2: "Math-Magic Class 2",
        3: "Math-Magic Class 3",
        4: "Math-Magic Class 4",
        5: "Math-Magic Class 5",
        6: "Mathematics Class 6",
        7: "Mathematics Class 7",
        8: "Mathematics Class 8"
    },
    "science": {
        3: "Looking Around Class 3",
        4: "Looking Around Class 4",
        5: "Looking Around Class 5",
        6: "Science Class 6",
        7: "Science Class 7",
        8: "Science Class 8"
    },
    "hindi": {
        1: "रिमझिम Class 1",
        2: "रिमझिम Class 2",
        3: "रिमझिम Class 3",
        4: "रिमझिम Class 4",
        5: "रिमझिम Class 5"
    }
}


def get_syllabus_for_grade(grade: int, subject: str = None) -> dict:
    """
    Get syllabus for a specific grade and optionally subject
    
    Args:
        grade: Grade level (1-8)
        subject: Subject name (optional)
    
    Returns:
        Syllabus dictionary
    """
    if grade not in NCERT_SYLLABUS:
        return {}
    
    grade_syllabus = NCERT_SYLLABUS[grade]
    
    if subject:
        return grade_syllabus.get(subject, {})
    
    return grade_syllabus


def get_topics_for_subject(grade: int, subject: str) -> list:
    """Get list of topics for a subject in a grade"""
    syllabus = get_syllabus_for_grade(grade, subject)
    return syllabus.get("topics", [])


def get_learning_objectives(grade: int, subject: str) -> list:
    """Get learning objectives for a grade and subject"""
    return LEARNING_OBJECTIVES.get(subject, {}).get(grade, [])


def get_textbook_reference(grade: int, subject: str) -> str:
    """Get NCERT textbook reference"""
    return NCERT_TEXTBOOKS.get(subject, {}).get(grade, "Standard Textbook")


def validate_topic(grade: int, subject: str, topic: str) -> bool:
    """Validate if a topic is part of the syllabus"""
    topics = get_topics_for_subject(grade, subject)
    topic_names = [t.get("name", "") for t in topics]
    return any(topic.lower() in name.lower() or name.lower() in topic.lower() 
               for name in topic_names)


def get_next_topic_in_syllabus(grade: int, subject: str, current_topic: str = None) -> dict:
    """Get next topic in syllabus sequence"""
    topics = get_topics_for_subject(grade, subject)
    
    if not topics:
        return {}
    
    if current_topic:
        # Find current topic index
        for i, topic in enumerate(topics):
            if current_topic.lower() in topic.get("name", "").lower():
                if i + 1 < len(topics):
                    return topics[i + 1]
                return {}  # Last topic
    
    # Return first topic
    return topics[0] if topics else {}


def get_syllabus_progress(grade: int, subject: str, completed_topics: list) -> dict:
    """Calculate syllabus completion progress"""
    all_topics = get_topics_for_subject(grade, subject)
    total_topics = len(all_topics)
    completed_count = len(completed_topics)
    
    progress_percentage = (completed_count / total_topics * 100) if total_topics > 0 else 0
    
    return {
        "total_topics": total_topics,
        "completed_topics": completed_count,
        "remaining_topics": total_topics - completed_count,
        "progress_percentage": progress_percentage,
        "all_topics": [t.get("name") for t in all_topics],
        "completed": completed_topics
    }


# Example usage
if __name__ == "__main__":
    # Get syllabus for Grade 5 Math
    print("Grade 5 Math Syllabus:")
    print(get_syllabus_for_grade(5, "math"))
    
    # Get topics
    print("\nTopics:")
    topics = get_topics_for_subject(5, "math")
    for topic in topics:
        print(f"- {topic['name']} ({topic['english']})")
    
    # Get learning objectives
    print("\nLearning Objectives:")
    print(get_learning_objectives(5, "math"))
    
    # Validate topic
    print("\nIs 'भिन्न' in Grade 5 Math syllabus?")
    print(validate_topic(5, "math", "भिन्न"))
