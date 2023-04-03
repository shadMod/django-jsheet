from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fn:
    README = fn.read()

setup(
    name="django-jsheet",
    version="0.1.6",
    packages=find_packages("django-jsheet"),
    package_dir={'': 'django-jsheet'},
    description="Django JSheet",
    long_description=README,
    long_description_content_type="text/markdown",
    author="ShadMod",
    author_email="support@shadmod.it",
    license="MIT License",
    python_requires=">=3.6",
    url="https://github.com/shadMod/django-jsheet",
    download_url="https://github.com/shadMod/django-jsheet/archive/refs/tags/0.1.6.tar.gz",
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
