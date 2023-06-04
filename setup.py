import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django_jsheet",
    version="0.2.4",
    author="shadMod",
    author_email="support@shadmod.it",
    description="A little tool to render a simple excel sheet in webpage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shadMod/django-jsheet",
    download_url="https://github.com/shadMod/django-jsheet/archive/refs/tags/0.2.4.tar.gz",
    project_urls={
        "Bug Tracker": "https://github.com/shadMod/django-jsheet/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=[
        "django_jsheet", "django_jsheet.src.core", "django_jsheet.src.templatetags",
    ],
    python_requires=">=3.7"
)
