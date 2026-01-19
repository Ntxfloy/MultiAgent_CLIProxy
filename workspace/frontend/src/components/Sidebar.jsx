// src/components/Sidebar.jsx
import ConversationList from './ConversationList';
import ModelSelector from './ModelSelector';
import './Sidebar.css';

function Sidebar({ conversations, onSelectConversation, onDeleteConversation, onNewChat, activeConversationId, onModelChange }) {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      overflow: 'hidden'
    }}>
      {/* Model Selector at Top */}
      <div style={{ 
        padding: 'var(--spacing-md)', 
        borderBottom: '1px solid var(--clr-border)',
        flexShrink: 0
      }}>
        <ModelSelector onModelChange={onModelChange} />
      </div>

      <div style={{ 
        padding: 'var(--spacing-md)', 
        borderBottom: '1px solid var(--clr-border)',
        flexShrink: 0
      }}>
        <button 
          onClick={onNewChat}
          style={{ 
            width: '100%',
            padding: 'var(--spacing-md)',
            fontSize: '1rem',
            fontWeight: 'bold',
            backgroundColor: 'var(--clr-primary)',
            color: 'var(--clr-background)',
            border: 'none',
            borderRadius: 'var(--border-radius-sm)',
            cursor: 'pointer'
          }}
        >
          + Новый чат
        </button>
      </div>

      {/* Conversation List - Scrollable */}
      <div style={{ 
        flexGrow: 1, 
        overflowY: 'auto',
        padding: 'var(--spacing-sm)'
      }}>
        <ConversationList
          conversations={conversations}
          onSelectConversation={onSelectConversation}
          onDeleteConversation={onDeleteConversation}
          onNewChat={onNewChat}
          activeConversationId={activeConversationId}
        />
      </div>
    </div>
  );
}

export default Sidebar;
