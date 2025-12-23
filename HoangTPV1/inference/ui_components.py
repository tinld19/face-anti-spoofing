"""
Custom UI Components - Reusable widgets following DRY principle
Tất cả custom widgets được đặt ở đây để tái sử dụng.
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from .ui_theme import UITheme


class VideoDisplayLabel(QtWidgets.QLabel):
    """Custom label cho hiển thị video frame"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet(UITheme.get_stylesheet_video_label())
        self.setText("Chưa bắt đầu...")
        self.setMinimumHeight(300)
    
    def display_frame(self, frame_bgr):
        """Display frame from BGR numpy array"""
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(qimg)
        self.setPixmap(
            pix.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        )


class LogBox(QtWidgets.QPlainTextEdit):
    """Custom log text area"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet(UITheme.get_stylesheet_log_box())
        self.setMaximumHeight(200)
    
    def log(self, text: str):
        """Add timestamped log message"""
        import time
        ts = time.strftime("%H:%M:%S")
        msg = f"[{ts}] {text}"
        self.appendPlainText(msg)
        
        # Auto scroll to bottom
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class SnapshotList(QtWidgets.QListWidget):
    """Custom list widget cho snapshots"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QtCore.QSize(96, 96))
        self.setStyleSheet(UITheme.get_stylesheet_list_widget())
        self.setMaximumHeight(250)
    
    def add_snapshot(self, pixmap: QtGui.QPixmap, label: str):
        """Add snapshot to list
        
        Args:
            pixmap: QPixmap to display
            label: Label text (usually timestamp)
        """
        item = QtWidgets.QListWidgetItem(QtGui.QIcon(pixmap), label)
        self.addItem(item)
        
        # Auto scroll to newest
        self.scrollToItem(item, QtWidgets.QAbstractItemView.EnsureVisible)


class StatusIndicator(QtWidgets.QLabel):
    """Visual status indicator with color and text"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                font-size: 14pt;
                font-weight: bold;
                padding: {UITheme.PADDING_MD}px;
                border-radius: {UITheme.BORDER_RADIUS}px;
                background-color: {UITheme.COLORS.BG_SECONDARY.value};
            }}
        """)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setFixedHeight(150)
        self.set_unknown()
    
    def set_real(self, score=None):
        """Show 'Real' status"""
        color = UITheme.COLORS.SUCCESS.value
        score_text = f" (Score: {score:.2f})" if score is not None else ""
        self.setText(f"✅ THẬT{score_text}")
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 15pt;
                font-weight: bold;
                padding: {UITheme.PADDING_MD}px;
                border-radius: {UITheme.BORDER_RADIUS}px;
                background-color: {UITheme.COLORS.BG_SECONDARY.value};
                border: 2px solid {color};
            }}
        """)
    
    def set_fake(self, score=None):
        """Show 'Fake' status"""
        color = UITheme.COLORS.DANGER.value
        score_text = f" (Score: {score:.2f})" if score is not None else ""
        self.setText(f"❌ GIẢ{score_text}")
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 15pt;
                font-weight: bold;
                padding: {UITheme.PADDING_MD}px;
                border-radius: {UITheme.BORDER_RADIUS}px;
                background-color: {UITheme.COLORS.BG_SECONDARY.value};
                border: 2px solid {color};
            }}
        """)
    
    def set_unknown(self):
        """Show 'Unknown' status"""
        color = UITheme.COLORS.WARNING.value
        self.setText("⚠️ ĐANG CHỜ")
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 15pt;
                font-weight: bold;
                padding: {UITheme.PADDING_MD}px;
                border-radius: {UITheme.BORDER_RADIUS}px;
                background-color: {UITheme.COLORS.BG_SECONDARY.value};
                border: 2px solid {color};
            }}
        """)


class InfoPanel(QtWidgets.QWidget):
    """Right panel chứa thông tin chi tiết"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI with tabs"""
        tabs = QtWidgets.QTabWidget(self)
        tabs.setStyleSheet(f"""
            QTabBar::tab {{
                background: {UITheme.COLORS.BG_TERTIARY.value};
                color: {UITheme.COLORS.TEXT_PRIMARY.value};
                padding: {UITheme.PADDING_MD}px {UITheme.PADDING_LG}px;
                border-radius: {UITheme.BORDER_RADIUS}px;
                font-size: {UITheme.FONTS.FONT_SIZE_BODY}px;
            }}
            QTabBar::tab:selected {{
                background: {UITheme.COLORS.BG_SECONDARY.value};
                color: {UITheme.COLORS.PRIMARY.value};
            }}
        """)
        # Status tab
        status_tab = QtWidgets.QWidget()
        status_layout = QtWidgets.QVBoxLayout(status_tab)
        status_layout.setSpacing(UITheme.SPACING_MD)
        status_layout.setContentsMargins(UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD)
        status_label = QtWidgets.QLabel("Trạng Thái:")
        status_label.setStyleSheet(f"font-weight: bold; color: {UITheme.COLORS.TEXT_SECONDARY.value};")
        self.status_indicator = StatusIndicator()
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_indicator)
        tabs.addTab(status_tab, "📊 Metrics")
        # Log tab
        log_tab = QtWidgets.QWidget()
        log_layout = QtWidgets.QVBoxLayout(log_tab)
        log_layout.setSpacing(UITheme.SPACING_MD)
        log_layout.setContentsMargins(UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD)
        log_label = QtWidgets.QLabel("Nhật Ký (Log):")
        log_label.setStyleSheet(f"font-weight: bold; color: {UITheme.COLORS.TEXT_SECONDARY.value};")
        self.log_box = LogBox()
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_box, stretch=2)
        tabs.addTab(log_tab, "📝 Log")
        # Snapshots tab
        snap_tab = QtWidgets.QWidget()
        snap_layout = QtWidgets.QVBoxLayout(snap_tab)
        snap_layout.setSpacing(UITheme.SPACING_MD)
        snap_layout.setContentsMargins(UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD)
        snapshots_label = QtWidgets.QLabel("Ảnh Chụp (Snapshots):")
        snapshots_label.setStyleSheet(f"font-weight: bold; color: {UITheme.COLORS.TEXT_SECONDARY.value};")
        self.snapshot_list = SnapshotList()
        snap_layout.addWidget(snapshots_label)
        snap_layout.addWidget(self.snapshot_list, stretch=1)
        tabs.addTab(snap_tab, "📸 Snapshots")
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(tabs)
