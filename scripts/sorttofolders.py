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

# ========== sorttofolders.py ==========
"""Organize files into category/date folders"""
import os
import shutil
import sys
from datetime import datetime

def get_script_directory():
    """Get the directory where the script is located"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as Python script
        return os.path.dirname(os.path.abspath(__file__))

def get_safe_default_directory():
    """Get a safe default directory that's not protected"""
    script_dir = get_script_directory()
    
    # Check if script directory is protected
    if not is_protected_directory(script_dir):
        return script_dir
    
    # If script directory is protected, try user's home directory
    home_dir = os.path.expanduser("~")
    if not is_protected_directory(home_dir):
        return home_dir
    
    # If home directory is also protected (unlikely), try current working directory
    current_dir = os.getcwd()
    if not is_protected_directory(current_dir):
        return current_dir
    
    # As a last resort, try creating a temporary directory
    temp_dir = os.path.join(os.path.expanduser("~"), "FileOrganizer")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def is_protected_directory(path):
    """Check if directory is protected system directory"""
    path_lower = os.path.abspath(path).lower().replace('\\', '/')
    
    # Check for root directories (C:\, D:\, etc.)
    if len(path_lower) <= 3 and ':' in path_lower:
        return True
    
    # Check for Windows system directories
    windows_system_paths = [
        '/windows/', '/system32/', '/system64/', '/program files/', 
        '/program files (x86)/', '/programdata/', '/boot/',
        '/system volume information/', '$windows.~bt', '$windows.~ws', 
        'windows.old', '/recovery/', '/perflogs/'
    ]
    
    # Check for Unix/Linux/Mac system directories
    unix_system_paths = [
        '/etc/', '/usr/', '/var/', '/lib/', '/bin/', '/sbin/', '/system/',
        '/library/', '/applications/'
    ]
    
    # Allow user directories but not the entire Users folder
    if '/users/' in path_lower:
        # Allow subdirectories of Users but not the root Users directory
        path_parts = path_lower.split('/')
        if 'users' in path_parts and path_parts.index('users') == len(path_parts) - 2:
            return True  # This is the Users root directory
    
    return (any(sys_path in path_lower for sys_path in windows_system_paths) or
            any(sys_path in path_lower for sys_path in unix_system_paths))

def get_file_categories():
    """Return file category mapping"""
    return {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.heic', '.raw'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'Video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.m4v', '.webm', '.mpeg', '.mpg'],
        'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.xml', '.json', '.yaml', '.yml'],
        'Executables': ['.exe', '.msi', '.deb', '.rpm', '.appimage', '.bat', '.sh', '.cmd'],
        'Data': ['.csv', '.json', '.xml', '.sql', '.db', '.sqlite', '.sqlite3'],
        'Fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
        'Other': []
    }

def progress_bar(progress, total, bar_length=40, prefix="Progress"):
    """Display a simple progress bar"""
    if total == 0:
        return
    
    percent = min(progress / total, 1.0)  # Ensure we don't exceed 100%
    arrow = '=' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    
    sys.stdout.write(f'\r{prefix}: [{arrow + spaces}] {int(percent * 100)}% ({progress}/{total})')
    sys.stdout.flush()

def show_main_menu():
    """Display the main menu options"""
    print("\n" + "="*50)
    print("📁 FILE ORGANIZER - MAIN MENU")
    print("="*50)
    print("1. 🗂  Organize by file type")
    print("2. 📅 Organize by date")
    print("3. 🔄 Organize by type and date")
    print("4. 📋 Show file categories")
    print("5. 📁 Change directory")
    print("6. 🚪 Exit")
    print("="*50)

def show_date_format_menu():
    """Display date format options"""
    print("\n" + "="*50)
    print("📅 DATE FORMAT OPTIONS")
    print("="*50)
    print("1. Year (e.g., 2023)")
    print("2. Year-Month (e.g., 2023-05)")
    print("3. Year-Month-Day (e.g., 2023-05-15)")
    print("4. Month (e.g., May)")
    print("5. Month-Year (e.g., May-2023)")
    print("="*50)

