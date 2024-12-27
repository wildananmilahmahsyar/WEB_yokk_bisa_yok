import subprocess
import threading

def run_flask():
    subprocess.run(["python", "app.py"])

def run_php():
    subprocess.run(["php", "-S", "0.0.0.0:8000"])

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    php_thread = threading.Thread(target=run_php)

    flask_thread.start()
    php_thread.start()

    flask_thread.join()
    php_thread.join()