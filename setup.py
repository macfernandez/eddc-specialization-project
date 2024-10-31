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
        'bs4==0.0.1',
        'jinja2==3.1.2',
        'lxml==4.9.3',
        'pandas==2.0.3',
        'pdfminer==20191125',
        'pdfminer-six==20221105',
        'requests==2.32.3',
        'selenium==4.10.0',
        'webdriver-manager==4.0.1'
      ],
      extras_require={
        "dev":[
          'pytest==7.2.1',
          'pytest-cov==4.0.0'
        ],
        "nb":[
          'inflection==0.5.1',
          'joblib==1.4.2',
          'nltk==3.8.1',
          'scikit-learn==1.3.0',
          'seaborn==0.12.2',
          'spacy==3.7.4',
          'es-core-news-md @ https://github.com/explosion/spacy-models/releases/download/es_core_news_md-3.7.0/es_core_news_md-3.7.0-py3-none-any.whl',
        ]
      }
     )