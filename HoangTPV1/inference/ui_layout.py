"""
UI Layout Components - Layout assembly and organization
Định nghĩa cấu trúc layout để dễ dàng bảo trì và tái sử dụng.
"""

from PyQt5 import QtCore, QtWidgets
from .ui_theme import UITheme


class ToolbarLayout(QtWidgets.QToolBar):
    """Custom toolbar with controls"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QtCore.QSize(24, 24))
        
        # Start/Stop buttons
        self.start_action = self.addAction("▶ Bắt Đầu")
        self.stop_action = self.addAction("⏹ Dừng")
        
        self.addSeparator()
        
        # Model selector
        self.model_selector = QtWidgets.QWidget()
        model_layout = QtWidgets.QHBoxLayout(self.model_selector)
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_layout.setSpacing(UITheme.SPACING_MD)
        
        model_label = QtWidgets.QLabel("Model:")
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.setStyleSheet(UITheme.get_stylesheet_combo_box())
        self.model_combo.setMinimumWidth(250)
        
        threshold_label = QtWidgets.QLabel("Threshold:")
        self.threshold_spin = QtWidgets.QDoubleSpinBox()
        self.threshold_spin.setStyleSheet(UITheme.get_stylesheet_spinbox())
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setSingleStep(0.05)
        self.threshold_spin.setValue(0.5)
        self.threshold_spin.setMinimumWidth(80)
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addSpacing(UITheme.PADDING_LG)
        model_layout.addWidget(threshold_label)
        model_layout.addWidget(self.threshold_spin)
        
        self.addWidget(self.model_selector)
        
        # Add stretch spacer
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.addWidget(spacer)


class CentralLayout(QtWidgets.QWidget):
    """Central widget layout - main content area"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {UITheme.COLORS.BG_PRIMARY.value};
            }}
        """)
        # Main layout: 3-zone (video, metrics, history)
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(UITheme.SPACING_XL)
        main_layout.setContentsMargins(
            UITheme.PADDING_XL,
            UITheme.PADDING_XL,
            UITheme.PADDING_XL,
            UITheme.PADDING_XL
        )
        from .ui_components import VideoDisplayLabel, InfoPanel, LogBox, SnapshotList
        # Left: Video
        self.left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(self.left_widget)
        left_layout.setSpacing(UITheme.SPACING_LG)
        self.video_label = VideoDisplayLabel()
        left_layout.addWidget(self.video_label)
        main_layout.addWidget(self.left_widget, stretch=4)
        # Center: Metrics/InfoPanel (tabs)
        self.center_widget = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(self.center_widget)
        center_layout.setSpacing(UITheme.SPACING_LG)
        self.info_panel = InfoPanel()
        center_layout.addWidget(self.info_panel)
        main_layout.addWidget(self.center_widget, stretch=3)
        # Right: History (Log + Snapshots)
        self.right_widget = QtWidgets.QWidget()
        self.right_widget.setMaximumWidth(350)
        right_layout = QtWidgets.QVBoxLayout(self.right_widget)
        right_layout.setSpacing(UITheme.SPACING_MD)
        right_layout.setContentsMargins(UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD)
        log_label = QtWidgets.QLabel("Lịch Sử Dự Đoán:")
        log_label.setStyleSheet(f"font-weight: bold; color: {UITheme.COLORS.TEXT_SECONDARY.value};")
        self.log_box = LogBox()
        right_layout.addWidget(log_label)
        right_layout.addWidget(self.log_box, stretch=2)
        snapshots_label = QtWidgets.QLabel("Ảnh Chụp:")
        snapshots_label.setStyleSheet(f"font-weight: bold; color: {UITheme.COLORS.TEXT_SECONDARY.value};")
        self.snapshot_list = SnapshotList()
        right_layout.addWidget(snapshots_label)
        right_layout.addWidget(self.snapshot_list, stretch=1)
        main_layout.addWidget(self.right_widget, stretch=2)
        
        main_layout.addWidget(self.right_widget, stretch=2)
        
        self.setLayout(main_layout)


class StatusBarLayout(QtWidgets.QStatusBar):
    """Custom status bar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QStatusBar {{
                background-color: {UITheme.COLORS.BG_SECONDARY.value};
                border-top: 1px solid {UITheme.COLORS.BORDER.value};
            }}
            QStatusBar::item {{
                border: none;
            }}
        """)
        
        # FPS indicator
        self.fps_label = QtWidgets.QLabel("FPS: 0")
        self.fps_label.setStyleSheet(f"color: {UITheme.COLORS.TEXT_SECONDARY.value};")
        self.addPermanentWidget(self.fps_label)
        
        # Status message
        self.showMessage("Sẵn sàng")
    
    def update_fps(self, fps: float):
        """Update FPS display"""
        self.fps_label.setText(f"FPS: {fps:.1f}")
    
    def set_message(self, message: str):
        """Set status message"""
        self.showMessage(message)

