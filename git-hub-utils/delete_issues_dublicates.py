import subprocess
import json
from collections import defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8')


# Получаем список всех открытых issues с названиями и номерами
print("Получаю все открытые issues...")
output = subprocess.check_output([
    "gh", "issue", "list", "--state", "open", "--json", "title,number"
])
issues = json.loads(output)

# Группировка issues по title
grouped = defaultdict(list)
for issue in issues:
    grouped[issue["title"]].append(issue["number"])

# Удаляем все дубликаты (оставляем первую)
for title, numbers in grouped.items():
    if len(numbers) > 1:
        to_delete = numbers[1:]  # оставляем только первый
        for number in to_delete:
            print(f"🗑 Удаляю дубликат issue #{number}: {title}")
            subprocess.run(["gh", "issue", "delete", str(number), "--yes"])
