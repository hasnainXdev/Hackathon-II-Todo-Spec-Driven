from typing import Dict, Any, List
from ..services.ai_service import AIService
from ..services.analytics_service import AnalyticsService
from ..algorithms.task_creation_suggestion_algorithm import TaskCreationSuggestionAlgorithm
from ..algorithms.task_prioritization_suggestion_algorithm import TaskPrioritizationSuggestionAlgorithm
from ..algorithms.task_completion_suggestion_algorithm import TaskCompletionSuggestionAlgorithm
from ..utils.task_behavior_aggregator import TaskBehaviorAggregator
from ..ai_models.personalized_suggestions_model import PersonalizedSuggestionsAIModel
from sqlmodel import Session


class SuggestionIntegrator:
    """
    Integrates AI-generated suggestions into chatbot responses
    """
    
    def __init__(
        self, 
        ai_service: AIService, 
        analytics_service: AnalyticsService,
        creation_suggester: TaskCreationSuggestionAlgorithm,
        prioritization_suggester: TaskPrioritizationSuggestionAlgorithm,
        completion_suggester: TaskCompletionSuggestionAlgorithm,
        behavior_aggregator: TaskBehaviorAggregator,
        ai_model: PersonalizedSuggestionsAIModel,
        session: Session
    ):
        self.ai_service = ai_service
        self.analytics_service = analytics_service
        self.creation_suggester = creation_suggester
        self.prioritization_suggester = prioritization_suggester
        self.completion_suggester = completion_suggester
        self.behavior_aggregator = behavior_aggregator
        self.ai_model = ai_model
        self.session = session
    
    async def generate_enhanced_response(
        self, 
        user_message: str, 
        user_id: str, 
        conversation_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate an AI response enhanced with personalized suggestions
        """
        # Get the base AI response
        base_response = await self.ai_service.process_user_message(
            message=user_message,
            user_context=conversation_context
        )
        
        # Generate personalized suggestions
        suggestions = await self._generate_personalized_suggestions(user_id)
        
        # Integrate suggestions into the response
        enhanced_response = self._integrate_suggestions(
            base_response=base_response,
            suggestions=suggestions,
            user_message=user_message
        )
        
        return enhanced_response
    
    async def _generate_personalized_suggestions(self, user_id: str) -> Dict[str, Any]:
        """
        Generate various types of personalized suggestions for the user
        """
        # Get user behavior data
        behavior_data = self.behavior_aggregator.aggregate_user_behavior(user_id)
        
        # Generate creation suggestions
        creation_suggestions = self.creation_suggester.suggest_new_tasks(user_id)
        
        # Generate prioritization suggestions
        prioritization_suggestions = self.prioritization_suggester.suggest_task_priorities(user_id)
        
        # Generate completion suggestions
        completion_suggestions = self.completion_suggester.suggest_tasks_for_completion(user_id)
        
        # Get batch completion opportunities
        batch_opportunities = self.completion_suggester.suggest_batch_completion_opportunities(user_id)
        
        # Generate AI model recommendations
        ai_recommendations = self.ai_model.recommend_new_tasks(behavior_data)
        
        return {
            "creation": creation_suggestions,
            "prioritization": prioritization_suggestions,
            "completion": completion_suggestions,
            "batch_opportunities": batch_opportunities,
            "ai_recommendations": ai_recommendations
        }
    
    def _integrate_suggestions(
        self, 
        base_response: Dict[str, Any], 
        suggestions: Dict[str, Any], 
        user_message: str
    ) -> Dict[str, Any]:
        """
        Integrate suggestions into the base AI response
        """
        # Determine which suggestions to include based on the user's message
        relevant_suggestions = self._filter_relevant_suggestions(suggestions, user_message)
        
        # Format suggestions for inclusion in response
        formatted_suggestions = self._format_suggestions_for_response(relevant_suggestions)
        
        # Enhance the base response with suggestions
        enhanced_content = base_response.get("response", "")
        
        if formatted_suggestions:
            # Add suggestions to the response if they're relevant
            suggestion_text = self._build_suggestion_text(formatted_suggestions)
            enhanced_content += f"\n\n{ suggestion_text}"
        
        # Add suggestions as a structured field
        enhanced_response = {
            **base_response,
            "response": enhanced_content,
            "suggestions": formatted_suggestions,
            "has_suggestions": len(formatted_suggestions) > 0
        }
        
        return enhanced_response
    
    def _filter_relevant_suggestions(self, suggestions: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """
        Filter suggestions based on relevance to the user's message
        """
        user_lower = user_message.lower()
        
        filtered = {}
        
        # Include creation suggestions if user seems to be looking for ideas
        if any(phrase in user_lower for phrase in ["what should i", "ideas for", "suggest", "recommend", "need to"]):
            filtered["creation"] = suggestions.get("creation", [])[:3]  # Limit to top 3
        
        # Include prioritization suggestions if user asks about priorities
        if any(phrase in user_lower for phrase in ["prioritize", "priority", "important", "focus on", "should i do"]):
            filtered["prioritization"] = suggestions.get("prioritization", [])[:3]
        
        # Include completion suggestions if user seems to be reviewing tasks
        if any(phrase in user_lower for phrase in ["what", "tasks", "list", "my tasks", "done", "complete"]):
            filtered["completion"] = suggestions.get("completion", [])[:3]
        
        # Always include AI recommendations if available
        if suggestions.get("ai_recommendations"):
            filtered["ai_recommendations"] = suggestions["ai_recommendations"][:2]
        
        return filtered
    
    def _format_suggestions_for_response(self, suggestions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format suggestions for inclusion in the chat response
        """
        formatted_suggestions = []
        
        # Format creation suggestions
        for suggestion in suggestions.get("creation", []):
            formatted_suggestions.append({
                "type": "creation",
                "title": suggestion.get("title", ""),
                "description": suggestion.get("description", ""),
                "confidence": suggestion.get("confidence", 0.0),
                "category": suggestion.get("category", "general")
            })
        
        # Format prioritization suggestions
        for suggestion in suggestions.get("prioritization", []):
            formatted_suggestions.append({
                "type": "prioritization",
                "task_id": suggestion.get("task_id", ""),
                "task_title": suggestion.get("task_title", ""),
                "suggested_priority": suggestion.get("suggested_priority", ""),
                "current_priority": suggestion.get("current_priority", ""),
                "confidence": suggestion.get("confidence", 0.0),
                "reasoning": suggestion.get("reasoning", "")
            })
        
        # Format completion suggestions
        for suggestion in suggestions.get("completion", []):
            formatted_suggestions.append({
                "type": "completion",
                "task_id": suggestion.get("task_id", ""),
                "task_title": suggestion.get("task_title", ""),
                "suggestion_reason": suggestion.get("suggestion_reason", ""),
                "confidence": suggestion.get("confidence", 0.0),
                "urgency": suggestion.get("urgency", 0.0)
            })
        
        # Format AI recommendations
        for recommendation in suggestions.get("ai_recommendations", []):
            formatted_suggestions.append({
                "type": "ai_recommendation",
                "title": recommendation.get("title", ""),
                "category": recommendation.get("category", ""),
                "predicted_priority": recommendation.get("predicted_priority", ""),
                "confidence": recommendation.get("confidence", 0.0),
                "reason": recommendation.get("reason", "")
            })
        
        return formatted_suggestions
    
    def _build_suggestion_text(self, formatted_suggestions: List[Dict[str, Any]]) -> str:
        """
        Build a textual representation of the suggestions to add to the response
        """
        if not formatted_suggestions:
            return ""
        
        suggestion_texts = []
        
        # Group suggestions by type
        by_type = {}
        for suggestion in formatted_suggestions:
            s_type = suggestion["type"]
            if s_type not in by_type:
                by_type[s_type] = []
            by_type[s_type].append(suggestion)
        
        # Add creation suggestions
        creation_suggestions = by_type.get("creation", [])
        if creation_suggestions:
            suggestion_texts.append("I have some suggestions for new tasks you might consider:")
            for i, suggestion in enumerate(creation_suggestions[:2]):  # Limit to 2 for brevity
                suggestion_texts.append(f"• {suggestion['title']}")
        
        # Add AI recommendations
        ai_recommendations = by_type.get("ai_recommendation", [])
        if ai_recommendations:
            suggestion_texts.append("\nBased on your patterns, you might also consider:")
            for i, rec in enumerate(ai_recommendations[:2]):  # Limit to 2 for brevity
                suggestion_texts.append(f"• {rec['title']} (priority: {rec['predicted_priority']})")
        
        # Add completion suggestions if any
        completion_suggestions = by_type.get("completion", [])
        if completion_suggestions:
            suggestion_texts.append("\nYou might want to complete these soon:")
            for i, suggestion in enumerate(completion_suggestions[:2]):  # Limit to 2 for brevity
                suggestion_texts.append(f"• {suggestion['task_title']} - {suggestion['suggestion_reason']}")
        
        return "\n".join(suggestion_texts)
    
    def should_offer_suggestions(self, user_message: str, conversation_context: Dict[str, Any] = None) -> bool:
        """
        Determine if suggestions should be offered based on the user's message and context
        """
        user_lower = user_message.lower()
        
        # Check if user is asking for suggestions or seems to need them
        asking_for_suggestions = any(phrase in user_lower for phrase in [
            "suggest", "recommend", "ideas", "what should i", 
            "what can i", "need ideas", "help me decide"
        ])
        
        # Check if user is reviewing tasks
        reviewing_tasks = any(phrase in user_lower for phrase in [
            "what", "tasks", "list", "my tasks", "show me", "view"
        ])
        
        # Check if user is asking about priorities
        about_priorities = any(phrase in user_lower for phrase in [
            "prioritize", "priority", "important", "focus on", "should i do"
        ])
        
        # If user is asking for suggestions or seems to need them
        return asking_for_suggestions or reviewing_tasks or about_priorities