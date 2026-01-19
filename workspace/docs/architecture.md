# System Architecture — Cyberpunk AI Chat UI Improvements

## Goals
- Add a persistent, professional chat UI with sidebar history, model selection, wider chat area, and improved UX.
- Maintain cyberpunk neon aesthetic across new components.
- Ensure architecture is modular, testable, and easy to extend.

## High-Level Architecture

### UI Layers
- **App Shell**: Root layout orchestrating Sidebar, Chat area, and ModelSelector.
- **Sidebar**: Displays conversation history and actions (new, delete, select).
- **Chat Interface**: Displays messages, typing indicator, and input area; handles smooth scrolling.
- **Model Selector**: Drop-down to choose model; persistence via localStorage.

### State & Data Flow
- **Conversation State** (centralized in parent container, e.g., `App` or `ChatPage`):
  - `conversations: Conversation[]`
  - `activeConversationId: string`
  - `activeModel: ModelName`
  - `isTyping: boolean`
- **Persistence** via `utils/storage.js` with localStorage keys:
  - `conversations`
  - `activeConversationId`
  - `activeModel`

### Persistence Lifecycle
1. On app start: load conversations & active model from localStorage.
2. On new message: update conversations array and persist.
3. On model change: update active model and persist.
4. On conversation change/delete: update state and persist.

### UX Behaviors
- Auto-generate conversation title from first user message.
- Show timestamps per message.
- Smooth scroll to new messages.
- Show `typing...` indicator while AI response is pending.

## File Structure
```
src/
  components/
    Sidebar.jsx
    ConversationList.jsx
    ModelSelector.jsx
    ChatInterface.jsx
    Message.jsx
  utils/
    storage.js
  styles/
    (existing cyberpunk theme styles)
  App.jsx
```

## Technology Stack
- **Framework**: React (existing)
- **Styling**: CSS/SCSS or CSS-in-JS (keep existing styling approach)
- **Storage**: Browser `localStorage`
- **Date Formatting**: Native `Date` or existing utility

## Data Models
```ts
ModelName = 'GPT-4' | 'GPT-3.5' | 'Claude' | 'Gemini'

Conversation = {
  id: string,
  title: string,
  model: ModelName,
  timestamp: number,
  messages: Message[]
}

Message = {
  id: string,
  role: 'user' | 'assistant',
  content: string,
  timestamp: number
}
```

## Layout Rules
- Sidebar: fixed 300px width on left.
- Main Chat Area: 70% of screen width.
- Messages: max-width 800px with increased spacing.

## Styling Guidelines
- Neon borders/glows for panels and buttons.
- Accent colors for active conversation and model selector.
- Smooth hover effects.

## Implementation Phases
1. Create new components & data flow.
2. Implement storage utilities.
3. Update ChatInterface layout and behaviors.
4. Apply styling & verify UX.

## Definition of Done
- Sidebar with history works and persists.
- Model selection persists.
- Conversation switching and deletion work.
- Chat area is wider and messages are readable.
- Typing indicator & timestamps work.
- UI retains cyberpunk look.
