import pathlib

from setuptools import setup, find_packages

DIR_ = pathlib.Path(__file__).parent
README = (DIR_ / "README.md").read_text()

setup(
    name="django-jsheet",
    packages=find_packages("django-jsheet"),
    package_dir={'': 'django-jsheet'},
    version="0.1.5",
    license="MIT License",
    description="Django JSheet",
    long_description=README,
    long_description_content_type="text/markdown",
    author="ShadMod",
    author_email="support@shadmod.it",
    url="https://github.com/shadMod/django-jsheet",
    download_url="https://github.com/shadMod/django-jsheet/archive/refs/tags/0.1.5.tar.gz",
    keywords=[
        "Django JSheet",
        "Django-JSheet",
        "Django_JSheet",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
