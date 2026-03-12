try:
    import google.generativeai
    print("Success: google.generativeai imported")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Other Error: {e}")

import sys
print(f"Python: {sys.executable}")
print(f"Path: {sys.path}")
