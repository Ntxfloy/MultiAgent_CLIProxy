// utils/storage.js

const CONVERSATIONS_STORAGE_KEY = 'cyberpunk-ai-chat-conversations';
const SELECTED_MODEL_STORAGE_KEY = 'cyberpunk-ai-chat-selected-model';

/**
 * Loads conversations from local storage.
 * @returns {Array} An array of conversation objects, or an empty array if none found.
 */
export const loadConversations = () => {
  try {
    const serializedState = localStorage.getItem(CONVERSATIONS_STORAGE_KEY);
    if (serializedState === null) {
      return [];
    }
    const conversations = JSON.parse(serializedState);
    // Ensure conversations are sorted by timestamp, newest first
    return conversations.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  } catch (error) {
    console.error("Error loading conversations from local storage:", error);
    return [];
  }
};

/**
 * Saves conversations to local storage.
 * @param {Array} conversations - An array of conversation objects to save.
 */
export const saveConversations = (conversations) => {
  try {
    const serializedState = JSON.stringify(conversations);
    localStorage.setItem(CONVERSATIONS_STORAGE_KEY, serializedState);
  } catch (error) {
    console.error("Error saving conversations to local storage:", error);
  }
};

/**
 * Loads the selected AI model from local storage.
 * @returns {string|null} The selected model name, or null if not found.
 */
export const loadSelectedModel = () => {
  try {
    return localStorage.getItem(SELECTED_MODEL_STORAGE_KEY);
  } catch (error) {
    console.error("Error loading selected model from local storage:", error);
    return null;
  }
};

/**
 * Saves the selected AI model to local storage.
 * @param {string} modelName - The name of the model to save.
 */
export const saveSelectedModel = (modelName) => {
  try {
    localStorage.setItem(SELECTED_MODEL_STORAGE_KEY, modelName);
  } catch (error) {
    console.error("Error saving selected model to local storage:", error);
  }
};
