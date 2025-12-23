"""
UI Theme Configuration - Dark Modern Theme
Định nghĩa toàn bộ color scheme, font, và styling để duy trì tính nhất quán.
"""

from dataclasses import dataclass
from enum import Enum


class ColorPalette(Enum):
    """Color palette - modern dark theme"""
    # Background colors
    # Neutrals (Grayscale)
    BG_DARK = "#0f0f0f"         # Near black
    BG_PRIMARY = "#1a1a1a"      # Main background
    BG_SECONDARY = "#262626"    # Elevated
    BG_TERTIARY = "#2a2a2a"     # Hover
    
    # Text colors
    TEXT_PRIMARY = "#f5f5f5"     # 98% white
    TEXT_SECONDARY = "#a3a3a3"   # 66% gray
    TEXT_MUTED = "#6b7280"       # 40% gray
    
    # Accent colors (toned down)
    SUCCESS = "#10b981"          # Emerald - Real
    DANGER = "#ef4444"           # Red - Fake
    WARNING = "#f59e0b"          # Amber - Unknown
    PRIMARY = "#3b82f6"          # Blue - Actions
    SECONDARY = "#8b5cf6"        # Purple - Secondary
    
    # Subtle
    BORDER = "#374151"           # Soft borders
    DIVIDER = "#1f2937"          # Light dividers


@dataclass
class FontConfig:
    """Font configuration for consistent typography"""
    FONT_FAMILY = "Segoe UI, SF Pro Display, Arial, sans-serif"
    FONT_SIZE_H1 = 28
    FONT_SIZE_H2 = 22
    FONT_SIZE_H3 = 18
    FONT_SIZE_BODY = 14
    FONT_SIZE_SMALL = 12
    FONT_SIZE_LABEL = 11
    FONT_WEIGHT_REGULAR = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_BOLD = 700
    LINE_HEIGHT = 1.5


