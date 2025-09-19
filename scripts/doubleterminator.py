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

# ========== doubleterminator.py ==========
"""Find and remove duplicate files"""
import os
import hashlib
import sys
import time
from collections import defaultdict
from datetime import datetime  # Added import for datetime formatting

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
    temp_dir = os.path.join(os.path.expanduser("~"), "DuplicateScan")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def is_protected_directory(path):
    """Check if directory is protected"""
    path_lower = os.path.abspath(path).lower().replace('\\', '/')
    
    # Check for root directories (C:\, D:\, etc.)
    if len(path_lower) <= 3 and ':' in path_lower:
        return True
    
    # Check for system directories
    protected_paths = [
        '/windows/', '/system32/', '/program files/',
        '/programdata/', '/boot/', '/etc/', '/usr/', '/var/', '/lib/'
    ]
    #Check for Copyright (c) 2025 joik2ww. See LICENSE.txt.
    return any(p in path_lower for p in protected_paths)

def calculate_file_hash(filepath, buffer_size=65536):
    """Calculate MD5 hash of a file"""
    md5 = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()
    except (IOError, OSError):
        return None

def progress_bar(progress, total, bar_length=40, prefix="Progress"):
    """Display a simple progress bar"""
    if total == 0:
        return
    
    percent = progress / total
    arrow = '=' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    
    sys.stdout.write(f'\r{prefix}: [{arrow + spaces}] {int(percent * 100)}% ({progress}/{total})')
    sys.stdout.flush()

def find_duplicates(directory, include_subfolders=False, show_progress=True):
    """Find duplicate files in the specified directory"""
    files_by_size = defaultdict(list)
    duplicates = defaultdict(list)
    
    # First, count total files for progress tracking
    total_files = 0
    if include_subfolders:
        for root, _, files in os.walk(directory):
            total_files += len(files)
    else:
        total_files = len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])
    
    if total_files == 0:
        return duplicates
    
    processed_files = 0
    
    # Walk through directory and group files by size
    if include_subfolders:
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    file_size = os.path.getsize(filepath)
                    files_by_size[file_size].append(filepath)
                    processed_files += 1
                    if show_progress and processed_files % 100 == 0:  # Update progress every 100 files
                        progress_bar(processed_files, total_files, prefix="Scanning files")
                except (OSError, IOError):
                    processed_files += 1
                    if show_progress and processed_files % 100 == 0:
                        progress_bar(processed_files, total_files, prefix="Scanning files")
                    continue
    else:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                try:
                    file_size = os.path.getsize(filepath)
                    files_by_size[file_size].append(filepath)
                    processed_files += 1
                    if show_progress and processed_files % 100 == 0:
                        progress_bar(processed_files, total_files, prefix="Scanning files")
                except (OSError, IOError):
                    processed_files += 1
                    if show_progress and processed_files % 100 == 0:
                        progress_bar(processed_files, total_files, prefix="Scanning files")
                    continue
    
    if show_progress:
        progress_bar(total_files, total_files, prefix="Scanning files")
        print()  # New line after progress bar
    
    # For files with same size, check hashes
    files_to_hash = sum(len(files) for files in files_by_size.values() if len(files) > 1)
    if files_to_hash == 0:
        if show_progress:
            print("No potential duplicates found.")
        return duplicates
    
    if show_progress:
        print(f"Hashing {files_to_hash} potential duplicates...")
    
    hashed_files = 0
    for file_size, files in files_by_size.items():
        if len(files) > 1:
            hashes = defaultdict(list)
            for filepath in files:
                file_hash = calculate_file_hash(filepath)
                if file_hash:
                    hashes[file_hash].append(filepath)
                hashed_files += 1
                if show_progress and hashed_files % 10 == 0:  # Update progress every 10 files
                    progress_bar(hashed_files, files_to_hash, prefix="Hashing files")
            
            for file_hash, file_list in hashes.items():
                if len(file_list) > 1:
                    duplicates[file_hash] = file_list
    
    if show_progress:
        progress_bar(files_to_hash, files_to_hash, prefix="Hashing files")
        print()  # New line after progress bar
    
    return duplicates

def delete_duplicates(duplicates, keep_oldest=True):
    """Delete duplicate files, keeping either oldest or newest"""
    deleted_count = 0
    reclaimed_space = 0
    
    for file_list in duplicates.values():
        # Sort by modification time
        file_list.sort(key=lambda x: os.path.getmtime(x))
        
        # Determine which file to keep
        if keep_oldest:
            files_to_delete = file_list[1:]  # Keep the oldest
        else:
            files_to_delete = file_list[:-1]  # Keep the newest
        
        # Delete the duplicates
        for filepath in files_to_delete:
            try:
                file_size = os.path.getsize(filepath)
                os.remove(filepath)
                deleted_count += 1
                reclaimed_space += file_size
            except (OSError, IOError):
                continue
    
    return deleted_count, reclaimed_space

