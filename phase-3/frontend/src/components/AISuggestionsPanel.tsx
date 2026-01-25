'use client';

import { useState, useEffect } from 'react';
import { FaLightbulb, FaTimes, FaCheck, FaRedo } from 'react-icons/fa';

interface Suggestion {
  type: string;
  title: string;
  description?: string;
  confidence?: number;
  category?: string;
  task_id?: string;
  task_title?: string;
  suggested_priority?: string;
  current_priority?: string;
  suggestion_reason?: string;
  urgency?: number;
  reason?: string;
  predicted_priority?: string;
}

interface AISuggestionsPanelProps {
  suggestions: Suggestion[];
  onAccept: (suggestion: Suggestion) => void;
  onDismiss: (suggestion: Suggestion) => void;
  onRegenerate: () => void;
  isVisible: boolean;
  onClose: () => void;
}

export default function AISuggestionsPanel({
  suggestions,
  onAccept,
  onDismiss,
  onRegenerate,
  isVisible,
  onClose
}: AISuggestionsPanelProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [fade, setFade] = useState(true);

  // Reset to first suggestion when suggestions change
  useEffect(() => {
    setCurrentIndex(0);
    setFade(true);
  }, [suggestions]);

  if (!isVisible || suggestions.length === 0) {
    return null;
  }

  const currentSuggestion = suggestions[currentIndex];

  const handleNext = () => {
    if (currentIndex < suggestions.length - 1) {
      setFade(false);
      setTimeout(() => {
        setCurrentIndex(prev => prev + 1);
        setFade(true);
      }, 150); // Match fade transition duration
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setFade(false);
      setTimeout(() => {
        setCurrentIndex(prev => prev - 1);
        setFade(true);
      }, 150); // Match fade transition duration
    }
  };

  const handleAccept = () => {
    if (currentSuggestion) {
      onAccept(currentSuggestion);
      if (currentIndex < suggestions.length - 1) {
        handleNext();
      }
    }
  };

  const handleDismiss = () => {
    if (currentSuggestion) {
      onDismiss(currentSuggestion);
      if (currentIndex < suggestions.length - 1) {
        handleNext();
      } else if (currentIndex > 0) {
        handlePrev();
      }
    }
  };

  // Format suggestion based on its type
  const formatSuggestion = (suggestion: Suggestion) => {
    switch (suggestion.type) {
      case 'creation':
        return (
          <div>
            <h3 className="font-bold text-lg flex items-center">
              <FaLightbulb className="mr-2 text-yellow-400" /> Suggested Task
            </h3>
            <p className="text-xl font-semibold mt-2 text-white">{suggestion.title}</p>
            {suggestion.description && (
              <p className="text-gray-400 mt-1">{suggestion.description}</p>
            )}
            {suggestion.category && (
              <span className="inline-block bg-blue-900/50 text-blue-300 text-xs px-2 py-1 rounded-full mt-2 border border-blue-800">
                {suggestion.category}
              </span>
            )}
            {suggestion.confidence !== undefined && (
              <div className="mt-2">
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${suggestion.confidence * 100}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">Confidence: {(suggestion.confidence * 100).toFixed(0)}%</p>
              </div>
            )}
          </div>
        );

      case 'prioritization':
        return (
          <div>
            <h3 className="font-bold text-lg flex items-center">
              <FaLightbulb className="mr-2 text-purple-400" /> Priority Suggestion
            </h3>
            <p className="text-lg font-medium mt-2 text-white">Task: {suggestion.task_title}</p>
            <div className="flex items-center mt-2">
              <span className="text-gray-400 mr-2">Current:</span>
              <span className={`px-2 py-1 rounded ${suggestion.current_priority === 'high' ? 'bg-red-900/50 text-red-300 border border-red-800' :
                suggestion.current_priority === 'medium' ? 'bg-yellow-900/50 text-yellow-300 border border-yellow-800' :
                  'bg-green-900/50 text-green-300 border border-green-800'}`}>
                {suggestion.current_priority}
              </span>
              <span className="mx-2 text-gray-500">→</span>
              <span className="text-gray-400 mr-2">Suggested:</span>
              <span className={`px-2 py-1 rounded font-bold ${suggestion.suggested_priority === 'high' ? 'bg-red-600 text-white' :
                suggestion.suggested_priority === 'medium' ? 'bg-yellow-600 text-gray-900' :
                  'bg-green-600 text-white'}`}>
                {suggestion.suggested_priority}
              </span>
            </div>
            {suggestion.reason && (
              <p className="text-sm text-gray-400 mt-2 italic">Reason: {suggestion.reason}</p>
            )}
            {suggestion.confidence !== undefined && (
              <p className="text-xs text-gray-400 mt-2">Confidence: {(suggestion.confidence * 100).toFixed(0)}%</p>
            )}
          </div>
        );

      case 'completion':
        return (
          <div>
            <h3 className="font-bold text-lg flex items-center">
              <FaLightbulb className="mr-2 text-green-400" /> Completion Suggestion
            </h3>
            <p className="text-lg font-medium mt-2 text-white">Complete: {suggestion.task_title}</p>
            {suggestion.suggestion_reason && (
              <p className="text-gray-400 mt-2">{suggestion.suggestion_reason}</p>
            )}
            {suggestion.urgency !== undefined && (
              <div className="mt-2">
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-red-500 h-2 rounded-full"
                    style={{ width: `${suggestion.urgency * 100}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">Urgency: {(suggestion.urgency * 100).toFixed(0)}%</p>
              </div>
            )}
          </div>
        );

      case 'ai_recommendation':
        return (
          <div>
            <h3 className="font-bold text-lg flex items-center">
              <FaLightbulb className="mr-2 text-indigo-400" /> AI Recommendation
            </h3>
            <p className="text-xl font-semibold mt-2 text-white">{suggestion.title}</p>
            {suggestion.category && (
              <span className="inline-block bg-indigo-900/50 text-indigo-300 text-xs px-2 py-1 rounded-full mt-2 border border-indigo-800">
                {suggestion.category}
              </span>
            )}
            {suggestion.predicted_priority && (
              <div className="mt-2">
                <span className="text-gray-400 mr-2">Predicted Priority:</span>
                <span className={`px-2 py-1 rounded ${suggestion.predicted_priority === 'high' ? 'bg-red-600 text-white' :
                  suggestion.predicted_priority === 'medium' ? 'bg-yellow-600 text-gray-900' :
                    'bg-green-600 text-white'}`}>
                  {suggestion.predicted_priority}
                </span>
              </div>
            )}
            {suggestion.confidence !== undefined && (
              <p className="text-xs text-gray-400 mt-2">Confidence: {(suggestion.confidence * 100).toFixed(0)}%</p>
            )}
            {suggestion.reason && (
              <p className="text-sm text-gray-400 mt-2 italic">Based on: {suggestion.reason}</p>
            )}
          </div>
        );

      default:
        return (
          <div>
            <h3 className="font-bold text-lg flex items-center">
              <FaLightbulb className="mr-2 text-gray-400" /> Suggestion
            </h3>
            <p className="text-lg font-medium mt-2 text-white">{suggestion.title || suggestion.task_title}</p>
          </div>
        );
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden flex flex-col border border-gray-700">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-gray-700">
          <h2 className="text-xl font-bold text-white flex items-center">
            <FaLightbulb className="mr-2 text-yellow-400" /> AI Suggestions
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-200 text-2xl"
          >
            <FaTimes />
          </button>
        </div>

        {/* Suggestion Content */}
        <div className="grow p-6 overflow-y-auto text-gray-100">
          {suggestions.length > 0 ? (
            <div className={`transition-opacity duration-150 ${fade ? 'opacity-100' : 'opacity-0'}`}>
              {formatSuggestion(currentSuggestion)}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No suggestions available</p>
          )}
        </div>

        {/* Navigation and Controls */}
        <div className="p-4 border-t bg-gray-900/50 border-gray-700">
          <div className="flex justify-between items-center">
            <div className="flex space-x-2">
              <button
                onClick={handlePrev}
                disabled={currentIndex === 0}
                className={`p-2 rounded-full ${currentIndex === 0 ? 'text-gray-600' : 'text-gray-400 hover:bg-gray-700'}`}
              >
                &lt;
              </button>

              <span className="px-3 py-2 text-gray-300">
                {currentIndex + 1} of {suggestions.length}
              </span>

              <button
                onClick={handleNext}
                disabled={currentIndex === suggestions.length - 1}
                className={`p-2 rounded-full ${currentIndex === suggestions.length - 1 ? 'text-gray-600' : 'text-gray-400 hover:bg-gray-700'}`}
              >
                &gt;
              </button>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={onRegenerate}
                className="p-2 text-gray-400 hover:bg-gray-700 rounded-full"
                title="Regenerate suggestions"
              >
                <FaRedo />
              </button>
            </div>
          </div>

          <div className="flex space-x-3 mt-4">
            <button
              onClick={handleAccept}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg flex items-center justify-center"
            >
              <FaCheck className="mr-2" /> Accept
            </button>

            <button
              onClick={handleDismiss}
              className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg"
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}