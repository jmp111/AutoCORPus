import regex as re
from bs4 import BeautifulSoup
import json
import nltk
# import fuzz
from fuzzywuzzy import fuzz

def get_files(base_dir,pattern=r'(.*).html'):
    """
    recursively retrieve all PMC.html files from the directory
    
    Args: 
        base_dir: base directory
    
    Return: 
        file_list: a list of filepath
    """
    file_list = []
    files = os.listdir(base_dir)
    for i in files:
        abs_path = os.path.join(base_dir,i)
        if re.match(pattern,abs_path):
            file_list.append(abs_path)
        elif os.path.isdir(abs_path)&('ipynb_checkpoints' not in abs_path):
            file_list+=get_files(abs_path)
    return file_list

def process_supsub(soup):
    """
    add underscore (_) before all superscript or subscript text
    
    Args: 
        soup: BeautifulSoup object of html
    
    """
    for sup in soup.find_all(['sup','sub']):
        s = sup.get_text()
        if sup.string==None:
            sup.extract()
        elif re.match('[_-]',s):
            sup.string.replace_with('{} '.format(s))
        else:
            sup.string.replace_with('_{} '.format(s))

def process_em(soup):
    """
    remove all emphasized text
    
    Args: 
        soup: BeautifulSoup object of html

    """
    for em in soup.find_all('em'):
        s = em.get_text()
        if em.string==None:
            em.extract()
        else:
            em.string.replace_with('{} '.format(s))

def read_mapping_file():
    mapping_dict = {}
    # with open('D:\imperial college\project2\IAO_FINAL_MAPPING.txt','r',encoding='utf-8') as f: # CHANGE DIRECT
    with open('./IAO_FINAL_MAPPING.txt','r',encoding='utf-8') as f: # CHANGE DIRECT
        lines = f.readlines()
        for line in lines:
            heading = line.split('\t')[0].lower().strip('\n')
            IAO_term = line.split('\t')[1].lower().strip('\n')
            if IAO_term != '':
                if '/' in IAO_term:
                    IAO_term_1 = IAO_term.split('/')[0].strip(' ')
                    IAO_term_2 = IAO_term.split('/')[1].strip(' ')
                    if IAO_term_1 in mapping_dict.keys():
                        mapping_dict[IAO_term_1].append(heading)
                    else:
                        mapping_dict.update({IAO_term_1:[heading]})
                        
                    if IAO_term_2 in mapping_dict.keys():
                        mapping_dict[IAO_term_2].append(heading)
                    else:
                        mapping_dict.update({IAO_term_2:[heading]})
                        
                else:
                    if IAO_term in mapping_dict.keys():
                        mapping_dict[IAO_term].append(heading)
                    else:
                        mapping_dict.update({IAO_term:[heading]})
    return mapping_dict

def read_maintext_json(json_file):
    mapping_dict = read_mapping_file()
    # paragraphs = list(json_file.values())[1]
    paragraphs = json_file['paragraphs']
    for paragraph in paragraphs:
        section_heading = paragraph['section_heading']
        tokenized_section_heading = nltk.wordpunct_tokenize(section_heading)
        text = nltk.Text(tokenized_section_heading)
        words = [w.lower() for w in text if w.isalpha()]
        h2_tmp = ' '.join(word for word in words)
        
        if h2_tmp !='':
            if ' and ' in h2_tmp:
                mapping_result = []
                h2_parts = h2_tmp.split(' and ')
                for h2_part in h2_parts:
                    for IAO_term,heading_list in mapping_dict.items():
                        if any([fuzz.ratio(h2_part,heading)>=94 for heading in heading_list]):
                            mapping_result.append(IAO_term)
                            break
                                
            else:
                for IAO_term,heading_list in mapping_dict.items():
                    if any([fuzz.ratio(h2_tmp,heading)>95 for heading in heading_list]):
                        mapping_result = [IAO_term]
                        break
                    else:
                        mapping_result = []
        else:
            h2=''
            mapping_result = ''
        paragraph.update({'IAO_term':mapping_result})
    return json_file

def read_abbreviations_table(json_file):
    abbreviations = json_file['abbreviations']
    if abbreviations=='':
        return {}
    return abbreviations
