# Interfaces & Component Contracts

## Components

### `Sidebar.jsx`
**Purpose**: Container for conversation actions and list.

**Props**:
- `conversations: Conversation[]`
- `activeConversationId: string`
- `onSelectConversation(id: string): void`
- `onDeleteConversation(id: string): void`
- `onNewConversation(): void`

**Behavior**:
- Renders `New Chat` button and `ConversationList`.

---

### `ConversationList.jsx`
**Purpose**: Render list of conversation items.

**Props**:
- `conversations: Conversation[]`
- `activeConversationId: string`
- `onSelectConversation(id: string): void`
- `onDeleteConversation(id: string): void`

**Conversation Item UI**:
- Title
- Date
- Preview (first message snippet)
- Delete button

---

### `ModelSelector.jsx`
**Purpose**: Select active AI model.

**Props**:
- `activeModel: ModelName`
- `models: ModelName[]`
- `onChange(model: ModelName): void`

**Behavior**:
- Dropdown with current model label.
- Persist selection via parent handler.

---

### `ChatInterface.jsx`
**Purpose**: Chat display and message entry.

**Props**:
- `conversation: Conversation | null`
- `isTyping: boolean`
- `onSendMessage(content: string): void`

**Behavior**:
- Render message list with timestamps.
- Smooth scroll to latest message.
- Show `typing...` indicator.
- Constrain message width to 800px.

---

## Utility Interfaces

### `utils/storage.js`
**Functions**:
- `loadConversations(): Conversation[]`
- `saveConversations(conversations: Conversation[]): void`
- `loadActiveConversationId(): string | null`
- `saveActiveConversationId(id: string): void`
- `loadActiveModel(): ModelName | null`
- `saveActiveModel(model: ModelName): void`

**Storage Keys**:
- `cyberpunk.conversations`
- `cyberpunk.activeConversationId`
- `cyberpunk.activeModel`

---

## Events & Data Flow
- `App` (or main container) owns state and passes to components.
- `Sidebar` triggers selection/deletion/new conversation events.
- `ModelSelector` changes active model.
- `ChatInterface` sends messages and triggers persistence.

---

## Non-Functional Requirements
- Conversations must be saved immediately after changes.
- Layout must maintain 300px sidebar and 70% chat width.
- UI should keep cyberpunk neon styling.
