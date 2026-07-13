import subprocess
import time
import sys

def main():
    while True:
        print("\n" + "="*56)
        print("[AUTO-UPDATE] Checking for latest code from GitHub...")
        print("="*56)
        try:
            # Explicitly pull origin main to avoid tracking branch issues
            subprocess.run(["git", "pull", "origin", "main"], check=True)
        except Exception as e:
            print(f"[AUTO-UPDATE] Git pull failed: {e}")
            
        print("\n" + "="*56)
        print("[SERVER] Starting Infreight Sourcing Backend...")
        print("="*56)
        
        try:
            # Run the server and wait for it to finish
            # Using sys.executable ensures we use the active virtual env python
            subprocess.run([sys.executable, "run_server.py"])
        except KeyboardInterrupt:
            # Catch KeyboardInterrupt if it bubbles up, so we don't exit the loop
            pass
            
        print("\n" + "="*56)
        print("[SERVER] Server stopped. Restarting in 5 seconds...")
        print("Press Ctrl+C again during this countdown to exit.")
        print("="*56)
        
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n[AUTO-UPDATE] Exiting update loop.")
            break

if __name__ == '__main__':
    main()
