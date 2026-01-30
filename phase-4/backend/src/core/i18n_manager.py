import json
from typing import Dict, List, Optional
from pathlib import Path


class I18nManager:
    """
    Internationalization manager for chat responses
    """
    
    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = Path(locales_dir)
        self.supported_locales = ["en", "es", "fr", "de", "ja", "zh"]
        self.translations = {}
        
        # Load translations for all supported locales
        self._load_translations()
    
    def _load_translations(self):
        """
        Load translation files for all supported locales
        """
        for locale in self.supported_locales:
            translation_file = self.locales_dir / f"{locale}.json"
            if translation_file.exists():
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations[locale] = json.load(f)
            else:
                # Create a default English translation if file doesn't exist
                self.translations[locale] = self._get_default_translations()
    
    def _get_default_translations(self) -> Dict[str, str]:
        """
        Get default English translations
        """
        return {
            # Generic responses
            "greeting": "Hello! How can I help you with your tasks today?",
            "confirmation": "Got it! I've updated your tasks.",
            "error_generic": "Sorry, I encountered an error processing your request.",
            "error_task_not_found": "Sorry, I couldn't find that task.",
            "error_permission": "You don't have permission to perform that action.",
            
            # Task-related responses
            "task_created": "I've created the task: {task_title}",
            "task_updated": "I've updated the task: {task_title}",
            "task_deleted": "I've deleted the task: {task_title}",
            "task_completed": "I've marked the task as completed: {task_title}",
            "task_reopened": "I've reopened the task: {task_title}",
            
            # Suggestion-related responses
            "suggestion_creation": "Based on your patterns, you might want to create: {suggestion}",
            "suggestion_priority": "I suggest setting the priority of '{task_title}' to {priority}",
            "suggestion_completion": "You might want to complete '{task_title}' soon: {reason}",
            
            # Help responses
            "help_intro": "I can help you manage your tasks. You can ask me to:",
            "help_create": "- Create tasks: 'Add a task to buy groceries'",
            "help_update": "- Update tasks: 'Change the meeting task to include Zoom link'",
            "help_complete": "- Complete tasks: 'Mark the laundry task as complete'",
            "help_delete": "- Delete tasks: 'Delete the old appointment task'",
            "help_list": "- List tasks: 'Show me my tasks'",
            "help_suggest": "- Get suggestions: 'What should I work on today?'",
            
            # Error responses for NLP
            "nlp_error_parsing": "I had trouble understanding your request: '{request}'. Could you rephrase it?",
            "nlp_error_ambiguous": "I'm not sure what you mean by: '{request}'. Could you clarify?",
            "nlp_error_unsupported": "I'm not sure how to help with that. Try asking me to create, update, or check your tasks."
        }
    
    def get_translation(self, key: str, locale: str = "en", **kwargs) -> str:
        """
        Get a translated string for the given key and locale
        """
        if locale not in self.supported_locales:
            locale = "en"  # Fallback to English
        
        translations = self.translations.get(locale, {})
        translation = translations.get(key, self.translations["en"].get(key, key))
        
        # Format with provided arguments
        try:
            return translation.format(**kwargs)
        except KeyError:
            # If formatting fails, return the original translation
            return translation
    
    def get_supported_locales(self) -> List[str]:
        """
        Get list of supported locales
        """
        return self.supported_locales[:]
    
    def add_locale(self, locale: str, translations: Dict[str, str]):
        """
        Add a new locale with its translations
        """
        if locale not in self.supported_locales:
            self.supported_locales.append(locale)
        
        self.translations[locale] = translations
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection based on common words
        Note: This is a simplified implementation. In production, use a proper NLP library.
        """
        text_lower = text.lower()
        
        # Common words in different languages
        lang_indicators = {
            "es": ["hola", "tarea", "crear", "actualizar", "completar", "eliminar", "por favor"],
            "fr": ["bonjour", "tâche", "créer", "mettre à jour", "compléter", "supprimer", "s'il vous plaît"],
            "de": ["hallo", "aufgabe", "erstellen", "aktualisieren", "abschließen", "löschen", "bitte"],
            "ja": ["こんにちは", "タスク", "作成", "更新", "完了", "削除"],  # Katakana/Hiragana indicators
            "zh": ["你好", "任务", "创建", "更新", "完成", "删除"]  # Simplified Chinese indicators
        }
        
        scores = {}
        for lang, words in lang_indicators.items():
            scores[lang] = sum(1 for word in words if word in text_lower)
        
        # Return the language with the highest score, default to English
        detected_lang = max(scores, key=scores.get) if scores else "en"
        return detected_lang if scores[detected_lang] > 0 else "en"
    
    def translate_response(self, response: str, target_locale: str, source_locale: str = "en") -> str:
        """
        Translate a response from source locale to target locale
        Note: This is a simplified implementation. In production, use a proper translation API.
        """
        # For this implementation, we'll just return the original response
        # since we don't have a translation API integrated
        return response


# Global i18n manager instance
i18n_manager = I18nManager()


def get_i18n_manager() -> I18nManager:
    """
    Get the global i18n manager instance
    """
    return i18n_manager


# Example usage functions
def get_localized_response(key: str, locale: str = "en", **kwargs) -> str:
    """
    Get a localized response for a given key
    """
    i18n = get_i18n_manager()
    return i18n.get_translation(key, locale, **kwargs)


def detect_user_language(text: str) -> str:
    """
    Detect the language of the user's input
    """
    i18n = get_i18n_manager()
    return i18n.detect_language(text)