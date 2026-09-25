import uvicorn
import os
import sys

# Ensure current directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("=" * 70)
    print("  IndustrialShield OT Cyber-Physical Defense Console")
    print("  Safe Hackathon Simulation: Zero real biometrics, zero real PLC attacks.")
    print("=" * 70)
    print("  Starting FastAPI server on http://localhost:8000")
    print("  Open your browser at: http://localhost:8000")
    print("  Interactive API Docs: http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
