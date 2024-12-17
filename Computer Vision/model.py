import torch
import cv2
import warnings
import time

class ChairMonitoring:
    def __init__(self, library_id, video_source, chair_coordinates):
        self.library_id = library_id
        self.video_source = video_source
        self.chair_coordinates = chair_coordinates

        # YOLO modelini yükle
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.model.classes = [0]  # Sadece insanları tespit et
        self.model.conf = 0.5

        self.cap = cv2.VideoCapture(self.video_source)
        self.frame_id = 0
        self.EMPTY_WAIT_TIME = 10  # Kişinin kalktıktan sonra bekleme süresi
        self.OCCUPANCY_CONFIRM_TIME = 3  # Sandalyenin dolu olarak kabul edilmesi için gereken süre

        # Sandalyelerin durumlarını ve sayaçlarını tutan veri yapıları
        self.chair_counters = {}
        self.last_chair_status = {}
        self.occupancy_timers = {}

    @staticmethod
    def is_person_near_chair(person, chair):
        """Kişinin sandalyeye oturup oturmadığını kontrol eder."""
        px1, py1, px2, py2 = person
        cx1, cy1, cx2, cy2 = chair

        person_lower_half = [px1, int(py2 * 0.7), px2, py2]  # Kişinin alt kısmını al
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
            warnings.filterwarnings("ignore", category=FutureWarning)

            ret, frame = self.cap.read()
            if not ret:
                break

            self.frame_id += 1
            if self.frame_id % 5 != 0:
                continue

            frame = cv2.resize(frame, (640, 360))

            # YOLO modeline frame gönder
            results = self.model(frame)

            # İnsan tespiti
            people = []
            for detection in results.xyxy[0]:
                x1, y1, x2, y2, conf, cls = detection.tolist()
                cls = int(cls)
                if cls == 0:  # Person
                    people.append([int(x1), int(y1), int(x2), int(y2)])

            # Sandalyelerin doluluk durumunu kontrol et
            for idx, chair in enumerate(self.chair_coordinates, 1):
                is_occupied = False
                for person in people:
                    if self.is_person_near_chair(person, chair):
                        is_occupied = True
                        if idx not in self.occupancy_timers:
                            self.occupancy_timers[idx] = {"start_time": time.time()}
                        break

                if is_occupied:
                    elapsed_time = time.time() - self.occupancy_timers[idx]["start_time"]
                    if elapsed_time >= self.OCCUPANCY_CONFIRM_TIME:
                        self.last_chair_status[idx] = "Dolu"
                        self.occupancy_timers.pop(idx, None)
                        self.chair_counters.pop(idx, None)
                else:
                    if idx in self.occupancy_timers:
                        self.occupancy_timers.pop(idx, None)
                    if self.last_chair_status.get(idx) == "Dolu":
                        if idx not in self.chair_counters or self.chair_counters[idx].get("start_time") is None:
                            self.chair_counters[idx] = {"start_time": time.time()}

                    if idx in self.chair_counters and self.chair_counters[idx]["start_time"] is not None:
                        elapsed_time = time.time() - self.chair_counters[idx]["start_time"]
                        if elapsed_time >= self.EMPTY_WAIT_TIME:
                            self.last_chair_status[idx] = "Bos (Sure Asimi)"
                            self.chair_counters[idx]["start_time"] = None

            # Görüntüyü göster
            for idx, chair in enumerate(self.chair_coordinates, 1):
                x1, y1, x2, y2 = chair
                status = self.last_chair_status.get(idx, "Bos")
                color = (0, 255, 0) if "Bos" in status else (0, 0, 255)

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

                if "Bos" in status and idx in self.chair_counters and self.chair_counters[idx].get("start_time"):
                    elapsed_time = time.time() - self.chair_counters[idx]["start_time"]
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

        self.cap.release()
        cv2.destroyAllWindows()




# Kullanım
current_library_id = input("Lütfen izlemek istediğiniz kütüphanenin ID sini giriniz: ")
CHAIR_COORDINATES_BY_LIBRARY = {
    "1": [[180, 100, 280, 300]],
    "2": [[0, 280, 110, 350], [180, 280, 280, 350], [350, 280, 460, 350]],
}
PREDEFINED_CHAIRS = CHAIR_COORDINATES_BY_LIBRARY.get(current_library_id, [])

monitoring = ChairMonitoring(current_library_id, f"Computer Vision/{current_library_id}.mp4", PREDEFINED_CHAIRS)
monitoring.monitor_chairs()
