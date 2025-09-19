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

# ========== test_script.py ==========
"""Simple test script to debug launching issues"""
import time
import sys
import os

def write_log(message):
    """Write message to log file"""
    log_file = "error_test_script.txt"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def main():
    """Main function with progress bar"""
    write_log("Script started successfully")
    print("Testing your crappy computer...")
    print("This should take about 5 seconds")
    print("-" * 40)
    
    # Simple progress bar
    for i in range(1, 101):
        time.sleep(0.05)  # 5 seconds total
        progress = i // 2
        bar = "[" + "=" * progress + " " * (50 - progress) + "]"
        print(f"\r{bar} {i}%", end='', flush=True)
    
    print("\n\n✅ Test completed successfully!")
    print("If you see this, the script launched correctly")
    write_log("Script completed successfully")
    
    # Keep window open if running standalone
    if not hasattr(sys, 'frozen'):
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_msg = f"CRASH: {str(e)}"
        print(f"❌ {error_msg}")
        write_log(error_msg)
        if not hasattr(sys, 'frozen'):
            input("\nPress Enter to exit...")
