"""
Custom UI Components - Reusable widgets following DRY principle
Tất cả custom widgets được đặt ở đây để tái sử dụng.
"""

import numpy as np
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


class HistogramWidget(QtWidgets.QLabel):
    """Mini histogram renderer for LBP bins"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(220)
        self.setStyleSheet(f"""
            QLabel {{
                border: {UITheme.BORDER_WIDTH}px solid {UITheme.COLORS.BORDER.value};
                border-radius: {UITheme.BORDER_RADIUS}px;
            }}
        """)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.real_hist = None
        self.fake_hist = None
        self.setText("Chưa có dữ liệu LBP")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render_histogram()

    def update_histograms(self, real_hist: np.ndarray | None, fake_hist: np.ndarray | None):
        self.real_hist = real_hist
        self.fake_hist = fake_hist
        self._render_histogram()

    def _render_histogram(self):
        if self.width() == 0 or self.height() == 0:
            return
        if self.real_hist is None and self.fake_hist is None:
            self.setPixmap(QtGui.QPixmap())
            self.setText("Chưa có dữ liệu LBP")
            return

        bins = len(self.real_hist) if self.real_hist is not None else len(self.fake_hist)
        if bins == 0:
            return

        width = max(self.width(), 320)
        height = max(self.height(), 200)
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtGui.QColor(UITheme.COLORS.BG_SECONDARY.value))
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        axis_pen = QtGui.QPen(QtGui.QColor(UITheme.COLORS.DIVIDER.value))
        painter.setPen(axis_pen)
        left = 12
        bottom = height - 16
        painter.drawLine(left, bottom, width - 12, bottom)
        painter.drawLine(left, bottom, left, 14)

        margin = 4
        content_height = bottom - margin
        content_width = width - left - margin
        bin_width = max(content_width / bins, 6)

        def draw_hist(hist, color_hex, offset=0):
            if hist is None:
                return
            painter.setPen(QtGui.QPen(QtGui.QColor(color_hex)))
            brush = QtGui.QBrush(QtGui.QColor(color_hex))
            brush.setStyle(QtCore.Qt.SolidPattern)
            painter.setBrush(brush)
            hist_arr = np.asarray(hist, dtype=np.float32)
            max_val = max(hist_arr.max(), 1e-3)
            for idx, value in enumerate(hist_arr):
                height_ratio = (value / max_val)
                bar_height = height_ratio * (content_height - 10)
                x = left + idx * bin_width + offset
                painter.drawRect(
                    int(x),
                    int(bottom - bar_height),
                    int(bin_width * 0.45),
                    int(max(bar_height, 1)),
                )

        real_color = UITheme.COLORS.SUCCESS.value
        fake_color = UITheme.COLORS.DANGER.value
        draw_hist(self.real_hist, real_color, offset=0)
        draw_hist(self.fake_hist, fake_color, offset=bin_width * 0.45)

        title_pen = QtGui.QPen(QtGui.QColor(UITheme.COLORS.TEXT_SECONDARY.value))
        painter.setPen(title_pen)
        painter.drawText(left + 2, 12, "LBP histogram")

        painter.end()
        self.setPixmap(pixmap)
        self.setText("")


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
        # LBP tab
        hist_tab = QtWidgets.QWidget()
        hist_layout = QtWidgets.QVBoxLayout(hist_tab)
        hist_layout.setSpacing(UITheme.SPACING_MD)
        hist_layout.setContentsMargins(UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD, UITheme.PADDING_MD)
        hist_label = QtWidgets.QLabel("LBP + Edge Insights:")
        hist_label.setStyleSheet(f"font-weight: bold; color: {UITheme.COLORS.TEXT_SECONDARY.value};")
        hist_layout.addWidget(hist_label)
        self.histogram_widget = HistogramWidget()
        hist_layout.addWidget(self.histogram_widget)
        self.lbp_summary_label = QtWidgets.QLabel("Chưa có dữ liệu LBP.")
        self.lbp_summary_label.setWordWrap(True)
        self.lbp_summary_label.setStyleSheet(f"color: {UITheme.COLORS.TEXT_MUTED.value};")
        hist_layout.addWidget(self.lbp_summary_label)
        self.lbp_count_label = QtWidgets.QLabel("")
        self.lbp_count_label.setStyleSheet(f"color: {UITheme.COLORS.TEXT_SECONDARY.value};")
        hist_layout.addWidget(self.lbp_count_label)
        hist_layout.addStretch()
        tabs.addTab(hist_tab, "📈 LBP")
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(tabs)

    def update_lbp_insights(
        self,
        real_hist: np.ndarray | None,
        fake_hist: np.ndarray | None,
        label: int | None,
        score: float | None,
        edge_density: float | None,
        laplacian_var: float | None,
        real_count: int,
        fake_count: int,
    ):
        """Refresh the LBP tab with the latest stats."""
        self.histogram_widget.update_histograms(real_hist, fake_hist)
        label_text = "Khung chưa có nhãn"
        if label is not None:
            status = "THẬT" if label == 0 else "GIẢ"
            score_text = f" (score {score:.2f})" if score is not None else ""
            label_text = f"Kết quả: {status}{score_text}"

        edge_text = (
            f"Độ dày cạnh: {edge_density*100:.1f}%"
            if edge_density is not None
            else "Độ dày cạnh: -"
        )
        lap_text = (
            f"Độ sắc nét (Laplacian var): {laplacian_var:.2f}"
            if laplacian_var is not None
            else "Độ sắc nét: -"
        )
        self.lbp_summary_label.setText(
            f"{label_text}\n{edge_text}\n{lap_text}"
        )
        self.lbp_count_label.setText(
            f"Khung đã ghi: THẬT={real_count}, GIẢ={fake_count}"
        )
