#!/usr/bin/env python
# coding: utf-8

"""
A Python 3 refactoring of Vincent Van Asch's Python 2 code at

http://www.cnts.ua.ac.be/~vincent/scripts/abbreviations.py

Based on

A Simple Algorithm for Identifying Abbreviations Definitions in Biomedical Text
A. Schwartz and M. Hearst
Biocomputing, 2003, pp 451-462.

"""
import os
from utils import *
import regex as re
import argparse
import json
import logging
import sys
from collections import defaultdict, Counter

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)
class Candidate(str):
    def __init__(self, value):
        super().__init__()
        self.start = 0
        self.stop = 0

    def set_position(self, start, stop):
        self.start = start
        self.stop = stop


def yield_lines_from_file(file_path):
    with open(file_path, 'rb') as f:
        for line in f:
            try:
                line = line.decode('utf-8')
            except UnicodeDecodeError:
                line = line.decode('latin-1').encode('utf-8').decode('utf-8')
            line = line.strip()
            yield line


def yield_lines_from_doc(doc_text):
    for line in doc_text.split("."):
        yield line.strip()


def best_candidates(sentence):
    """
    :param sentence: line read from input file
    :return: a Candidate iterator
    """

    if '(' in sentence:
        # Check some things first
        if sentence.count('(') != sentence.count(')'):
            raise ValueError("Unbalanced parentheses: {}".format(sentence))

        if sentence.find('(') > sentence.find(')'):
            raise ValueError("First parentheses is right: {}".format(sentence))

        close_index = -1
        while 1:
            # Look for open parenthesis. Need leading whitespace to avoid matching mathematical and chemical formulae
            open_index = sentence.find(' (', close_index + 1)

            if open_index == -1: break

            # Advance beyond whitespace
            open_index += 1

            # Look for closing parentheses
            close_index = open_index + 1
            open_count = 1
            skip = False
            while open_count:
                try:
                    char = sentence[close_index]
                except IndexError:
                    # We found an opening bracket but no associated closing bracket
                    # Skip the opening bracket
                    skip = True
                    break
                if char == '(':
                    open_count += 1
                elif char in [')', ';', ':']:
                    open_count -= 1
                close_index += 1

            if skip:
                close_index = open_index + 1
                continue

            # Output if conditions are met
            start = open_index + 1
            stop = close_index - 1
            candidate = sentence[start:stop]

            # Take into account whitespace that should be removed
            start = start + len(candidate) - len(candidate.lstrip())
            stop = stop - len(candidate) + len(candidate.rstrip())
            candidate = sentence[start:stop]
            #print (candidate)

            if conditions(candidate):
                new_candidate = Candidate(candidate)
                new_candidate.set_position(start, stop)
                yield new_candidate
            #elif LF_in_parentheses:


def conditions(candidate):
    """
    Based on Schwartz&Hearst

    2 <= len(str) <= 10
    len(tokens) <= 2
    re.search(r'\p{L}', str)
    str[0].isalnum()

    and extra:
    if it matches (\p{L}\.?\s?){2,}
    it is a good candidate.

    :param candidate: candidate abbreviation
    :return: True if this is a good candidate
    """
    LF_in_parentheses=False
    viable = True
    if re.match(r'(\p{L}\.?\s?){2,}', candidate.lstrip()):
        viable = True
    if len(candidate) < 2 or len(candidate) > 10:
        viable = False
    if len(candidate.split()) > 2:
        viable = False
        LF_in_parentheses=True                #customize funcition find LF in parentheses
    if candidate.islower():                   #customize funcition discard all lower case candidate
        viable = False
    if not re.search(r'\p{L}', candidate): # \p{L} = All Unicode letter
        viable = False
    if not candidate[0].isalnum():
        viable = False

    return viable


