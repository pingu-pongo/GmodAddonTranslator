import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from threading import Thread
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
        clear_button.pack(side=tk.LEFT)
        
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
        messagebox.showerror(
            "Initialization Failed",
            "Could not find the Garry's Mod workshop folder.\n"
            "Please ensure the game is installed."
        )
        
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