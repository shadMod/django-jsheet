import os
import glob
import setuptools

__version__ = "0.3.7"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_install_requires() -> list:
    """Returns requirements.txt parsed to a list"""
    fname = os.path.join(os.path.dirname(__file__), "requirements.txt")
    targets = []
    if os.path.exists(fname):
        with open(fname, "r") as f:
            targets = f.read().splitlines()
    return targets


setuptools.setup(
    name="django_jsheet",
    version=__version__,
    author="shadMod",
    author_email="support@shadmod.it",
    description="Little tools to render a simple spreadsheet in webpage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shadMod/django-jsheet",
    download_url=f"https://github.com/shadMod/django-jsheet/archive/refs/tags/{__version__}.tar.gz",
    project_urls={
        "Documentation": "https://docs.shadmod.it/django_jsheet/index",
        "GitHub": "https://github.com/shadMod/django-jsheet/",
        "Bug Tracker": "https://github.com/shadMod/django-jsheet/issues/",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=[
        "django_jsheet",
        "django_jsheet.src.core",
        "django_jsheet.src.templatetags",
    ],
    install_requires=get_install_requires(),
    data_files=[
        (
            "libs/assets",
            [fn for fn in glob.iglob("django_jsheet/src/core/assets/**/*", recursive=True) if "." in fn],
        ),
        (
            "libs/libs",
            [fn for fn in glob.iglob("django_jsheet/libs/django_jsheet_assets/assets/**/*", recursive=True) if
             "." in fn],
        ),
    ],
    python_requires=">=3.8",
)