def delete_interactive(duplicates, keep_oldest=True):
    """Interactive deletion of duplicates"""
    deleted_count = 0
    reclaimed_space = 0
    
    for file_hash, file_list in duplicates.items():
        # Sort by modification time
        file_list.sort(key=lambda x: os.path.getmtime(x))
        
        # Determine which file to keep
        if keep_oldest:
            file_to_keep = file_list[0]
            files_to_delete = file_list[1:]
        else:
            file_to_keep = file_list[-1]
            files_to_delete = file_list[:-1]
        
        print(f"\n🔍 Duplicate group ({len(file_list)} files, {os.path.getsize(file_list[0]) / 1024:.1f} KB each):")
        for i, filepath in enumerate(file_list, 1):
            mod_time = os.path.getmtime(filepath)
            # FIXED: Format the timestamp properly
            mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{i}. {filepath} (modified: {mod_date})")
        
        print(f"💾 Keeping: {file_to_keep}")
        
        confirm = input("❓ Delete duplicates in this group? (y/N): ").strip().lower()
        if confirm == 'y':
            for filepath in files_to_delete:
                try:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    deleted_count += 1
                    reclaimed_space += file_size
                    print(f"🗑️  Deleted: {filepath}")
                except (OSError, IOError):
                    print(f"❌ Failed to delete: {filepath}")
    
    return deleted_count, reclaimed_space

def show_duplicates_list(duplicates):
    """Display the list of duplicate files"""
    print("\n📋 LIST OF DUPLICATE FILES")
    print("="*60)
    
    group_number = 1
    for file_hash, file_list in duplicates.items():
        file_size = os.path.getsize(file_list[0])
        print(f"\nGroup #{group_number} ({len(file_list)} files, {file_size / 1024:.1f} KB each):")
        
        # Sort by modification time (oldest first)
        file_list.sort(key=lambda x: os.path.getmtime(x))
        
        for i, filepath in enumerate(file_list, 1):
            mod_time = os.path.getmtime(filepath)
            # FIXED: Format the timestamp properly
            mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {i}. {filepath} (modified: {mod_date})")
        
        group_number += 1
    
    input("\nPress Enter to return to the menu...")

def show_main_menu():
    """Display the main menu options"""
    print("\n" + "="*50)
    print("1. 🎯 Interactive deletion (confirm each group)")
    print("2. 💥 Bulk deletion (delete all duplicates)")
    print("3. 📁 Change directory")
    print("4. 📋 Show list of duplicate files")
    print("5. 🔄 Rescan for duplicates")
    print("6. 🚪 Exit")
    print("="*50)

