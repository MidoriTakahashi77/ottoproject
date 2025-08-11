"""
Setup script for storage_service package
"""

from setuptools import setup, find_packages

setup(
    name='storage-service',
    version='1.0.0',
    description='Unified storage service interface for OttoProject',
    packages=find_packages(),
    install_requires=[
        'supabase>=2.0.0',
    ],
    extras_require={
        's3': ['boto3>=1.0.0'],
    },
    python_requires='>=3.8',
)