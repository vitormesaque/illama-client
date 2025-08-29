from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='illama_client',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'requests>=2.20',
        'urllib3>=1.26',
    ],
    entry_points={
        'console_scripts': [
            'extract_issues=illama_client.issue_extractor:main',
        ],
    },
    author='Vitor Mesaque Alves de Lima',
    author_email='vitor.lima@ufms.br',
    description='A package to extract issues from user reviews using an API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vitormesaque/illama-client',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
