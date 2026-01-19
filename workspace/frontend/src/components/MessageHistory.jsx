import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/atom-one-dark.css';
import './MessageHistory.css';

function MessageHistory({ messages }) {
  // Функция для обработки текста - заменяем \n на реальные переносы
  const processText = (text) => {
    if (!text) return '';
    // Заменяем экранированные \n на реальные переносы строк
    return text.replace(/\\n/g, '\n');
  };

  return (
    <div className="message-history">
      {messages.map((message) => (
        <div key={message.id} className={`message-bubble ${message.sender}`}>
          <div className="message-sender">
            {message.sender === 'user' ? 'Вы' : 'Бот'}
          </div>
          <div className="message-text">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                // Кастомные стили для code blocks
                code({node, inline, className, children, ...props}) {
                  return inline ? (
                    <code className="inline-code" {...props}>
                      {children}
                    </code>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
                // Кастомные стили для ссылок
                a({node, children, ...props}) {
                  return (
                    <a {...props} target="_blank" rel="noopener noreferrer" className="markdown-link">
                      {children}
                    </a>
                  );
                }
              }}
            >
              {processText(message.text)}
            </ReactMarkdown>
          </div>
        </div>
      ))}
    </div>
  );
}

export default MessageHistory;
