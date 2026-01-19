// src/types.ts

export interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: string; // ISO 8601 string
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  model: string;
  timestamp: string; // ISO 8601 string, for sorting and display
}

export type AIModel = 'GPT-4' | 'GPT-3.5' | 'Claude' | 'Gemini';
