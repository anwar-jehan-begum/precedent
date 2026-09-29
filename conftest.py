# conftest.py for PRECEDENT test suite
# Sets up sys.path so all imports resolve correctly regardless of CWD.
import sys
import os

# Add project root to path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