def get_definition(candidate, sentence):
    """
    Takes a candidate and a sentence and returns the definition candidate.

    The definition candidate is the set of tokens (in front of the candidate)
    that starts with a token starting with the first character of the candidate

    :param candidate: candidate abbreviation
    :param sentence: current sentence (single line from input file)
    :return: candidate definition for this abbreviation
    """
    # Take the tokens in front of the candidate
    tokens = re.split(r'[\s\-]+', sentence[:candidate.start - 2].lower())
    # the char that we are looking for
    key = candidate[0].lower()

    # Count the number of tokens that start with the same character as the candidate
    first_chars = [t[0] for t in filter(None, tokens)]

    definition_freq = first_chars.count(key)
    candidate_freq = candidate.lower().count(key)

    # Look for the list of tokens in front of candidate that
    # have a sufficient number of tokens starting with key
    if candidate_freq <= definition_freq:
        # we should at least have a good number of starts
        count = 0
        start = 0
        start_index = len(first_chars) - 1
        while count < candidate_freq:
            if abs(start) > len(first_chars):
                raise ValueError("candidate {} not found".format(candidate))
            start -= 1
            # Look up key in the definition
            try:
                start_index = first_chars.index(key, len(first_chars) + start)
            except ValueError:
                pass

            # Count the number of keys in definition
            count = first_chars[start_index:].count(key)

        # We found enough keys in the definition so return the definition as a definition candidate
        start = len(' '.join(tokens[:start_index]))
        stop = candidate.start - 1
        candidate = sentence[start:stop]

        # Remove whitespace
        start = start + len(candidate) - len(candidate.lstrip())
        stop = stop - len(candidate) + len(candidate.rstrip())
        candidate = sentence[start:stop]

        new_candidate = Candidate(candidate)
        new_candidate.set_position(start, stop)
        return new_candidate

    else:
        raise ValueError('There are less keys in the tokens in front of candidate than there are in the candidate')


def select_definition(definition, abbrev):
    """
    Takes a definition candidate and an abbreviation candidate
    and returns True if the chars in the abbreviation occur in the definition

    Based on
    A simple algorithm for identifying abbreviation definitions in biomedical texts, Schwartz & Hearst
    :param definition: candidate definition
    :param abbrev: candidate abbreviation
    :return:
    """

    if len(definition) < len(abbrev):
        raise ValueError('Abbreviation is longer than definition')

    if abbrev in definition.split():
        raise ValueError('Abbreviation is full word of definition')

    s_index = -1
    l_index = -1

    while 1:
        try:
            long_char = definition[l_index].lower()
        except IndexError:
            raise

        short_char = abbrev[s_index].lower()

        if not short_char.isalnum():
            s_index -= 1

        if s_index == -1 * len(abbrev):
            if short_char == long_char:
                if l_index == -1 * len(definition) or not definition[l_index - 1].isalnum():
                    break
                else:
                    l_index -= 1
            else:
                l_index -= 1
                if l_index == -1 * (len(definition) + 1):
                    raise ValueError("definition {} was not found in {}".format(abbrev, definition))

        else:
            if short_char == long_char:
                s_index -= 1
                l_index -= 1
            else:
                l_index -= 1

    new_candidate = Candidate(definition[l_index:len(definition)])
    new_candidate.set_position(definition.start, definition.stop)
    definition = new_candidate

    tokens = len(definition.split())
    length = len(abbrev)

    if tokens > min([length + 5, length * 2]):
        raise ValueError("did not meet min(|A|+5, |A|*2) constraint")

    # Do not return definitions that contain unbalanced parentheses
    if definition.count('(') != definition.count(')'):
        raise ValueError("Unbalanced parentheses not allowed in a definition")

    return definition


