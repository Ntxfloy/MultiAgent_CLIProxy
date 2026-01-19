"""
Тестирует ВСЕ модели из cliProxy и сохраняет рабочие в JSON
"""
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8317/v1"
API_KEY = "test-key-123"

def test_model(model_id: str) -> dict:
    """Тестирует одну модель"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": "Say OK"}],
                "max_tokens": 10
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "model": model_id,
                "status": "✅ OK",
                "response": content[:50],
                "error": None
            }
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", response.text)
            
            status = "❌ FAIL"
            if response.status_code == 429:
                status = "⚠️ RATE_LIMIT"
            elif response.status_code >= 500:
                status = "⚠️ SERVER_ERROR"
            elif response.status_code in [401, 403]:
                status = "🔒 AUTH_ERROR"
            
            return {
                "model": model_id,
                "status": status,
                "response": None,
                "error": f"[{response.status_code}] {error_msg}"[:100]
            }
            
    except Exception as e:
        return {
            "model": model_id,
            "status": "❌ FAIL",
            "response": None,
            "error": str(e)[:100]
        }

def main():
    print("\n" + "="*60)
    print("🧪 TESTING ALL MODELS FROM CLIPROXY")
    print("="*60 + "\n")
    
    # Получаем список всех моделей
    response = requests.get(
        f"{BASE_URL}/models",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    
    all_models = [m["id"] for m in response.json()["data"]]
    print(f"📋 Found {len(all_models)} models\n")
    
    # Тестируем все модели параллельно (по 5 за раз)
    results = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_model = {executor.submit(test_model, model): model for model in all_models}
        
        for i, future in enumerate(as_completed(future_to_model), 1):
            result = future.result()
            results.append(result)
            
            # Показываем прогресс
            print(f"[{i}/{len(all_models)}] {result['status']} {result['model']}")
            if result['error']:
                print(f"      Error: {result['error']}")
    
    # Сортируем по статусу
    working = [r for r in results if r['status'] == '✅ OK']
    rate_limited = [r for r in results if 'RATE_LIMIT' in r['status']]
    failed = [r for r in results if r['status'] not in ['✅ OK', '⚠️ RATE_LIMIT']]
    
    print("\n" + "="*60)
    print(f"✅ Working: {len(working)}")
    print(f"⚠️  Rate Limited: {len(rate_limited)}")
    print(f"❌ Failed: {len(failed)}")
    print("="*60 + "\n")
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = {
        "timestamp": timestamp,
        "total": len(all_models),
        "working": [r['model'] for r in working],
        "rate_limited": [r['model'] for r in rate_limited],
        "failed": [r['model'] for r in failed],
        "details": results
    }
    
    filename = f"model_test_results_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {filename}\n")
    
    # Показываем рабочие модели по провайдерам
    if working:
        print("✅ WORKING MODELS BY PROVIDER:\n")
        
        # Группируем по провайдерам
        providers = {}
        for r in working:
            # Определяем провайдера по префиксу
            if r['model'].startswith('gpt-'):
                provider = 'OpenAI'
            elif r['model'].startswith('gemini-') and not r['model'].startswith('gemini-claude'):
                provider = 'Google'
            elif r['model'].startswith('gemini-claude') or r['model'].startswith('gpt-oss'):
                provider = 'Antigravity'
            elif r['model'].startswith('kiro-'):
                provider = 'Kiro'
            elif r['model'].startswith('tab_'):
                provider = 'Antigravity'
            else:
                provider = 'Other'
            
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(r['model'])
        
        for provider, models in sorted(providers.items()):
            print(f"  {provider} ({len(models)}):")
            for model in sorted(models):
                print(f"    - {model}")
            print()
    
    return output

if __name__ == "__main__":
    main()
