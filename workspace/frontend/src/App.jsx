import { useState, useEffect, useRef } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import { loadConversations, saveConversations, loadSelectedModel } from './utils/storage';

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [selectedModel, setSelectedModel] = useState('gpt-5.2-codex');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // Changed to true by default
  const isInitialized = useRef(false);

  // Load conversations and model on mount
  useEffect(() => {
    console.log('App mounted, loading data...');
    const loadedConversations = loadConversations();
    const loadedModel = loadSelectedModel();
    
    console.log('Loaded conversations:', loadedConversations);
    console.log('Loaded model:', loadedModel);
    
    setConversations(loadedConversations);
    if (loadedModel) {
      setSelectedModel(loadedModel);
    }
    
    if (loadedConversations.length === 0) {
      handleNewChat();
    } else {
      setActiveConversationId(loadedConversations[0].id);
    }
    
    isInitialized.current = true;
  }, []);

  // Save conversations when they change (but not on first load)
  useEffect(() => {
    if (isInitialized.current && conversations.length > 0) {
      console.log('Saving conversations:', conversations);
      saveConversations(conversations);
    }
  }, [conversations]);

  const handleNewChat = () => {
    const newConversation = {
      id: Date.now(),
      title: 'Новый чат',
      messages: [],
      model: selectedModel,
      timestamp: Date.now()
    };
    setConversations(prev => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
    setIsSidebarOpen(false);
  };

  const handleSelectConversation = (id) => {
    setActiveConversationId(id);
    setIsSidebarOpen(false);
  };

  const handleDeleteConversation = (id) => {
    setConversations(prev => {
      const updated = prev.filter(conv => conv.id !== id);
      if (activeConversationId === id && updated.length > 0) {
        setActiveConversationId(updated[0].id);
      } else if (updated.length === 0) {
        handleNewChat();
      }
      return updated;
    });
  };

  const handleUpdateConversation = (updatedConversation) => {
    setConversations(prev =>
      prev.map(conv => conv.id === updatedConversation.id ? updatedConversation : conv)
    );
  };

  const handleModelChange = (model) => {
    setSelectedModel(model);
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const activeConversation = conversations.find(conv => conv.id === activeConversationId);

  return (
    <div id="root-layout">
      {/* Sidebar Toggle Button - Always visible */}
      <button
        className="sidebar-toggle-button"
        onClick={toggleSidebar}
        aria-controls="sidebar"
        aria-expanded={isSidebarOpen}
        title={isSidebarOpen ? "Скрыть панель" : "Показать панель"}
        style={{
          position: 'fixed',
          top: 'var(--spacing-md)',
          left: isSidebarOpen ? '290px' : 'var(--spacing-md)',
          zIndex: 1002,
          backgroundColor: 'var(--clr-primary)',
          color: 'var(--clr-background)',
          border: 'none',
          borderRadius: '50%',
          width: '40px',
          height: '40px',
          cursor: 'pointer',
          boxShadow: 'var(--glow-primary)',
          transition: 'all var(--transition-speed)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '1.2rem',
          fontWeight: 'bold'
        }}
      >
        {isSidebarOpen ? '◀' : '▶'}
      </button>

      {/* Sidebar */}
      <aside 
        id="sidebar" 
        className={`sidebar-container ${isSidebarOpen ? 'sidebar-visible' : 'sidebar-hidden'}`}
      >
        <div style={{ padding: 'var(--spacing-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--clr-border)' }}>
          <h3 style={{ margin: 0, color: 'var(--clr-primary)' }}>Киберпанк ИИ</h3>
        </div>
        
        <Sidebar
          conversations={conversations}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
          onNewChat={handleNewChat}
          activeConversationId={activeConversationId}
          onModelChange={handleModelChange}
        />
      </aside>

      {/* Main Chat Area */}
      <main className="main-content">
        {activeConversation ? (
          <ChatInterface
            conversation={activeConversation}
            onUpdateConversation={handleUpdateConversation}
            model={selectedModel}
          />
        ) : (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            height: '100%',
            color: 'var(--clr-text-secondary)',
            fontSize: '1.2rem'
          }}>
            Начните новый разговор
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
