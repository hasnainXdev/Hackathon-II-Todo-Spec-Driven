from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
from models.task import Task


class TaskPrioritizationSuggestionAlgorithm:
    """
    Algorithm for suggesting task prioritization based on various factors
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def suggest_task_priorities(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Suggest priorities for user's tasks based on various factors
        """
        # Get all tasks for the user
        task_statement = select(Task).where(Task.user_id == user_id)
        tasks = self.session.exec(task_statement).all()
        
        suggestions = []
        
        for task in tasks:
            if not getattr(task, 'completed', False):  # Only suggest for incomplete tasks
                priority_suggestion = self._evaluate_task_priority(task)
                suggestions.append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "suggested_priority": priority_suggestion["priority"],
                    "confidence": priority_suggestion["confidence"],
                    "reasoning": priority_suggestion["reasoning"]
                })
        
        # Sort by confidence score (descending)
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions
    
    def _evaluate_task_priority(self, task: Task) -> Dict[str, Any]:
        """
        Evaluate priority for a single task based on multiple factors
        """
        # Initialize scoring factors
        urgency_score = 0
        importance_score = 0
        deadline_score = 0
        consequence_score = 0
        
        # Factor 1: Deadline proximity (urgency)
        if hasattr(task, 'due_date') and task.due_date:
            days_until_deadline = (task.due_date - datetime.now()).days
            
            if days_until_deadline <= 1:  # Due today or overdue
                urgency_score = 1.0
            elif days_until_deadline <= 3:
                urgency_score = 0.8
            elif days_until_deadline <= 7:
                urgency_score = 0.5
            elif days_until_deadline <= 30:
                urgency_score = 0.3
            else:
                urgency_score = 0.1
        
        # Factor 2: Importance indicators in title/description
        title_desc = (getattr(task, 'title', '') + " " + getattr(task, 'description', '')).lower()
        importance_keywords = [
            'urgent', 'important', 'critical', 'crucial', 'essential', 
            'vital', 'mandatory', 'required', 'priority', 'top'
        ]
        
        importance_matches = [kw for kw in importance_keywords if kw in title_desc]
        importance_score = min(1.0, len(importance_matches) * 0.3)  # Max 0.9 for importance
        
        # Factor 3: Consequences of not completing
        consequence_keywords = [
            'fine', 'penalty', 'fee', 'late', 'missed', 'cancelled',
            'lost', 'failed', 'rejected', 'denied', 'expired'
        ]
        
        consequence_matches = [kw for kw in consequence_keywords if kw in title_desc]
        consequence_score = min(1.0, len(consequence_matches) * 0.4)  # Higher weight for consequences
        
        # Combine scores with weights
        # Weights can be adjusted based on user preferences or learning
        final_score = (
            urgency_score * 0.4 +
            importance_score * 0.2 +
            consequence_score * 0.3 +
            deadline_score * 0.1  # Deadline is factored into urgency
        )
        
        # Map score to priority level
        if final_score >= 0.8:
            priority = "high"
            confidence = 0.9
        elif final_score >= 0.5:
            priority = "medium"
            confidence = 0.8
        elif final_score >= 0.3:
            priority = "medium"
            confidence = 0.7
        else:
            priority = "low"
            confidence = 0.6
        
        # Generate reasoning
        reasoning_parts = []
        if urgency_score > 0.5:
            if hasattr(task, 'due_date'):
                days_left = (task.due_date - datetime.now()).days
                if days_left <= 0:
                    reasoning_parts.append("Task is overdue")
                elif days_left == 1:
                    reasoning_parts.append("Task is due tomorrow")
                else:
                    reasoning_parts.append(f"Task is due in {days_left} days")
        
        if importance_score > 0.3:
            reasoning_parts.append("Keywords suggest high importance")
        
        if consequence_score > 0.3:
            reasoning_parts.append("Potential negative consequences")
        
        if not reasoning_parts:
            reasoning_parts.append("Default priority based on general heuristics")
        
        return {
            "priority": priority,
            "confidence": confidence,
            "reasoning": "; ".join(reasoning_parts)
        }
    
    def suggest_reordering_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Suggest a reordering of tasks based on priority and deadlines
        """
        suggestions = self.suggest_task_priorities(user_id)
        
        # Enhance with deadline information
        task_statement = select(Task).where(Task.user_id == user_id)
        tasks = {task.id: task for task in self.session.exec(task_statement).all()}
        
        reordering_suggestions = []
        for suggestion in suggestions:
            task = tasks.get(suggestion["task_id"])
            if task and not getattr(task, 'completed', False):
                reordering_suggestions.append({
                    "task_id": suggestion["task_id"],
                    "task_title": suggestion["task_title"],
                    "current_priority": getattr(task, 'priority', 'medium'),
                    "suggested_priority": suggestion["suggested_priority"],
                    "confidence": suggestion["confidence"],
                    "reasoning": suggestion["reasoning"],
                    "due_date": getattr(task, 'due_date', None)
                })
        
        # Sort by suggested priority (high first) and then by deadline
        reordering_suggestions.sort(
            key=lambda x: (
                {"high": 3, "medium": 2, "low": 1}.get(x["suggested_priority"], 1),
                x["due_date"] or datetime.max  # Tasks with no due date go last
            ),
            reverse=True
        )
        
        return reordering_suggestions