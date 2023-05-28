import argparse

from src.downloader import download
from src.preprocessor import convert_pdf2txt
from src.config_hander import ConfigHandler


CONFIG = 'config.yaml'
config = ConfigHandler(CONFIG)

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest='action')
subparser_download = subparser.add_parser('download')
subparser_download.add_argument('data', default='data', choices=['biblio', 'data'])
args = parser.parse_args()

if args.action == 'download':
    if args.data == 'data':
        data_config = config.get(args.data)
        pdf_out = download(**data_config)
        txt_out = convert_pdf2txt(pdf_out)