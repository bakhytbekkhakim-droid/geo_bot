import fitz  # PyMuPDF
import os

# Файл атауы мен папканы тексеріңіз
pdf_path = "7-2025 География.pdf"
output_folder = "images"

# Папка жоқ болса, жасау
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# PDF-ті ашу
doc = fitz.open(pdf_path)
print(f"Оқулық сәтті ашылды. Жалпы бет саны: {len(doc)}")

# 1-ден 30-ға дейінгі беттерді сурет қылып сақтау
# (range(30) дегеніміз 0-ден 29-ға дейінгі индекстер, яғни 1-30 беттер)
for i in range(30):
    page = doc[i]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Сапасын жақсарту
    pix.save(f"{output_folder}/page_{i+1}.png")
    
    if (i + 1) % 5 == 0:
        print(f"{i + 1} бет дайындалды...")

print("✅ Дайын! Енді images папкасын тексеріңіз.")