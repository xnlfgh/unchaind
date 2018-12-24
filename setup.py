from setuptools import setup

setup(
    name="kaart_killbot",
    version="0.1",
    description="Wormhole space kill notification tool for EVE Online.",
    url="https://github.com/supakeen/kaart_killbot",
    author="supakeen",
    author_email="cmdr@supakeen.com",
    packages=["kaart_killbot"],
    install_requires=["tornado", "lxml"],
    tests_require=["nose", "aiounittest"],
    entry_points={
        "console_scripts": ["kaart-killbot=kaart_killbot.command:main"]
    },
    extras_require={"dev": ["pre-commit", "flake8", "black"]},
    test_suite="nose.collector",
)