def extract_abbreviation_definition_pairs(file_path=None,
                                          doc_text=None,
                                          most_common_definition=False,
                                          first_definition=False,
                                          all_definition=True):
    abbrev_map = dict()
    list_abbrev_map = defaultdict(list)
    counter_abbrev_map = dict()
    omit = 0
    written = 0
    if file_path:
        sentence_iterator = enumerate(yield_lines_from_file(file_path))
    elif doc_text:
        sentence_iterator = enumerate(yield_lines_from_doc(doc_text))
    else:
        return abbrev_map

    collect_definitions = False
    if most_common_definition or first_definition or all_definition:
        collect_definitions = True

    for i, sentence in sentence_iterator:
        # Remove any quotes around potential candidate terms
        clean_sentence = re.sub(r'([(])[\'"\p{Pi}]|[\'"\p{Pf}]([);:])', r'\1\2', sentence)
        try:
            for candidate in best_candidates(clean_sentence):
                try:
                    definition = get_definition(candidate, clean_sentence)
                except (ValueError, IndexError) as e:
                    log.debug("{} Omitting candidate {}. Reason: {}".format(i, candidate, e.args[0]))
                    omit += 1
                else:
                    try:
                        definition = select_definition(definition, candidate)
                    except (ValueError, IndexError) as e:
                        log.debug("{} Omitting definition {} for candidate {}. Reason: {}".format(i, definition, candidate, e.args[0]))
                        omit += 1
                    else:
                        # Either append the current definition to the list of previous definitions ...
                        if collect_definitions:
                            list_abbrev_map[candidate].append(definition)
                        else:
                            # Or update the abbreviations map with the current definition
                            abbrev_map[candidate] = definition
                        written += 1
        except (ValueError, IndexError) as e:
            log.debug("{} Error processing sentence {}: {}".format(i, sentence, e.args[0]))
    log.debug("{} abbreviations detected and kept ({} omitted)".format(written, omit))

    # Return most common definition for each term
    if collect_definitions:
        if most_common_definition:
            # Return the most common definition for each term
            for k,v in list_abbrev_map.items():
                counter_abbrev_map[k] = Counter(v).most_common(1)[0][0]
        elif first_definition:
            # Return the first definition for each term
            for k, v in list_abbrev_map.items():
                counter_abbrev_map[k] = v
        elif all_definition:
            for k, v in list_abbrev_map.items():
                counter_abbrev_map[k] = v
        return counter_abbrev_map

    # Or return the last encountered definition for each term
    return abbrev_map

def merge_pair_Dict(pairs,whole_pair_dict):
    for SF, LF in pairs.items():
        if SF in list(whole_pair_dict.keys()):
            if LF.lower() not in whole_pair_dict[SF]:
                whole_pair_dict[SF].append(LF.lower())
        else:
            whole_pair_dict[SF]=[LF.lower()]
    return whole_pair_dict

def listToDict(lst):
    op = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return op

def abbre_table_to_dict(t):
    abbre_list=[]
    rows = t.findAll("tr")
    for i in rows:
        elements = i.findAll(['td', 'th'])
        vals = [j.get_text() for j in elements]
        if len(vals)>1:
            abbre_list+=vals
    abbre_dict=listToDict(abbre_list)
    return abbre_dict

def abbre_list_to_dict(t):
    abbre_list=[]
    SF = t.findAll("dt")
    SF_list = [SF_word.get_text() for SF_word in SF]
    LF = t.findAll("dd")
    LF_list = [LF_word.get_text() for LF_word in LF]
    abbre_dict=dict(zip(SF_list, LF_list))
    return abbre_dict
    
def get_abbre_plain_text(soup_og):
    abbre_text=soup_og.get_text()
    abbre_list=abbre_text.split(';')
    list_lenth=len(abbre_list)
    return abbre_list,list_lenth

def get_abbre_dict_given_by_author(soup_og):

    header = soup_og.find_all('h2',recursive=True)
    abbre_dict={}
    for number, element in enumerate(header):
        if re.search('abbreviation',element.get_text(),re.IGNORECASE):
            nearest_down_tag = element.next_element
            while nearest_down_tag:
                tag_name = nearest_down_tag.name
                
            # when abbre is table
                if tag_name == 'table':
                    abbre_dict=abbre_table_to_dict(nearest_down_tag)
                    break

            # when abbre is list
                elif tag_name=='dl':
                    abbre_dict=abbre_list_to_dict(nearest_down_tag)
                    break

            # when abbre is plain text
                elif tag_name=='p':
                    abbre_list,list_lenth = get_abbre_plain_text(nearest_down_tag)
                    if list_lenth<=2:
                        nearest_down_tag = nearest_down_tag.next_element
                        continue
                    else:
                        for abbre_pair in abbre_list:
                            if len(abbre_pair.split(':'))==2:abbre_dict.update({abbre_pair.split(':')[0]:abbre_pair.split(':')[1]})
                            elif len(abbre_pair.split(','))==2:abbre_dict.update({abbre_pair.split(',')[0]:abbre_pair.split(',')[1]})
                            elif len(abbre_pair.split(' '))==2:abbre_dict.update({abbre_pair.split(' ')[0]:abbre_pair.split(' ')[1]})
                        break
                        
            # search until next h2
                elif tag_name=='h2':
                    break
                else:
                    nearest_down_tag = nearest_down_tag.next_element
    return abbre_dict
    
    
