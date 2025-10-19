import os
import shutil
import subprocess
import string
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

class GModAddonTranslator:
    def __init__(self, progress_callback=None, log_callback=None):
        self.steam_path = None
        self.workshop_path = None
        self.translated_path = None
        self.gmad_path = None
        self.cache_path = None
        self.print_lock = Lock()

        # Callbacks for GUI updates
        self.progress_callback = progress_callback
        self.log_callback = log_callback

        # Default path candidates for auto-detection
        self.WORKSHOP_PATH_CANDIDATES = [
            # Linux paths
            os.path.expanduser("~/.steam/steam/steamapps/workshop/content/4000"),
            os.path.expanduser("~/.local/share/Steam/steamapps/workshop/content/4000"),
            # Windows paths (will be expanded with drive letters)
            "Program Files (x86)/Steam/steamapps/workshop/content/4000",
            "Steam/steamapps/workshop/content/4000",
        ]

        self.GMAD_PATH_CANDIDATES = [
            # Linux paths
            os.path.expanduser("~/.steam/steam/steamapps/common/GarrysMod/bin/linux64/gmad"),
            os.path.expanduser("~/.local/share/Steam/steamapps/common/GarrysMod/bin/linux64/gmad"),
            # Windows paths (relative, will be combined with drives)
            "Program Files (x86)/Steam/steamapps/common/GarrysMod/bin/gmad.exe",
            "Steam/steamapps/common/GarrysMod/bin/gmad.exe",
        ]

        self.CACHE_PATH_CANDIDATES = [
            # Linux paths
            os.path.expanduser("~/.steam/steam/steamapps/common/GarrysMod/garrysmod/cache/workshop"),
            os.path.expanduser("~/.local/share/Steam/steamapps/common/GarrysMod/garrysmod/cache/workshop"),
            # Windows paths (relative, will be combined with drives)
            "Program Files (x86)/Steam/steamapps/common/GarrysMod/garrysmod/cache/workshop",
            "Steam/steamapps/common/GarrysMod/garrysmod/cache/workshop",
        ]
        
    def log(self, message):
        """Log a message (to console or GUI)"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def update_progress(self, current, total):
        """Update progress (for GUI)"""
        if self.progress_callback:
            self.progress_callback(current, total)
    
    def safe_log(self, message):
        """Thread-safe logging"""
        with self.print_lock:
            self.log(message)
        
    def get_windows_drives(self):
        """Get all available Windows drive letters"""
        return [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

    def find_steam_workshop(self):
        """Search for the Steam workshop folder using multiple path candidates"""
        self.log("Searching for Steam workshop folder...")

        # First check all absolute path candidates (primarily Linux paths)
        for candidate in self.WORKSHOP_PATH_CANDIDATES:
            if os.path.isabs(candidate) and os.path.exists(candidate):
                self.log(f"✓ Found workshop folder: {candidate}")
                self.workshop_path = candidate
                return True

        # Then check Windows paths with all available drives
        drives = self.get_windows_drives()
        for drive in drives:
            for candidate in self.WORKSHOP_PATH_CANDIDATES:
                if not os.path.isabs(candidate):  # Only relative paths (Windows paths)
                    full_path = os.path.join(drive, candidate)
                    if os.path.exists(full_path):
                        self.log(f"✓ Found workshop folder: {full_path}")
                        self.workshop_path = full_path
                        return True

        self.log("✗ Steam workshop folder not found automatically")
        return False
    
    def find_gmad_exe(self):
        """Locate gmad executable using multiple path candidates"""
        self.log("Searching for gmad executable...")

        # First check all absolute path candidates (primarily Linux paths)
        for candidate in self.GMAD_PATH_CANDIDATES:
            if os.path.isabs(candidate) and os.path.exists(candidate):
                self.log(f"✓ Found gmad: {candidate}")
                self.gmad_path = str(candidate)
                self.find_cache_folder()
                return True

        # Then check Windows paths with all available drives
        drives = self.get_windows_drives()
        for drive in drives:
            for candidate in self.GMAD_PATH_CANDIDATES:
                if not os.path.isabs(candidate):  # Only relative paths (Windows paths)
                    full_path = os.path.join(drive, candidate)
                    if os.path.exists(full_path):
                        self.log(f"✓ Found gmad: {full_path}")
                        self.gmad_path = str(full_path)
                        self.find_cache_folder()
                        return True

        self.log("⚠ gmad executable not found. Decompilation will be skipped.")
        return False

    def find_cache_folder(self):
        """Locate the cache folder using multiple path candidates"""
        self.log("Searching for cache folder...")

        # First check all absolute path candidates (primarily Linux paths)
        for candidate in self.CACHE_PATH_CANDIDATES:
            if os.path.isabs(candidate) and os.path.exists(candidate):
                self.log(f"✓ Found cache folder: {candidate}")
                self.cache_path = Path(candidate)
                return True

        # Then check Windows paths with all available drives
        drives = self.get_windows_drives()
        for drive in drives:
            for candidate in self.CACHE_PATH_CANDIDATES:
                if not os.path.isabs(candidate):  # Only relative paths (Windows paths)
                    full_path = os.path.join(drive, candidate)
                    if os.path.exists(full_path):
                        self.log(f"✓ Found cache folder: {full_path}")
                        self.cache_path = Path(full_path)
                        return True

        self.log("⚠ Cache folder not found")
        self.cache_path = None
        return False
    
    def get_addon_name(self, addon_id):
        """Fetch addon name from Steam Workshop"""
        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={addon_id}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title_div = soup.find('div', class_='workshopItemTitle')
                
                if title_div:
                    title = title_div.text.strip()
                    # Clean title for folder name (remove invalid characters)
                    invalid_chars = '<>:"/\\|?*'
                    for char in invalid_chars:
                        title = title.replace(char, '')
                    return title
                    
        except Exception as e:
            self.safe_log(f"  ⚠ Error fetching addon {addon_id}: {e}")
            
        return None
    
    def create_translated_folder(self):
        """Create the 4000Translated folder"""
        parent_dir = os.path.dirname(self.workshop_path)
        self.translated_path = os.path.join(parent_dir, "4000Translated")
        
        if not os.path.exists(self.translated_path):
            os.makedirs(self.translated_path)
            self.log(f"✓ Created folder: {self.translated_path}")
        else:
            self.log(f"✓ Using existing folder: {self.translated_path}")
            
        return True
    
    def process_addons(self, max_workers=6):
        """Process all addon folders with multi-threading"""
        self.log("\nProcessing addons...")
        
        # Get all addon ID folders
        addon_folders = [f for f in os.listdir(self.workshop_path) 
                        if os.path.isdir(os.path.join(self.workshop_path, f)) 
                        and f.isdigit()]
        
        total = len(addon_folders)
        self.log(f"Found {total} addons in workshop folder")
        
        # Filter out addons that are already processed
        addons_to_process = []
        skipped = 0
        
        self.log("Checking for already processed addons...")
        for addon_id in addon_folders:
            # Check if any folder in translated_path contains this addon_id in a shortcut
            if self.is_addon_already_processed(addon_id):
                skipped += 1
            else:
                addons_to_process.append(addon_id)
        
        if skipped > 0:
            self.log(f"✓ Skipping {skipped} already processed addons")
        
        if len(addons_to_process) == 0:
            self.log("✓ All addons are already processed!")
            return True
        
        self.log(f"Processing {len(addons_to_process)} new addons")
        self.log(f"Using {max_workers} threads\n")
        
        completed = 0
        total_to_process = len(addons_to_process)
        
        # Process addons in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_addon = {
                executor.submit(self.process_single_addon, addon_id, idx, total_to_process): addon_id 
                for idx, addon_id in enumerate(addons_to_process, 1)
            }
            
            # Process completed tasks
            for future in as_completed(future_to_addon):
                addon_id = future_to_addon[future]
                try:
                    future.result()
                    completed += 1
                    self.update_progress(completed, total_to_process)
                except Exception as e:
                    self.safe_log(f"✗ Error processing addon {addon_id}: {e}")
                    completed += 1
                    self.update_progress(completed, total_to_process)
        
        self.log(f"\n✓ Completed processing {completed}/{total_to_process} new addons!")
        self.log(f"✓ Total addons in library: {total} ({skipped} previously processed + {completed} newly processed)")
        return True
    
    def is_addon_already_processed(self, addon_id):
        """Check if an addon has already been processed by looking for its shortcut"""
        if not os.path.exists(self.translated_path):
            return False
        
        # Check all folders in the translated path
        try:
            for folder_name in os.listdir(self.translated_path):
                folder_path = os.path.join(self.translated_path, folder_name)
                if os.path.isdir(folder_path):
                    # Check if the workshop shortcut exists and contains this addon_id
                    shortcut_path = os.path.join(folder_path, "View on Steam Workshop.url")
                    if os.path.exists(shortcut_path):
                        try:
                            with open(shortcut_path, 'r') as f:
                                content = f.read()
                                if f"id={addon_id}" in content:
                                    return True
                        except:
                            pass
        except Exception as e:
            self.log(f"⚠ Error checking processed addons: {e}")
        
        return False
    
    def process_single_addon(self, addon_id, idx, total):
        """Process a single addon (called by multiple threads)"""
        self.safe_log(f"[{idx}/{total}] Processing addon {addon_id}...")
        
        # Get addon name from Steam Workshop
        addon_name = self.get_addon_name(addon_id)
        
        if not addon_name:
            self.safe_log(f"  ⚠ Could not fetch name, using ID: {addon_id}")
            addon_name = f"addon_{addon_id}"
        else:
            self.safe_log(f"  ✓ Found name: {addon_name}")
        
        # Create source and destination paths
        source_path = os.path.join(self.workshop_path, addon_id)
        dest_path = os.path.join(self.translated_path, addon_name)
        
        # Copy the folder (this should only happen for new addons now)
        try:
            shutil.copytree(source_path, dest_path)
            self.safe_log(f"  ✓ Copied to: {addon_name}")
        except FileExistsError:
            self.safe_log(f"  ⚠ Folder already exists, skipping copy")
        except Exception as e:
            self.safe_log(f"  ✗ Error copying: {e}")
            return
        
        # Create a shortcut to the Steam Workshop page
        shortcut_path = os.path.join(dest_path, "View on Steam Workshop.url")
        if not os.path.exists(shortcut_path):
            self.create_workshop_shortcut(dest_path, addon_id, addon_name)
        
        # Find and decompile .gma files
        self.decompile_gma_files(dest_path, addon_id)
    
    def create_workshop_shortcut(self, addon_path, addon_id, addon_name):
        """Create a .url shortcut file to the Steam Workshop page"""
        try:
            shortcut_path = os.path.join(addon_path, "View on Steam Workshop.url")
            workshop_url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={addon_id}"
            
            # Create a .url file (Windows Internet Shortcut)
            with open(shortcut_path, 'w') as f:
                f.write("[InternetShortcut]\n")
                f.write(f"URL={workshop_url}\n")
                f.write(f"IconIndex=0\n")
            
            self.safe_log(f"  ✓ Created workshop shortcut")
            
        except Exception as e:
            self.safe_log(f"  ⚠ Could not create shortcut: {e}")
    
    def decompile_gma_files(self, addon_path, addon_id):
        """Find and decompile all .gma files in the addon folder"""
        if not self.gmad_path:
            self.safe_log("  ⚠ gmad.exe not found, skipping decompilation")
            return
        
        gma_found = False
        
        # First, check in the addon folder itself
        for root, dirs, files in os.walk(addon_path):
            for file in files:
                if file.endswith('.gma'):
                    gma_found = True
                    gma_path = os.path.join(root, file)
                    output_dir = addon_path  # Decompile to the root of the addon folder
                    
                    self.safe_log(f"  → Attempting to decompile: {file}")
                    
                    if self.decompile_single_gma(gma_path, output_dir):
                        self.safe_log(f"  ✓ Decompiled: {file}")
                    else:
                        self.safe_log(f"  ✗ Failed to decompile {file}")
        
        # If no .gma found in the addon folder, check the cache
        if not gma_found and self.cache_path:
            self.safe_log(f"  ℹ No .gma files in addon folder, checking cache...")
            
            # Look for .gma file with the addon ID in the cache folder
            cache_gma_path = os.path.join(self.cache_path, f"{addon_id}.gma")
            
            if os.path.exists(cache_gma_path):
                self.safe_log(f"  → Found cached .gma: {addon_id}.gma")
                
                if self.decompile_single_gma(cache_gma_path, addon_path):
                    self.safe_log(f"  ✓ Decompiled from cache: {addon_id}.gma")
                else:
                    self.safe_log(f"  ✗ Failed to decompile cached file")
            else:
                self.safe_log(f"  ⚠ No .gma file found in cache either")
        
        elif not gma_found:
            self.safe_log(f"  ℹ No .gma files found (cache folder not available)")
    
    def decompile_single_gma(self, gma_path, output_dir):
        """Decompile a single .gma file to the specified output directory"""
        try:
            # Run gmad.exe to extract the .gma file
            cmd = [self.gmad_path, "extract", "-file", gma_path, "-out", output_dir]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True
            else:
                if result.stderr:
                    self.safe_log(f"     Error: {result.stderr.strip()}")
                if result.stdout:
                    self.safe_log(f"     Output: {result.stdout.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            self.safe_log(f"     Timeout while decompiling")
            return False
        except Exception as e:
            self.safe_log(f"     Exception: {e}")
            return False
    
    def get_folder_size(self, folder_path):
        """Calculate the total size of a folder in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            self.log(f"⚠ Error calculating folder size: {e}")
        return total_size
    
    def format_size(self, bytes_size):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
    
    def validate_workshop_path(self, path):
        """Validate a workshop path provided by the user"""
        if not path or not os.path.exists(path):
            return False, "Path does not exist"

        if not os.path.isdir(path):
            return False, "Path is not a directory"

        # Check if it contains numeric folders (addon IDs)
        try:
            items = os.listdir(path)
            has_addon = any(item.isdigit() and os.path.isdir(os.path.join(path, item)) for item in items)
            if not has_addon:
                return False, "Path does not contain any addon folders (numeric directories)"
        except Exception as e:
            return False, f"Cannot read directory: {e}"

        return True, "Valid workshop path"

    def validate_gmad_path(self, path):
        """Validate a gmad executable path provided by the user"""
        if not path:
            return True, "gmad is optional (will skip decompilation)"

        if not os.path.exists(path):
            return False, "Path does not exist"

        if not os.path.isfile(path):
            return False, "Path is not a file"

        # Check if it's executable (on Linux) or has correct extension (on Windows)
        if not (os.access(path, os.X_OK) or path.endswith('.exe')):
            return False, "File is not executable"

        return True, "Valid gmad executable"

    def validate_cache_path(self, path):
        """Validate a cache path provided by the user"""
        if not path:
            return True, "Cache is optional"

        if not os.path.exists(path):
            return False, "Path does not exist"

        if not os.path.isdir(path):
            return False, "Path is not a directory"

        return True, "Valid cache path"

    def set_manual_paths(self, workshop_path, gmad_path=None, cache_path=None):
        """Set paths manually after validation"""
        # Validate workshop path (required)
        valid, message = self.validate_workshop_path(workshop_path)
        if not valid:
            return False, f"Invalid workshop path: {message}"

        self.workshop_path = workshop_path
        self.log(f"✓ Workshop path set: {workshop_path}")

        # Validate and set gmad path (optional)
        if gmad_path:
            valid, message = self.validate_gmad_path(gmad_path)
            if not valid:
                return False, f"Invalid gmad path: {message}"
            self.gmad_path = gmad_path
            self.log(f"✓ gmad path set: {gmad_path}")
        else:
            self.log("⚠ No gmad path provided, decompilation will be skipped")

        # Validate and set cache path (optional)
        if cache_path:
            valid, message = self.validate_cache_path(cache_path)
            if not valid:
                return False, f"Invalid cache path: {message}"
            self.cache_path = Path(cache_path)
            self.log(f"✓ Cache path set: {cache_path}")
        else:
            self.log("⚠ No cache path provided")

        # Create translated folder
        self.create_translated_folder()

        return True, "All paths set successfully"

    def initialize(self):
        """Initialize the translator by finding all necessary paths"""
        if not self.find_steam_workshop():
            return False

        if not self.find_gmad_exe():
            self.log("⚠ Continuing without gmad (files won't be decompiled)")

        self.create_translated_folder()
        return True
    
    def get_folder_size(self, folder_path):
        """Calculate the total size of a folder in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            self.log(f"⚠ Error calculating folder size: {e}")
        return total_size
    
    def format_size(self, bytes_size):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"