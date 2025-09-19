# Copyright 2025 joik2ww
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import subprocess
import tempfile
import platform
import logging
import traceback
import glob

# Force UTF-8 in frozen mode
if getattr(sys, 'frozen', False):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup logging with UTF-8
try:
    logging.basicConfig(
        filename='error_4.0k.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
except Exception as e:
    print(f"ERROR: LOGGING SETUP FAILED: {str(e)}")
    logging.basicConfig(level=logging.DEBUG)

# Terminal color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Windows color support
if platform.system() == 'Windows':
    try:
        import colorama
        colorama.init()
    except ImportError:
        class Colors:
            RED = ''
            GREEN = ''
            YELLOW = ''
            BLUE = ''
            MAGENTA = ''
            CYAN = ''
            WHITE = ''
            RESET = ''
            BOLD = ''

def print_error(message):
    print(f"{Colors.RED}{Colors.BOLD}ERROR:{Colors.RESET} {message}")

def print_success(message):
    print(f"{Colors.GREEN}{Colors.BOLD}SUCCESS:{Colors.RESET} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}{Colors.BOLD}WARNING:{Colors.RESET} {message}")

def print_info(message):
    print(f"{Colors.CYAN}{Colors.BOLD}INFO:{Colors.RESET} {message}")

def print_debug(message):
    print(f"{Colors.MAGENTA}{Colors.BOLD}DEBUG:{Colors.RESET} {message}")

def print_header(message):
    print(f"{Colors.BLUE}{Colors.BOLD}{message}{Colors.RESET}")

# Debug: Check frozen mode (your suggestion)
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print_debug('running in a PyInstaller bundle')
else:
    print_debug('running in a normal Python process')

def setup_global_error_handling():
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        print_error(f"CATASTROPHIC FAILURE: {exc_value}")
        print_error("Check error_4.0k.log for details")
        if is_frozen():
            input("Press Enter to exit...")
    sys.excepthook = handle_exception

setup_global_error_handling()

def is_frozen():
    return getattr(sys, 'frozen', False)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        if is_frozen():
            # For external files next to EXE
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        base_path = os.getcwd()
    return os.path.join(base_path, relative_path)

def get_app_dir():
    try:
        if is_frozen():
            # Use resource_path for consistency
            return resource_path(".")
        return os.path.dirname(os.path.abspath(__file__))
    except Exception as e:
        logging.error(f"Path error: {str(e)}\n{traceback.format_exc()}")
        return os.getcwd()

def scan_for_scripts():
    """Scan for all Python scripts in main directory and scripts subfolder"""
    app_dir = get_app_dir()
    script_locations = [app_dir, resource_path("scripts")]  # Use resource_path for subfolder
    
    print_debug(f"DEBUG: App dir: {app_dir}, CWD: {os.getcwd()}")  # Debug
    
    found_scripts = {}
    
    for location in script_locations:
        print_debug(f"DEBUG: Scanning {location}")  # Debug
        if os.path.exists(location):
            # Find Python files
            py_files = glob.glob(os.path.join(location, "*.py"))
            print_debug(f"DEBUG: Found {len(py_files)} .py files")  # Debug
            for py_file in py_files:
                script_name = os.path.basename(py_file)
                if script_name.lower() != "fileorganizer4.0k.py":  # Skip self
                    # Get friendly name from filename
                    friendly_name = script_name.replace('.py', '').replace('_', ' ').title()
                    found_scripts[script_name] = (friendly_name, py_file)
            
            # Find executable files
            if platform.system() == 'Windows':
                exe_files = glob.glob(os.path.join(location, "*.exe"))
            else:
                exe_files = glob.glob(os.path.join(location, "*"))  # All files on Unix
                
            print_debug(f"DEBUG: Found {len(exe_files)} potential exes")  # Debug
            for exe_file in exe_files:
                if os.access(exe_file, os.X_OK):  # Check if executable
                    script_name = os.path.basename(exe_file)
                    friendly_name = script_name.replace('.exe', '').replace('_', ' ').title()
                    found_scripts[script_name] = (friendly_name, exe_file)
        else:
            print_debug(f"DEBUG: Location does not exist: {location}")
    
    return found_scripts
    
	#Check for Copyright (c) 2025 joik2ww. See LICENSE.txt.
	
def launch_script(full_path, args=None, is_py=True):
    if args is None:
        args = []
    
    script_name = os.path.basename(full_path)
    logging.info(f"Launching: {full_path}")
    
    if not os.path.exists(full_path):
        print_error(f"File not found: {full_path}")
        return None

    try:
        if is_py and full_path.endswith('.py'):
            cmd = [sys.executable, full_path] + args
        else:
            cmd = [full_path] + args

        # Use subprocess.call with the command as a list
        # This automatically handles paths with spaces
        return_code = subprocess.call(cmd)
        
        if return_code != 0:
            print_error(f"{script_name} failed with code {return_code}")
            return return_code
        else:
            print_success(f"{script_name} completed successfully")
            return 0

    except Exception as e:
        logging.error(f"Launch failed: {str(e)}\n{traceback.format_exc()}")
        print_error(f"Failed to launch {script_name}: {str(e)}")
        return None

def main():
    print_header("🚀 File Organizer 4.0k - Master Launcher")
    print("Scanning for available scripts...")
    
    # Scan for scripts
    scripts = scan_for_scripts()
    
    if not scripts:
        print_error("No scripts found! Place .py or .exe files in the main folder or scripts/ subfolder")
        if is_frozen():
            input("Press Enter to exit...")
        return
    
    # Create numbered menu
    script_list = list(scripts.items())
    
    while True:
        print_header("\n🛠️ === AVAILABLE TOOLS ===")
        for i, (script_file, (friendly_name, path)) in enumerate(script_list, 1):
            file_type = "Python" if script_file.endswith('.py') else "Executable"
            print(f"🔢 {i:2d}. {friendly_name} ({file_type})")
        
        print(f"🔢 {len(script_list) + 1:2d}. 🔄 Rescan for scripts")
        print(f"🔢 {len(script_list) + 2:2d}. 🚪 Quit")
        print_header("═" * 25)
        
        try:
            choice = input("\n👉 Select tool: ").strip()
            
            if choice == str(len(script_list) + 2) or choice.lower() in ['q', 'quit', 'exit']:
                break
                
            if choice == str(len(script_list) + 1):
                print_info("Rescanning for scripts...")
                scripts = scan_for_scripts()
                script_list = list(scripts.items())
                if not scripts:
                    print_error("No scripts found after rescan!")
                continue
            
            choice_num = int(choice) - 1
            if 0 <= choice_num < len(script_list):
                script_file, (friendly_name, script_path) = script_list[choice_num]
                is_py = script_file.endswith('.py')
                
                print_info(f"Launching: {friendly_name}")
                result = launch_script(script_path, is_py=is_py)
                
                if result is not None:
                    if result == 0:
                        print_success(f"{friendly_name} completed successfully!")
                    else:
                        print_error(f"{friendly_name} failed with error code {result}")
            else:
                print_error("Invalid selection!")
                
        except ValueError:
            print_error("Please enter a valid number!")
        except KeyboardInterrupt:
            print_info("\nOperation cancelled by user")
            break

# This should be at the very end of the file
if __name__ == "__main__":
    main()
