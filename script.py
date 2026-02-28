import pandas as pd
import json

# 1. Читаем и собираем данные
df = pd.read_excel('kazakhstan_sites.geojson.xlsx')
json_lines = [df.columns[0]] + df.iloc[:, 0].astype(str).tolist()
json_text = "\n".join(json_lines)
geo_data = json.loads(json_text)

# 2. Сохраняем в правильный файл .geojson
output_filename = 'kazakhstan_sites.geojson'

with open(output_filename, 'w', encoding='utf-8') as f:
    # ensure_ascii=False нужен, чтобы русские/казахские буквы сохранились нормально, а не иероглифами
    json.dump(geo_data, f, ensure_ascii=False, indent=2)

print(f"Готово! Данные успешно сохранены в чистый файл: {output_filename}")