def organize_files(directory, mode=1, date_format=2, include_subfolders=True, show_progress=True):
    """Organize files in directory based on mode and date format"""
    if is_protected_directory(directory):
        print("🚫 ERROR: Protected system directory - operation cancelled")
        return False
    
    if not os.path.exists(directory):
        print(f"❌ ERROR: Directory not found: {directory}")
        return False
    
    if not os.path.isdir(directory):
        print(f"❌ ERROR: Not a directory: {directory}")
        return False

    categories = get_file_categories()
    file_list = []
    
    print(f"🔍 Scanning: {directory}")
    
    # Scan for files
    if include_subfolders:
        # Count files first for progress bar
        total_files = 0
        for root, dirs, files in os.walk(directory):
            total_files += len([f for f in files if not f.startswith('.') and os.path.isfile(os.path.join(root, f))])
        
        if total_files == 0:
            print("📭 No files found to organize")
            return False
            
        processed_files = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    file_list.append((file_path, file))
                    processed_files += 1
                    if show_progress and processed_files % 10 == 0:
                        progress_bar(processed_files, total_files, prefix="Scanning files")
    else:
        # Only process files in the current directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and not f.startswith('.')]
        total_files = len(files)
        
        if total_files == 0:
            print("📭 No files found to organize")
            return False
            
        for i, file in enumerate(files):
            file_path = os.path.join(directory, file)
            file_list.append((file_path, file))
            if show_progress and i % 10 == 0:
                progress_bar(i + 1, total_files, prefix="Scanning files")
    
    if show_progress:
        progress_bar(total_files, total_files, prefix="Scanning files")
        print()  # New line after progress bar

    print(f"📊 Found {len(file_list)} files to organize")
    moved = 0
    errors = 0
    skipped = 0
    
    for i, (file_path, filename) in enumerate(file_list):
        try:
            ext = os.path.splitext(filename)[1].lower()
            category = next((k for k, v in categories.items() if ext in v), 'Other')
            
            mod_time = os.path.getmtime(file_path)
            mod_date = datetime.fromtimestamp(mod_time)
            
            # Determine date folder based on format
            date_folder = ""
            if mode in [2, 3]:  # Date is involved
                if date_format == 1:  # Year only
                    date_folder = f"{mod_date.year}"
                elif date_format == 2:  # Year-Month
                    date_folder = f"{mod_date.year}-{mod_date.month:02d}"
                elif date_format == 3:  # Year-Month-Day
                    date_folder = f"{mod_date.year}-{mod_date.month:02d}-{mod_date.day:02d}"
                elif date_format == 4:  # Month only
                    date_folder = f"{mod_date.strftime('%B')}"  # Full month name
                elif date_format == 5:  # Month-Year
                    date_folder = f"{mod_date.strftime('%B')}-{mod_date.year}"  # Month-Year
            
            # Determine target directory based on mode
            if mode == 1:  # Type only
                target_dir = os.path.join(directory, category)
            elif mode == 2:  # Date only
                target_dir = os.path.join(directory, date_folder)
            elif mode == 3:  # Type + Date
                target_dir = os.path.join(directory, category, date_folder)
            else:
                print("❌ ERROR: Invalid mode")
                return False
                
            # Create target directory and move file
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, filename)
            
            # Skip if file already exists in target
            if os.path.exists(target_path):
                skipped += 1
                continue
                
            shutil.move(file_path, target_path)
            moved += 1
            
            if show_progress and (i + 1) % 10 == 0:
                progress_bar(i + 1, len(file_list), prefix="Organizing files")
            
        except Exception as e:
            print(f"❌ Error moving {filename}: {str(e)}")
            errors += 1
    
    if show_progress:
        progress_bar(len(file_list), len(file_list), prefix="Organizing files")
        print()  # New line after progress bar
    
    print(f"\n✅ Successfully organized {moved} files")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} files (already exist in target)")
    if errors > 0:
        print(f"❌ {errors} files had errors")
    return True

def show_categories():
    """Display file categories and their extensions"""
    categories = get_file_categories()
    print("\n📋 FILE CATEGORIES:")
    print("="*50)
    for category, extensions in categories.items():
        print(f"{category}: {', '.join(extensions) or 'All other file types'}")
    input("\nPress Enter to continue...")

