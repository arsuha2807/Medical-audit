import json

# Загружаем оригинальный JSON
with open("merged_rules_clean.json", "r", encoding="utf-8") as f:
    all_rules = json.load(f)

# Критические препараты для ИМпST (которые ОБЯЗАТЕЛЬНО должны быть назначены)
CRITICAL_DRUGS = [
    "ацетилсалициловая кислота",
    "АСК",
    "клопидогрел",
    "тикагрелор",
    "прасугрел",
    "аторвастатин",
    "розувастатин",
    "метопролол",
    "бисопролол",
    "карведилол",
    "лизиноприл",
    "валсартан",
    "зофеноприл",
    "рамиприл",
    "эналаприл",
    "спиронолактон",
    "эплеренон",
]

# Функция для проверки, нужно ли правило
def is_critical_rule(rule):
    drug = rule.get("drug", "").lower()
    
    # Проверяем, входит ли препарат в критический список
    for critical in CRITICAL_DRUGS:
        if critical in drug:
            return True
    
    # Дополнительно: ингибиторы протонного насоса (важно для ДАТТ)
    if "протонный" in drug or "омепразол" in drug or "пантопразол" in drug:
        return True
    
    return False

# Фильтруем
filtered_rules = [rule for rule in all_rules if is_critical_rule(rule)]

# Убираем дубликаты (по препарату и дозировке)
seen = set()
unique_rules = []
for rule in filtered_rules:
    key = (rule.get("drug", ""), rule.get("dosage", ""))
    if key not in seen:
        seen.add(key)
        unique_rules.append(rule)

print(f"Оригинальных правил: {len(all_rules)}")
print(f"После фильтрации: {len(unique_rules)}")

# Сохраняем отфильтрованный JSON
with open("merged_rules_filtered.json", "w", encoding="utf-8") as f:
    json.dump(unique_rules, f, ensure_ascii=False, indent=2)

print("✅ Сохранено в merged_rules_filtered.json")

# Показываем, какие правила остались
print("\n📋 Оставшиеся правила:")
for rule in unique_rules:
    print(f"  - {rule['drug']}: {rule['dosage'][:50]}...")