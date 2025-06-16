import subprocess
import sys
import os

def build_executable():
    print("Membangun executable Kontenware...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=Kontenware-mini",
        "--icon=app.ico",
        "kontenware_mini.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build berhasil!")
        print("File executable tersedia di folder 'dist/Kontenware-mini.exe'")

    except subprocess.CalledProcessError as e:
        print(f"Build gagal: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        
    except FileNotFoundError:
        print("PyInstaller tidak ditemukan. Install dengan: pip install pyinstaller")

if __name__ == "__main__":
    build_executable()