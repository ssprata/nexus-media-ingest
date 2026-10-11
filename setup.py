from setuptools import setup, find_packages

setup(
    name="nexus-media-ingest",
    version="1.0.0",
    description="High-Speed Multi-Threaded Media Batch Ingest",
    author="Nexus Team",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.4.0",
        "requests>=2.31.0",
        "yt-dlp>=2026.8.19",
        "instaloader>=4.13",
    ],
    entry_points={
        "gui_scripts": [
            "nexus=main:main",
        ],
    },
)
