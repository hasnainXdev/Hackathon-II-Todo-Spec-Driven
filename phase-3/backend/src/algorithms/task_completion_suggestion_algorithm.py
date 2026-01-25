from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select
from models.task import Task


class TaskCompletionSuggestionAlgorithm:
    """
    Algorithm for suggesting tasks that should be completed
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def suggest_tasks_for_completion(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Suggest tasks that should be completed based on various factors
        """
        # Get all incomplete tasks for the user
        task_statement = select(Task).where(
            Task.user_id == user_id,
            getattr(Task, 'completed', False) == False
        )
        tasks = self.session.exec(task_statement).all()
        
        suggestions = []
        
        for task in tasks:
            completion_suggestion = self._evaluate_completion_readiness(task)
            if completion_suggestion["should_complete"]:
                suggestions.append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "suggestion_reason": completion_suggestion["reason"],
                    "confidence": completion_suggestion["confidence"],
                    "urgency": completion_suggestion["urgency"],
                    "due_date": getattr(task, 'due_date', None)
                })
        
        # Sort by urgency and confidence (descending)
        suggestions.sort(key=lambda x: (x["urgency"], x["confidence"]), reverse=True)
        return suggestions[:limit]
    
    def _evaluate_completion_readiness(self, task: Task) -> Dict[str, Any]:
        """
        Evaluate if a task is ready for completion
        """
        # Initialize evaluation factors
        is_overdue = False
        is_ready = False
        has_dependencies_met = True
        is_low_effort = False
        
        # Factor 1: Check if task is overdue
        if hasattr(task, 'due_date') and task.due_date:
            if datetime.now() > task.due_date:
                is_overdue = True
        
        # Factor 2: Check if task is ready to be completed
        # This is a simplified check - in a real system, you might have more complex logic
        title = getattr(task, 'title', '')
        if title is None:
            title = ''
        description = getattr(task, 'description', '')
        if description is None:
            description = ''
        title_desc = (title + " " + description).lower()
        
        # Check for indicators that the task might be completed
        ready_indicators = [
            'already', 'done', 'finished', 'completed', 'achieved', 'accomplished',
            'ready', 'set', 'prepared', 'arranged', 'organized'
        ]
        
        ready_matches = [indicator for indicator in ready_indicators if indicator in title_desc]
        if ready_matches:
            is_ready = True
        
        # Factor 3: Estimate effort level based on title/description
        # Shorter, simpler tasks might be easier to complete
        total_length = len(getattr(task, 'title', '')) + len(getattr(task, 'description', ''))
        if total_length < 50:  # Arbitrary threshold
            is_low_effort = True
        
        # Determine if task should be suggested for completion
        should_complete = False
        reason = ""
        confidence = 0.5  # Default confidence
        urgency = 0.5     # Default urgency
        
        if is_overdue:
            should_complete = True
            reason = "Task is overdue and should be completed"
            urgency = 1.0
            confidence = 0.9
        elif is_ready:
            should_complete = True
            reason = f"Task title/description contains indicators it might be completed ({', '.join(ready_matches)})"
            urgency = 0.7
            confidence = 0.7
        elif is_low_effort and not hasattr(task, 'due_date'):
            # Simple tasks without deadlines might be good candidates for completion
            should_complete = True
            reason = "Simple task that could be completed quickly"
            urgency = 0.4
            confidence = 0.6
        elif is_low_effort and is_ready:
            should_complete = True
            reason = f"Simple task with indicators it might be completed ({', '.join(ready_matches)})"
            urgency = 0.8
            confidence = 0.8
        
        return {
            "should_complete": should_complete,
            "reason": reason,
            "confidence": confidence,
            "urgency": urgency
        }
    
    def suggest_batch_completion_opportunities(self, user_id: str) -> Dict[str, Any]:
        """
        Suggest groups of tasks that could be completed together
        """
        # Get incomplete tasks
        task_statement = select(Task).where(
            Task.user_id == user_id,
            getattr(Task, 'completed', False) == False
        )
        tasks = self.session.exec(task_statement).all()
        
        # Group tasks by category (simplified approach using keywords)
        category_groups = {}
        for task in tasks:
            title_desc = (getattr(task, 'title', '') + " " + getattr(task, 'description', '')).lower()
            
            # Determine category based on keywords
            category = "other"
            if any(word in title_desc for word in ["email", "call", "message", "contact", "phone"]):
                category = "communication"
            elif any(word in title_desc for word in ["buy", "shop", "purchase", "grocer", "store"]):
                category = "shopping"
            elif any(word in title_desc for word in ["clean", "wash", "organize", "tidy", "laundry"]):
                category = "household"
            elif any(word in title_desc for word in ["work", "project", "document", "write", "report"]):
                category = "work"
            elif any(word in title_desc for word in ["exercise", "gym", "run", "walk", "meditate"]):
                category = "health"
            
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(task)
        
        # Find groups with multiple tasks
        batch_opportunities = []
        for category, category_tasks in category_groups.items():
            if len(category_tasks) > 1:
                # Calculate average readiness for completion
                avg_urgency = 0
                avg_confidence = 0
                task_details = []
                
                for task in category_tasks:
                    eval_result = self._evaluate_completion_readiness(task)
                    avg_urgency += eval_result["urgency"]
                    avg_confidence += eval_result["confidence"]
                    
                    task_details.append({
                        "task_id": task.id,
                        "task_title": task.title,
                        "readiness": eval_result["reason"]
                    })
                
                avg_urgency /= len(category_tasks)
                avg_confidence /= len(category_tasks)
                
                batch_opportunities.append({
                    "category": category,
                    "task_count": len(category_tasks),
                    "average_urgency": avg_urgency,
                    "average_confidence": avg_confidence,
                    "tasks": task_details
                })
        
        # Sort by average urgency and task count
        batch_opportunities.sort(key=lambda x: (x["average_urgency"], x["task_count"]), reverse=True)
        
        return {
            "batch_opportunities": batch_opportunities,
            "total_opportunities": len(batch_opportunities)
        }