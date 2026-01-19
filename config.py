import os

BASE_URL = "http://127.0.0.1:8317/v1"
API_KEY = "test-key-123"

# Распределение моделей с fallback цепочками
MODELS = {
    "architect": "gpt-5.2-codex",
    "reviewer": "gpt-5.2-codex",
    "manager": "gemini-2.5-pro",
    "coder_frontend": "gemini-2.5-flash",
    "coder_backend": "gemini-2.5-flash",
    "tester": "gemini-2.5-pro"
}

# Fallback цепочки для каждой роли (ТОЛЬКО РАБОТАЮЩИЕ МОДЕЛИ!)
FALLBACK_CHAINS = {
    "architect": [
        "gpt-5.2-codex",           # Основная - лучшая для архитектуры
        "gpt-5.1-codex-max",       # Запасная 1
        "gpt-5.1-codex",           # Запасная 2
        "gpt-5.2",                 # Запасная 3
        "gemini-2.5-pro"           # Последняя надежда
    ],
    "reviewer": [
        "gpt-5.2-codex",           # Основная - лучшая для проверки кода
        "gpt-5.1-codex-max",       # Запасная 1
        "gpt-5.1-codex",           # Запасная 2
        "gpt-5-codex",             # Запасная 3
        "gemini-2.5-pro"           # Последняя надежда
    ],
    "manager": [
        "gemini-2.5-pro",          # Основная - хороший баланс
        "gpt-5.1",                 # Запасная 1
        "gpt-5.2",                 # Запасная 2
        "gpt-5",                   # Запасная 3
        "gemini-2.5-flash"         # Последняя надежда
    ],
    "coder_frontend": [
        "gemini-2.5-flash",        # Основная - быстрая и дешевая
        "gpt-5-codex-mini",        # Запасная 1
        "gemini-3-flash-preview",  # Запасная 2
        "tab_flash_lite_preview",  # Запасная 3
        "gemini-2.5-flash-lite"    # Последняя надежда
    ],
    "coder_backend": [
        "gemini-2.5-flash",        # Основная - быстрая и дешевая
        "gpt-5-codex-mini",        # Запасная 1
        "gemini-3-flash-preview",  # Запасная 2
        "tab_flash_lite_preview",  # Запасная 3
        "gemini-2.5-flash-lite"    # Последняя надежда
    ],
    "tester": [
        "gemini-2.5-pro",          # Основная
        "gpt-5.1",                 # Запасная 1
        "gpt-5.2",                 # Запасная 2
        "gpt-5",                   # Запасная 3
        "gemini-2.5-flash"         # Последняя надежда
    ]
}