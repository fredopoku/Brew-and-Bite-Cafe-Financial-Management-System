"""
Test suite for the Brew and Bite Café Management System.
This package contains all test modules for unit testing and integration testing.
"""

import os
import sys

# Add the src directory to Python path for imports
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.append(src_path)

__version__ = '1.0.0'