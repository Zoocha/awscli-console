from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='awscli-console',
    install_requires=requirements,
    packages=find_packages(),
    entry_points={'console_scripts': [
        'aws-console=awscli_console.cli:main',
        'aws-console-qutebrowser=awscli_console.qute:main'
    ]},
)
