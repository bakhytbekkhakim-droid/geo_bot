import cv2
import os

def highlight_map_automatically(input_path, output_path):
    # Суретті жүктеу
    img = cv2.imread(input_path)
    if img is None:
        print(f"❌ Қате: {input_path} табылмады!")
        return

    # Суретті өңдеу (сұр түс -> бұлдырату -> жиектерді анықтау)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edged = cv2.Canny(blurred, 50, 150)

    # Контурларды іздеу
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Ең үлкен контурды табу (әдетте бұл оқулықтағы негізгі сурет немесе карта)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Егер табылған нысан тым кішкентай болмаса, жақтау салу
        if w > 100 and h > 100:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 5)
            print(f"✅ Нысан табылды: Координаттары {x}, {y}, {w}, {h}")

    # Нәтижені сақтау
    cv2.imwrite(output_path, img)
    print(f"✅ Дайын сурет сақталды: {output_path}")

# Іске қосу
if not os.path.exists("images"):
    os.makedirs("images")

highlight_map_automatically("images/page_8.png", "images/page_8_ai.png")# ai_finder.py файлының ең соңына қосыңыз:
highlight_map_automatically("images/page_15.png", "images/page_15_ai.png")
highlight_map_automatically("images/page_22.png", "images/page_22_ai.png")