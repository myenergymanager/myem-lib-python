from setuptools import find_packages, setup


setup(
    name="Myem-Lib-Python",
    version="1.0",
    url="",
    license="",
    author="",
    author_email="",
    description="",
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[],
    extras_require={
        "dev": [
            # this depdency should be present in the client, we only used it here for test.
            "nameko-sqlalchemy==1.5.0",
            "pytest==6.2.5",
            "pytest-mock==3.6.1",
            "pyjwt",
            "coverage==4.5.3",
            "flake8==3.7.7",
            "pytest-dotenv",
            "pre-commit==2.14.0",
            "pydocstyle==6.1.1",
            "pylint==2.9.6",
            "mypy==0.910",
            "typed-ast",
            "cryptography",
            "pycryptodome==3.11.0",
        ],
    },
    entry_points={"pytest11": ["myem_lib=myem_lib.pytest_fixtures"]},
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
