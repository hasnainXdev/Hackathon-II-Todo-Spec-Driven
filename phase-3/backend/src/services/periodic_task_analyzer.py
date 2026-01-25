import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlmodel import Session, select
from ..models.task import Task
from ..services.analytics_service import AnalyticsService
from ..utils.task_behavior_aggregator import TaskBehaviorAggregator
from ..algorithms.task_creation_suggestion_algorithm import TaskCreationSuggestionAlgorithm
from ..algorithms.task_prioritization_suggestion_algorithm import TaskPrioritizationSuggestionAlgorithm
from ..algorithms.task_completion_suggestion_algorithm import TaskCompletionSuggestionAlgorithm


class PeriodicTaskAnalyzer:
    """
    Performs periodic analysis of user task data to generate insights and suggestions
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.analytics_service = AnalyticsService(session)
        self.behavior_aggregator = TaskBehaviorAggregator(session)
        self.creation_suggester = TaskCreationSuggestionAlgorithm(self.behavior_aggregator)
        self.prioritization_suggester = TaskPrioritizationSuggestionAlgorithm(session)
        self.completion_suggester = TaskCompletionSuggestionAlgorithm(session)
        
        self.logger = logging.getLogger(__name__)
    
    async def run_periodic_analysis(self, user_ids: list = None) -> Dict[str, Any]:
        """
        Run periodic analysis for all users or specific users
        """
        start_time = datetime.now()
        self.logger.info(f"Starting periodic analysis at {start_time}")
        
        # Get all users if none specified
        if user_ids is None:
            user_ids = await self._get_all_user_ids()
        
        results = {
            "analysis_start_time": start_time.isoformat(),
            "users_analyzed": [],
            "summary": {
                "total_users": len(user_ids),
                "successful_analyses": 0,
                "failed_analyses": 0,
                "start_time": start_time.isoformat(),
                "end_time": None,
                "duration_seconds": None
            }
        }
        
        for user_id in user_ids:
            try:
                user_result = await self._analyze_single_user(user_id)
                results["users_analyzed"].append({
                    "user_id": user_id,
                    "success": True,
                    "analysis": user_result
                })
                results["summary"]["successful_analyses"] += 1
                
                self.logger.info(f"Completed analysis for user {user_id}")
            except Exception as e:
                self.logger.error(f"Failed to analyze user {user_id}: {str(e)}")
                results["users_analyzed"].append({
                    "user_id": user_id,
                    "success": False,
                    "error": str(e)
                })
                results["summary"]["failed_analyses"] += 1
        
        end_time = datetime.now()
        results["summary"]["end_time"] = end_time.isoformat()
        results["summary"]["duration_seconds"] = (end_time - start_time).total_seconds()
        
        self.logger.info(f"Completed periodic analysis at {end_time}, took {results['summary']['duration_seconds']} seconds")
        
        return results
    
    async def _analyze_single_user(self, user_id: str) -> Dict[str, Any]:
        """
        Perform analysis for a single user
        """
        # Get user insights
        user_insights = self.analytics_service.get_user_task_insights(user_id)
        
        # Get behavior aggregation
        behavior_data = self.behavior_aggregator.aggregate_user_behavior(user_id)
        
        # Generate task creation suggestions
        creation_suggestions = self.creation_suggester.suggest_new_tasks(user_id)
        
        # Generate prioritization suggestions
        prioritization_suggestions = self.prioritization_suggester.suggest_task_priorities(user_id)
        
        # Generate completion suggestions
        completion_suggestions = self.completion_suggester.suggest_tasks_for_completion(user_id)
        
        # Get batch completion opportunities
        batch_opportunities = self.completion_suggester.suggest_batch_completion_opportunities(user_id)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "user_insights": user_insights,
            "behavior_data": behavior_data,
            "suggestions": {
                "creation": creation_suggestions,
                "prioritization": prioritization_suggestions,
                "completion": completion_suggestions
            },
            "opportunities": {
                "batch_completion": batch_opportunities
            }
        }
    
    async def _get_all_user_ids(self) -> list:
        """
        Get all user IDs from the database
        """
        # This assumes there's a User model - we'll need to create a basic query
        # For now, we'll return an empty list or a mock implementation
        # In a real system, this would query the User table
        return []  # Placeholder - would query actual user table in real implementation
    
    async def schedule_regular_analysis(self, interval_minutes: int = 1440):  # Default to once per day
        """
        Schedule regular analysis to run at specified intervals
        """
        self.logger.info(f"Scheduling regular analysis every {interval_minutes} minutes")
        
        while True:
            try:
                await self.run_periodic_analysis()
                
                # Wait for the specified interval
                await asyncio.sleep(interval_minutes * 60)  # Convert minutes to seconds
            except Exception as e:
                self.logger.error(f"Error in scheduled analysis: {str(e)}")
                # Wait a shorter time before retrying after an error
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def generate_user_report(self, user_id: str) -> Dict[str, Any]:
        """
        Generate a detailed report for a specific user
        """
        # Run analysis for the specific user
        analysis_result = asyncio.run(self._analyze_single_user(user_id))
        
        # Format the report
        report = {
            "report_date": datetime.now().isoformat(),
            "user_id": user_id,
            "productivity_summary": {
                "total_tasks": analysis_result["user_insights"]["total_tasks"],
                "completed_tasks": analysis_result["user_insights"]["completed_tasks"],
                "pending_tasks": analysis_result["user_insights"]["pending_tasks"],
                "completion_rate": analysis_result["user_insights"]["completed_tasks"] / analysis_result["user_insights"]["total_tasks"] if analysis_result["user_insights"]["total_tasks"] > 0 else 0,
                "productivity_score": analysis_result["user_insights"]["performance_metrics"]["productivity_score"]
            },
            "behavioral_insights": {
                "most_active_hours": analysis_result["behavior_data"]["time_based_patterns"]["busiest_hours"],
                "preferred_categories": analysis_result["behavior_data"]["category_preferences"],
                "peak_activity_times": analysis_result["behavior_data"]["peak_activity_times"]
            },
            "suggestions": analysis_result["suggestions"],
            "recommendations": self._generate_recommendations(analysis_result)
        }
        
        return report
    
    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> list:
        """
        Generate actionable recommendations based on the analysis
        """
        recommendations = []
        
        # Productivity recommendations
        prod_score = analysis_result["user_insights"]["performance_metrics"]["productivity_score"]
        if prod_score < 50:
            recommendations.append("Consider focusing on completing a few high-priority tasks rather than starting many new ones.")
        
        if prod_score > 80:
            recommendations.append("Great job on productivity! Consider taking on more challenging tasks.")
        
        # Task completion recommendations
        completion_rate = analysis_result["user_insights"]["completed_tasks"] / analysis_result["user_insights"]["total_tasks"] if analysis_result["user_insights"]["total_tasks"] > 0 else 0
        if completion_rate < 0.5:
            recommendations.append("Try breaking larger tasks into smaller, more manageable pieces to improve completion rates.")
        
        # Timing recommendations
        busiest_hours = analysis_result["behavior_data"]["time_based_patterns"]["busiest_hours"]
        if busiest_hours:
            recommendations.append(f"You're most active around hour(s) {[hour for hour, count in busiest_hours[:2]]}. Consider scheduling important tasks during these times.")
        
        # Category recommendations
        categories = analysis_result["behavior_data"]["category_preferences"]
        dominant_category = max(categories, key=categories.get) if categories else None
        if dominant_category and categories[dominant_category] > 3:
            recommendations.append(f"You frequently create {dominant_category} tasks. Consider setting up recurring tasks for routine {dominant_category} activities.")
        
        return recommendations