#!/usr/bin/env python

from distutils.core import setup

setup(name='eddc',
      version='1.0',
      description='EDDC Project',
      author='Macarena Fernández Urquiza',
      author_email='m.fernanndezurquiza@gmail.com',
      url='https://github.com/macfernandez/eddc-specialization-project',
      packages=['src'],
      install_requires=[
        'jinja2==3.1.2',
        'pandas==2.0.3',
        'pdfminer==20191125',
        'pdfminer-six==20221105',
        'requests==2.28.2',
        'selenium==4.10.0'
      ],
      extras_require={
        "dev":[
            'pytest==7.2.1',
            'pytest-cov==4.0.0'
        ]
      }
     )