class UITheme:
    """Central theme configuration - tất cả styling đi vào đây"""
    
    # Color palette
    COLORS = ColorPalette
    
    # Fonts
    FONTS = FontConfig
    
    # Spacing
    # Spacing system (8px grid)
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    SPACING_2XL = 32
    PADDING_XS = 4
    PADDING_SM = 8
    PADDING_MD = 12
    PADDING_LG = 16
    PADDING_XL = 24
    PADDING_2XL = 32
    # Border radius
    BORDER_RADIUS = 6
    BORDER_RADIUS_LG = 12
    # Shadow/Border width
    BORDER_WIDTH = 1
    BORDER_WIDTH_FOCUS = 2

    @classmethod
    def get_stylesheet_base(cls) -> str:
        """Base stylesheet cho toàn app (loại bỏ thuộc tính không hỗ trợ)"""
        return f"""
            QWidget {{
                background-color: {cls.COLORS.BG_PRIMARY.value};
                color: {cls.COLORS.TEXT_PRIMARY.value};
                font-family: {cls.FONTS.FONT_FAMILY};
                font-size: {cls.FONTS.FONT_SIZE_BODY}px;
            }}
            QMainWindow {{
                background-color: {cls.COLORS.BG_PRIMARY.value};
            }}
            QLabel {{
                color: {cls.COLORS.TEXT_PRIMARY.value};
            }}
            QToolBar {{
                background-color: {cls.COLORS.BG_SECONDARY.value};
                border: none;
                border-bottom: {cls.BORDER_WIDTH}px solid {cls.COLORS.BORDER.value};
                padding: {cls.PADDING_SM}px;
            }}
            QToolBar::separator {{
                background-color: {cls.COLORS.BORDER.value};
                margin: 0 {cls.PADDING_SM}px;
                width: {cls.BORDER_WIDTH}px;
            }}
            QPushButton {{
                background-color: {cls.COLORS.PRIMARY.value};
                color: {cls.COLORS.TEXT_PRIMARY.value};
                border: none;
                border-radius: {cls.BORDER_RADIUS}px;
                padding: {cls.PADDING_MD}px;
                font-weight: bold;
                font-size: {cls.FONTS.FONT_SIZE_BODY}px;
            }}
            QPushButton:hover {{
                background-color: #2563eb;
            }}
            QPushButton:pressed {{
                background-color: #1d4ed8;
            }}
            QPushButton:disabled {{
                background-color: {cls.COLORS.BG_TERTIARY.value};
                color: {cls.COLORS.TEXT_MUTED.value};
            }}
        """

    @classmethod
    def get_stylesheet_video_label(cls) -> str:
        """Stylesheet cho video display label"""
        return f"""
            QLabel {{
                background-color: {cls.COLORS.BG_SECONDARY.value};
                border: {cls.BORDER_WIDTH}px solid {cls.COLORS.BORDER.value};
                border-radius: {cls.BORDER_RADIUS_LG}px;
                color: {cls.COLORS.TEXT_MUTED.value};
            }}
        """

    @classmethod
    def get_stylesheet_log_box(cls) -> str:
        """Stylesheet cho log text area"""
        return f"""
            QPlainTextEdit {{
                background-color: {cls.COLORS.BG_SECONDARY.value};
                color: {cls.COLORS.SUCCESS.value};
                border: {cls.BORDER_WIDTH}px solid {cls.COLORS.BORDER.value};
                border-radius: {cls.BORDER_RADIUS}px;
                padding: {cls.PADDING_SM}px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: {cls.FONTS.FONT_SIZE_BODY}px;
            }}
            
            QPlainTextEdit:focus {{
                border: {cls.BORDER_WIDTH_FOCUS}px solid {cls.COLORS.PRIMARY.value};
            }}
        """

    @classmethod
    def get_stylesheet_list_widget(cls) -> str:
        """Stylesheet cho snapshot list"""
        return f"""
            QListWidget {{
                background-color: {cls.COLORS.BG_SECONDARY.value};
                border: {cls.BORDER_WIDTH}px solid {cls.COLORS.BORDER.value};
                border-radius: {cls.BORDER_RADIUS}px;
            }}
            
            QListWidget::item {{
                padding: {cls.PADDING_SM}px;
                border-radius: {cls.BORDER_RADIUS}px;
            }}
            
            QListWidget::item:hover {{
                background-color: {cls.COLORS.BG_TERTIARY.value};
            }}
            
            QListWidget::item:selected {{
                background-color: {cls.COLORS.PRIMARY.value};
            }}
        """

    @classmethod
    def get_stylesheet_combo_box(cls) -> str:
        """Stylesheet cho combobox"""
        return f"""
            QComboBox {{
                background-color: {cls.COLORS.BG_SECONDARY.value};
                color: {cls.COLORS.TEXT_PRIMARY.value};
                border: {cls.BORDER_WIDTH}px solid {cls.COLORS.BORDER.value};
                border-radius: {cls.BORDER_RADIUS}px;
                padding: {cls.PADDING_SM}px;
            }}
            
            QComboBox:focus {{
                border: {cls.BORDER_WIDTH_FOCUS}px solid {cls.COLORS.PRIMARY.value};
            }}
            
            QComboBox::drop-down {{
                border: none;
                padding-right: {cls.PADDING_SM}px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {cls.COLORS.BG_SECONDARY.value};
                color: {cls.COLORS.TEXT_PRIMARY.value};
                selection-background-color: {cls.COLORS.PRIMARY.value};
                border: {cls.BORDER_WIDTH}px solid {cls.COLORS.BORDER.value};
            }}
        """

    @classmethod
    def get_stylesheet_spinbox(cls) -> str:
        """Stylesheet cho spinbox"""
        return f"""
            QDoubleSpinBox {{
                background-color: {cls.COLORS.BG_SECONDARY.value};
                color: {cls.COLORS.TEXT_PRIMARY.value};
                border: {cls.BORDER_WIDTH}px solid {cls.COLORS.BORDER.value};
                border-radius: {cls.BORDER_RADIUS}px;
                padding: {cls.PADDING_SM}px;
            }}
            
            QDoubleSpinBox:focus {{
                border: {cls.BORDER_WIDTH_FOCUS}px solid {cls.COLORS.PRIMARY.value};
            }}
            
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                width: 20px;
                background-color: {cls.COLORS.BG_TERTIARY.value};
            }}
        """

    @classmethod
    def get_status_color(cls, label: int) -> str:
        """Get color based on prediction label
        
        Args:
            label: 1 for real face, 0 for fake face
        
        Returns:
            Color string (hex)
        """
        if label == 1:
            return cls.COLORS.SUCCESS.value
        elif label == 0:
            return cls.COLORS.DANGER.value
        else:
            return cls.COLORS.WARNING.value

    @classmethod
    def get_status_text(cls, label: int) -> str:
        """Get status text based on prediction label
        
        Args:
            label: 1 for real face, 0 for fake face
        
        Returns:
            Status text string
        """
        if label == 1:
            return "✓ THẬT"
        elif label == 0:
            return "✗ GIẢ"
        else:
            return "? KHÔNG XÁC ĐỊNH"
