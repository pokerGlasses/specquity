import cv2
from ultralytics import YOLO

# Load your optimized model
model = YOLO('models/poker_best.ncnn') 

def capture_and_identify():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return []

    results = model(frame)
    detected_cards = []
    for box in results[0].boxes:
        label = model.names[int(box.cls)]
        detected_cards.append(label)
        
    return list(set(detected_cards))