def main():
    """Main function with interactive menu"""
    # Check if we were launched with arguments
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        include_subfolders = '--subfolders' in sys.argv
        
        # Run in non-interactive mode
        if not os.path.isdir(directory):
            print(f"❌ ERROR: Directory not found: {directory}")
            return
        
        if is_protected_directory(directory):
            print("🚫 ERROR: Protected system directory - operation cancelled")
            return

        duplicates = find_duplicates(directory, include_subfolders, show_progress=False)
        
        if not duplicates:
            print("\n🎉 No duplicates found!")
            return
        
        # Ask for confirmation before bulk deletion
        total_duplicates = sum(len(files) - 1 for files in duplicates.values())
        total_space = sum(os.path.getsize(files[0]) * (len(files) - 1) for files in duplicates.values())
        
        print(f"\n🚨 Found {len(duplicates)} duplicate groups")
        print(f"📦 Total duplicate files: {total_duplicates}")
        print(f"💾 Reclaimable space: {total_space / (1024*1024):.2f} MB")
        
        confirm = input(f"\n❓ Delete {total_duplicates} duplicates? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Operation cancelled")
            return
        
        # Ask which files to keep
        keep_option = input("💾 Keep oldest files? (Y/n): ").strip().lower()
        keep_oldest = keep_option not in ['n', 'no']
        
        # Delete duplicates
        print("\n🗑️  Deleting duplicates...")
        deleted_count, reclaimed_space = delete_duplicates(duplicates, keep_oldest)
        
        # Results
        print(f"\n✅ Deleted {deleted_count} duplicate files")
        print(f"💾 Reclaimed {reclaimed_space / (1024*1024):.2f} MB")
        print("🎉 Duplicate cleanup complete!")
        return

    # Interactive mode
    print("🔥 DUPLICATE TERMINATOR - INTERACTIVE MODE")
    
    # Ask for directory first
    default_dir = get_safe_default_directory()
    directory_input = input(f"📁 Enter directory to scan (press Enter for '{default_dir}'): ").strip()
    
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
    keep_oldest = True
    duplicates = None
    
    while True:
        # Check if directory is protected
        if is_protected_directory(directory):
            print(f"🚫 ERROR: Protected system directory: {directory}")
            # Get a new directory from user
            new_dir = input("📁 Enter a safe directory to scan: ").strip()
            if new_dir and os.path.isdir(new_dir):
                directory = os.path.abspath(new_dir)
                duplicates = None
                continue
            else:
                print("❌ Invalid directory. Using default safe directory.")
                directory = get_safe_default_directory()
                continue
        
        # Ask about subfolders if we haven't scanned yet
        if duplicates is None:
            include_subfolders = input("\n🔍 Include subfolders in search? (y/N): ").strip().lower() == 'y'
            
            # Scan for duplicates with progress bar
            print(f"\n📁 Scanning: {directory}")
            duplicates = find_duplicates(directory, include_subfolders, show_progress=True)
            
            if not duplicates:
                print("\n🎉 No duplicates found!")
                duplicates = None
        
        # If we have duplicates, show the menu
        if duplicates:
            # Show results and menu
            total_duplicates = sum(len(files) - 1 for files in duplicates.values())
            total_space = sum(os.path.getsize(files[0]) * (len(files) - 1) for files in duplicates.values())
            
            print(f"\n🚨 Found {len(duplicates)} duplicate groups")
            print(f"📦 Total duplicate files: {total_duplicates}")
            print(f"💾 Reclaimable space: {total_space / (1024*1024):.2f} MB")
            
            show_main_menu()
            choice = input("\n🎯 Select option (1-6): ").strip()
        else:
            # If no duplicates found, show a simplified menu
            print("\n1. 📁 Change directory")
            print("2. 🔄 Rescan for duplicates")
            print("3. 🚪 Exit")
            choice = input("\n🎯 Select option (1-3): ").strip()
            
            # Map simplified choices to full menu options
            if choice == '1':
                choice = '3'  # Change directory
            elif choice == '2':
                choice = '5'  # Rescan
            elif choice == '3':
                choice = '6'  # Exit
        
        if choice == '1':
            # Interactive deletion
            keep_option = input("💾 Keep oldest files? (Y/n): ").strip().lower()
            keep_oldest = keep_option not in ['n', 'no']
            
            print("\n🗑️  Starting interactive deletion...")
            deleted_count, reclaimed_space = delete_interactive(duplicates, keep_oldest)
            
            print(f"\n✅ Deleted {deleted_count} duplicate files")
            print(f"💾 Reclaimed {reclaimed_space / (1024*1024):.2f} MB")
            
            # Rescan after deletion
            duplicates = None
        
        elif choice == '2':
            # Bulk deletion
            confirm = input(f"\n⚠️  WARNING: This will delete {total_duplicates} files without confirmation! Continue? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Operation cancelled")
                continue
            
            keep_option = input("💾 Keep oldest files? (Y/n): ").strip().lower()
            keep_oldest = keep_option not in ['n', 'no']
            
            print("\n💥 Deleting all duplicates...")
            deleted_count, reclaimed_space = delete_duplicates(duplicates, keep_oldest)
            
            print(f"\n✅ Deleted {deleted_count} duplicate files")
            print(f"💾 Reclaimed {reclaimed_space / (1024*1024):.2f} MB")
            print("🎉 Bulk deletion complete!")
            
            # Rescan after deletion
            duplicates = None
        
        elif choice == '3':
            # Change directory
            new_dir = input("\n📁 Enter new directory (or press Enter to keep current): ").strip()
            if new_dir:
                if os.path.isdir(new_dir):
                    directory = os.path.abspath(new_dir)
                    print(f"📁 Changed to: {directory}")
                    duplicates = None
                else:
                    print(f"❌ Directory not found: {new_dir}")
            else:
                print("📁 Keeping current directory")
        
        elif choice == '4':
            # Show list of duplicate files
            show_duplicates_list(duplicates)
        
        elif choice == '5':
            # Rescan
            duplicates = None
            print("🔄 Rescanning directory...")
        
        elif choice == '6':
            # Exit
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