def extract_abbreviation(main_text):
    text_to_be_written=''
    pairs = extract_abbreviation_definition_pairs(doc_text=main_text,most_common_definition=True)

    return pairs


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath", type=str, help="filepath of of html file to be processed")
    parser.add_argument("-fh", "--htmlfilepath", type=str, help="filepath of of html file to be processed")
    parser.add_argument("-t", "--target_dir", type=str, help="target directory for output")
    
    args = parser.parse_args()
    filepath = args.filepath
    htmlfilepath = args.htmlfilepath

    target_dir = args.target_dir
    if not os.path.isdir(target_dir):
        try: 
            os.makedirs(target_dir)
        except:
            raise FileNotFoundError('Target filepath does not exist')
    # read original soup
    with open(htmlfilepath, 'r', encoding='UTF-8') as f:
        text = f.read()
    soup_og = BeautifulSoup(text, 'html.parser')

    # assign heading by fuzzy match    
    with open(filepath,'r',encoding='UTF-8',errors='ignore') as f:
        maintext_json = json.load(f)
    maintext_json = read_maintext_json(maintext_json)

    
    # assign heading by DAG
    paper = {}
    paragraphs = maintext_json['paragraphs']
    for paragraph in paragraphs:
        h2 = paragraph['section_heading']
        IAO_term = paragraph['IAO_term']
        paper.update({h2:IAO_term})

    mapping_dict_with_DAG = assgin_heading_by_DAG(paper)
    for paragraph in paragraphs:
        h2 = paragraph['section_heading']
        if h2 in mapping_dict_with_DAG.keys():
            paragraph.update({'IAO_term':mapping_dict_with_DAG[h2]})
            
    # map IAO terms to IAO IDs       
    IAO_term_to_no_dict = read_IAO_term_to_ID_file()
    for paragraph in paragraphs:
        mapping_result_ID_version = []
        IAO_terms = paragraph['IAO_term']
        if IAO_terms != '' and IAO_terms != []:
            for IAO_term in IAO_terms:
                if IAO_term in IAO_term_to_no_dict.keys():
                    mapping_result_ID_version.append(IAO_term_to_no_dict[IAO_term])
        else:
            mapping_result_ID_version = ''
        paragraph.update({'IAO_ID':mapping_result_ID_version})
        
    with open(filepath,'w', encoding='UTF-8') as f:
        json.dump(maintext_json, f, indent=1, ensure_ascii=False)


    paragraphs = maintext_json['paragraphs']
    all_abbreviations = {}
    for paragraph in paragraphs:
        maintext = paragraph['body']
        pairs = extract_abbreviation(maintext)
        all_abbreviations.update(pairs)
    
    
    additional_abbreviations = {}

    author_provided_abbreviations = get_abbre_dict_given_by_author(soup_og)
    for SF, LF in all_abbreviations.items():
        if SF not in author_provided_abbreviations.keys():
                additional_abbreviations.update({SF:LF})
    all_abbreviations.update(author_provided_abbreviations)
    
    abbrev_json = {}
    abbrev_json['author_provided_abbreviations'] = author_provided_abbreviations
    abbrev_json['additional_abbreviations'] = additional_abbreviations
    abbrev_json['all_abbreviations'] = all_abbreviations
    
    output_path = os.path.join(target_dir, os.path.basename(filepath).replace("_maintext.json",'') + '_abbreviations' + '.json')
    with open(output_path,'w', encoding='UTF-8') as f:
        json.dump(abbrev_json,f,indent=2,ensure_ascii=False)
