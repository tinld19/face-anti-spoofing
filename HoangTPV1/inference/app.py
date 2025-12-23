
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
from .ui_theme import UITheme
from .ui_layout import ToolbarLayout, CentralLayout, StatusBarLayout


MODEL_EXT = "*.onnx"


class MainWindow(QtWidgets.QMainWindow):
    """Main application window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_window()
        self._build_ui()
        self._init_paths()
        self._init_state()
        self._connect_signals()
        self._apply_theme()
    
    def _init_window(self):
        """Initialize window properties"""
        self.setWindowTitle("Face Anti-Spoofing Detection")
        self.resize(1400, 750)
        self.setMinimumSize(1200, 600)
    
    def _init_paths(self):
        """Initialize directory paths"""
        self.model_dir = ROOT_DIR / "saved_models"
        self.session_dir = Path(tempfile.mkdtemp(prefix="facespoof_"))
        self._log(f"Model directory: {self.model_dir}")
    
    def _init_state(self):
        """Initialize application state"""
        self.predictor = None
        self.cap = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.last_saved_ts = 0
        self.result_history = deque(maxlen=5)
        self.fps_counter = deque(maxlen=30)
    
    def _build_ui(self):
        """Build UI components"""
        # Toolbar
        self.toolbar = ToolbarLayout()
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)
        
        # Central widget
        self.central = CentralLayout()
        self.setCentralWidget(self.central)
        
        # Status bar
        self.status_bar = StatusBarLayout()
        self.setStatusBar(self.status_bar)
    
    def _connect_signals(self):
        """Connect all signals and slots"""
        # Toolbar signals
        self.toolbar.start_action.triggered.connect(lambda _: self.start_camera())
        self.toolbar.stop_action.triggered.connect(self.stop_camera)
        self.toolbar.model_combo.currentIndexChanged.connect(
            lambda: self.reload_predictor()
        )
        self.toolbar.threshold_spin.valueChanged.connect(
            lambda: self.reload_predictor()
        )
    
    def _apply_theme(self):
        """Apply theme to application"""
        self.setStyleSheet(UITheme.get_stylesheet_base())
        self._populate_models()
        self.reload_predictor(log=False)
    
    def _populate_models(self):
        """Populate model combo box with available models"""
        if self.model_dir.exists():
            for model in sorted(self.model_dir.glob(MODEL_EXT)):
                self.toolbar.model_combo.addItem(model.name)
        else:
            self._log("Model directory not found!")
    
    def reload_predictor(self, log=True):
        """Reload prediction model with current settings"""
        if self.toolbar.model_combo.count() == 0:
            self._log("No ONNX model found in saved_models")
            return
        
        model_name = self.toolbar.model_combo.currentText()
        model_path = self.model_dir / model_name
        threshold = self.toolbar.threshold_spin.value()
        
        try:
            self.predictor = Predictor(
                model_path=str(model_path),
                threshold=threshold
            )
            if log:
                self._log(f"Loaded {model_name} @ threshold={threshold:.2f}")
            self.status_bar.set_message(f"Model: {model_name} | Threshold: {threshold:.2f}")
        except Exception as e:
            self._log(f"Error loading model: {str(e)}")
    
    def start_camera(self, source=0):
        """Start camera capture"""
        if self.cap is not None:
            self._log("Camera already running")
            return
        
        if self.toolbar.model_combo.count() == 0:
            self._log("Please load a model first")
            return
        
        try:
            self.cap = cv2.VideoCapture(int(source), cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self._log("Failed to open camera")
                self.cap = None
                return
            
            self.timer.start(30)
            self._log("Camera started ✓")
            self.status_bar.set_message("Camera: Running")
        except Exception as e:
            self._log(f"Camera error: {str(e)}")
            self.cap = None
    
    def stop_camera(self):
        """Stop camera capture"""
        if self.timer.isActive():
            self.timer.stop()
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self._log("Camera stopped")
        self.status_bar.set_message("Camera: Stopped")
        self.central.video_label.setText("Đã dừng")
    
    def update_frame(self):
        """Capture and process frame from camera"""
        if not self.cap or not self.predictor:
            return
        
        ok, frame = self.cap.read()
        if not ok:
            self._log("End of stream")
            self.stop_camera()
            return
        
        # Predict
        result = self.predictor.predict(frame)
        self.result_history.append(result)
        smoothed = self._smooth_result()
        chosen = smoothed or result
        
        # Annotate and display
        annotated = self.predictor.annotate(frame.copy(), chosen)
        self.central.video_label.display_frame(annotated)
        self._handle_result(chosen)
        
        # Update FPS
        self._update_fps()
    
    def _smooth_result(self) -> PredictionResult | None:
        """Smooth prediction results over history"""
        if not self.result_history:
            return None
        
        labels = [r.label for r in self.result_history if r.label is not None]
        if not labels:
            return None
        
        majority_label = Counter(labels).most_common(1)[0][0]
        scores_for_label = [
            r.score for r in self.result_history
            if r.label == majority_label and r.score is not None
        ]
        avg_score = (
            sum(scores_for_label) / len(scores_for_label)
            if scores_for_label else None
        )
        
        last_bbox = next(
            (r.bbox for r in reversed(self.result_history) if r.bbox is not None),
            None
        )
        last_crop = next(
            (r.face_crop_bgr for r in reversed(self.result_history)
             if r.face_crop_bgr is not None),
            None
        )
        last_elapsed = self.result_history[-1].elapsed_ms
        
        return PredictionResult(last_bbox, majority_label, avg_score, last_elapsed, last_crop)
    
    def _handle_result(self, result: PredictionResult):
        """Handle prediction result"""
        if result.bbox is None:
            return
        
        # Log result
        self._log(
            f"Label={result.label} | Score={result.score:.2f} | "
            f"Time={result.elapsed_ms:.1f}ms"
        )
        
        # Update status indicator
        if result.label == 0:
            self.central.info_panel.status_indicator.set_real()
        elif result.label == 1:
            self.central.info_panel.status_indicator.set_fake()
        else:
            self.central.info_panel.status_indicator.set_unknown()
        
        # Save snapshot periodically
        now = time.time()
        if now - self.last_saved_ts > 1.0 and result.face_crop_bgr is not None:
            self.last_saved_ts = now
            self._add_snapshot(result.face_crop_bgr)
    
    def _add_snapshot(self, crop_bgr):
        """Add snapshot to snapshot list"""
        snapshot_path = self.session_dir / f"{int(time.time()*1000)}.png"
        cv2.imwrite(str(snapshot_path), crop_bgr)
        
        pix = QtGui.QPixmap(str(snapshot_path)).scaled(
            96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        label = time.strftime("%H:%M:%S")
        self.central.info_panel.snapshot_list.add_snapshot(pix, label)
    
    def _update_fps(self):
        """Update FPS counter"""
        now = time.time()
        self.fps_counter.append(now)
        
        if len(self.fps_counter) > 1:
            time_delta = self.fps_counter[-1] - self.fps_counter[0]
            if time_delta > 0:
                fps = (len(self.fps_counter) - 1) / time_delta
                self.status_bar.update_fps(fps)
    
    def _log(self, text: str):
        """Log message"""
        self.central.info_panel.log_box.log(text)
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.stop_camera()
        self._cleanup_session()
        event.accept()
    
    def _cleanup_session(self):
        """Clean up temporary session directory"""
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir, ignore_errors=True)
            self._log("Session cleaned up")


def run_app():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()