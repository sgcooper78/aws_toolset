from setuptools import setup, find_packages

with open('README.md') as fh:
    long_description = fh.read()

setup(
    name="aws_toolkit",
    version="0.0.2",
    url='https://github.com/sgcooper78/aws_toolkit',
    author="Scott Cooper",
    author_email="sgcooper78@gmail.com",
    description="AWS Toolkit for AWS Devs",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['boto3', 'inquirer'],
    keywords=['python', 'aws', 'boto3'],
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Operating System :: OS Independent",
    ],
    entry_points={'console_scripts': ['aws_toolkit = aws_toolkit.aws_toolkit:main']},
    include_package_data=True
)