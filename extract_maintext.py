#!/usr/bin/env python
# coding: utf-8

import os
from utils import *
import re
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from bs4 import element
from itertools import product
import argparse
import json


def clean_text(result):
    '''
    clean the main text body output of extract_text() further as follows:
        remove duplicated texts from each section (assuming the text from html file has hierarchy up to h3, i.e. no subsubsections);
        remove items with empty bodies

    Args: 
        result: dict of the maintext 


    Return: 
        result: cleaned dict of the maintext 
    '''
    # Remove duplicated contents from the 'result' output of extract_text()

    # Identify unique section headings and the index of their first appearance
    section_unique = []
    idx_section = []
    section_headings = [i['section_heading'] for i in result['paragraphs']]
    i = 0
    for heading in section_headings:
        if heading not in section_unique:
            section_unique.append(heading)
            idx_section.append(i)
        i += 1

    for i in range(len(section_unique)):
        try:
            if idx_section[i+1]-idx_section[i] <= 1:  # if only one subsection
                continue
            idx_section_last = idx_section[i+1]
        except IndexError:
            idx_section_last = len(result['paragraphs'])

        p = result['paragraphs'][idx_section[i]+1]['body']
        for idx_subsection in range(idx_section[i]+1, idx_section_last):
            if result['paragraphs'][idx_subsection]['body'] in result['paragraphs'][idx_section[i]]['body']:
                result['paragraphs'][idx_section[i]]['body'] = result['paragraphs'][idx_section[i]]['body'].replace(
                    result['paragraphs'][idx_subsection]['body'], '')

            if (idx_section[i]+1 != idx_subsection) and (p in result['paragraphs'][idx_subsection]['body']):
                result['paragraphs'][idx_subsection]['body'] = result['paragraphs'][idx_subsection]['body'].replace(
                    p, '')
        for idx_subsection in range(idx_section[i]+1, idx_section_last):
            if result['paragraphs'][idx_subsection]['subsection_heading'] == result['paragraphs'][idx_section[i]]['subsection_heading']:
                result['paragraphs'][idx_section[i]]['subsection_heading'] = ''

    result['paragraphs'] = [
        p for p in result['paragraphs'] if p['body'].replace('Go to:', '').strip() != '']
    return result


def extract_text(soup, config):
    """
    convert beautiful soup object into a python dict object with cleaned main text body

    Args: 
        soup: BeautifulSoup object of html

    Return: 
        result: dict of the maintext 
    """
    result = {}

    # Tags of text body to be extracted are hard-coded as p (main text) and span (keywords and refs)
    body_select_tag = 'p,span'

    # Extract title
    try:
        h1 = soup.find(config['title']['name'],
                       config['title']['attrs']).get_text().strip('\n')
    except:
        h1 = ''
    result['title'] = h1

    # Extract abbreviations table
    try:
        abbreviations_table = soup.find(
            config['abbreviations_table']['name'], config['abbreviations_table']['attrs'])
        abbreviations = {}
        for tr in abbreviations_table.find_all('tr'):
            short_form, long_form = [td.get_text() for td in tr.find_all('td')]
            abbreviations[short_form] = long_form
    except:
        abbreviations = ''
    result['abbreviations'] = abbreviations

    maintext = []
    sections = soup.find_all(config['body']['name'], config['body']['attrs'])
    for p in sections:
        paragraph = {}
        h2_select_tag = config['heading']['name']
        h2_select_tag += ''.join(['[{}*={}]'.format(k, config['heading']['attrs'][k])
                                 for k in config['heading']['attrs'] if config['heading']['attrs'][k]])

        h3_select_tag = config['heading2']['name']
        h3_select_tag += ''.join(['[{}*={}]'.format(k, config['heading2']['attrs'][k])
                                 for k in config['heading2']['attrs'] if config['heading2']['attrs'][k]])

        _h2 = p.select(h2_select_tag)
        if _h2:
            h2 = _h2[0].get_text().strip('\n')

        h3 = p.select(h3_select_tag)

        if h3:
            h3 = h3[0].get_text().strip('\n')
        else:
            h3 = ''
        try:
            paragraph['section_heading'] = h2
        except UnboundLocalError:
            paragraph['section_heading'] = ''
        paragraph['subsection_heading'] = h3
        paragraph['body'] = ' '.join([i.get_text()
                                      for i in p.select(body_select_tag)])
        maintext.append(paragraph)

    result['paragraphs'] = maintext
    return clean_text(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath", type=str,
                        help="filepath of of html file to be processed")
    parser.add_argument("-t", "--target_dir", type=str,
                        help="target directory for output")
    parser.add_argument("-c", "--config", type=str,
                        help="filepath for configuration JSON file")

    args = parser.parse_args()
    filepath = args.filepath
    target_dir = args.target_dir
    config_path = args.config

    if not os.path.isdir(target_dir):
        try:
            os.makedirs(target_dir)
        except:
            raise FileNotFoundError('Target filepath does not exist')

    with open(config_path, 'rb') as f:
        config = json.load(f)

    with open(filepath, 'r', encoding='UTF-8') as f:
        text = f.read()
    soup = BeautifulSoup(text, 'html.parser')

    for e in soup.find_all(attrs={'style': ['display:none', 'visibility:hidden']}):
        e.extract()
    # what to do with in sentence reference
    for ref in soup.find_all(attrs={'class': ['supplementary-material', 'figpopup', 'popnode', 'bibr']}):
        ref.extract()
    process_supsub(soup)
    process_em(soup)

    result = extract_text(soup, config)

    # result = clean_text(result)

    basename = os.path.basename(filepath).replace(".html", '')
    with open(os.path.join(target_dir, "{}_maintext.json".format(basename)), "w", encoding='UTF-8') as outfile:
        json.dump(result, outfile, indent=2, ensure_ascii=False)