def main():
    """Main function with interactive menu"""
    # Check if we were launched with arguments
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        mode = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        date_format = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        include_subfolders = '--subfolders' in sys.argv or '-s' in sys.argv
        
        if mode not in [1, 2, 3]:
            print("❌ ERROR: Mode must be 1, 2, or 3")
            return
            
        if date_format not in [1, 2, 3, 4, 5]:
            print("❌ ERROR: Date format must be between 1 and 5")
            return
        
        # Run in non-interactive mode
        print(f"🗂️  Starting organization of: {directory}")
        print(f"🔧 Mode: {['Type', 'Date', 'Type+Date'][mode-1]}")
        print(f"📅 Date format: {['Year', 'Year-Month', 'Year-Month-Day', 'Month', 'Month-Year'][date_format-1]}")
        print(f"📁 Include subfolders: {'Yes' if include_subfolders else 'No'}")
        print("─" * 50)
        
        success = organize_files(directory, mode, date_format, include_subfolders, show_progress=True)
        
        if success:
            print("🎉 Organization complete!")
        else:
            print("❌ Organization failed")
        return

    # Interactive mode
    print("🗂️  FILE ORGANIZER - INTERACTIVE MODE")
    
    # Ask for directory first
    default_dir = get_safe_default_directory()
    directory_input = input(f"📁 Enter directory to organize (press Enter for '{default_dir}'): ").strip()
    
    if directory_input:
        if os.path.isdir(directory_input):
            directory = os.path.abspath(directory_input)
        else:
            print(f"❌ Directory not found: {directory_input}")
            print(f"📁 Using default directory: {default_dir}")
            directory = default_dir
    else:
        directory = default_dir
    
    include_subfolders = False
    mode = 1
    date_format = 2
    
    while True:
        # Check if directory is protected
        if is_protected_directory(directory):
            print(f"🚫 ERROR: Protected system directory: {directory}")
            # Get a new directory from user
            new_dir = input("📁 Enter a safe directory to organize: ").strip()
            if new_dir and os.path.isdir(new_dir):
                directory = os.path.abspath(new_dir)
                continue
            else:
                print("❌ Invalid directory. Using default safe directory.")
                directory = get_safe_default_directory()
                continue
        
        show_main_menu()
        choice = input("\n🎯 Select option (1-6): ").strip()
        
        if choice == '1':
            # Organize by type only
            include_subfolders = input("\n🔍 Include subfolders? (y/N): ").strip().lower() == 'y'
            print(f"\n🗂️  Organizing by type in: {directory}")
            success = organize_files(directory, mode=1, date_format=date_format, 
                                   include_subfolders=include_subfolders, show_progress=True)
            if success:
                print("🎉 Organization complete!")
        
        elif choice == '2':
            # Organize by date only
            show_date_format_menu()
            date_choice = input("🎯 Select date format (1-5): ").strip()
            if date_choice in ['1', '2', '3', '4', '5']:
                date_format = int(date_choice)
                include_subfolders = input("\n🔍 Include subfolders? (y/N): ").strip().lower() == 'y'
                print(f"\n📅 Organizing by date in: {directory}")
                success = organize_files(directory, mode=2, date_format=date_format, 
                                       include_subfolders=include_subfolders, show_progress=True)
                if success:
                    print("🎉 Organization complete!")
            else:
                print("❌ Invalid date format selection")
        
        elif choice == '3':
            # Organize by type and date
            show_date_format_menu()
            date_choice = input("🎯 Select date format (1-5): ").strip()
            if date_choice in ['1', '2', '3', '4', '5']:
                date_format = int(date_choice)
                include_subfolders = input("\n🔍 Include subfolders? (y/N): ").strip().lower() == 'y'
                print(f"\n🔄 Organizing by type and date in: {directory}")
                success = organize_files(directory, mode=3, date_format=date_format, 
                                       include_subfolders=include_subfolders, show_progress=True)
                if success:
                    print("🎉 Organization complete!")
            else:
                print("❌ Invalid date format selection")
        
        elif choice == '4':
            # Show categories
            show_categories()
        
        elif choice == '5':
            # Change directory
            new_dir = input("\n📁 Enter new directory (or press Enter to keep current): ").strip()
            if new_dir:
                if os.path.isdir(new_dir):
                    directory = os.path.abspath(new_dir)
                    print(f"📁 Changed to: {directory}")
                else:
                    print(f"❌ Directory not found: {new_dir}")
            else:
                print("📁 Keeping current directory")
        
        elif choice == '6':
            # Exit
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
