#!/usr/bin/env python3
"""
QR Code Generator and Scanner
Advanced QR code creation, scanning, and management application.

Features:
- Generate QR codes for various data types
- Scan QR codes from images and camera
- Batch processing capabilities
- Custom styling and logos
- Multiple output formats
- QR code analytics

Requirements:
- qrcode
- opencv-python
- Pillow (PIL)
- pyzbar
- tkinter

Author: Python Central Hub
Date: 2025-09-05
"""

import qrcode
import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageDraw, ImageFont
from pyzbar import pyzbar
import numpy as np
import json
import os
from datetime import datetime
import threading
import webbrowser


class QRCodeGenerator:
    """Advanced QR code generator with customization options."""
    
    def __init__(self):
        self.default_settings = {
            'version': 1,
            'error_correction': qrcode.constants.ERROR_CORRECT_M,
            'box_size': 10,
            'border': 4,
            'fill_color': 'black',
            'back_color': 'white'
        }
    
    def generate_qr_code(self, data, settings=None):
        """Generate QR code with specified settings."""
        if settings is None:
            settings = self.default_settings
        
        qr = qrcode.QRCode(
            version=settings.get('version', 1),
            error_correction=settings.get('error_correction', qrcode.constants.ERROR_CORRECT_M),
            box_size=settings.get('box_size', 10),
            border=settings.get('border', 4),
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(
            fill_color=settings.get('fill_color', 'black'),
            back_color=settings.get('back_color', 'white')
        )
        
        return qr_image
    
    def add_logo(self, qr_image, logo_path, logo_size_ratio=0.2):
        """Add logo to center of QR code."""
        try:
            logo = Image.open(logo_path)
            
            # Calculate logo size
            qr_width, qr_height = qr_image.size
            logo_size = int(min(qr_width, qr_height) * logo_size_ratio)
            
            # Resize logo
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Create a white background for logo
            logo_bg = Image.new('RGB', (logo_size + 20, logo_size + 20), 'white')
            logo_bg.paste(logo, (10, 10))
            
            # Calculate position to center logo
            logo_pos = (
                (qr_width - logo_bg.width) // 2,
                (qr_height - logo_bg.height) // 2
            )
            
            # Paste logo onto QR code
            qr_image.paste(logo_bg, logo_pos)
            
            return qr_image
        except Exception as e:
            print(f"Error adding logo: {e}")
            return qr_image
    
    def generate_batch_qr_codes(self, data_list, output_dir, settings=None):
        """Generate multiple QR codes from data list."""
        results = []
        
        for i, data in enumerate(data_list):
            try:
                qr_image = self.generate_qr_code(data, settings)
                
                # Generate filename
                safe_data = "".join(c for c in str(data)[:20] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"qr_{i+1:03d}_{safe_data}.png"
                filepath = os.path.join(output_dir, filename)
                
                # Save image
                qr_image.save(filepath)
                
                results.append({
                    'data': data,
                    'filename': filename,
                    'filepath': filepath,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'data': data,
                    'error': str(e),
                    'success': False
                })
        
        return results


class QRCodeScanner:
    """QR code scanner for images and camera feed."""
    
    def __init__(self):
        self.camera = None
        self.scanning = False
    
    def scan_image(self, image_path):
        """Scan QR codes from image file."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            return self.decode_qr_codes(image)
        except Exception as e:
            print(f"Error scanning image: {e}")
            return None
    
    def scan_pil_image(self, pil_image):
        """Scan QR codes from PIL image."""
        try:
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return self.decode_qr_codes(opencv_image)
        except Exception as e:
            print(f"Error scanning PIL image: {e}")
            return None
    
    def decode_qr_codes(self, image):
        """Decode QR codes from OpenCV image."""
        try:
            # Decode QR codes
            qr_codes = pyzbar.decode(image)
            
            results = []
            for qr_code in qr_codes:
                # Extract data
                data = qr_code.data.decode('utf-8')
                qr_type = qr_code.type
                
                # Get bounding box
                points = qr_code.polygon
                if len(points) == 4:
                    bbox = {
                        'x': min(p.x for p in points),
                        'y': min(p.y for p in points),
                        'width': max(p.x for p in points) - min(p.x for p in points),
                        'height': max(p.y for p in points) - min(p.y for p in points)
                    }
                else:
                    bbox = None
                
                results.append({
                    'data': data,
                    'type': qr_type,
                    'bbox': bbox,
                    'raw_data': qr_code.data
                })
            
            return results
        except Exception as e:
            print(f"Error decoding QR codes: {e}")
            return []
    
    def start_camera_scan(self, callback=None):
        """Start camera scanning for QR codes."""
        try:
            self.camera = cv2.VideoCapture(0)
            self.scanning = True
            
            while self.scanning:
                ret, frame = self.camera.read()
                if not ret:
                    break
                
                # Scan for QR codes
                qr_codes = self.decode_qr_codes(frame)
                
                # Draw bounding boxes
                for qr_code in qr_codes:
                    if qr_code['bbox']:
                        bbox = qr_code['bbox']
                        cv2.rectangle(
                            frame,
                            (bbox['x'], bbox['y']),
                            (bbox['x'] + bbox['width'], bbox['y'] + bbox['height']),
                            (0, 255, 0), 2
                        )
                        cv2.putText(
                            frame, qr_code['data'][:30],
                            (bbox['x'], bbox['y'] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                        )
                
                # Show frame
                cv2.imshow('QR Code Scanner', frame)
                
                # Call callback if QR codes found
                if qr_codes and callback:
                    callback(qr_codes)
                
                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as e:
            print(f"Camera error: {e}")
        finally:
            self.stop_camera_scan()
    
    def stop_camera_scan(self):
        """Stop camera scanning."""
        self.scanning = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()


class QRCodeApp:
    """Main QR code application with GUI."""
    
    def __init__(self):
        self.generator = QRCodeGenerator()
        self.scanner = QRCodeScanner()
        
        self.root = tk.Tk()
        self.root.title("QR Code Generator & Scanner")
        self.root.geometry("900x700")
        
        self.setup_gui()
        
        # QR code history
        self.qr_history = []
    
    def setup_gui(self):
        """Setup the graphical user interface."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generator tab
        self.create_generator_tab(notebook)
        
        # Scanner tab
        self.create_scanner_tab(notebook)
        
        # Batch operations tab
        self.create_batch_tab(notebook)
        
        # History tab
        self.create_history_tab(notebook)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_generator_tab(self, notebook):
        """Create QR code generator tab."""
        gen_frame = ttk.Frame(notebook)
        notebook.add(gen_frame, text="Generator")
        
        # Left panel for inputs
        left_panel = ttk.Frame(gen_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Data input
        ttk.Label(left_panel, text="Data to encode:").pack(anchor=tk.W)
        self.data_text = scrolledtext.ScrolledText(left_panel, height=6, width=40)
        self.data_text.pack(fill=tk.X, pady=5)
        
        # Quick data templates
        templates_frame = ttk.LabelFrame(left_panel, text="Quick Templates")
        templates_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(templates_frame, text="Website URL", 
                  command=lambda: self.data_text.insert(tk.END, "https://")).pack(fill=tk.X, pady=2)
        ttk.Button(templates_frame, text="Email", 
                  command=lambda: self.data_text.insert(tk.END, "mailto:")).pack(fill=tk.X, pady=2)
        ttk.Button(templates_frame, text="Phone", 
                  command=lambda: self.data_text.insert(tk.END, "tel:")).pack(fill=tk.X, pady=2)
        ttk.Button(templates_frame, text="WiFi", 
                  command=self.insert_wifi_template).pack(fill=tk.X, pady=2)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(left_panel, text="QR Code Settings")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Error correction
        ttk.Label(settings_frame, text="Error Correction:").pack(anchor=tk.W)
        self.error_correction_var = tk.StringVar(value="Medium")
        error_combo = ttk.Combobox(settings_frame, textvariable=self.error_correction_var,
                                 values=["Low", "Medium", "Quartile", "High"], state="readonly")
        error_combo.pack(fill=tk.X, pady=2)
        
        # Size
        ttk.Label(settings_frame, text="Size:").pack(anchor=tk.W)
        self.size_var = tk.IntVar(value=10)
        size_scale = ttk.Scale(settings_frame, from_=5, to=20, variable=self.size_var, orient=tk.HORIZONTAL)
        size_scale.pack(fill=tk.X, pady=2)
        
        # Colors
        color_frame = ttk.Frame(settings_frame)
        color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(color_frame, text="Fill Color:").pack(side=tk.LEFT)
        self.fill_color_var = tk.StringVar(value="black")
        ttk.Entry(color_frame, textvariable=self.fill_color_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(color_frame, text="Background:").pack(side=tk.LEFT, padx=(10,0))
        self.back_color_var = tk.StringVar(value="white")
        ttk.Entry(color_frame, textvariable=self.back_color_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Logo
        logo_frame = ttk.Frame(settings_frame)
        logo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(logo_frame, text="Logo:").pack(side=tk.LEFT)
        self.logo_path_var = tk.StringVar()
        ttk.Entry(logo_frame, textvariable=self.logo_path_var, width=20).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo).pack(side=tk.RIGHT)
        
        # Generate button
        ttk.Button(left_panel, text="Generate QR Code", 
                  command=self.generate_qr_code).pack(fill=tk.X, pady=10)
        
        # Right panel for preview
        right_panel = ttk.Frame(gen_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Preview area
        preview_frame = ttk.LabelFrame(right_panel, text="QR Code Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = ttk.Label(preview_frame, text="Generate a QR code to preview")
        self.preview_label.pack(expand=True)
        
        # Save button
        self.save_button = ttk.Button(right_panel, text="Save QR Code", 
                                     command=self.save_qr_code, state=tk.DISABLED)
        self.save_button.pack(pady=10)
    
    def create_scanner_tab(self, notebook):
        """Create QR code scanner tab."""
        scan_frame = ttk.Frame(notebook)
        notebook.add(scan_frame, text="Scanner")
        
        # Control buttons
        button_frame = ttk.Frame(scan_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Scan from File", 
                  command=self.scan_from_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Scan from Camera", 
                  command=self.scan_from_camera).pack(side=tk.LEFT, padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(scan_frame, text="Scan Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.scan_results = scrolledtext.ScrolledText(results_frame, height=20)
        self.scan_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action buttons for scanned data
        action_frame = ttk.Frame(scan_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(action_frame, text="Open URL", 
                  command=self.open_scanned_url).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Copy to Clipboard", 
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Clear Results", 
                  command=lambda: self.scan_results.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
    
    def create_batch_tab(self, notebook):
        """Create batch operations tab."""
        batch_frame = ttk.Frame(notebook)
        notebook.add(batch_frame, text="Batch Operations")
        
        # Input methods
        input_frame = ttk.LabelFrame(batch_frame, text="Input Data")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Text input
        ttk.Label(input_frame, text="Enter data (one per line):").pack(anchor=tk.W)
        self.batch_text = scrolledtext.ScrolledText(input_frame, height=8)
        self.batch_text.pack(fill=tk.X, pady=5)
        
        # File input
        file_input_frame = ttk.Frame(input_frame)
        file_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_input_frame, text="Or load from file:").pack(side=tk.LEFT)
        self.batch_file_var = tk.StringVar()
        ttk.Entry(file_input_frame, textvariable=self.batch_file_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_input_frame, text="Browse", command=self.browse_batch_file).pack(side=tk.RIGHT)
        
        # Output settings
        output_frame = ttk.LabelFrame(batch_frame, text="Output Settings")
        output_frame.pack(fill=tk.X, padx=10, pady=10)
        
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_dir_frame, text="Output Directory:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(output_dir_frame, textvariable=self.output_dir_var).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_dir_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.RIGHT)
        
        # Process button
        ttk.Button(batch_frame, text="Generate Batch QR Codes", 
                  command=self.generate_batch_qr_codes).pack(pady=20)
        
        # Progress bar
        self.batch_progress_var = tk.DoubleVar()
        self.batch_progress = ttk.Progressbar(batch_frame, variable=self.batch_progress_var, maximum=100)
        self.batch_progress.pack(fill=tk.X, padx=10, pady=5)
        
        # Results
        batch_results_frame = ttk.LabelFrame(batch_frame, text="Batch Results")
        batch_results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.batch_results = scrolledtext.ScrolledText(batch_results_frame, height=8)
        self.batch_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_history_tab(self, notebook):
        """Create QR code history tab."""
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="History")
        
        # History list
        history_list_frame = ttk.LabelFrame(history_frame, text="Generated QR Codes")
        history_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for history
        columns = ('Date', 'Data', 'Type')
        self.history_tree = ttk.Treeview(history_list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # History actions
        history_actions = ttk.Frame(history_frame)
        history_actions.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(history_actions, text="Regenerate Selected", 
                  command=self.regenerate_from_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_actions, text="Export History", 
                  command=self.export_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_actions, text="Clear History", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
    
    def insert_wifi_template(self):
        """Insert WiFi QR code template."""
        template = "WIFI:T:WPA;S:NetworkName;P:Password;H:false;"
        self.data_text.insert(tk.END, template)
    
    def browse_logo(self):
        """Browse for logo file."""
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Logo", filetypes=file_types)
        if filename:
            self.logo_path_var.set(filename)
    
    def generate_qr_code(self):
        """Generate QR code with current settings."""
        data = self.data_text.get(1.0, tk.END).strip()
        if not data:
            messagebox.showwarning("Warning", "Please enter data to encode.")
            return
        
        try:
            # Get settings
            error_correction_map = {
                "Low": qrcode.constants.ERROR_CORRECT_L,
                "Medium": qrcode.constants.ERROR_CORRECT_M,
                "Quartile": qrcode.constants.ERROR_CORRECT_Q,
                "High": qrcode.constants.ERROR_CORRECT_H
            }
            
            settings = {
                'version': 1,
                'error_correction': error_correction_map[self.error_correction_var.get()],
                'box_size': self.size_var.get(),
                'border': 4,
                'fill_color': self.fill_color_var.get(),
                'back_color': self.back_color_var.get()
            }
            
            # Generate QR code
            self.current_qr_image = self.generator.generate_qr_code(data, settings)
            
            # Add logo if specified
            logo_path = self.logo_path_var.get()
            if logo_path and os.path.exists(logo_path):
                self.current_qr_image = self.generator.add_logo(self.current_qr_image, logo_path)
            
            # Display preview
            self.display_qr_preview(self.current_qr_image)
            
            # Add to history
            self.add_to_history(data, "Manual Generation")
            
            self.save_button.config(state=tk.NORMAL)
            self.status_var.set("QR code generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {e}")
    
    def display_qr_preview(self, qr_image):
        """Display QR code preview."""
        # Resize for preview (max 300x300)
        preview_size = (300, 300)
        preview_image = qr_image.copy()
        preview_image.thumbnail(preview_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.preview_photo = ImageTk.PhotoImage(preview_image)
        self.preview_label.config(image=self.preview_photo, text="")
    
    def save_qr_code(self):
        """Save generated QR code."""
        if not hasattr(self, 'current_qr_image'):
            messagebox.showwarning("Warning", "No QR code to save.")
            return
        
        file_types = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*")
        ]
        filename = filedialog.asksaveasfilename(
            title="Save QR Code",
            defaultextension=".png",
            filetypes=file_types
        )
        
        if filename:
            try:
                self.current_qr_image.save(filename)
                self.status_var.set(f"QR code saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save QR code: {e}")
    
    def scan_from_file(self):
        """Scan QR codes from image file."""
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Image", filetypes=file_types)
        
        if filename:
            results = self.scanner.scan_image(filename)
            self.display_scan_results(results, filename)
    
    def scan_from_camera(self):
        """Start camera scanning."""
        def camera_callback(qr_codes):
            self.root.after(0, lambda: self.display_scan_results(qr_codes, "Camera"))
        
        # Start camera in separate thread
        camera_thread = threading.Thread(target=self.scanner.start_camera_scan, args=(camera_callback,))
        camera_thread.daemon = True
        camera_thread.start()
        
        self.status_var.set("Camera scanning started. Press 'q' to stop.")
    
    def display_scan_results(self, results, source):
        """Display scan results."""
        if not results:
            self.scan_results.insert(tk.END, f"No QR codes found in {source}\n")
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.scan_results.insert(tk.END, f"=== Scan Results from {source} ===\n")
        self.scan_results.insert(tk.END, f"Time: {timestamp}\n")
        self.scan_results.insert(tk.END, f"Found {len(results)} QR code(s)\n\n")
        
        for i, result in enumerate(results, 1):
            self.scan_results.insert(tk.END, f"QR Code {i}:\n")
            self.scan_results.insert(tk.END, f"  Data: {result['data']}\n")
            self.scan_results.insert(tk.END, f"  Type: {result['type']}\n")
            if result['bbox']:
                bbox = result['bbox']
                self.scan_results.insert(tk.END, f"  Position: ({bbox['x']}, {bbox['y']}) {bbox['width']}x{bbox['height']}\n")
            self.scan_results.insert(tk.END, "\n")
        
        self.scan_results.insert(tk.END, "=" * 50 + "\n\n")
        self.scan_results.see(tk.END)
        
        # Store last scanned data for actions
        self.last_scan_results = results
    
    def open_scanned_url(self):
        """Open URL from scanned QR code."""
        if hasattr(self, 'last_scan_results'):
            for result in self.last_scan_results:
                data = result['data']
                if data.startswith(('http://', 'https://')):
                    webbrowser.open(data)
                    self.status_var.set(f"Opened URL: {data}")
                    return
            messagebox.showinfo("Info", "No valid URLs found in scanned QR codes.")
    
    def copy_to_clipboard(self):
        """Copy scanned data to clipboard."""
        if hasattr(self, 'last_scan_results') and self.last_scan_results:
            data = self.last_scan_results[0]['data']
            self.root.clipboard_clear()
            self.root.clipboard_append(data)
            self.status_var.set("Data copied to clipboard")
    
    def browse_batch_file(self):
        """Browse for batch input file."""
        file_types = [
            ("Text files", "*.txt"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Batch File", filetypes=file_types)
        if filename:
            self.batch_file_var.set(filename)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def generate_batch_qr_codes(self):
        """Generate QR codes in batch."""
        # Get data list
        data_list = []
        
        # From text area
        text_data = self.batch_text.get(1.0, tk.END).strip()
        if text_data:
            data_list.extend(line.strip() for line in text_data.split('\n') if line.strip())
        
        # From file
        batch_file = self.batch_file_var.get()
        if batch_file and os.path.exists(batch_file):
            try:
                with open(batch_file, 'r') as f:
                    file_data = f.read().strip()
                    data_list.extend(line.strip() for line in file_data.split('\n') if line.strip())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read batch file: {e}")
                return
        
        if not data_list:
            messagebox.showwarning("Warning", "No data to process.")
            return
        
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showwarning("Warning", "Please select output directory.")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Process in separate thread
        thread = threading.Thread(target=self.process_batch, args=(data_list, output_dir))
        thread.daemon = True
        thread.start()
    
    def process_batch(self, data_list, output_dir):
        """Process batch QR code generation."""
        try:
            self.root.after(0, lambda: self.status_var.set("Processing batch..."))
            
            # Get current settings
            error_correction_map = {
                "Low": qrcode.constants.ERROR_CORRECT_L,
                "Medium": qrcode.constants.ERROR_CORRECT_M,
                "Quartile": qrcode.constants.ERROR_CORRECT_Q,
                "High": qrcode.constants.ERROR_CORRECT_H
            }
            
            settings = {
                'version': 1,
                'error_correction': error_correction_map[self.error_correction_var.get()],
                'box_size': self.size_var.get(),
                'border': 4,
                'fill_color': self.fill_color_var.get(),
                'back_color': self.back_color_var.get()
            }
            
            # Generate QR codes
            results = self.generator.generate_batch_qr_codes(data_list, output_dir, settings)
            
            # Update progress and results
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful
            
            self.root.after(0, lambda: self.batch_progress_var.set(100))
            self.root.after(0, lambda: self.display_batch_results(results, successful, failed))
            self.root.after(0, lambda: self.status_var.set(f"Batch complete: {successful} successful, {failed} failed"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Batch processing failed: {e}"))
    
    def display_batch_results(self, results, successful, failed):
        """Display batch processing results."""
        self.batch_results.delete(1.0, tk.END)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.batch_results.insert(tk.END, f"=== Batch Processing Results ===\n")
        self.batch_results.insert(tk.END, f"Time: {timestamp}\n")
        self.batch_results.insert(tk.END, f"Total: {len(results)} | Successful: {successful} | Failed: {failed}\n\n")
        
        for result in results:
            if result['success']:
                self.batch_results.insert(tk.END, f"✓ {result['data'][:50]}... → {result['filename']}\n")
            else:
                self.batch_results.insert(tk.END, f"✗ {result['data'][:50]}... → {result['error']}\n")
        
        self.batch_results.see(tk.END)
    
    def add_to_history(self, data, operation_type):
        """Add QR code to history."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.qr_history.append({
            'timestamp': timestamp,
            'data': data,
            'type': operation_type
        })
        
        # Update history tree
        self.history_tree.insert('', tk.END, values=(timestamp, data[:50], operation_type))
    
    def regenerate_from_history(self):
        """Regenerate QR code from history selection."""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item from history.")
            return
        
        item = self.history_tree.item(selection[0])
        data = item['values'][1]
        
        # Find full data in history
        for hist_item in self.qr_history:
            if hist_item['data'].startswith(data):
                self.data_text.delete(1.0, tk.END)
                self.data_text.insert(1.0, hist_item['data'])
                self.generate_qr_code()
                break
    
    def export_history(self):
        """Export QR code history."""
        if not self.qr_history:
            messagebox.showinfo("Info", "No history to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export History",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.qr_history, f, indent=2)
                self.status_var.set(f"History exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export history: {e}")
    
    def clear_history(self):
        """Clear QR code history."""
        if messagebox.askyesno("Confirm", "Clear all history?"):
            self.qr_history.clear()
            self.history_tree.delete(*self.history_tree.get_children())
            self.status_var.set("History cleared")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main function to run the QR code application."""
    try:
        app = QRCodeApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Make sure you have installed all required packages:")
        print("pip install qrcode[pil] opencv-python pyzbar")


if __name__ == "__main__":
    main()
