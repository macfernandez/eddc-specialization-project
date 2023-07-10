import argparse

from src.config_hander import ConfigHandler
from src.downloaders.data import download as download_data
from src.preprocessor.pipeline import convert_pdf2txt, preprocess
from src.downloaders.attendees import download as download_attendees


CONFIG = 'config.json'
config = ConfigHandler(CONFIG)

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest='action', required=True)
subparser_download = subparser.add_parser('download')
subparser_download.add_argument('data', choices=['biblio', 'data', "attendees"])
args = parser.parse_args()

if args.action == 'download':
    if args.data == 'data':
        data_config = config.get(args.data)
        pdf_out = download_data(**data_config)
        txt_out = convert_pdf2txt(pdf_out)
        csv_out, xml_out = preprocess(txt_out)
    elif args.data == 'attendees':
        data_config = config.get(args.data)
        download_attendees(**data_config)
