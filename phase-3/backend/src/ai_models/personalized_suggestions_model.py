import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import pickle
import os


class PersonalizedSuggestionsAIModel:
    """
    AI model for generating personalized task suggestions based on user behavior
    """
    
    def __init__(self, model_storage_path: str = "./models/personalized_suggestions_model.pkl"):
        self.model_storage_path = model_storage_path
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.clustering_model = KMeans(n_clusters=5, random_state=42)
        self.prediction_model = LogisticRegression(random_state=42)
        self.is_trained = False
        
    def train(self, user_task_data: List[Dict[str, Any]], user_behavior_data: Dict[str, Any]) -> None:
        """
        Train the model on user task and behavior data
        """
        # Prepare text data from task titles and descriptions
        texts = []
        labels = []  # For prediction model (e.g., priority levels)

        for task in user_task_data:
            title = task.get('title', '')
            description = task.get('description', '')
            text = f"{title} {description}".strip()
            texts.append(text)

            # Create labels based on task properties (e.g., priority)
            priority = task.get('priority', 'medium')
            label_map = {'low': 0, 'medium': 1, 'high': 2}
            labels.append(label_map.get(priority, 1))  # Default to medium

        if not texts:
            print("No text data available for training")
            return

        # Vectorize the text data
        X = self.vectorizer.fit_transform(texts)

        # Adjust number of clusters based on the number of samples
        n_samples = X.shape[0]
        n_clusters = min(5, n_samples)  # Use minimum of 5 or number of samples
        if n_clusters < 1:
            n_clusters = 1

        # Reinitialize clustering model with appropriate number of clusters
        self.clustering_model = KMeans(n_clusters=n_clusters, random_state=42)

        # Train clustering model to identify task categories/patterns
        self.clustering_model.fit(X)
        
        # Train prediction model to predict task properties
        if labels:
            self.prediction_model.fit(X, labels)
        
        self.is_trained = True
        
        # Save the trained model
        self.save_model()
        
        print(f"Model trained on {len(texts)} tasks")
    
    def predict_task_priority(self, task_title: str, task_description: str = "") -> Tuple[str, float]:
        """
        Predict the priority level for a new task
        """
        if not self.is_trained:
            # Default prediction if model is not trained
            return "medium", 0.5
        
        # Vectorize the input text
        text = f"{task_title} {task_description}".strip()
        X = self.vectorizer.transform([text])
        
        # Predict priority
        prediction_proba = self.prediction_model.predict_proba(X)[0]
        predicted_class = self.prediction_model.predict(X)[0]
        
        # Map back to priority labels
        label_map = {0: 'low', 1: 'medium', 2: 'high'}
        predicted_priority = label_map[predicted_class]
        
        # Get confidence score (max probability)
        confidence = max(prediction_proba)
        
        return predicted_priority, confidence
    
    def suggest_similar_tasks(self, task_title: str, task_description: str = "", top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Suggest similar tasks based on user's history
        """
        if not self.is_trained:
            return []
        
        # Vectorize the input text
        text = f"{task_title} {task_description}".strip()
        X_input = self.vectorizer.transform([text])
        
        # Get all vectors from the fitted vectorizer (this would need to be stored separately in a real implementation)
        # For this implementation, we'll return an empty list as we don't have the original vectors
        return []
    
    def identify_task_categories(self, user_tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify categories of tasks based on clustering
        """
        if not self.is_trained or not user_tasks:
            return {}
        
        # Prepare text data
        texts = []
        for task in user_tasks:
            title = task.get('title', '')
            description = task.get('description', '')
            text = f"{title} {description}".strip()
            texts.append(text)
        
        # Vectorize the texts
        X = self.vectorizer.transform(texts)
        
        # Predict clusters
        clusters = self.clustering_model.predict(X)
        
        # Group tasks by cluster
        categorized_tasks = {}
        for i, cluster_id in enumerate(clusters):
            cluster_name = f"Category_{cluster_id}"
            if cluster_name not in categorized_tasks:
                categorized_tasks[cluster_name] = []
            categorized_tasks[cluster_name].append(user_tasks[i])
        
        return categorized_tasks
    
    def recommend_new_tasks(self, user_behavior_data: Dict[str, Any], num_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        Recommend new tasks based on user behavior patterns
        """
        recommendations = []
        
        # This is a simplified recommendation approach
        # In a real model, this would use more sophisticated ML techniques
        
        # Get user's most frequent task categories
        category_freq = user_behavior_data.get('category_preferences', {})
        
        # Sort categories by frequency
        sorted_categories = sorted(category_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Generate sample tasks based on frequent categories
        category_tasks = {
            'work': ['schedule team meeting', 'review project proposal', 'prepare presentation'],
            'personal': ['call family member', 'plan weekend activity', 'organize personal space'],
            'health': ['schedule doctor appointment', 'plan workout routine', 'meal prep for the week'],
            'finance': ['review monthly budget', 'pay outstanding bills', 'update financial records'],
            'shopping': ['buy groceries for the week', 'order household supplies', 'compare prices for big purchase'],
            'learning': ['enroll in online course', 'read industry articles', 'practice new skill']
        }
        
        added_tasks = set()
        for category, freq in sorted_categories:
            if len(recommendations) >= num_suggestions:
                break
                
            if category in category_tasks:
                for task_template in category_tasks[category]:
                    if len(recommendations) >= num_suggestions:
                        break
                    
                    task_title = task_template
                    if task_title not in added_tasks:
                        # Predict priority for the recommended task
                        priority, confidence = self.predict_task_priority(task_title)
                        
                        recommendations.append({
                            "title": task_title.capitalize(),
                            "category": category,
                            "predicted_priority": priority,
                            "confidence": confidence,
                            "reason": f"Based on your frequent {category} tasks"
                        })
                        added_tasks.add(task_title)
        
        return recommendations[:num_suggestions]
    
    def save_model(self) -> None:
        """
        Save the trained model to disk
        """
        model_data = {
            'vectorizer': self.vectorizer,
            'clustering_model': self.clustering_model,
            'prediction_model': self.prediction_model,
            'is_trained': self.is_trained
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_storage_path), exist_ok=True)
        
        with open(self.model_storage_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {self.model_storage_path}")
    
    def load_model(self) -> bool:
        """
        Load a trained model from disk
        """
        if not os.path.exists(self.model_storage_path):
            print(f"No saved model found at {self.model_storage_path}")
            return False
        
        with open(self.model_storage_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.clustering_model = model_data['clustering_model']
        self.prediction_model = model_data['prediction_model']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {self.model_storage_path}")
        return True
    
    def update_model(self, new_task_data: List[Dict[str, Any]], user_behavior_data: Dict[str, Any]) -> None:
        """
        Update the model with new data (simplified approach)
        """
        # For this implementation, we'll retrain the model with the combined old and new data
        # In a production system, you might want to implement incremental learning
        
        # Combine with any existing training data if available
        self.train(new_task_data, user_behavior_data)