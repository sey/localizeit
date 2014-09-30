#!/usr/bin/python

from oauth2client.client    import OAuth2WebServerFlow
from oauth2client.file      import Storage
from oauth2client           import tools
from oauth2client           import clientsecrets

import httplib2
import gspread

import argparse
import localizable
import os
import io
import json
import re

REDIRECT_URI = 'http://localhost/'
SCOPE = 'https://spreadsheets.google.com/feeds'
APP_NAME = 'localizeit'
IOS_KEY_COL = 0
AND_KEY_COL = 1
IOS_COM_COL = 2
AND_COM_COL = 3
FR_COL = 4
EN_COL = 5
ES_COL = 6

def log(string):
    print(string)

def clean_value(value):
    return value.replace('\n', '\\n')

def parse_row(args, row):
    return {
        'comment': row[IOS_COM_COL],
        'keys': {
            'ios': row[IOS_KEY_COL],
            'android': row[AND_KEY_COL]
        },
        'values': {
            'fr': clean_value(row[FR_COL]),
            'en': clean_value(row[EN_COL]),
            'es': clean_value(row[ES_COL])
        }
    }

def build_languages_dict(args):
    return {
        'fr': '',
        'en': '',
        'es': ''
    }

def get_format_string(platform):
    if 'ios' == platform:
        return u'/* {comment} */\n"{key} = {value}";\n\n'
    if 'android' == platform:
        return u'\t<string name="{key}">{value}</string>\n'
    return ''

def build_entry_from_row(args, lang, row_dict):
    format_str = get_format_string(args.platform)
    value = row_dict['values'][lang]
    if args.platform == 'android':
        value = value.replace("'", r"\'")
        value = value.replace("&", "&amp;")

        if '%' in value:
            value = re.sub('%(?!\d)', '\%%', value)

    if value == '':
        value = '__MISSING__'

    key = row_dict['keys'][args.platform]
    if key == '':
        return None

    entry = format_str.format( 
        comment=row_dict['comment'], 
        key=key,
        value=value)
    return entry

def parse_worksheet(args, worksheet):
    rows = worksheet.get_all_values()
    result_dict = build_languages_dict(args)

    row_count = 1
    for row in rows:
        # Skip header row
        if row_count == 1:
            row_count += 1
            continue

        row_dict = parse_row(args, row)

        for lang_key in result_dict:
            entry = build_entry_from_row(args, lang_key, row_dict)
            if entry is None:
                continue
            result_dict[lang_key] += entry
        row_count += 1
        
    return result_dict

def create_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def build_filepath(args, lang):
    if 'ios' == args.platform:
        output_dir = args.output + '/' + lang + '.lproj'
        create_if_not_exists(output_dir)    
        return output_dir + '/Localizable.strings'
    if 'android' == args.platform:
        output_dir = ''
        if 'en' == lang:
            output_dir = args.output + '/values'
        else:
            output_dir = args.output + '/values-' + lang
        create_if_not_exists(output_dir)    
        return output_dir + '/strings.xml'
    raise Exception('Unsupported platform')

def generate(args):
    log('GENERATE')

    platform = args.platform
    output_base_dir = args.output
    spreadsheet_name = args.spreadsheet

    client = authorize(args)
    spreadsheet = client.open(spreadsheet_name)
    worksheet = spreadsheet.sheet1

    result = parse_worksheet(args, worksheet)

    for lang in ['fr', 'en', 'es']:
        filepath = build_filepath(args, lang)
        output_file = io.open(filepath, 'w', encoding='utf8')

        if 'ios' == platform:
            output_file.write(result[lang])
        elif 'android' == platform:
            output_file.write(u'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n')
            output_file.write(result[lang])
            output_file.write(u'</resources>')
        output_file.close()
    log('DONE')



def parse_config(args):
    f = io.open(args.config, 'r', encoding='utf8')
    config_str = f.read()
    config_json = json.loads(config_str)
    return config_json

def get_credentials(args):
    # First check existing credentials
    storage = Storage('.localizeit.storage')
    credentials = storage.get()
    if not credentials == None:
        return credentials

    config = parse_config(args)
    # Run the oauth authorization flow
    flow = OAuth2WebServerFlow(
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        scope=SCOPE,
        redirect_uri=REDIRECT_URI)
    flags = args
    http = httplib2.Http()
    return tools.run_flow(flow=flow, storage=storage, flags=flags, http=http)

def authorize(args):
    credentials = get_credentials(args)
    if credentials.access_token_expired:
        credentials.refresh(httplib2.Http())
    client = gspread.authorize(credentials)
    return client

def main():
    parser = argparse.ArgumentParser(parents=[tools.argparser])

    parser.add_argument('-v', '--verbose', 
        help='Display more information about the files generation',
        action='store_true')


    subparsers = parser.add_subparsers(help='Available actions')

    
    generate_parser = subparsers.add_parser('generate', 
        help='Generate files from Google Spreadsheet')
    generate_parser.set_defaults(func=generate)
    generate_parser.add_argument('platform',
        help='The platform determines the format of the output files and the location of the output files',
        choices=['ios', 'android'])
    generate_parser.add_argument('-s', '--spreadsheet',
        help='Google Spreadsheet to read/write from',
        required=True)
    generate_parser.add_argument('-c', '--config',
        help='Path to the JSON config file used to store the client ID and SECRET',
        default='localizeit.json')
    generate_parser.add_argument('-o', '--output',
        help='The destination path of the generated files',
        required=True,
        default='.')
    
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__': main()
