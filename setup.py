from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='pulpo-beanstalk-cli',
      version='0.0.1',
      author='Mighty Pulpo',
      author_email='jayray.net@gmail.com',
      description='CLI for beanstalkd',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(),
      install_requires=['greenstalk==2.0.2','loguru==0.7.0'],
      classifiers=[
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
      ],
      python_requires='>=3.6',
      keywords='beanstalkd,cli,pulpo-messaging')
