# run_app.py
import streamlit as st
import subprocess
import sys
import os


def main():
    print("🚀 Starting Smart Interview Prep AI...")
    print("📱 Opening web interface...")

    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])


if __name__ == "__main__":
    main()