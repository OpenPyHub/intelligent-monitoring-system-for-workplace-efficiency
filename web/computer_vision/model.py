import torch
import cv2
import warnings
import time
import numpy as np

class ChairMonitoring:
    def __init__(self, workplace_id, video_source, chair_coordinates):
        self.workplace_id = workplace_id
        self.video_source = video_source
        self.chair_coordinates = chair_coordinates

        # YOLO modelini yükle
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.model.classes = [0]    # Sadece insanları tespit et
        self.model.conf = 0.5

        self.cap = cv2.VideoCapture(self.video_source)
        self.frame_id = 0
        self.EMPTY_WAIT_TIME = 10    # Kişinin kalktıktan sonra bekleme süresi
        self.OCCUPANCY_CONFIRM_TIME = 2    # Sandalyenin dolu olarak kabul edilmesi için gereken süre

        # Sandalyelerin durumlarını ve sayaçlarını tutan veri yapıları
        self.chair_counters = {}
        self.last_chair_status = {}
        self.occupancy_timers = {}

    @staticmethod
    def is_person_near_chair(person, chair):
        """Kişinin sandalyeye oturup oturmadığını kontrol eder."""
        px1, py1, px2, py2 = person
        cx1, cy1, cx2, cy2 = chair

        person_lower_half = [px1, int(py2 * 0.7), px2, py2]    # Kişinin alt kısmını al
        chair_seat_area = [cx1, cy1, cx2, cy1 + (cy2 - cy1) // 2]

        # Kesişim kontrolü
        return (
            person_lower_half[0] < chair_seat_area[2]
            and person_lower_half[2] > chair_seat_area[0]
            and person_lower_half[1] < chair_seat_area[3]
            and person_lower_half[3] > chair_seat_area[1]
        )
    
    def monitor_chairs(self):    
        while self.cap.isOpened():
            warnings.filterwarnings('ignore', category=FutureWarning)

            ret, frame = self.cap.read()
            if not ret:
                break

            self.frame_id += 1
            if self.frame_id % 5 != 0:
                continue

            # 1. Çözünürlük Ayarlama
            frame = cv2.resize(frame, (640, 360))

            # 2. Gri Tonlamaya Dönüştürme
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 3. Histogram Eşitleme (Konstrat arttırma) 
            equalized_frame = cv2.equalizeHist(gray_frame)

            # 4. Gürültü Azaltmak İçin Blur
            blurred_frame = cv2.bilateralFilter(equalized_frame, 3, 25, 25)

            # 5. Keskinleştirme (Kenar belirginliğini arttırma)
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened_frame = cv2.filter2D(blurred_frame, -1, kernel)


            # YOLO modeline frame gönder
            results = self.model(sharpened_frame)

            # İnsan tespiti
            people = []
            for detection in results.xyxy[0]:
                x1, y1, x2, y2, conf, cls = detection.tolist()
                cls = int(cls)
                if cls == 0:    # Person
                    people.append([int(x1), int(y1), int(x2), int(y2)])

            # Sandalyelerin doluluk durumunu kontrol et
            for idx, chair in enumerate(self.chair_coordinates, 1):
                is_occupied = False
                for person in people:
                    if self.is_person_near_chair(person, chair):
                        is_occupied = True
                        if idx not in self.occupancy_timers:
                            self.occupancy_timers[idx] = {'start_time': time.time()}
                        break

                if is_occupied:
                    elapsed_time = time.time() - self.occupancy_timers[idx]['start_time']
                    if elapsed_time >= self.OCCUPANCY_CONFIRM_TIME:
                        self.last_chair_status[idx] = 'Dolu'
                        self.occupancy_timers.pop(idx, None)
                        self.chair_counters.pop(idx, None)
                else:
                    if idx in self.occupancy_timers:
                        self.occupancy_timers.pop(idx, None)
                    if self.last_chair_status.get(idx) == 'Dolu':
                        if idx not in self.chair_counters or self.chair_counters[idx].get('start_time') is None:
                            self.chair_counters[idx] = {'start_time': time.time()}

                    if idx in self.chair_counters and self.chair_counters[idx]['start_time'] is not None:
                        elapsed_time = time.time() - self.chair_counters[idx]['start_time']
                        if elapsed_time >= self.EMPTY_WAIT_TIME:
                            self.last_chair_status[idx] = 'Bos (Sure Asimi)'
                            self.chair_counters[idx]['start_time'] = None

            # Görüntüyü göster
            for idx, chair in enumerate(self.chair_coordinates, 1):
                x1, y1, x2, y2 = chair
                status = self.last_chair_status.get(idx, 'Bos')
                color = (0, 255, 0) if 'Bos' in status else (0, 0, 255)

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

                if 'Dolu' in status and idx in self.chair_counters and self.chair_counters[idx].get('start_time'):
                    elapsed_time = time.time() - self.chair_counters[idx]['start_time']
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
                cv2.putText(frame, 'Kisi', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Frame'i JPEG formatında encode et ve tarayıcıya ilet
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            # JPEG verisini gönder
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        self.cap.release()