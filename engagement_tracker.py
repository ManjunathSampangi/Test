"""
Engagement Tracker
Tracks student engagement and provides gamification
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class EngagementTracker:
    """
    Tracks student engagement and provides gamification elements
    Prevents boredom and maintains interest
    """
    
    def __init__(self):
        """Initialize engagement tracker"""
        self.engagement_data_dir = Path("engagement_data")
        self.engagement_data_dir.mkdir(exist_ok=True)
        
        # Engagement metrics
        self.metrics = {
            "lesson_completion": 0.3,
            "assessment_score": 0.3,
            "interaction_frequency": 0.2,
            "time_spent": 0.2
        }
        
        # Gamification elements
        self.badges = self._initialize_badges()
        self.streaks = {}  # student_id -> streak_count
    
    def _initialize_badges(self) -> Dict:
        """Initialize badge system"""
        return {
            "first_lesson": {"name": "पहला पाठ", "en_name": "First Lesson", "threshold": 1},
            "week_warrior": {"name": "सप्ताह योद्धा", "en_name": "Week Warrior", "threshold": 7},
            "perfect_score": {"name": "पूर्ण अंक", "en_name": "Perfect Score", "threshold": 100},
            "doubt_solver": {"name": "संदेह समाधानकर्ता", "en_name": "Doubt Solver", "threshold": 10},
            "consistent_learner": {"name": "निरंतर शिक्षार्थी", "en_name": "Consistent Learner", "threshold": 14}
        }
    
    def record_interaction(self, student_id: str, interaction_type: str, 
                          metadata: Optional[Dict] = None):
        """
        Record student interaction
        
        Args:
            student_id: Student identifier
            interaction_type: Type of interaction (lesson_completed, assessment_completed, doubt_asked, etc.)
            metadata: Additional metadata
        """
        data_file = self.engagement_data_dir / f"{student_id}.json"
        
        # Load existing data
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "student_id": student_id,
                "interactions": [],
                "engagement_score": 0.0,
                "badges_earned": [],
                "current_streak": 0,
                "longest_streak": 0,
                "total_lessons": 0,
                "total_assessments": 0,
                "total_doubts": 0
            }
        
        # Record interaction
        interaction = {
            "type": interaction_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        data["interactions"].append(interaction)
        
        # Update counters
        if interaction_type == "lesson_completed":
            data["total_lessons"] = data.get("total_lessons", 0) + 1
            self._update_streak(student_id, data)
        elif interaction_type == "assessment_completed":
            data["total_assessments"] = data.get("total_assessments", 0) + 1
        elif interaction_type == "doubt_asked":
            data["total_doubts"] = data.get("total_doubts", 0) + 1
        
        # Check for badges
        new_badges = self._check_badges(data)
        if new_badges:
            data["badges_earned"].extend(new_badges)
            logger.info(f"Student {student_id} earned badges: {new_badges}")
        
        # Save data
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _update_streak(self, student_id: str, data: Dict):
        """Update learning streak"""
        today = datetime.now().date()
        last_lesson_date = data.get("last_lesson_date")
        
        if last_lesson_date:
            try:
                last_date = datetime.fromisoformat(last_lesson_date).date()
                if (today - last_date).days == 1:
                    # Consecutive day
                    data["current_streak"] = data.get("current_streak", 0) + 1
                elif (today - last_date).days > 1:
                    # Streak broken
                    data["current_streak"] = 1
                # Same day - don't update streak
            except:
                data["current_streak"] = 1
        else:
            data["current_streak"] = 1
        
        data["last_lesson_date"] = datetime.now().isoformat()
        data["longest_streak"] = max(data.get("longest_streak", 0), data["current_streak"])
    
    def _check_badges(self, data: Dict) -> List[str]:
        """Check if student earned any new badges"""
        earned = []
        current_badges = set(data.get("badges_earned", []))
        
        # Check each badge
        for badge_id, badge_info in self.badges.items():
            if badge_id in current_badges:
                continue
            
            earned_badge = False
            
            if badge_id == "first_lesson":
                earned_badge = data.get("total_lessons", 0) >= badge_info["threshold"]
            elif badge_id == "week_warrior":
                earned_badge = data.get("current_streak", 0) >= badge_info["threshold"]
            elif badge_id == "perfect_score":
                # Check recent assessment scores
                recent_scores = self._get_recent_scores(data["student_id"])
                earned_badge = any(score >= badge_info["threshold"] for score in recent_scores)
            elif badge_id == "doubt_solver":
                earned_badge = data.get("total_doubts", 0) >= badge_info["threshold"]
            elif badge_id == "consistent_learner":
                earned_badge = data.get("current_streak", 0) >= badge_info["threshold"]
            
            if earned_badge:
                earned.append(badge_id)
        
        return earned
    
    def _get_recent_scores(self, student_id: str) -> List[float]:
        """Get recent assessment scores"""
        # This would typically load from assessment results
        # For now, return empty list
        return []
    
    def update_engagement_score(self, student_id: str, contribution: float):
        """
        Update engagement score
        
        Args:
            student_id: Student identifier
            contribution: Contribution to engagement (0.0 to 1.0)
        """
        data_file = self.engagement_data_dir / f"{student_id}.json"
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"student_id": student_id, "engagement_score": 0.0}
        
        # Update engagement score (weighted average)
        current_score = data.get("engagement_score", 0.0)
        new_score = current_score * 0.7 + contribution * 0.3
        data["engagement_score"] = min(1.0, max(0.0, new_score))
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_engagement_score(self, student_id: str) -> float:
        """Get current engagement score"""
        data_file = self.engagement_data_dir / f"{student_id}.json"
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("engagement_score", 0.0)
        
        return 0.0
    
    def get_engagement_stats(self, student_id: str) -> Dict:
        """Get comprehensive engagement statistics"""
        data_file = self.engagement_data_dir / f"{student_id}.json"
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            return {
                "engagement_score": 0.0,
                "total_lessons": 0,
                "current_streak": 0,
                "badges_earned": []
            }
        
        return {
            "engagement_score": data.get("engagement_score", 0.0),
            "total_lessons": data.get("total_lessons", 0),
            "total_assessments": data.get("total_assessments", 0),
            "total_doubts": data.get("total_doubts", 0),
            "current_streak": data.get("current_streak", 0),
            "longest_streak": data.get("longest_streak", 0),
            "badges_earned": data.get("badges_earned", []),
            "recent_interactions": data.get("interactions", [])[-10:]  # Last 10 interactions
        }
    
    def get_motivational_message(self, student_id: str, language: str = "hi") -> str:
        """Get motivational message based on engagement"""
        score = self.get_engagement_score(student_id)
        stats = self.get_engagement_stats(student_id)
        
        messages = {
            "hi": {
                "high": f"बहुत बढ़िया! आप {stats['current_streak']} दिन से लगातार सीख रहे हैं!",
                "medium": f"अच्छा काम कर रहे हैं! {stats['total_lessons']} पाठ पूरे कर चुके हैं!",
                "low": "कोशिश जारी रखें! आप बेहतर कर सकते हैं!"
            },
            "en": {
                "high": f"Excellent! You've been learning for {stats['current_streak']} days straight!",
                "medium": f"Good work! You've completed {stats['total_lessons']} lessons!",
                "low": "Keep trying! You can do better!"
            }
        }
        
        lang_messages = messages.get(language, messages["en"])
        
        if score >= 0.7:
            return lang_messages["high"]
        elif score >= 0.4:
            return lang_messages["medium"]
        else:
            return lang_messages["low"]
    
    def suggest_break(self, student_id: str) -> bool:
        """Suggest if student needs a break"""
        data_file = self.engagement_data_dir / f"{student_id}.json"
        
        if not data_file.exists():
            return False
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check recent interactions
        recent_interactions = [i for i in data.get("interactions", []) 
                              if self._is_recent(i.get("timestamp", ""))]
        
        # If too many interactions in short time, suggest break
        if len(recent_interactions) > 5:
            return True
        
        return False
    
    def _is_recent(self, timestamp: str, minutes: int = 30) -> bool:
        """Check if timestamp is within recent minutes"""
        try:
            dt = datetime.fromisoformat(timestamp)
            return (datetime.now() - dt).total_seconds() < minutes * 60
        except:
            return False
