// src/components/ConversationList.jsx
import './ConversationList.css';

function ConversationList({ conversations, onSelectConversation, onDeleteConversation, activeConversationId }) {
  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const getPreview = (messages) => {
    if (messages && messages.length > 0) {
      const userMessage = messages.find(msg => msg.sender === 'user');
      return userMessage ? userMessage.text.substring(0, 50) + (userMessage.text.length > 50 ? '...' : '') : 'Нет сообщений';
    }
    return 'Нет сообщений';
  };

  return (
    <div className="conversation-list-container">
      <div className="conversation-list">
        {conversations.length === 0 ? (
          <p style={{ 
            textAlign: 'center', 
            color: 'var(--clr-text-secondary)',
            padding: 'var(--spacing-lg)'
          }}>
            Пока нет разговоров.
          </p>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${conv.id === activeConversationId ? 'active' : ''}`}
              onClick={() => onSelectConversation(conv.id)}
              style={{
                padding: 'var(--spacing-md)',
                marginBottom: 'var(--spacing-sm)',
                backgroundColor: conv.id === activeConversationId ? 'var(--clr-active-bg)' : 'var(--clr-input-bg)',
                border: `1px solid ${conv.id === activeConversationId ? 'var(--clr-primary)' : 'var(--clr-border)'}`,
                borderRadius: 'var(--border-radius-sm)',
                cursor: 'pointer',
                transition: 'all var(--transition-speed)',
                position: 'relative'
              }}
            >
              <div className="conversation-info">
                <h3 style={{ 
                  margin: '0 0 var(--spacing-xs) 0',
                  color: 'var(--clr-text-primary)',
                  fontSize: '0.95rem',
                  fontWeight: 'bold'
                }}>
                  {conv.title || 'Без названия'}
                </h3>
                <p style={{ 
                  margin: '0 0 var(--spacing-xs) 0',
                  color: 'var(--clr-text-secondary)',
                  fontSize: '0.75rem'
                }}>
                  {formatDate(conv.timestamp)}
                </p>
                <p style={{ 
                  margin: 0,
                  color: 'var(--clr-text-secondary)',
                  fontSize: '0.8rem',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {getPreview(conv.messages)}
                </p>
              </div>
              <button
                className="delete-conversation-button"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteConversation(conv.id);
                }}
                style={{
                  position: 'absolute',
                  top: 'var(--spacing-sm)',
                  right: 'var(--spacing-sm)',
                  padding: 'var(--spacing-xs) var(--spacing-sm)',
                  fontSize: '0.75rem',
                  backgroundColor: 'transparent',
                  color: 'var(--clr-text-secondary)',
                  border: '1px solid var(--clr-border)',
                  borderRadius: 'var(--border-radius-sm)',
                  cursor: 'pointer',
                  minWidth: 'auto',
                  minHeight: 'auto'
                }}
              >
                ✖
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ConversationList;
