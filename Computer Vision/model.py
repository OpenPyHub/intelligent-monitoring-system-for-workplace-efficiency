import torch
import cv2
import warnings
import time



# Kütüphane ID'sine göre sandalye konumları
CHAIR_COORDINATES_BY_LIBRARY = {
    "1": [
        [180, 100, 280, 300],
    ],
    "2": [
        [0, 280, 110, 350],
        [180, 280, 280, 350],
        [350, 280, 460, 350],
    ],
}


current_library_id = input("Lütfen izlemek istediğiniz kütüphanenin ID sini giriniz: ")
PREDEFINED_CHAIRS = CHAIR_COORDINATES_BY_LIBRARY.get(current_library_id, [])

# YOLO modelini yükle
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model.classes = [0]
model.conf = 0.5


cap = cv2.VideoCapture(f'{current_library_id}.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
frame_id = 0


EMPTY_WAIT_TIME = 10  # Kişinin kalktıktan sonra bekleme süresi
OCCUPANCY_CONFIRM_TIME = 3  # Sandalyenin dolu olarak kabul edilmesi için gereken süre

# Sandalyelerin durumlarını ve sayaçlarını tutan veri yapıları
chair_counters = {}
last_chair_status = {}
occupancy_timers = {}

# Kişinin sandalyede olup olmadığını kontrol eden fonksiyon
def is_person_near_chair(person, chair):
    """Kişinin sandalyeye oturup oturmadığını kontrol eder."""
    px1, py1, px2, py2 = person
    cx1, cy1, cx2, cy2 = chair

    
    person_lower_half = [px1, int(py2 * 0.7), px2, py2] # Kişinin alt kısmını al
    chair_seat_area = [cx1, cy1, cx2, cy1 + (cy2 - cy1) // 2]

    # Kesişim kontrolü
    return (
        person_lower_half[0] < chair_seat_area[2]
        and person_lower_half[2] > chair_seat_area[0]
        and person_lower_half[1] < chair_seat_area[3]
        and person_lower_half[3] > chair_seat_area[1]
    )

while cap.isOpened():
    warnings.filterwarnings("ignore", category=FutureWarning)

    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1
    if frame_id % 5 != 0:
        continue

    frame = cv2.resize(frame, (640, 360))

    # YOLO modeline frame gönder
    results = model(frame)

    # İnsan tespiti
    people = []
    for detection in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = detection.tolist()
        cls = int(cls)
        if cls == 0:  # Person
            people.append([int(x1), int(y1), int(x2), int(y2)])

    # Sandalyelerin doluluk durumunu kontrol et
    for idx, chair in enumerate(PREDEFINED_CHAIRS, 1):  # Sandalyeler
        is_occupied = False  # Sandalye başta boş kabul edilir
        for person in people:
            if is_person_near_chair(person, chair):
                is_occupied = True
                # Eğer kişi sandalyeye yakınsa sayaç başlat
                if idx not in occupancy_timers:
                    occupancy_timers[idx] = {"start_time": time.time()}
                break

        if is_occupied:
            # Kişi belirli bir süre boyunca sandalyeye yakınsa "Dolu" olarak işaretle
            elapsed_time = time.time() - occupancy_timers[idx]["start_time"]
            if elapsed_time >= OCCUPANCY_CONFIRM_TIME:
                last_chair_status[idx] = "Dolu"
                occupancy_timers.pop(idx, None)  # Sayaç sıfırla
                chair_counters.pop(idx, None)  # Boş sayaç sıfırla
        else:
            # Sandalye boş ise
            if idx in occupancy_timers:
                occupancy_timers.pop(idx, None)  # Yakınlık zamanlayıcısını sıfırla
            if last_chair_status.get(idx) == "Dolu":
                if idx not in chair_counters or chair_counters[idx].get("start_time") is None:
                    chair_counters[idx] = {"start_time": time.time()}

            # Sandalye uzun süredir boş ise
            if idx in chair_counters and chair_counters[idx]["start_time"] is not None:
                elapsed_time = time.time() - chair_counters[idx]["start_time"]
                if elapsed_time >= EMPTY_WAIT_TIME:
                    last_chair_status[idx] = "Bos (Sure Asimi)"
                    chair_counters[idx]["start_time"] = None

    # Görüntüyü göster
    for idx, chair in enumerate(PREDEFINED_CHAIRS, 1):  # Sandalyeler
        x1, y1, x2, y2 = chair
        status = last_chair_status.get(idx, "Bos")
        color = (0, 255, 0) if "Bos" in status else (0, 0, 255)  # Yeşil renk

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            f"{idx}. Sandalye - {status}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )

        # Eğer sandalye boşsa ve süre devam ediyorsa göster
        if "Bos" in status and idx in chair_counters and chair_counters[idx].get("start_time"):
            elapsed_time = time.time() - chair_counters[idx]["start_time"]
            cv2.putText(
                frame,
                f"Bos Sure: {elapsed_time:.2f} saniye",
                (x1, y1 - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                2,
            )

    for person in people:
        x1, y1, x2, y2 = person
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, "Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


    cv2.imshow("Kamera", frame)

    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
