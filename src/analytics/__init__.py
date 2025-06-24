# src/analytics/__init__.py
"""
Big Data Analytics module for Face Recognition System
Provides Spark-based distributed analytics capabilities
"""

try:
    from .spark_analytics import SparkAnalyticsEngine
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False
    SparkAnalyticsEngine = None

__all__ = ['SparkAnalyticsEngine', 'SPARK_AVAILABLE']