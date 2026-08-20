from datetime import datetime
import platform, time, os

name = os.environ.get("STUDENT_NAME", "selector0073")

print(f"""
============================================
  Hello! My name is {name}
  Date: {datetime.now().strftime("%Y-%M-%d %H:%M:%S")}
  Python: {platform.python_version()}
  Platform: {platform.platform()}
============================================
""")

while True:
    print(f"[{datetime.now().strftime("%H:%M:%S")}] {name} - program running...")
    time.sleep(5)