import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance as dist

class FaceDetector:
    """
    Deteksi wajah & mata menggunakan MediaPipe FaceMesh,
    serta menghitung EAR (Eye Aspect Ratio).
    """

    def __init__(self, threshold=0.21):
        """
        Inisialisasi FaceMesh dan parameter EAR
        """
        self.threshold = threshold

        # MediaPipe FaceMesh
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Indeks landmark mata dari MediaPipe
        # Mata kiri (6 titik)
        self.left_eye_idx = [33, 160, 158, 133, 153, 144]
        # Mata kanan (6 titik)
        self.right_eye_idx = [362, 385, 387, 263, 373, 380]

    # -------------------------------------------------------------------------
    # FRAME PROCESSING
    # -------------------------------------------------------------------------
    def process_frame(self, frame):
        """
        Memproses 1 frame kamera untuk deteksi wajah & EAR.

        Return:
        --------
        processed_frame, ear_value, status
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        ear_value = None
        status = "Tidak Terdeteksi"

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]

            # Ambil koordinat mata kiri & kanan
            left_eye = self._get_eye_points(face_landmarks, self.left_eye_idx, frame)
            right_eye = self._get_eye_points(face_landmarks, self.right_eye_idx, frame)

            # Jika kedua mata valid
            if left_eye and right_eye:
                left_ear = self._calculate_ear(left_eye)
                right_ear = self._calculate_ear(right_eye)

                ear_value = (left_ear + right_ear) / 2.0

                # Tentukan status
                status = "Mengantuk" if ear_value <= self.threshold else "Normal"

                # Gambar titik-titik landmark mata
                self._draw_points(frame, left_eye, (0, 255, 0))
                self._draw_points(frame, right_eye, (0, 255, 0))

                # Tampilkan EAR & status di frame
                cv2.putText(frame, f"EAR: {ear_value:.3f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                cv2.putText(frame, f"Status: {status}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        return frame, ear_value, status

    # -------------------------------------------------------------------------
    # HELPER FUNCTIONS
    # -------------------------------------------------------------------------
    def _get_eye_points(self, landmarks, indexes, frame):
        """
        Mengubah landmark MediaPipe ke koordinat pixel frame.
        """
        h, w, _ = frame.shape
        points = []

        for idx in indexes:
            lm = landmarks.landmark[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            points.append((x, y))

        return points

    def _calculate_ear(self, eye_points):
        """
        Menghitung Eye Aspect Ratio (EAR).

        EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
        """
        p1, p2, p3, p4, p5, p6 = eye_points

        # Hitung jarak Euclidean antar titik
        vertical_1 = dist.euclidean(p2, p6)
        vertical_2 = dist.euclidean(p3, p5)
        horizontal = dist.euclidean(p1, p4)

        if horizontal == 0:
            return 0.0

        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        return ear

    def _draw_points(self, frame, points, color):
        """Menggambar titik landmark mata pada frame"""
        for (x, y) in points:
            cv2.circle(frame, (x, y), 2, color, -1)
