import json
import os

# Путь к JSON
json_path = os.path.join(os.path.dirname(__file__), "merged_rules_clean.json")
print(f"Ищем файл: {json_path}")

# Проверяем, существует ли файл
if os.path.exists(json_path):
    print("✅ Файл найден")
    
    # Читаем
    with open(json_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    print(f"✅ Загружено {len(rules)} правил")
    print(f"Первое правило: {rules[0] if rules else 'пусто'}")
    
    # Проверяем структуру
    if rules:
        print(f"Ключи первого правила: {rules[0].keys()}")
else:
    print("❌ Файл НЕ найден")