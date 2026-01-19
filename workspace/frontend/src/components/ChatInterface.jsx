import { useState, useEffect, useRef } from 'react';
import MessageHistory from './MessageHistory';

const API_ENDPOINT = 'http://localhost:8000/chat';

function ChatInterface({ conversation, onUpdateConversation, model }) {
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const messages = conversation?.messages || [];
  const messageHistoryRef = useRef(null);

  // Scroll to bottom of message history when new messages arrive
  useEffect(() => {
    if (messageHistoryRef.current) {
      messageHistoryRef.current.scrollTop = messageHistoryRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading || !conversation) return;

    const userMessage = { 
      id: Date.now(), 
      text: inputMessage, 
      sender: 'user',
      timestamp: Date.now()
    };
    
    const updatedMessages = [...messages, userMessage];
    let updatedConv = { 
      ...conversation, 
      messages: updatedMessages,
      title: conversation.title === 'Новый чат' && updatedMessages.length === 1 
        ? inputMessage.substring(0, 30) + (inputMessage.length > 30 ? '...' : '')
        : conversation.title
    };
    onUpdateConversation(updatedConv);
    
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      // Формируем историю для API (конвертируем в формат OpenAI)
      const history = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));

      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: inputMessage, 
          model,
          history  // Отправляем историю
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Network response was not ok');
      }

      const data = await response.json();
      const botMessage = { 
        id: Date.now() + 1, 
        text: data.response, 
        sender: 'bot',
        timestamp: Date.now()
      };
      
      updatedConv = {
        ...updatedConv,
        messages: [...updatedConv.messages, botMessage]
      };
      onUpdateConversation(updatedConv);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Ошибка: Не удалось подключиться к серверу. Попробуйте снова.');
      const errorMessage = {
        id: Date.now() + 1, 
        text: `[СИСТЕМНАЯ ОШИБКА]: ${err.message}`, 
        sender: 'bot', 
        isError: true,
        timestamp: Date.now()
      };
      updatedConv = {
        ...updatedConv,
        messages: [...updatedConv.messages, errorMessage]
      };
      onUpdateConversation(updatedConv);
    } finally {
      setIsLoading(false);
    }
  };

  // Обработка нажатия клавиш
  const handleKeyDown = (e) => {
    // Enter без Shift - отправить
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e);
    }
    // Shift+Enter - перенос строки (по умолчанию работает в textarea)
  };

  return (
    <div className="chat-interface" style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      width: '100%'
    }}>
      {/* Message History Area */}
      <div 
        className="message-history-container" 
        ref={messageHistoryRef}
        style={{
          flexGrow: 1,
          overflowY: 'auto',
          padding: 'var(--spacing-lg)',
          width: '100%'
        }}
      >
        {messages.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            color: 'var(--clr-text-secondary)',
            padding: 'var(--spacing-xxl)',
            fontSize: '1.2rem'
          }}>
            <h2 style={{ color: 'var(--clr-primary)', marginBottom: 'var(--spacing-lg)' }}>
              НЕОНОВЫЙ ЧАТБОТ
            </h2>
            <p>Начните печатать, чтобы начать разговор...</p>
          </div>
        ) : (
          <>
            <MessageHistory messages={messages} />
            {isLoading && (
              <div className="loading-indicator" style={{
                color: 'var(--clr-primary)',
                padding: 'var(--spacing-md)',
                textAlign: 'center'
              }}>
                <span className="dot">.</span><span className="dot">.</span><span className="dot">.</span> Обработка...
              </div>
            )}
          </>
        )}
      </div>

      {/* Input Form - Fixed at Bottom */}
      <form 
        className="chat-input-form" 
        onSubmit={sendMessage}
        style={{
          padding: 'var(--spacing-lg)',
          backgroundColor: 'var(--clr-background)',
          display: 'flex',
          gap: 'var(--spacing-sm)',
          width: '100%',
          alignItems: 'flex-end'
        }}
      >
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Введите ваше сообщение... (Enter - отправить, Shift+Enter - новая строка)"
          disabled={isLoading}
          rows={1}
          style={{
            flexGrow: 1,
            padding: 'var(--spacing-md)',
            fontSize: '1rem',
            backgroundColor: 'var(--clr-input-bg)',
            border: '1px solid var(--clr-input-border)',
            borderRadius: '24px',
            color: 'var(--clr-text-primary)',
            outline: 'none',
            resize: 'none',
            minHeight: '48px',
            maxHeight: '200px',
            overflow: 'auto',
            fontFamily: 'inherit',
            lineHeight: '1.5'
          }}
        />
        <button 
          type="submit" 
          disabled={isLoading || !inputMessage.trim()}
          style={{
            padding: '0 var(--spacing-xl)',
            fontSize: '1rem',
            fontWeight: 'bold',
            backgroundColor: isLoading || !inputMessage.trim() ? 'var(--clr-text-secondary)' : 'var(--clr-primary)',
            color: 'var(--clr-background)',
            border: 'none',
            borderRadius: '24px',
            cursor: isLoading || !inputMessage.trim() ? 'not-allowed' : 'pointer',
            minWidth: '100px'
          }}
        >
          {isLoading ? 'Отправка...' : 'Отправить'}
        </button>
      </form>
      
      {error && (
        <div style={{
          position: 'fixed',
          bottom: 'var(--spacing-lg)',
          right: 'var(--spacing-lg)',
          backgroundColor: '#ff0000',
          color: '#fff',
          padding: 'var(--spacing-md)',
          borderRadius: 'var(--border-radius-sm)',
          boxShadow: 'var(--glow-secondary)',
          maxWidth: '400px',
          zIndex: 1000
        }}>
          {error}
        </div>
      )}
    </div>
  );
}

export default ChatInterface;
