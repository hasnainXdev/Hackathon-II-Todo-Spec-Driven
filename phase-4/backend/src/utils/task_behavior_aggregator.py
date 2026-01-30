from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlmodel import Session, select
from models.task import Task  # Import Task from the models directory
from src.models.conversation import Message  # Using conversation messages to understand user patterns


class TaskBehaviorAggregator:
    """
    Aggregates data about user task behavior for analytics and suggestions
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def aggregate_user_behavior(self, user_id: str) -> Dict[str, any]:
        """
        Aggregate various behavioral metrics for a user
        """
        # Get all tasks for the user
        task_statement = select(Task).where(Task.user_id == user_id)
        tasks = self.session.exec(task_statement).all()
        
        aggregated_data = {
            "task_frequency": self._calculate_task_frequency(tasks),
            "completion_patterns": self._analyze_completion_patterns(tasks),
            "time_based_patterns": self._analyze_time_based_patterns(tasks),
            "category_preferences": self._analyze_category_preferences(tasks),
            "peak_activity_times": self._identify_peak_activity_times(tasks),
            "task_interdependency": self._analyze_task_interdependencies(tasks),
            "performance_metrics": self._calculate_performance_metrics(tasks)
        }
        
        return aggregated_data
    
    def _calculate_task_frequency(self, tasks: List[Task]) -> Dict[str, int]:
        """
        Calculate how often user creates tasks
        """
        if not tasks:
            return {"daily_avg": 0, "weekly_avg": 0, "monthly_avg": 0}
        
        # Find the date range
        creation_dates = [task.created_at.date() for task in tasks if hasattr(task, 'created_at')]
        if not creation_dates:
            return {"daily_avg": 0, "weekly_avg": 0, "monthly_avg": 0}
        
        min_date = min(creation_dates)
        max_date = max(creation_dates)
        date_range = (max_date - min_date).days + 1  # +1 to include both start and end dates
        
        daily_avg = len(creation_dates) / date_range if date_range > 0 else 0
        weekly_avg = daily_avg * 7
        monthly_avg = daily_avg * 30  # Approximate
        
        return {
            "daily_avg": round(daily_avg, 2),
            "weekly_avg": round(weekly_avg, 2),
            "monthly_avg": round(monthly_avg, 2)
        }
    
    def _analyze_completion_patterns(self, tasks: List[Task]) -> Dict[str, any]:
        """
        Analyze how and when user completes tasks
        """
        completed_tasks = [t for t in tasks if getattr(t, 'completed', False)]
        
        if not tasks:
            return {"completion_rate": 0, "avg_completion_time": None}
        
        completion_rate = len(completed_tasks) / len(tasks)
        
        # Calculate average time to completion
        completion_times = []
        for task in completed_tasks:
            if hasattr(task, 'created_at') and hasattr(task, 'updated_at'):
                time_to_complete = (task.updated_at - task.created_at).total_seconds()
                completion_times.append(time_to_complete)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else None
        
        return {
            "completion_rate": round(completion_rate, 2),
            "avg_completion_time": avg_completion_time,  # in seconds
            "total_completed": len(completed_tasks)
        }
    
    def _analyze_time_based_patterns(self, tasks: List[Task]) -> Dict[str, any]:
        """
        Analyze patterns based on time (hour of day, day of week, etc.)
        """
        creation_times = [(task.created_at.hour, task.created_at.weekday()) for task in tasks if hasattr(task, 'created_at')]
        
        if not creation_times:
            return {"busiest_hours": [], "busiest_days": []}
        
        hours_count = {}
        days_count = {}
        
        for hour, day in creation_times:
            hours_count[hour] = hours_count.get(hour, 0) + 1
            days_count[day] = days_count.get(day, 0) + 1
        
        # Get top 3 busiest hours and days
        busiest_hours = sorted(hours_count.items(), key=lambda x: x[1], reverse=True)[:3]
        busiest_days = sorted(days_count.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Convert day numbers to names
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        busiest_day_names = [(day_names[day], count) for day, count in busiest_days]
        
        return {
            "busiest_hours": busiest_hours,
            "busiest_days": busiest_day_names
        }
    
    def _analyze_category_preferences(self, tasks: List[Task]) -> Dict[str, int]:
        """
        Analyze preferred task categories based on keywords
        """
        categories = {
            "work": 0,
            "personal": 0,
            "health": 0,
            "finance": 0,
            "shopping": 0,
            "learning": 0,
            "other": 0
        }
        
        for task in tasks:
            title = getattr(task, 'title', '').lower()
            desc = getattr(task, 'description', '').lower()
            content = title + " " + desc
            
            if any(word in content for word in ["work", "meeting", "report", "email", "project", "presentation", "deadline"]):
                categories["work"] += 1
            elif any(word in content for word in ["doctor", "exercise", "meditation", "yoga", "health", "fitness", "appointment"]):
                categories["health"] += 1
            elif any(word in content for word in ["pay", "bill", "money", "bank", "finance", "tax", "budget"]):
                categories["finance"] += 1
            elif any(word in content for word in ["buy", "shop", "grocer", "store", "purchase", "amazon"]):
                categories["shopping"] += 1
            elif any(word in content for word in ["learn", "study", "course", "book", "read", "education", "skill"]):
                categories["learning"] += 1
            elif any(word in content for word in ["call", "visit", "family", "friend", "personal", "social"]):
                categories["personal"] += 1
            else:
                categories["other"] += 1
        
        return categories
    
    def _identify_peak_activity_times(self, tasks: List[Task]) -> List[Tuple[int, int]]:
        """
        Identify peak activity times based on task creation and completion
        """
        activity_times = []
        
        # Add creation times
        for task in tasks:
            if hasattr(task, 'created_at'):
                hour = task.created_at.hour
                activity_times.append((hour, "creation"))
        
        # Add completion times for completed tasks
        completed_tasks = [t for t in tasks if getattr(t, 'completed', False)]
        for task in completed_tasks:
            if hasattr(task, 'updated_at'):
                hour = task.updated_at.hour
                activity_times.append((hour, "completion"))
        
        if not activity_times:
            return []
        
        # Count activities by hour
        hour_counts = {}
        for hour, activity_type in activity_times:
            if hour not in hour_counts:
                hour_counts[hour] = {"creation": 0, "completion": 0}
            hour_counts[hour][activity_type] += 1
        
        # Return top 5 peak hours
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1]["creation"] + x[1]["completion"], reverse=True)[:5]
        return [(hour, counts) for hour, counts in peak_hours]
    
    def _analyze_task_interdependencies(self, tasks: List[Task]) -> List[Dict[str, any]]:
        """
        Analyze potential interdependencies between tasks
        """
        # This is a simplified implementation
        # In a real system, you'd use NLP to identify dependencies in task descriptions
        title_keywords = {}
        
        for i, task in enumerate(tasks):
            title = getattr(task, 'title', '').lower()
            # Extract key terms from the title
            terms = [word for word in title.split() if len(word) > 3]  # Only consider words with more than 3 chars
            
            for term in terms:
                if term not in title_keywords:
                    title_keywords[term] = []
                title_keywords[term].append(i)
        
        # Find terms that appear in multiple tasks (potential interdependencies)
        interdependencies = []
        for term, task_indices in title_keywords.items():
            if len(task_indices) > 1:
                interdependencies.append({
                    "keyword": term,
                    "related_tasks": [tasks[i].title for i in task_indices],
                    "count": len(task_indices)
                })
        
        # Sort by count of related tasks
        interdependencies.sort(key=lambda x: x["count"], reverse=True)
        return interdependencies[:10]  # Return top 10
    
    def _calculate_performance_metrics(self, tasks: List[Task]) -> Dict[str, any]:
        """
        Calculate various performance metrics
        """
        if not tasks:
            return {
                "productivity_score": 0,
                "consistency_score": 0,
                "goal_achievement_rate": 0
            }
        
        completed_tasks = [t for t in tasks if getattr(t, 'completed', False)]
        
        # Productivity score: based on completion rate and frequency
        completion_rate = len(completed_tasks) / len(tasks) if tasks else 0
        frequency_factor = self._calculate_task_frequency(tasks)["daily_avg"]
        
        productivity_score = min(100, (completion_rate * 50) + (frequency_factor * 10))  # Scale to 0-100
        
        # Consistency score: how regularly tasks are completed
        consistency_score = self._calculate_consistency_score(tasks)
        
        # Goal achievement rate: percentage of tasks completed on time
        on_time_completions = 0
        for task in completed_tasks:
            if hasattr(task, 'due_date') and hasattr(task, 'updated_at'):
                if task.updated_at <= task.due_date:
                    on_time_completions += 1
        
        goal_achievement_rate = on_time_completions / len(completed_tasks) if completed_tasks else 0
        
        return {
            "productivity_score": round(productivity_score, 2),
            "consistency_score": round(consistency_score, 2),
            "goal_achievement_rate": round(goal_achievement_rate, 2)
        }
    
    def _calculate_consistency_score(self, tasks: List[Task]) -> float:
        """
        Calculate consistency score based on regular task completion
        """
        if not tasks:
            return 0
        
        completed_tasks = [t for t in tasks if getattr(t, 'completed', False)]
        
        # Group tasks by week
        weekly_completion = {}
        for task in completed_tasks:
            if hasattr(task, 'created_at'):
                week = task.created_at.isocalendar()[:2]  # (year, week_number)
                if week not in weekly_completion:
                    weekly_completion[week] = 0
                weekly_completion[week] += 1
        
        if len(weekly_completion) < 2:
            return 50  # Neutral score if insufficient data
        
        # Calculate variance in weekly completion
        completions = list(weekly_completion.values())
        mean_completion = sum(completions) / len(completions)
        
        if mean_completion == 0:
            return 0
        
        variance = sum((x - mean_completion) ** 2 for x in completions) / len(completions)
        coefficient_of_variation = (variance ** 0.5) / mean_completion if mean_completion > 0 else 0
        
        # Lower coefficient of variation means more consistent
        consistency_score = max(0, 100 * (1 - coefficient_of_variation))
        
        return consistency_score