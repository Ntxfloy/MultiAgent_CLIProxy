// src/components/ModelSelector.jsx
import React, { useState, useEffect, useRef } from 'react';
import { loadSelectedModel, saveSelectedModel } from '../utils/storage';
import './ModelSelector.css';

// Реальные модели из cliProxy (только рабочие)
const models = [
  { id: 'gpt-5.2-codex', name: 'GPT-5.2 Codex (Best)' },
  { id: 'gpt-5.2', name: 'GPT-5.2' },
  { id: 'gpt-5.1-codex-max', name: 'GPT-5.1 Codex Max' },
  { id: 'gpt-5.1-codex', name: 'GPT-5.1 Codex' },
  { id: 'gpt-5-codex', name: 'GPT-5 Codex' },
  { id: 'gpt-5.1', name: 'GPT-5.1' },
  { id: 'gpt-5', name: 'GPT-5' },
  { id: 'gpt-5-codex-mini', name: 'GPT-5 Codex Mini' },
  { id: 'gpt-5.1-codex-mini', name: 'GPT-5.1 Codex Mini' },
  { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro' },
  { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash' },
  { id: 'gemini-2.5-flash-lite', name: 'Gemini 2.5 Flash Lite (Fast)' },
  { id: 'gemini-3-flash-preview', name: 'Gemini 3 Flash Preview' },
  { id: 'gemini-2.5-computer-use-preview-10-2025', name: 'Gemini Computer Use' },
  { id: 'tab_flash_lite_preview', name: 'Tab Flash Lite' }
];

function ModelSelector({ onModelChange }) {
  const [selectedModel, setSelectedModel] = useState(() => {
    const storedModel = loadSelectedModel();
    return storedModel || models[0].id;
  });
  
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      onModelChange(selectedModel);
      return;
    }
    
    saveSelectedModel(selectedModel);
    onModelChange(selectedModel);
  }, [selectedModel]);

  const handleModelChange = (event) => {
    setSelectedModel(event.target.value);
  };

  return (
    <div className="model-selector-container">
      <label htmlFor="model-select" className="model-label">Модель:</label>
      <select
        id="model-select"
        className="model-dropdown"
        value={selectedModel}
        onChange={handleModelChange}
      >
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default ModelSelector;
