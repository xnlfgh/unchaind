from setuptools import setup, find_packages

setup(
    name="unchaind",
    version="0.1.1",
    description="Wormhole space kill notification tool for EVE Online.",
    url="https://github.com/supakeen/unchaind",
    author="supakeen",
    author_email="cmdr@supakeen.com",
    packages=find_packages(),
    install_requires=["tornado", "lxml"],
    tests_require=["nose", "aiounittest"],
    entry_points={
        "console_scripts": ["unchaind=unchaind.command:main"]
    },
    extras_require={"dev": ["pre-commit", "flake8", "black"]},
    test_suite="nose.collector",
)
