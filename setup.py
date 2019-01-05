from setuptools import setup, find_packages

setup(
    name="unchaind",
    version="0.1.3",
    description="Wormhole space kill notification tool for EVE Online.",
    url="https://github.com/supakeen/unchaind",
    author="supakeen",
    author_email="cmdr@supakeen.com",
    packages=find_packages(),
    setup_requires=["pytest-runner", "pytest-cov"],
    install_requires=["tornado", "lxml", "click", "pytoml"],
    tests_require=["pytest", "pytest-cov"],
    entry_points={"console_scripts": ["unchaind=unchaind.command:main"]},
    extras_require={
        "dev": ["pre-commit", "flake8", "black", "pytest", "pytest-cov"]
    },
    package_data={"unchaind": ["unchaind/data"]},
    include_package_data=True,
)
