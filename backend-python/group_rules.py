import json
import re

# Загружаем оригинальный JSON
with open("merged_rules_clean.json", "r", encoding="utf-8") as f:
    all_rules = json.load(f)

# Словарь для группировки правил по диагнозам
groups = {
    "I21": {  # ИМпST (инфаркт миокарда)
        "keywords": ["ИМпST", "инфаркт миокарда", "острый коронарный", "стентирование", "ЧКВ", "ТЛТ"],
        "drugs": ["ацетилсалициловая", "клопидогрел", "тикагрелор", "прасугрел", 
                  "аторвастатин", "розувастатин", "эзетимиб",
                  "метопролол", "бисопролол", "карведилол",
                  "лизиноприл", "валсартан", "зофеноприл",
                  "спиронолактон", "эплеренон", "омепразол"],
        "rules": []
    },
    "I50": {  # Хроническая сердечная недостаточность
        "keywords": ["сердечная недостаточность", "ХСН", "застойная", "сниженной ФВ", "LVEF", "фракция выброса"],
        "drugs": ["метопролол", "бисопролол", "карведилол", "лизиноприл", "валсартан",
                  "спиронолактон", "эплеренон", "торасемид", "фуросемид",
                  "дапаглифлозин", "эмпаглифлозин"],
        "rules": []
    },
    "I10": {  # Гипертоническая болезнь
        "keywords": ["гипертоническая", "артериальная гипертензия", "АГ", "гипертония", "повышение АД"],
        "drugs": ["лизиноприл", "валсартан", "амлодипин", "моксонидин", "лозартан"],
        "rules": []
    },
    "E11": {  # Сахарный диабет 2 типа
        "keywords": ["сахарный диабет", "СД", "диабет", "глюкоза", "HbA1c"],
        "drugs": ["метформин", "дапаглифлозин", "эмпаглифлозин", "глибенкламид", "инсулин"],
        "rules": []
    },
    "I48": {  # Фибрилляция предсердий
        "keywords": ["фибрилляция предсердий", "мерцательная аритмия", "ФП", "трепетание"],
        "drugs": ["ривароксабан", "апиксабан", "дабигатрана", "варфарин"],
        "rules": []
    }
}

# Вспомогательная функция для определения группы правила
def get_rule_group(rule):
    drug = rule.get("drug", "").lower()
    condition = rule.get("condition", "").lower()
    
    # Сначала проверяем по ключевым словам в condition
    for group_id, group_info in groups.items():
        for keyword in group_info["keywords"]:
            if keyword.lower() in condition:
                return group_id
    
    # Потом проверяем по препарату
    for group_id, group_info in groups.items():
        for critical_drug in group_info["drugs"]:
            if critical_drug in drug:
                return group_id
    
    return "OTHER"

# Группируем правила
for rule in all_rules:
    group_id = get_rule_group(rule)
    
    if group_id in groups:
        groups[group_id]["rules"].append(rule)
    else:
        # Для OTHER создаём группу, если нужно
        if "OTHER" not in groups:
            groups["OTHER"] = {"keywords": [], "drugs": [], "rules": []}
        groups["OTHER"]["rules"].append(rule)

# Удаляем дубликаты в каждой группе
for group_id, group_info in groups.items():
    seen = set()
    unique = []
    for rule in group_info["rules"]:
        key = (rule.get("drug", ""), rule.get("dosage", ""))
        if key not in seen:
            seen.add(key)
            unique.append(rule)
    group_info["rules"] = unique

# Сохраняем каждую группу в отдельный файл
print("\n📊 СТАТИСТИКА ГРУППИРОВКИ ПРАВИЛ:")
print("=" * 50)

for group_id, group_info in groups.items():
    count = len(group_info["rules"])
    print(f"   {group_id}: {count} правил")
    
    # Сохраняем в файл
    if count > 0:
        filename = f"rules_{group_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(group_info["rules"], f, ensure_ascii=False, indent=2)
        print(f"      ✅ Сохранено в {filename}")

# Сохраняем полную группировку
with open("rules_by_diagnosis.json", "w", encoding="utf-8") as f:
    output = {group_id: group_info["rules"] for group_id, group_info in groups.items()}
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n✅ Готово! Правила сгруппированы по диагнозам.")
print("\n📋 Для проверки эпикриза используйте rules_I21.json (ИМпST)")