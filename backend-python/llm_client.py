import json
import httpx
import fitz
import re
from typing import List, Dict

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

async def extract_rules_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Извлекает правила из клинических рекомендаций через Qwen
    """
    print(f"📖 Читаем PDF: {pdf_path}")
    
    # Проверяем, существует ли файл
    import os
    if not os.path.exists(pdf_path):
        print(f"❌ Файл не найден: {pdf_path}")
        return get_default_rules()
    
    # Извлекаем текст из PDF
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        print(f"📄 Извлечено {len(text)} символов")
    except Exception as e:
        print(f"❌ Ошибка чтения PDF: {e}")
        return get_default_rules()
    
    # Если текста слишком много, берем первые 20000 символов + разделы про лекарства
    if len(text) > 20000:
        # Ищем разделы про лекарственную терапию
        drug_sections = []
        keywords = ["антитромбоцитарн", "статины", "бета-блокатор", "иАПФ", "антагонист альдостерон", "липидснижающ"]
        
        for keyword in keywords:
            idx = text.lower().find(keyword)
            if idx != -1:
                start = max(0, idx - 500)
                end = min(len(text), idx + 2000)
                drug_sections.append(text[start:end])
        
        if drug_sections:
            text = " ".join(drug_sections)
        else:
            text = text[:20000]
    
    prompt = f"""Ты — медицинский эксперт. Проанализируй фрагмент клинических рекомендаций по лечению острого инфаркта миокарда с подъемом ST (ИМпST).

Извлеки рекомендации по следующим группам препаратов:
- Ацетилсалициловая кислота (аспирин)
- Клопидогрел (плавикс, зилт)
- Аторвастатин, розувастатин (статины)
- Метопролол, бисопролол, карведилол (бета-блокаторы)
- Лизиноприл, валсартан (иАПФ/БРА)
- Спиронолактон (антагонист альдостерона)

Для каждого найденного препарата укажи:
- drug: точное название на русском
- dosage: дозировка (например, "75 мг/сут" или "40-80 мг/сут")
- condition: условие применения (если есть)

Верни ТОЛЬКО JSON массив. Если дозировка не найдена, используй стандартную.
Если препарат не упоминается в тексте, НЕ включай его в ответ.

Пример ответа:
[
    {"drug": "Ацетилсалициловая кислота", "dosage": "75-100 мг/сут", "condition": ""},
    {"drug": "Клопидогрел", "dosage": "75 мг/сут", "condition": ""},
    {"drug": "Спиронолактон", "dosage": "25 мг/сут", "condition": "ФВ ЛЖ < 40%"}
]

Фрагмент клинических рекомендаций:
{text}
"""
    
    try:
        print("🔄 Отправляем запрос к Qwen (может занять 1-2 минуты)...")
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Низкая температура для предсказуемых ответов
                        "num_predict": 2048  # Максимум токенов в ответе
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                resp_text = result.get("response", "")
                print(f"📝 Ответ Qwen получен ({len(resp_text)} символов)")
                
                # Пробуем извлечь JSON
                rules = extract_json_from_response(resp_text)
                
                if rules:
                    print(f"✅ Qwen извлекла {len(rules)} правил")
                    for r in rules:
                        print(f"   - {r['drug']}: {r['dosage']} ({r.get('condition', '')})")
                    return rules
                else:
                    print("❌ Не удалось извлечь JSON из ответа")
                    print(f"Ответ Qwen: {resp_text[:500]}...")
                    return get_default_rules()
            else:
                print(f"❌ Ошибка Qwen: HTTP {response.status_code}")
                return get_default_rules()
                
    except httpx.TimeoutException:
        print("❌ Таймаут подключения к Qwen (более 3 минут)")
        return get_default_rules()
    except Exception as e:
        print(f"❌ Ошибка подключения к Qwen: {e}")
        return get_default_rules()


def extract_json_from_response(text: str) -> List[Dict]:
    """
    Извлекает JSON массив из ответа Qwen
    """
    # Пробуем найти JSON между квадратными скобками
    start = text.find('[')
    end = text.rfind(']')
    
    if start != -1 and end != -1 and end > start:
        json_str = text[start:end+1]
        try:
            rules = json.loads(json_str)
            if isinstance(rules, list):
                return rules
        except json.JSONDecodeError:
            # Пробуем починить распространенные ошибки
            # Убираем лишние запятые
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            try:
                rules = json.loads(json_str)
                if isinstance(rules, list):
                    return rules
            except:
                pass
    
    return []


def get_default_rules() -> List[Dict]:
    """
    Резервные правила на случай ошибки Qwen
    """
    return [
        {"drug": "Ацетилсалициловая кислота", "dosage": "75-100 мг/сут", "condition": "", "contraindication": ""},
        {"drug": "Клопидогрел", "dosage": "75 мг/сут", "condition": "", "contraindication": ""},
        {"drug": "Аторвастатин", "dosage": "40-80 мг/сут", "condition": "", "contraindication": ""},
        {"drug": "Метопролол", "dosage": "25-100 мг/сут", "condition": "", "contraindication": ""},
        {"drug": "Лизиноприл", "dosage": "5-10 мг/сут", "condition": "", "contraindication": ""},
        {"drug": "Спиронолактон", "dosage": "25 мг/сут", "condition": "ФВ ЛЖ < 40%", "contraindication": ""},
    ]


# Синхронная обертка для совместимости (если нужно)
def extract_rules_sync(pdf_path: str) -> List[Dict]:
    import asyncio
    return asyncio.run(extract_rules_from_pdf(pdf_path))