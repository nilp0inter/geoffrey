"""
This module is used for correctly measure coverage with parallel process.
"""
try:
    import coverage
    coverage.process_startup()
except ImportError:
    import warnings
    warnings.warn("coverage not found")
