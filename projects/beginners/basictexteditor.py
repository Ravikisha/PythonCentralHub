# Basic Text Editor

import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter import ttk
import os

class BasicTextEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Basic Text Editor")
        self.root.geometry("800x600")
        
        self.current_file = None
        self.text_changed = False
        
        self.create_menu()
        self.create_toolbar()
        self.create_text_area()
        self.create_status_bar()
        
        # Bind events
        self.text_area.bind('<KeyPress>', self.on_text_change)
        self.text_area.bind('<Button-1>', self.update_status)
        self.text_area.bind('<KeyRelease>', self.update_status)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        
        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Font", command=self.change_font)
        format_menu.add_command(label="Word Wrap", command=self.toggle_word_wrap)
        
        # Bind keyboard shortcuts
        self.root.bind_all("<Control-n>", lambda e: self.new_file())
        self.root.bind_all("<Control-o>", lambda e: self.open_file())
        self.root.bind_all("<Control-s>", lambda e: self.save_file())
        self.root.bind_all("<Control-f>", lambda e: self.find_text())
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        # File operations
        ttk.Button(toolbar, text="New", command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Edit operations
        ttk.Button(toolbar, text="Cut", command=self.cut).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Copy", command=self.copy).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Paste", command=self.paste).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Find
        ttk.Button(toolbar, text="Find", command=self.find_text).pack(side=tk.LEFT, padx=2)
    
    def create_text_area(self):
        """Create the main text area"""
        # Frame for text area and scrollbars
        text_frame = tk.Frame(self.root)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text area
        self.text_area = tk.Text(text_frame, wrap=tk.WORD, undo=True, maxundo=20)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.text_area.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
        self.text_area.config(xscrollcommand=h_scrollbar.set)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready | Line: 1, Column: 1", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def new_file(self):
        """Create a new file"""
        if self.text_changed:
            if not self.ask_save_changes():
                return
        
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.text_changed = False
        self.update_title()
    
    def open_file(self):
        """Open an existing file"""
        if self.text_changed:
            if not self.ask_save_changes():
                return
        
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, content)
                self.current_file = file_path
                self.text_changed = False
                self.update_title()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{str(e)}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END + '-1c')
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.text_changed = False
                self.update_title()
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save the file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END + '-1c')
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.text_changed = False
                self.update_title()
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
    
    def cut(self):
        """Cut selected text"""
        try:
            self.text_area.event_generate("<<Cut>>")
        except tk.TclError:
            pass
    
    def copy(self):
        """Copy selected text"""
        try:
            self.text_area.event_generate("<<Copy>>")
        except tk.TclError:
            pass
    
    def paste(self):
        """Paste text from clipboard"""
        try:
            self.text_area.event_generate("<<Paste>>")
        except tk.TclError:
            pass
    
    def select_all(self):
        """Select all text"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
    
    def undo(self):
        """Undo last action"""
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass
    
    def redo(self):
        """Redo last undone action"""
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass
    
    def find_text(self):
        """Open find dialog"""
        search_window = tk.Toplevel(self.root)
        search_window.title("Find")
        search_window.geometry("300x100")
        search_window.transient(self.root)
        search_window.grab_set()
        
        tk.Label(search_window, text="Find:").pack(pady=5)
        search_entry = tk.Entry(search_window, width=30)
        search_entry.pack(pady=5)
        search_entry.focus()
        
        def search():
            query = search_entry.get()
            if query:
                start_pos = self.text_area.search(query, tk.INSERT, tk.END)
                if start_pos:
                    end_pos = f"{start_pos}+{len(query)}c"
                    self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
                    self.text_area.tag_add(tk.SEL, start_pos, end_pos)
                    self.text_area.mark_set(tk.INSERT, end_pos)
                    self.text_area.see(tk.INSERT)
                else:
                    messagebox.showinfo("Not Found", f"'{query}' not found.")
        
        tk.Button(search_window, text="Find", command=search).pack(pady=5)
        search_entry.bind('<Return>', lambda e: search())
    
    def change_font(self):
        """Open font selection dialog"""
        current_font = font.Font(font=self.text_area['font'])
        
        font_window = tk.Toplevel(self.root)
        font_window.title("Font")
        font_window.geometry("300x200")
        font_window.transient(self.root)
        font_window.grab_set()
        
        # Font family
        tk.Label(font_window, text="Font:").pack()
        font_var = tk.StringVar(value=current_font.actual()['family'])
        font_combo = ttk.Combobox(font_window, textvariable=font_var, values=list(font.families()))
        font_combo.pack(pady=5)
        
        # Font size
        tk.Label(font_window, text="Size:").pack()
        size_var = tk.StringVar(value=str(current_font.actual()['size']))
        size_entry = tk.Entry(font_window, textvariable=size_var)
        size_entry.pack(pady=5)
        
        def apply_font():
            try:
                new_font = (font_var.get(), int(size_var.get()))
                self.text_area.config(font=new_font)
                font_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid font size")
        
        tk.Button(font_window, text="OK", command=apply_font).pack(pady=10)
    
    def toggle_word_wrap(self):
        """Toggle word wrap"""
        current_wrap = self.text_area.cget('wrap')
        new_wrap = tk.NONE if current_wrap == tk.WORD else tk.WORD
        self.text_area.config(wrap=new_wrap)
    
    def on_text_change(self, event=None):
        """Handle text changes"""
        if not self.text_changed:
            self.text_changed = True
            self.update_title()
    
    def update_status(self, event=None):
        """Update status bar with cursor position"""
        cursor_pos = self.text_area.index(tk.INSERT)
        line, column = cursor_pos.split('.')
        self.status_bar.config(text=f"Line: {line}, Column: {int(column)+1}")
    
    def update_title(self):
        """Update window title"""
        title = "Basic Text Editor"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.text_changed:
            title += " *"
        self.root.title(title)
    
    def ask_save_changes(self):
        """Ask user if they want to save changes"""
        result = messagebox.askyesnocancel("Save Changes", "Do you want to save changes?")
        if result is True:
            self.save_file()
            return not self.text_changed
        elif result is False:
            return True
        else:
            return False
    
    def on_closing(self):
        """Handle window closing"""
        if self.text_changed:
            if self.ask_save_changes():
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the text editor"""
        self.root.mainloop()

def main():
    """Main function to run the text editor"""
    editor = BasicTextEditor()
    editor.run()

if __name__ == "__main__":
    main()
