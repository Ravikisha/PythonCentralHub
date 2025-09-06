#!/usr/bin/env python3
"""
Image Slider App using PyQt
A comprehensive image viewer and slider application with advanced features.

Features:
- Image browsing and navigation
- Slideshow functionality
- Image editing tools
- Metadata display
- Thumbnail gallery
- Full-screen mode

Requirements:
- PyQt5 or PyQt6
- Pillow (PIL)
- numpy

Author: Python Central Hub
Date: 2025-09-05
"""

import sys
import os
from pathlib import Path
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    PYQT_VERSION = 5
except ImportError:
    try:
        from PyQt6.QtWidgets import *
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *
        PYQT_VERSION = 6
    except ImportError:
        print("❌ PyQt5 or PyQt6 required. Install with: pip install PyQt5 or pip install PyQt6")
        sys.exit(1)

from PIL import Image, ImageEnhance
import json


class ImageSliderApp(QMainWindow):
    """Main image slider application window."""
    
    def __init__(self):
        super().__init__()
        self.images = []
        self.current_index = 0
        self.slideshow_timer = QTimer()
        self.slideshow_timer.timeout.connect(self.next_image)
        self.slideshow_interval = 3000  # 3 seconds
        self.is_fullscreen = False
        
        # Supported image formats
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
        
        self.init_ui()
        self.setup_shortcuts()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Image Slider App")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        content_layout = QHBoxLayout()
        
        # Left panel for thumbnails
        self.thumbnail_widget = ThumbnailWidget()
        self.thumbnail_widget.image_selected.connect(self.select_image)
        content_layout.addWidget(self.thumbnail_widget, 1)
        
        # Center panel for main image
        self.image_viewer = ImageViewer()
        content_layout.addWidget(self.image_viewer, 4)
        
        # Right panel for controls and info
        self.control_panel = ControlPanel()
        self.control_panel.brightness_changed.connect(self.adjust_brightness)
        self.control_panel.contrast_changed.connect(self.adjust_contrast)
        self.control_panel.rotation_requested.connect(self.rotate_image)
        content_layout.addWidget(self.control_panel, 1)
        
        main_layout.addLayout(content_layout)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_folder_action = QAction('Open Folder', self)
        open_folder_action.setShortcut('Ctrl+O')
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        fullscreen_action = QAction('Toggle Fullscreen', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        slideshow_action = QAction('Start Slideshow', self)
        slideshow_action.setShortcut('F5')
        slideshow_action.triggered.connect(self.toggle_slideshow)
        view_menu.addAction(slideshow_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create application toolbar."""
        toolbar = self.addToolBar('Main')
        
        # Navigation buttons
        prev_action = QAction('Previous', self)
        prev_action.setShortcut('Left')
        prev_action.triggered.connect(self.previous_image)
        toolbar.addAction(prev_action)
        
        next_action = QAction('Next', self)
        next_action.setShortcut('Right')
        next_action.triggered.connect(self.next_image)
        toolbar.addAction(next_action)
        
        toolbar.addSeparator()
        
        # Zoom buttons
        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.setShortcut('Ctrl+=')
        zoom_in_action.triggered.connect(self.image_viewer.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.image_viewer.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        fit_action = QAction('Fit to Window', self)
        fit_action.setShortcut('Ctrl+0')
        fit_action.triggered.connect(self.image_viewer.fit_to_window)
        toolbar.addAction(fit_action)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        QShortcut(QKeySequence('Space'), self, self.next_image)
        QShortcut(QKeySequence('Backspace'), self, self.previous_image)
        QShortcut(QKeySequence('Delete'), self, self.delete_current_image)
        
    def open_folder(self):
        """Open folder and load images."""
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.load_images_from_folder(folder)
    
    def load_images_from_folder(self, folder_path):
        """Load all images from the specified folder."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        self.images = []
        folder = Path(folder_path)
        
        # Find all image files
        for file_path in folder.iterdir():
            if file_path.suffix.lower() in self.supported_formats:
                self.images.append(str(file_path))
        
        self.images.sort()  # Sort alphabetically
        
        if self.images:
            self.current_index = 0
            self.thumbnail_widget.load_images(self.images)
            self.display_current_image()
            self.status_bar.showMessage(f"Loaded {len(self.images)} images")
        else:
            self.status_bar.showMessage("No images found in folder")
        
        self.progress_bar.setVisible(False)
    
    def display_current_image(self):
        """Display the current image."""
        if self.images and 0 <= self.current_index < len(self.images):
            image_path = self.images[self.current_index]
            self.image_viewer.load_image(image_path)
            self.thumbnail_widget.highlight_image(self.current_index)
            self.control_panel.update_image_info(image_path)
            
            # Update window title
            filename = os.path.basename(image_path)
            self.setWindowTitle(f"Image Slider - {filename} ({self.current_index + 1}/{len(self.images)})")
    
    def next_image(self):
        """Navigate to next image."""
        if self.images and self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.display_current_image()
    
    def previous_image(self):
        """Navigate to previous image."""
        if self.images and self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()
    
    def select_image(self, index):
        """Select image by index."""
        if 0 <= index < len(self.images):
            self.current_index = index
            self.display_current_image()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.is_fullscreen = not self.is_fullscreen
    
    def toggle_slideshow(self):
        """Toggle slideshow mode."""
        if self.slideshow_timer.isActive():
            self.slideshow_timer.stop()
            self.status_bar.showMessage("Slideshow stopped")
        else:
            self.slideshow_timer.start(self.slideshow_interval)
            self.status_bar.showMessage("Slideshow started")
    
    def delete_current_image(self):
        """Delete current image (move to trash)."""
        if not self.images or not (0 <= self.current_index < len(self.images)):
            return
        
        current_image = self.images[self.current_index]
        filename = os.path.basename(current_image)
        
        reply = QMessageBox.question(
            self, 'Delete Image',
            f'Move "{filename}" to trash?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Move to trash (simplified - just remove from list)
                self.images.pop(self.current_index)
                self.thumbnail_widget.remove_image(self.current_index)
                
                if self.images:
                    if self.current_index >= len(self.images):
                        self.current_index = len(self.images) - 1
                    self.display_current_image()
                else:
                    self.image_viewer.clear()
                    self.control_panel.clear_info()
                    self.setWindowTitle("Image Slider")
                
                self.status_bar.showMessage(f"Deleted {filename}")
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not delete image: {e}')
    
    def adjust_brightness(self, value):
        """Adjust image brightness."""
        self.image_viewer.set_brightness(value / 100.0)
    
    def adjust_contrast(self, value):
        """Adjust image contrast."""
        self.image_viewer.set_contrast(value / 100.0)
    
    def rotate_image(self, angle):
        """Rotate current image."""
        self.image_viewer.rotate_image(angle)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, 'About Image Slider',
            'Image Slider App v1.0\n\n'
            'A feature-rich image viewer and slideshow application.\n\n'
            'Features:\n'
            '• Image browsing and navigation\n'
            '• Slideshow functionality\n'
            '• Zoom and rotation\n'
            '• Image adjustments\n'
            '• Thumbnail gallery\n\n'
            'Keyboard Shortcuts:\n'
            '• Arrow keys: Navigate\n'
            '• Space/Backspace: Next/Previous\n'
            '• F5: Toggle slideshow\n'
            '• F11: Toggle fullscreen\n'
            '• Delete: Remove image\n'
            '• Ctrl+O: Open folder'
        )


class ImageViewer(QLabel):
    """Custom image viewer widget with zoom and enhancement capabilities."""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid gray;")
        self.setMinimumSize(400, 300)
        
        self.original_pixmap = None
        self.current_pixmap = None
        self.scale_factor = 1.0
        self.brightness = 1.0
        self.contrast = 1.0
        self.rotation = 0
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def load_image(self, image_path):
        """Load image from file path."""
        try:
            self.original_pixmap = QPixmap(image_path)
            if self.original_pixmap.isNull():
                self.setText("Failed to load image")
                return False
            
            self.apply_adjustments()
            self.fit_to_window()
            return True
        except Exception as e:
            self.setText(f"Error loading image: {e}")
            return False
    
    def apply_adjustments(self):
        """Apply brightness, contrast, and rotation adjustments."""
        if not self.original_pixmap:
            return
        
        # Convert to PIL Image for adjustments
        qimage = self.original_pixmap.toImage()
        width, height = qimage.width(), qimage.height()
        
        # Convert QImage to PIL Image
        ptr = qimage.bits()
        if PYQT_VERSION == 5:
            ptr.setsize(qimage.byteCount())
        else:
            ptr.setsize(qimage.sizeInBytes())
        
        pil_image = Image.frombuffer("RGBA", (width, height), ptr, "raw", "BGRA", 0, 1)
        
        # Apply brightness
        if self.brightness != 1.0:
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(self.brightness)
        
        # Apply contrast
        if self.contrast != 1.0:
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(self.contrast)
        
        # Convert back to QPixmap
        qimage = QImage(pil_image.tobytes(), width, height, QImage.Format_RGBA8888)
        adjusted_pixmap = QPixmap.fromImage(qimage)
        
        # Apply rotation
        if self.rotation != 0:
            transform = QTransform().rotate(self.rotation)
            adjusted_pixmap = adjusted_pixmap.transformed(transform, Qt.SmoothTransformation)
        
        self.current_pixmap = adjusted_pixmap
        self.update_display()
    
    def update_display(self):
        """Update the displayed image with current scale."""
        if self.current_pixmap:
            scaled_pixmap = self.current_pixmap.scaled(
                self.current_pixmap.size() * self.scale_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
    
    def zoom_in(self):
        """Zoom in by 25%."""
        self.scale_factor *= 1.25
        self.update_display()
    
    def zoom_out(self):
        """Zoom out by 25%."""
        self.scale_factor *= 0.8
        self.update_display()
    
    def fit_to_window(self):
        """Fit image to window size."""
        if not self.current_pixmap:
            return
        
        widget_size = self.size()
        pixmap_size = self.current_pixmap.size()
        
        scale_x = widget_size.width() / pixmap_size.width()
        scale_y = widget_size.height() / pixmap_size.height()
        self.scale_factor = min(scale_x, scale_y, 1.0)  # Don't scale up
        
        self.update_display()
    
    def set_brightness(self, value):
        """Set brightness adjustment."""
        self.brightness = value
        self.apply_adjustments()
    
    def set_contrast(self, value):
        """Set contrast adjustment."""
        self.contrast = value
        self.apply_adjustments()
    
    def rotate_image(self, angle):
        """Rotate image by specified angle."""
        self.rotation = (self.rotation + angle) % 360
        self.apply_adjustments()
    
    def clear(self):
        """Clear the image display."""
        self.clear()
        self.original_pixmap = None
        self.current_pixmap = None
        self.scale_factor = 1.0
        self.setText("No image loaded")
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event for drag and drop functionality."""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.parent().parent().load_images_from_folder(os.path.dirname(files[0]))


class ThumbnailWidget(QListWidget):
    """Widget to display image thumbnails."""
    
    image_selected = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(100, 100))
        self.setResizeMode(QListWidget.Adjust)
        self.setMaximumWidth(200)
        
        self.itemClicked.connect(self.on_item_clicked)
    
    def load_images(self, image_paths):
        """Load thumbnail images."""
        self.clear()
        
        for i, image_path in enumerate(image_paths):
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    thumbnail = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    item = QListWidgetItem()
                    item.setIcon(QIcon(thumbnail))
                    item.setToolTip(os.path.basename(image_path))
                    item.setData(Qt.UserRole, i)
                    
                    self.addItem(item)
            except Exception as e:
                print(f"Error loading thumbnail for {image_path}: {e}")
    
    def on_item_clicked(self, item):
        """Handle thumbnail click."""
        index = item.data(Qt.UserRole)
        self.image_selected.emit(index)
    
    def highlight_image(self, index):
        """Highlight the specified image."""
        if 0 <= index < self.count():
            self.setCurrentRow(index)
    
    def remove_image(self, index):
        """Remove image at specified index."""
        if 0 <= index < self.count():
            self.takeItem(index)


class ControlPanel(QWidget):
    """Control panel for image adjustments and information."""
    
    brightness_changed = pyqtSignal(int)
    contrast_changed = pyqtSignal(int)
    rotation_requested = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setMaximumWidth(250)
        self.init_ui()
    
    def init_ui(self):
        """Initialize control panel UI."""
        layout = QVBoxLayout(self)
        
        # Image adjustments group
        adj_group = QGroupBox("Image Adjustments")
        adj_layout = QVBoxLayout(adj_group)
        
        # Brightness control
        adj_layout.addWidget(QLabel("Brightness:"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(10, 200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.brightness_changed.emit)
        adj_layout.addWidget(self.brightness_slider)
        
        # Contrast control
        adj_layout.addWidget(QLabel("Contrast:"))
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(10, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.contrast_changed.emit)
        adj_layout.addWidget(self.contrast_slider)
        
        # Rotation buttons
        rotation_layout = QHBoxLayout()
        rotate_left_btn = QPushButton("↺ 90°")
        rotate_left_btn.clicked.connect(lambda: self.rotation_requested.emit(-90))
        rotate_right_btn = QPushButton("↻ 90°")
        rotate_right_btn.clicked.connect(lambda: self.rotation_requested.emit(90))
        rotation_layout.addWidget(rotate_left_btn)
        rotation_layout.addWidget(rotate_right_btn)
        adj_layout.addLayout(rotation_layout)
        
        layout.addWidget(adj_group)
        
        # Image information group
        info_group = QGroupBox("Image Information")
        info_layout = QVBoxLayout(info_group)
        
        self.info_label = QLabel("No image selected")
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignTop)
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_group)
        
        # Spacer
        layout.addStretch()
    
    def update_image_info(self, image_path):
        """Update image information display."""
        try:
            # Get file info
            file_stat = os.stat(image_path)
            file_size = file_stat.st_size
            
            # Get image dimensions
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            info_text = f"""
<b>Filename:</b> {os.path.basename(image_path)}<br>
<b>Dimensions:</b> {width} × {height}<br>
<b>Mode:</b> {mode}<br>
<b>File Size:</b> {size_str}<br>
<b>Format:</b> {os.path.splitext(image_path)[1].upper()[1:]}
            """.strip()
            
            self.info_label.setText(info_text)
            
        except Exception as e:
            self.info_label.setText(f"Error reading image info: {e}")
    
    def clear_info(self):
        """Clear image information."""
        self.info_label.setText("No image selected")


def main():
    """Main function to run the image slider application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Image Slider")
    app.setOrganizationName("Python Central Hub")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = ImageSliderApp()
    window.show()
    
    # Check command line arguments for folder
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        if os.path.isdir(folder_path):
            window.load_images_from_folder(folder_path)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
