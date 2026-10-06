import sqlite3

DB_PATH = "quality_checker.db"

base_rules = [
    {"drug": "Ацетилсалициловая кислота", "dosage": "75-100", "condition": "", "contraindication": ""},
    {"drug": "Клопидогрел", "dosage": "75", "condition": "", "contraindication": ""},
    {"drug": "Аторвастатин", "dosage": "40-80", "condition": "", "contraindication": ""},
    {"drug": "Метопролол", "dosage": "25-100", "condition": "", "contraindication": ""},
    {"drug": "Бисопролол", "dosage": "2.5-10", "condition": "", "contraindication": ""},
    {"drug": "Лизиноприл", "dosage": "5-10", "condition": "", "contraindication": ""},
    {"drug": "Валсартан", "dosage": "40-160", "condition": "", "contraindication": ""},
    {"drug": "Спиронолактон", "dosage": "25", "condition": "ФВ ЛЖ < 40%", "contraindication": ""},
    {"drug": "Омепразол", "dosage": "20", "condition": "Двойная антитромбоцитарная терапия", "contraindication": ""},
]

extra_rules = [
    {"drug": "Лизиноприл", "dosage": "5-10", "condition": "Сахарный диабет", "contraindication": ""},
    {"drug": "Валсартан", "dosage": "40-160", "condition": "Сахарный диабет", "contraindication": ""},
    
    {"drug": "Эзетимиб", "dosage": "10", "condition": "ЛПНП > 1.4 ммоль/л на фоне статина", "contraindication": ""},
    
    {"drug": "Торасемид", "dosage": "5-10", "condition": "ХСН с отеками", "contraindication": ""},
    {"drug": "Фуросемид", "dosage": "20-40", "condition": "ХСН с отеками", "contraindication": ""},
    
    {"drug": "Метформин", "dosage": "1000-2000", "condition": "Сахарный диабет 2 типа", "contraindication": ""},
    {"drug": "Дапаглифлозин", "dosage": "10", "condition": "Сахарный диабет + ХСН", "contraindication": ""},
    {"drug": "Эмпаглифлозин", "dosage": "10", "condition": "Сахарный диабет + ХСН", "contraindication": ""},
    
    {"drug": "Амлодипин", "dosage": "5-10", "condition": "Недостижение целевого АД", "contraindication": ""},
    
    {"drug": "Ривароксабан", "dosage": "15-20", "condition": "Фибрилляция предсердий", "contraindication": ""},
    {"drug": "Апиксабан", "dosage": "5", "condition": "Фибрилляция предсердий", "contraindication": ""},
    {"drug": "Варфарин", "dosage": "2.5-5", "condition": "Фибрилляция предсердий", "contraindication": "МНО контроль"},
]

all_rules = base_rules + extra_rules

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DELETE FROM quality_criteria")
print(f"Старые правила удалены")

for rule in all_rules:
    cursor.execute("""
        INSERT INTO quality_criteria (drug, dosage, condition, contraindication)
        VALUES (?, ?, ?, ?)
    """, (rule["drug"], rule["dosage"], rule["condition"], rule["contraindication"]))

conn.commit()

cursor.execute("SELECT COUNT(*) FROM quality_criteria")
count = cursor.fetchone()[0]
print(f"Добавлено правил: {count}")

cursor.execute("SELECT drug, dosage, condition FROM quality_criteria")
print("\n📋 Все правила в БД:")
for drug, dosage, condition in cursor.fetchall():
    cond = f" ({condition})" if condition else ""
    print(f"   - {drug}: {dosage}{cond}")

conn.close()