import torch
import cv2
import warnings
import time

# COCO sınıf etiketleri
COCO_CLASSES = {0: 'Person', 56: 'Chair'}

# YOLO modelini yükle
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model.classes = [0, 56]
model.conf = 0.5

# Kamerayı başlat
cap = cv2.VideoCapture('video.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
frame_id = 0

# Sandalyenin etrafındaki yakınlık bölgesi genişliği
CHAIR_PROXIMITY_THRESHOLD = 50  # Piksel cinsinden

# Boş sandalyeler için sayaçlar (süreyi takip edeceğiz)
chair_counters = {}

# Kişinin sandalyenin etrafındaki yakınlık bölgesinde olup olmadığını kontrol etme
def is_person_near_chair(person, chair):
    """Kişinin alt vücut kısmının sandalyeye yakın olup olmadığını kontrol et."""
    px1, py1, px2, py2 = person  # Kişinin koordinatları
    cx1, cy1, cx2, cy2 = chair  # Sandalyenin koordinatları

    # Kişinin kalça bölgesini belirleyelim (alt kısmı)
    person_lower_half = [px1, int(py2 * 0.7), px2, py2]  # Kişinin alt vücudu, üst kısmın %30'u hariç

    # Sandalyenin üst kısmına (oturma yüzeyi) göre kişiyi kontrol edelim
    chair_seat_area = [cx1, cy1, cx2, cy1 + (cy2 - cy1) // 2]  # Sandalyenin oturma kısmı

    # Kişinin alt vücudu, sandalyenin oturma kısmıyla örtüşüyorsa, kişi sandalyeye oturuyor demektir
    return (person_lower_half[0] < chair_seat_area[2] and
            person_lower_half[2] > chair_seat_area[0] and
            person_lower_half[1] < chair_seat_area[3] and
            person_lower_half[3] > chair_seat_area[1])

# Görüntü işleme adımları
def preprocess_frame(frame):
    """Görüntü üzerinde OpenCV işlemleri yap."""
    # 1. Gri tonlama
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2. Gaussian Blur (bulanıklaştırma)
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # 3. Thresholding (eşiğe göre ikili görüntü oluşturma)
    #_, thresh_frame = cv2.threshold(blurred_frame, 127, 255, cv2.THRESH_BINARY)

    # Dönüştürülmüş frame'i yeniden 3 kanal haline getirelim (modelin kabul ettiği formatta)
    processed_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_GRAY2BGR)

    return processed_frame

while cap.isOpened():
    warnings.filterwarnings("ignore", category=FutureWarning)
    
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1
    if frame_id % 5 != 0:  # Çerçeve atla
        continue

    frame = cv2.resize(frame, (640, 360))  # Çözünürlüğü küçült

    # Görüntü işleme işlemlerini uygula
    processed_frame = preprocess_frame(frame)

    # YOLO modelini işlenmiş görüntü üzerinde çalıştır
    results = model(processed_frame)

    # Sandalye ve insan tespitlerini ayır
    chairs = []
    people = []
    for detection in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = detection.tolist()
        cls = int(cls)
        if cls == 56:  # Chair
            chairs.append([int(x1), int(y1), int(x2), int(y2)])
        elif cls == 0:  # Person
            people.append([int(x1), int(y1), int(x2), int(y2)])

    # Sandalyelerin doluluk durumunu kontrol et
    chair_status = {}
    for idx, chair in enumerate(chairs, 1):  # Sandalyelere numara ekleme
        is_occupied = False  # Sandalye başta boş kabul edilir
        for person in people:
            if is_person_near_chair(person, chair):
                is_occupied = True
                break
        chair_status[idx] = "Dolu" if is_occupied else "Bos"

        # Eğer sandalye boşsa, sayacı arttır
        if chair_status[idx] == "Bos":
            if idx not in chair_counters:
                chair_counters[idx] = {'counter': 0, 'start_time': time.time()}
            chair_counters[idx]['counter'] += 1  # Sayaç artır
        else:
            # Sandalye dolduğunda sayaç sıfırlanır
            if idx in chair_counters:
                chair_counters[idx]['counter'] = 0
                chair_counters[idx]['start_time'] = time.time()  # Yeniden başlat

    # Görüntüyü göster
    for idx, chair in enumerate(chairs, 1):  # Sandalyelere numara ekleme
        x1, y1, x2, y2 = chair
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        status = chair_status[idx]  # Sandalyenin durumunu al
        cv2.putText(frame, f"{idx}. Sandalye - {status}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Eğer sandalye boşsa, geçen süreyi göster
        if status == "Bos":
            elapsed_time = time.time() - chair_counters[idx]['start_time']
            cv2.putText(frame, f"Boş Süre: {elapsed_time:.2f} saniye", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    for person in people:
        x1, y1, x2, y2 = person
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, "Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Görüntüyü göster
    cv2.imshow("Kamera", frame)

    # İşlenmiş frame'i ayrı bir pencere olarak göster
    cv2.imshow("Processed Frame", processed_frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
