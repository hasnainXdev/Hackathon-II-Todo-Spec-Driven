export interface Task {
  id: string;
  title: string;
  description?: string;
  completion_status: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface UserPreference {
  id: string;
  user_id: string;
  preference_key: string;
  preference_value: string;
  created_at: string;
  updated_at: string;
}