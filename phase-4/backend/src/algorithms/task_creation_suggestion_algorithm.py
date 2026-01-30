from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.utils.task_behavior_aggregator import TaskBehaviorAggregator
from models.task import Task


class TaskCreationSuggestionAlgorithm:
    """
    Algorithm for suggesting new tasks based on user behavior patterns
    """
    
    def __init__(self, behavior_aggregator: TaskBehaviorAggregator):
        self.behavior_aggregator = behavior_aggregator
    
    def suggest_new_tasks(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Suggest new tasks based on user's historical patterns
        """
        # Get user's behavioral data
        behavior_data = self.behavior_aggregator.aggregate_user_behavior(user_id)
        
        suggestions = []
        
        # 1. Suggest recurring tasks that might be due
        suggestions.extend(self._suggest_recurring_tasks(behavior_data))
        
        # 2. Suggest tasks based on time patterns
        suggestions.extend(self._suggest_time_based_tasks(behavior_data))
        
        # 3. Suggest tasks based on category preferences
        suggestions.extend(self._suggest_category_based_tasks(behavior_data))
        
        # 4. Suggest tasks based on interdependencies
        suggestions.extend(self._suggest_interdependent_tasks(behavior_data))
        
        # Limit and return suggestions
        return suggestions[:limit]
    
    def _suggest_recurring_tasks(self, behavior_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest tasks that might be recurring based on historical patterns
        """
        suggestions = []
        
        # This would identify tasks that the user tends to create regularly
        # For example, if they create "buy groceries" every week, suggest it again
        interdependencies = behavior_data.get("task_interdependency", [])
        
        for dep in interdependencies:
            if dep["count"] >= 3:  # If this keyword appears in 3+ tasks, it might be recurring
                suggestions.append({
                    "title": f"Consider adding a task related to '{dep['keyword']}'",
                    "description": f"You often create tasks related to '{dep['keyword']}'. Would you like to add a new one?",
                    "priority": "medium",
                    "category": "pattern-based",
                    "confidence": 0.7
                })
        
        return suggestions
    
    def _suggest_time_based_tasks(self, behavior_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest tasks based on user's time-based patterns
        """
        suggestions = []
        
        # Get current time characteristics
        now = datetime.now()
        current_hour = now.hour
        current_weekday = now.weekday()  # Monday is 0, Sunday is 6
        
        # Check if current time matches user's peak activity times
        peak_times = behavior_data.get("peak_activity_times", [])
        
        for hour, counts in peak_times:
            if abs(current_hour - hour) <= 2:  # Within 2 hours of peak time
                suggestions.append({
                    "title": "Time for your typical tasks",
                    "description": f"It's around {current_hour}:00, which is when you typically create tasks. Would you like to add something?",
                    "priority": "low",
                    "category": "time-based",
                    "confidence": 0.6
                })
                break  # Only add one time-based suggestion
        
        # Check if current day matches user's busy days
        busy_days = behavior_data.get("time_based_patterns", {}).get("busiest_days", [])
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_day_name = day_names[current_weekday]
        
        for day_name, count in busy_days:
            if day_name == current_day_name:
                suggestions.append({
                    "title": "It's your typical busy day",
                    "description": f"{current_day_name}s are typically busy for you. Consider planning your tasks for the week.",
                    "priority": "medium",
                    "category": "time-based",
                    "confidence": 0.65
                })
                break  # Only add one day-based suggestion
        
        return suggestions
    
    def _suggest_category_based_tasks(self, behavior_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest tasks based on user's preferred categories
        """
        suggestions = []
        
        # Get user's category preferences
        categories = behavior_data.get("category_preferences", {})
        
        # Find the most common category
        if categories:
            dominant_category = max(categories, key=categories.get)
            if categories[dominant_category] > 2:  # If user has 3+ tasks in this category
                suggestions.append({
                    "title": f"More {dominant_category} tasks?",
                    "description": f"You frequently create {dominant_category} tasks. Would you like to add another?",
                    "priority": "medium",
                    "category": dominant_category,
                    "confidence": 0.7
                })
        
        return suggestions
    
    def _suggest_interdependent_tasks(self, behavior_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest tasks that might be related to recently completed tasks
        """
        suggestions = []
        
        # This would suggest tasks that often follow other tasks
        # For example, if "buy ingredients" is often followed by "cook meal"
        interdependencies = behavior_data.get("task_interdependency", [])
        
        for dep in interdependencies:
            if dep["count"] >= 2:
                suggestions.append({
                    "title": f"Related to '{dep['keyword']}' tasks",
                    "description": f"You often create tasks related to '{dep['keyword']}'. Would you like to add a new one?",
                    "priority": "medium",
                    "category": "interdependency",
                    "confidence": 0.6
                })
        
        return suggestions
    
    def _calculate_suggestion_confidence(self, suggestion: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a suggestion based on user profile
        """
        # This would adjust the confidence based on how well the suggestion matches the user's patterns
        category = suggestion.get("category", "")
        user_categories = user_profile.get("category_preferences", {})
        
        if category in user_categories:
            # Higher confidence if it matches user's preferred category
            category_ratio = user_categories[category] / sum(user_categories.values())
            suggestion["confidence"] = max(suggestion["confidence"], category_ratio)
        
        return suggestion["confidence"]