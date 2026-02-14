export interface Task {
  id: string;
  title: string;
  description?: string;
  completion_status: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
  priority: 'low' | 'medium' | 'high';  // New priority field
  tags: string[];  // New tags field
  due_date?: string;  // Existing due date field
}

export interface UserPreference {
  id: string;
  user_id: string;
  preference_key: string;
  preference_value: string;
  created_at: string;
  updated_at: string;
}