try:
    import coverage
    coverage.process_startup()
except ImportError:
    import warnings
    warnings.warn("coverage not found")
