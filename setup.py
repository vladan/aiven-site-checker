"""
Setup file for the website checker.
"""
from setuptools import setup  # type: ignore


setup(
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    python_requires='>=3.6, <4',
    install_requires=[
        'aiokafka==0.6.0',
        'asyncpg==0.21.0',
        'pydantic==1.6.1',
        'PyYAML==5.3.1',
        'requests==2.24.0',
    ],
    include_package_data=True,
)
