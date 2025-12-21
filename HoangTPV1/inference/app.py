
import shutil
import sys
import tempfile
import time
from collections import Counter, deque
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets

from .video_predict import PredictionResult, Predictor


MODEL_EXT = "*.onnx"


def bgr_to_qimage(frame_bgr):
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    bytes_per_line = ch * w
    return QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Face Anti-Spoofing")
        self.resize(1100, 650)

        self.base_dir = Path(__file__).resolve().parent
        # saved_models sit in the HoangTPV1 root, not inside the inference folder
        self.model_dir = ROOT_DIR / "saved_models"
        self.log(f"Using model directory: {self.model_dir}")
        self.session_dir = Path(tempfile.mkdtemp(prefix="facespoof_"))

        self.predictor = None
        self.cap = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.last_saved_ts = 0
        self.result_history = deque(maxlen=5)

        self.video_label = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.video_label.setStyleSheet("background: #111; color: #ddd;")

        self.log_box = QtWidgets.QPlainTextEdit(readOnly=True)
        self.log_box.setStyleSheet("background: #000; color: #0f0;")

        self.snapshot_list = QtWidgets.QListWidget()
        self.snapshot_list.setIconSize(QtCore.QSize(96, 96))

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(QtWidgets.QLabel("Log"))
        right_layout.addWidget(self.log_box, stretch=1)
        right_layout.addWidget(QtWidgets.QLabel("Snapshots"))
        right_layout.addWidget(self.snapshot_list, stretch=1)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.video_label, stretch=3)
        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, stretch=2)

        central = QtWidgets.QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        toolbar = QtWidgets.QToolBar()
        self.addToolBar(toolbar)
        self.start_action = toolbar.addAction("Start")
        self.stop_action = toolbar.addAction("Stop")
        self.start_action.triggered.connect(lambda _: self.start_camera())
        self.stop_action.triggered.connect(self.stop_camera)

        self.model_combo = QtWidgets.QComboBox()
        if self.model_dir.exists():
            for model in sorted(self.model_dir.glob(MODEL_EXT)):
                self.model_combo.addItem(model.name)
        self.threshold_spin = QtWidgets.QDoubleSpinBox()
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setSingleStep(0.05)
        self.threshold_spin.setValue(0.5)

        toolbar.addSeparator()
        toolbar.addWidget(QtWidgets.QLabel("Model:"))
        toolbar.addWidget(self.model_combo)
        toolbar.addWidget(QtWidgets.QLabel("Threshold:"))
        toolbar.addWidget(self.threshold_spin)

        self.model_combo.currentIndexChanged.connect(self.reload_predictor)
        self.threshold_spin.valueChanged.connect(self.reload_predictor)
        self.reload_predictor(log=False)

    def reload_predictor(self, log=True):
        if self.model_combo.count() == 0:
            self.log("Không tìm thấy model ONNX trong saved_models")
            return
        model_name = self.model_combo.currentText()
        model_path = self.model_dir / model_name
        threshold = self.threshold_spin.value()
        self.predictor = Predictor(model_path=str(model_path), threshold=threshold)
        if log:
            self.log(f"Predictor load {model_name} @ threshold={threshold:.2f}")

    def start_camera(self, source=0):
        if self.cap or self.model_combo.count() == 0:
            return
        self.cap = cv2.VideoCapture(int(source), cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.log("Không mở được camera")
            self.cap = None
            return
        self.timer.start(30)
        self.log("Camera started")

    def stop_camera(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.log("Camera stopped")

    def closeEvent(self, event):
        self.stop_camera()
        self.cleanup_session()
        event.accept()

    def cleanup_session(self):
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir, ignore_errors=True)
            self.log("Session cache cleared")

    def update_frame(self):
        if not self.cap or not self.predictor:
            return
        ok, frame = self.cap.read()
        if not ok:
            self.log("End of stream")
            self.stop_camera()
            return

        result = self.predictor.predict(frame)
        self.result_history.append(result)
        smoothed = self.smooth_result()

        chosen = smoothed or result
        annotated = self.predictor.annotate(frame.copy(), chosen)
        self.display_frame(annotated)
        self.handle_result(chosen)

    def smooth_result(self):
        if not self.result_history:
            return None

        labels = [r.label for r in self.result_history if r.label is not None]
        if not labels:
            return None

        majority_label = Counter(labels).most_common(1)[0][0]
        scores_for_label = [r.score for r in self.result_history if r.label == majority_label and r.score is not None]
        avg_score = sum(scores_for_label) / len(scores_for_label) if scores_for_label else None

        last_bbox = next((r.bbox for r in reversed(self.result_history) if r.bbox is not None), None)
        last_crop = next((r.face_crop_bgr for r in reversed(self.result_history) if r.face_crop_bgr is not None), None)
        last_elapsed = self.result_history[-1].elapsed_ms

        return PredictionResult(last_bbox, majority_label, avg_score, last_elapsed, last_crop)

    def display_frame(self, frame_bgr):
        qimg = bgr_to_qimage(frame_bgr)
        pix = QtGui.QPixmap.fromImage(qimg)
        self.video_label.setPixmap(
            pix.scaled(
                self.video_label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        )

    def handle_result(self, result):
        if result.bbox is None:
            return
        self.log(
            f"label={result.label} score={result.score:.2f} time={result.elapsed_ms:.1f}ms bbox={result.bbox}"
        )
        now = time.time()
        if now - self.last_saved_ts > 1.0 and result.face_crop_bgr is not None:
            self.last_saved_ts = now
            self.add_snapshot(result.face_crop_bgr)

    def add_snapshot(self, crop_bgr):
        snapshot_path = self.session_dir / f"{int(time.time()*1000)}.png"
        cv2.imwrite(str(snapshot_path), crop_bgr)
        pix = QtGui.QPixmap(str(snapshot_path)).scaled(
            96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        item = QtWidgets.QListWidgetItem(QtGui.QIcon(pix), time.strftime("%H:%M:%S"))
        self.snapshot_list.addItem(item)

    def log(self, text):
        ts = time.strftime("%H:%M:%S")
        msg = f"[{ts}] {text}"
        if hasattr(self, "log_box") and self.log_box is not None:
            self.log_box.appendPlainText(msg)
        else:
            print(msg)


def app():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__app__":
    app()