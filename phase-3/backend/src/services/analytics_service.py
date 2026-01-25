from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlmodel import Session, select
from models.task import Task  # Assuming task model exists from phase-2
from src.models.conversation import Message  # Using conversation messages to understand user patterns


class AnalyticsService:
    """
    Service for tracking and analyzing user task patterns
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def _get_task_completion_status(self, task) -> bool:
        """
        Helper method to get the completion status of a task,
        supporting both 'completion_status' and 'completed' field names
        """
        if hasattr(task, 'completion_status'):
            return getattr(task, 'completion_status', False)
        else:
            return getattr(task, 'completed', False)

    def get_user_task_insights(self, user_id: str) -> Dict[str, any]:
        """
        Get insights about a user's task patterns
        """
        # Get all tasks for the user
        task_statement = select(Task).where(Task.user_id == user_id)
        tasks = self.session.exec(task_statement).all()

        insights = {
            "total_tasks": len(tasks),
            "completed_tasks": len([t for t in tasks if self._get_task_completion_status(t)]),
            "pending_tasks": len([t for t in tasks if not self._get_task_completion_status(t)]),
            "average_completion_time": self._calculate_avg_completion_time(tasks),
            "most_common_times": self._find_most_common_times(tasks),
            "recurrence_patterns": self._find_recurrence_patterns(tasks),
            "category_breakdown": self._get_category_breakdown(tasks),
            "productivity_trends": self._get_productivity_trends(tasks)
        }

        return insights
    
    def _calculate_avg_completion_time(self, tasks: List[Task]) -> Optional[float]:
        """
        Calculate average time taken to complete tasks
        """
        completed_tasks = [t for t in tasks if self._get_task_completion_status(t) and hasattr(t, 'created_at') and hasattr(t, 'updated_at')]
        
        if not completed_tasks:
            return None
        
        total_duration = 0
        for task in completed_tasks:
            duration = (task.updated_at - task.created_at).total_seconds()
            total_duration += duration
        
        avg_seconds = total_duration / len(completed_tasks)
        return avg_seconds / (24 * 3600)  # Convert to days
    
    def _find_most_common_times(self, tasks: List[Task]) -> Dict[str, any]:
        """
        Find the most common times for creating and completing tasks
        """
        creation_hours = []
        completion_hours = []
        
        for task in tasks:
            if hasattr(task, 'created_at'):
                creation_hours.append(task.created_at.hour)
            
            if getattr(task, 'completed', False) and hasattr(task, 'updated_at'):
                completion_hours.append(task.updated_at.hour)
        
        return {
            "common_creation_hours": self._get_top_items(creation_hours, 3),
            "common_completion_hours": self._get_top_items(completion_hours, 3)
        }
    
    def _find_recurrence_patterns(self, tasks: List[Task]) -> List[str]:
        """
        Identify recurring task patterns
        """
        # This is a simplified implementation
        # In a real system, you'd look for tasks with similar titles or created at regular intervals
        titles = [getattr(t, 'title', '').lower() for t in tasks]
        
        # Find tasks that might be recurring (same or similar titles)
        recurring_candidates = []
        seen_titles = set()
        for title in titles:
            if title in seen_titles:
                if title not in recurring_candidates:
                    recurring_candidates.append(title)
            else:
                seen_titles.add(title)
        
        return recurring_candidates
    
    def _get_category_breakdown(self, tasks: List[Task]) -> Dict[str, int]:
        """
        Break down tasks by category (based on keywords in titles/descriptions)
        """
        categories = {
            "work": 0,
            "personal": 0,
            "health": 0,
            "finance": 0,
            "shopping": 0,
            "other": 0
        }
        
        for task in tasks:
            title = getattr(task, 'title', '')
            if title is None:
                title = ''
            title = title.lower()

            desc = getattr(task, 'description', '')
            if desc is None:
                desc = ''
            desc = desc.lower()
            content = title + " " + desc
            
            if any(word in content for word in ["work", "meeting", "report", "email", "project", "presentation"]):
                categories["work"] += 1
            elif any(word in content for word in ["doctor", "exercise", "meditation", "yoga", "health", "fitness"]):
                categories["health"] += 1
            elif any(word in content for word in ["pay", "bill", "money", "bank", "finance", "tax"]):
                categories["finance"] += 1
            elif any(word in content for word in ["buy", "shop", "grocer", "store", "purchase"]):
                categories["shopping"] += 1
            elif any(word in content for word in ["call", "visit", "family", "friend", "personal"]):
                categories["personal"] += 1
            else:
                categories["other"] += 1
        
        return categories
    
    def _get_productivity_trends(self, tasks: List[Task]) -> Dict[str, any]:
        """
        Get productivity trends over time
        """
        # Calculate completion rates for different time periods
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Tasks created in the last week/month
        recent_tasks_w = [t for t in tasks if hasattr(t, 'created_at') and t.created_at >= week_ago]
        recent_tasks_m = [t for t in tasks if hasattr(t, 'created_at') and t.created_at >= month_ago]
        
        # Tasks completed in the last week/month
        completed_w = [t for t in recent_tasks_w if getattr(t, 'completed', False)]
        completed_m = [t for t in recent_tasks_m if getattr(t, 'completed', False)]
        
        return {
            "weekly_completion_rate": len(completed_w) / len(recent_tasks_w) if recent_tasks_w else 0,
            "monthly_completion_rate": len(completed_m) / len(recent_tasks_m) if recent_tasks_m else 0,
            "avg_weekly_tasks": len(recent_tasks_w) / 7 if recent_tasks_w else 0
        }
    
    def _get_top_items(self, items_list: List, n: int) -> List:
        """
        Get the top n most common items from a list
        """
        if not items_list:
            return []
        
        # Count occurrences
        counts = {}
        for item in items_list:
            counts[item] = counts.get(item, 0) + 1
        
        # Sort by count and return top n
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_items[:n]]
    
    def track_user_interaction(self, user_id: str, interaction_type: str, details: Dict[str, any]):
        """
        Track user interactions for behavioral analysis
        """
        # In a real implementation, you would store this in a dedicated table
        # For now, we'll just log it
        print(f"Tracking interaction for user {user_id}: {interaction_type} - {details}")
        
        # This could include:
        # - Types of tasks frequently created
        # - Times of day when user is most active
        # - Preferred task categories
        # - Response to suggestions
        # - Task completion patterns