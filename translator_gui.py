import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from threading import Thread
import os
import subprocess
import shutil
from translator_logic import GModAddonTranslator

class TranslatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Garry's Mod Addon Translator")
        self.root.geometry("750x700")
        self.root.resizable(True, True)
        
        self.translator = None
        self.processing = False
        
        self.setup_gui()
        
    def setup_gui(self):
        """Create all GUI elements"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Garry's Mod Addon Translator",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=(0, 5))
        
        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Translates workshop addon IDs to readable names and decompiles .gma files",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        desc_label.pack(pady=(0, 5))
        
        # Developer credit
        dev_label = ttk.Label(
            main_frame,
            text="Developed by Pingu  •  discord: pingu._",
            font=("Segoe UI", 8),
            foreground="darkgray"
        )
        dev_label.pack(pady=(0, 20))
        
        # Workshop folder status frame
        folder_frame = ttk.LabelFrame(main_frame, text="Workshop Folder Status", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.folder_label = ttk.Label(
            folder_frame,
            text="Click 'Initialize' to search for workshop folder...",
            font=("Segoe UI", 9),
            wraplength=680,
            foreground="gray"
        )
        self.folder_label.pack()
        
        # Initialize button
        self.init_button = ttk.Button(
            folder_frame,
            text="Initialize",
            command=self.initialize_translator
        )
        self.init_button.pack(pady=(10, 0))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Thread count selector
        thread_frame = ttk.Frame(settings_frame)
        thread_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            thread_frame,
            text="Number of threads:",
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.thread_spinbox = ttk.Spinbox(
            thread_frame,
            from_=1,
            to=20,
            width=10,
            font=("Segoe UI", 9)
        )
        self.thread_spinbox.set(6)
        self.thread_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(
            thread_frame,
            text="(Recommended: 4-8)",
            font=("Segoe UI", 8),
            foreground="gray"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Progress label
        self.progress_label = ttk.Label(
            progress_frame,
            text="Ready to start",
            font=("Segoe UI", 9)
        )
        self.progress_label.pack(pady=(0, 10))
        
        # Status text area
        self.status_text = scrolledtext.ScrolledText(
            progress_frame,
            height=12,
            width=80,
            font=("Consolas", 8),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 5))
        
        # Start button (larger and more prominent)
        self.start_button = ttk.Button(
            button_frame,
            text="▶ Start Processing",
            command=self.start_processing,
            state=tk.DISABLED,
            width=25
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear log button
        clear_button = ttk.Button(
            button_frame,
            text="Clear Log",
            command=self.clear_log,
            width=15
        )
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open folder button
        self.open_folder_button = ttk.Button(
            button_frame,
            text="Open Translated Folder",
            command=self.open_translated_folder,
            state=tk.DISABLED,
            width=25
        )
        self.open_folder_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delete folder button
        self.delete_folder_button = ttk.Button(
            button_frame,
            text="Delete Translated Folder",
            command=self.delete_translated_folder,
            state=tk.DISABLED,
            width=25
        )
        self.delete_folder_button.pack(side=tk.LEFT)
        
    def log_message(self, message):
        """Add a message to the status text area"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        
    def update_progress(self, current, total):
        """Update the progress bar and label"""
        percentage = (current / total) * 100
        self.progress_bar['value'] = percentage
        self.progress_label.config(text=f"Processing: {current}/{total} addons ({percentage:.1f}%)")
        
    def clear_log(self):
        """Clear the status text area"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def open_translated_folder(self):
        """Open the translated folder in File Explorer"""
        if self.translator and self.translator.translated_path:
            try:
                if os.path.exists(self.translator.translated_path):
                    # Open folder in file manager (cross-platform)
                    import platform
                    system = platform.system()

                    if system == "Windows":
                        os.startfile(self.translator.translated_path)
                    elif system == "Darwin":  # macOS
                        subprocess.run(["open", self.translator.translated_path])
                    else:  # Linux and others
                        subprocess.run(["xdg-open", self.translator.translated_path])
                else:
                    messagebox.showerror("Folder Not Found", "The translated folder does not exist yet.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder:\n{e}")
        else:
            messagebox.showwarning("Not Initialized", "Please initialize first to locate the folder.")
    
    def delete_translated_folder(self):
        """Delete the translated folder after confirmation"""
        if not self.translator or not self.translator.translated_path:
            messagebox.showwarning("Not Initialized", "Please initialize first to locate the folder.")
            return
        
        if not os.path.exists(self.translator.translated_path):
            messagebox.showinfo("Already Deleted", "The translated folder does not exist.")
            return
        
        # Calculate folder size for the confirmation message
        try:
            size_bytes = self.translator.get_folder_size(self.translator.translated_path)
            size_formatted = self.translator.format_size(size_bytes)
            size_info = f"\nFolder size: {size_formatted}"
        except:
            size_info = ""
        
        # Confirmation dialog
        result = messagebox.askyesno(
            "Delete Translated Folder",
            f"Are you sure you want to delete the translated folder?{size_info}\n\n"
            f"Path: {self.translator.translated_path}\n\n"
            "⚠️ This action cannot be undone!",
            icon='warning'
        )
        
        if result:
            self.log_message("\n" + "=" * 70)
            self.log_message("🗑️ Deletion confirmed - Starting folder deletion...")
            self.log_message("This may take a while for large folders...")
            self.log_message("=" * 70)
            
            # Disable buttons during deletion
            self.delete_folder_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.DISABLED)
            self.open_folder_button.config(state=tk.DISABLED)
            self.thread_spinbox.config(state=tk.DISABLED)
            
            # Reset and show progress bar
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Deleting folder...")
            
            def delete_with_progress():
                try:
                    folder_path = self.translator.translated_path
                    
                    # Count total items for progress
                    total_items = sum(len(files) + len(dirs) for _, dirs, files in os.walk(folder_path))
                    deleted_items = 0
                    
                    # Delete files and track progress
                    for root, dirs, files in os.walk(folder_path, topdown=False):
                        for name in files:
                            try:
                                os.remove(os.path.join(root, name))
                                deleted_items += 1
                                if deleted_items % 50 == 0:  # Update every 50 items
                                    progress = (deleted_items / total_items) * 100
                                    self.root.after(0, lambda p=progress: self.progress_bar.config(value=p))
                                    self.root.after(0, lambda d=deleted_items, t=total_items: 
                                                  self.progress_label.config(text=f"Deleting... {d}/{t} items"))
                            except Exception as e:
                                self.root.after(0, lambda err=e: self.log_message(f"  ⚠ Error deleting file: {err}"))
                        
                        for name in dirs:
                            try:
                                os.rmdir(os.path.join(root, name))
                                deleted_items += 1
                            except Exception as e:
                                self.root.after(0, lambda err=e: self.log_message(f"  ⚠ Error deleting directory: {err}"))
                    
                    # Remove the main folder
                    os.rmdir(folder_path)
                    
                    self.root.after(0, self.on_deletion_complete)
                    
                except Exception as e:
                    self.root.after(0, lambda err=e: self.on_deletion_error(str(err)))
            
            # Run deletion in background thread
            Thread(target=delete_with_progress, daemon=True).start()
    
    def on_deletion_complete(self):
        """Called when folder deletion completes"""
        self.progress_bar['value'] = 100
        self.progress_label.config(text="Deletion complete")
        self.log_message("\n✓ Translated folder deleted successfully")
        self.log_message("=" * 70)
        
        # Re-enable buttons
        self.delete_folder_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)
        self.thread_spinbox.config(state=tk.NORMAL)
        
        # Keep Open Folder button disabled since folder is gone
        self.open_folder_button.config(state=tk.DISABLED)
        
        # Reset progress after a moment
        self.root.after(2000, lambda: self.progress_bar.config(value=0))
        self.root.after(2000, lambda: self.progress_label.config(text="Ready to start"))
    
    def on_deletion_error(self, error):
        """Called when folder deletion encounters an error"""
        self.log_message(f"\n✗ Error deleting folder: {error}")
        self.log_message("=" * 70)
        
        # Re-enable buttons
        self.delete_folder_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)
        self.open_folder_button.config(state=tk.NORMAL)
        self.thread_spinbox.config(state=tk.NORMAL)
        
        messagebox.showerror("Deletion Error", f"Could not delete folder:\n{error}")
        
    def initialize_translator(self):
        """Initialize the translator and find workshop folders"""
        self.init_button.config(state=tk.DISABLED)
        self.folder_label.config(text="Initializing...", foreground="blue")
        
        def init_thread():
            self.translator = GModAddonTranslator(
                progress_callback=self.update_progress,
                log_callback=self.log_message
            )
            
            if self.translator.initialize():
                self.root.after(0, self.on_init_success)
            else:
                self.root.after(0, self.on_init_failure)
        
        Thread(target=init_thread, daemon=True).start()
        
    def on_init_success(self):
        """Called when initialization succeeds"""
        self.folder_label.config(
            text=f"✓ Found: {self.translator.workshop_path}\n"
                 f"Output: {self.translator.translated_path}",
            foreground="green"
        )
        self.start_button.config(state=tk.NORMAL)
        self.open_folder_button.config(state=tk.NORMAL)
        self.delete_folder_button.config(state=tk.NORMAL)
        self.init_button.config(text="Re-Initialize", state=tk.NORMAL)
        self.log_message("=" * 70)
        self.log_message("✓ Initialization complete! Ready to process addons.")
        self.log_message("Click 'Start Processing' to begin.")
        self.log_message("=" * 70)
        
    def on_init_failure(self):
        """Called when initialization fails"""
        self.folder_label.config(
            text="✗ Workshop folder not found. Please ensure Garry's Mod is installed.",
            foreground="red"
        )
        self.init_button.config(state=tk.NORMAL)

        # Ask if user wants to manually configure paths
        result = messagebox.askyesno(
            "Initialization Failed",
            "Could not find the Garry's Mod workshop folder automatically.\n\n"
            "Would you like to manually configure the paths?",
            icon='question'
        )

        if result:
            self.show_manual_path_dialog()

    def show_manual_path_dialog(self):
        """Show dialog for manually entering paths"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Manual Path Configuration")
        dialog.geometry("800x325")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"800x325+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(
            main_frame,
            text="Manual Path Configuration",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=(0, 10), anchor="center")

        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="Please provide the paths to your Garry's Mod files.\n"
                 "Workshop path is required. gmad and cache are optional but recommended.",
            font=("Segoe UI", 9),
            foreground="gray",
            justify="center"
        )
        instructions.pack(pady=(0, 20), anchor="center")

        # Workshop path (required)
        workshop_frame = ttk.LabelFrame(main_frame, text="Workshop Path (Required)", padding="10")
        workshop_frame.pack(fill=tk.X, pady=(0, 10))

        workshop_entry = ttk.Entry(workshop_frame, width=60, font=("Segoe UI", 9))
        workshop_entry.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            workshop_frame,
            text="Browse...",
            command=lambda: self.browse_directory(workshop_entry)
        ).pack(side=tk.LEFT)

        workshop_hint = ttk.Label(
            workshop_frame,
            text="Example: ~/.steam/steam/steamapps/workshop/content/4000",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        workshop_hint.pack(anchor=tk.E, pady=(5, 0))

        # gmad path (optional)
        gmad_frame = ttk.LabelFrame(main_frame, text="gmad Executable Path (Optional)", padding="10")
        gmad_frame.pack(fill=tk.X, pady=(0, 10))

        gmad_entry = ttk.Entry(gmad_frame, width=60, font=("Segoe UI", 9))
        gmad_entry.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            gmad_frame,
            text="Browse...",
            command=lambda: self.browse_file(gmad_entry)
        ).pack(side=tk.LEFT)

        gmad_hint = ttk.Label(
            gmad_frame,
            text="Example: ~/.steam/steam/steamapps/common/GarrysMod/bin/linux64/gmad",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        gmad_hint.pack(anchor=tk.E, pady=(5, 0))

        # Cache path (optional)
        cache_frame = ttk.LabelFrame(main_frame, text="Cache Path (Optional)", padding="10")
        cache_frame.pack(fill=tk.X, pady=(0, 20))

        cache_entry = ttk.Entry(cache_frame, width=60, font=("Segoe UI", 9))
        cache_entry.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            cache_frame,
            text="Browse...",
            command=lambda: self.browse_directory(cache_entry)
        ).pack(side=tk.LEFT)

        cache_hint = ttk.Label(
            cache_frame,
            text="Example: ~/.steam/steam/steamapps/common/GarrysMod/garrysmod/cache/workshop",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        cache_hint.pack(anchor=tk.E, pady=(5, 0))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def validate_and_apply():
            workshop = workshop_entry.get().strip()
            gmad = gmad_entry.get().strip() or None
            cache = cache_entry.get().strip() or None

            if not workshop:
                messagebox.showerror(
                    "Missing Workshop Path",
                    "Workshop path is required!",
                    parent=dialog
                )
                return

            # Expand ~ to home directory
            workshop = os.path.expanduser(workshop)
            if gmad:
                gmad = os.path.expanduser(gmad)
            if cache:
                cache = os.path.expanduser(cache)

            # Set paths in translator
            success, message = self.translator.set_manual_paths(workshop, gmad, cache)

            if success:
                dialog.destroy()
                self.on_manual_init_success()
            else:
                messagebox.showerror(
                    "Validation Failed",
                    message,
                    parent=dialog
                )

        ttk.Button(
            button_frame,
            text="Apply",
            command=validate_and_apply,
            width=15
        ).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=15
        ).pack(side=tk.RIGHT)

    def browse_directory(self, entry_widget):
        """Open directory browser and set the selected path in entry widget"""
        initial_dir = entry_widget.get().strip()
        if initial_dir:
            initial_dir = os.path.expanduser(initial_dir)
            if not os.path.exists(initial_dir):
                initial_dir = os.path.expanduser("~")
        else:
            initial_dir = os.path.expanduser("~")

        directory = filedialog.askdirectory(
            title="Select Directory",
            initialdir=initial_dir
        )

        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)

    def browse_file(self, entry_widget):
        """Open file browser and set the selected path in entry widget"""
        initial_dir = entry_widget.get().strip()
        if initial_dir:
            initial_dir = os.path.dirname(os.path.expanduser(initial_dir))
            if not os.path.exists(initial_dir):
                initial_dir = os.path.expanduser("~")
        else:
            initial_dir = os.path.expanduser("~")

        filepath = filedialog.askopenfilename(
            title="Select File",
            initialdir=initial_dir
        )

        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)

    def on_manual_init_success(self):
        """Called when manual path configuration succeeds"""
        self.folder_label.config(
            text=f"✓ Found: {self.translator.workshop_path}\n"
                 f"Output: {self.translator.translated_path}",
            foreground="green"
        )
        self.start_button.config(state=tk.NORMAL)
        self.open_folder_button.config(state=tk.NORMAL)
        self.delete_folder_button.config(state=tk.NORMAL)
        self.init_button.config(text="Re-Initialize", state=tk.NORMAL)
        self.log_message("=" * 70)
        self.log_message("✓ Manual path configuration successful!")
        self.log_message("Click 'Start Processing' to begin.")
        self.log_message("=" * 70)
        
    def start_processing(self):
        """Start the addon processing in a background thread"""
        if self.processing:
            return
            
        try:
            threads = int(self.thread_spinbox.get())
            if threads < 1 or threads > 20:
                raise ValueError()
        except:
            messagebox.showerror("Invalid Input", "Please enter a valid number of threads (1-20)")
            return
        
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.init_button.config(state=tk.DISABLED)
        self.thread_spinbox.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting...")
        
        def process_thread():
            try:
                self.translator.process_addons(max_workers=threads)
                self.root.after(0, self.on_processing_complete)
            except Exception as e:
                self.root.after(0, lambda: self.on_processing_error(str(e)))
        
        Thread(target=process_thread, daemon=True).start()
        
    def on_processing_complete(self):
        """Called when processing completes successfully"""
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.open_folder_button.config(state=tk.NORMAL)
        self.thread_spinbox.config(state=tk.NORMAL)
        self.progress_bar['value'] = 100
        
        # Calculate and display folder size
        def calculate_size():
            size_bytes = self.translator.get_folder_size(self.translator.translated_path)
            size_formatted = self.translator.format_size(size_bytes)
            
            self.root.after(0, lambda: self.log_message("\n" + "=" * 70))
            self.root.after(0, lambda: self.log_message("✓ Processing complete!"))
            self.root.after(0, lambda: self.log_message(f"📁 Total folder size: {size_formatted}"))
            self.root.after(0, lambda: self.log_message(f"📂 Location: {self.translator.translated_path}"))
            self.root.after(0, lambda: self.log_message("=" * 70))
        
        # Calculate size in background thread to avoid freezing UI
        Thread(target=calculate_size, daemon=True).start()
        
    def on_processing_error(self, error):
        """Called when processing encounters an error"""
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.thread_spinbox.config(state=tk.NORMAL)
        
        messagebox.showerror(
            "Processing Error",
            f"An error occurred during processing:\n\n{error}"
        )
        
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TranslatorGUI()
    app.run()