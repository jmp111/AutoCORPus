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

            
def extract_text(soup,config):
    """
    convert beautiful soup object into a python dict object with cleaned main text body
    
    Args: 
        soup: BeautifulSoup object of html
    
    Return: 
        result: dict of the maintext 
    """
    result = {}
    # Extract title
    try:
        h1 = soup.find(config['title']['name'],config['title']['attrs']).get_text().strip('\n')
    except:
        h1 = ''
    result['title'] = h1

    # Extract abbreviations table
    try:
        abbreviations_table = soup.find(config['abbreviations_table']['name'],config['abbreviations_table']['attrs'])
        abbreviations = {}
        for tr in abbreviations_table.find_all('tr'):
            short_form, long_form = [td.get_text() for td in tr.find_all('td')]
            abbreviations[short_form] = long_form
    except:
        abbreviations = ''
    result['abbreviations'] = abbreviations

    maintext = []
    sections = soup.find_all(config['body']['name'],config['body']['attrs'])
    for p in sections:
        paragraph = {}
        h2 = p.find_previous(config['heading']['name'],config['heading']['attrs'])
        if h2:
            h2=h2.get_text().strip('\n')
        else:
            h2=''
        h3 = p.find_previous_sibling(config['heading2']['name'],config['heading2']['attrs'])
        if h3:
            h3=h3.get_text().strip('\n')
        else:
            h3=''
        paragraph['section_heading'] = h2
        paragraph['subsection_heading'] = h2
        paragraph['body'] = p.get_text()
        maintext.append(paragraph)

    result['paragraphs'] = maintext
    return result

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath", type=str, help="filepath of of html file to be processed")
    parser.add_argument("-t", "--target_dir", type=str, help="target directory for output")
    parser.add_argument("-c", "--config", type=str, help="filepath for configuration JSON file")
    
    args = parser.parse_args()
    filepath = args.filepath
    target_dir = args.target_dir
    config_path = args.config

    if not os.path.isdir(target_dir):
        try: 
            os.makedirs(target_dir)
        except:
            raise FileNotFoundError('Target filepath does not exist')

    with open(config_path,'rb') as f:
        config = json.load(f)

    with open(filepath,'r',encoding='UTF-8') as f:
        text = f.read()
    soup = BeautifulSoup(text, 'html.parser')

    for e in soup.find_all(attrs={'style':['display:none','visibility:hidden']}):
        e.extract()
    # what to do with in sentence reference
    for ref in soup.find_all(attrs={'class':['supplementary-material','figpopup','popnode','bibr']}):
        ref.extract()
    process_supsub(soup)
    process_em(soup)
    
    result = extract_text(soup,config)

    basename = os.path.basename(filepath).replace(".html",'')
    with open(os.path.join(target_dir,"{}_maintext.json".format(basename)), "w",encoding='UTF-8') as outfile: 
        json.dump(result, outfile, indent=2, ensure_ascii=False)
