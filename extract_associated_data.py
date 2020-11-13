import argparse
import os
import re
from itertools import product
import json
import xlrd,xlwt
import openpyxl


def check_superrow(row):
    """
    check if the current row is a superrow
    ––––––––––––––––––––––––––––––––––––––––––––––––––
    params: row, list object
    return: bool
    """
    if len(set([i for i in row if (str(i)!='')&(str(i)!='\n')&(str(i)!='None')]))==1:
        return True
    else:
        return False

def get_superrows(t):
    """
    determine if there exists a splittable pattern in the header cell

    Args:
        t: BeautifulSoup object of table

    Returns:
        idx_list: a list of superrow index

    """
    idx_list = []
    for idx,row in enumerate(t):
        if check_superrow(row):
            idx_list.append(idx)
    return idx_list

def table2json(table_2d, header_idx, subheader_idx, superrow_idx, table_num, caption, footer):
    tables = []
    sections = []
    cur_table = {}
    cur_section = {}

    pre_header = []
    pre_superrow = None
    cur_header = ''
    cur_superrow = ''
    for row_idx,row in enumerate(table_2d):
        if not any([i for i in row if i not in ['','None']]):
            continue
        if row_idx in header_idx:
            cur_header = [table_2d[i] for i in [i for i in subheader_idx if row_idx in i][0]]
        elif row_idx in superrow_idx:
            cur_superrow = [i for i in row if i not in ['','None']][0]
        else:      
            if cur_header!=pre_header:
                sections = []
                pre_superrow = None
                cur_table = {'identifier':str(table_num+1), 
                             'title':caption, 
                             'columns':cur_header,
                             'section':sections,
                             'footer':footer}
                tables.append(cur_table)
            elif cur_header==pre_header:
                cur_table['section'] = sections
            if cur_superrow!=pre_superrow:
                cur_section = {'section_name':cur_superrow, 
                               'results': [row]}
                sections.append(cur_section)
            elif cur_superrow==pre_superrow:
                cur_section['results'].append(row)

            pre_header = cur_header
            pre_superrow = cur_superrow

    if len(tables)>1:
        for table_idx,table in enumerate(tables):
            table['identifier'] += '.{}'.format(table_idx+1)
    return tables


def xls_read(filepath):
    workbook = xlrd.open_workbook(filepath)
    tables = []
    # skip the last sheet
    for i in range(len(workbook.sheets())):
        sheet = workbook.sheet_by_index(i)
        if sheet.nrows==0 and sheet.ncols==0:
            continue
        table = []
        for i in range(sheet.nrows):
            table.append([])
            for j in range(sheet.ncols):
                v = sheet.row_values(i)[j]
                if v==None:
                    v=''
                table[i].append(v)
        tables.append(table)
    return tables

def xlsx_read(filepath):
    tables = []
    workbook = openpyxl.load_workbook(filepath)
    for sheetname in workbook.sheetnames:
        worksheet = workbook[sheetname]
        rows = list(worksheet.rows)
        if rows==[]:
            continue
        table = []
        for row in rows:
            row = [item.value or '' for item in row]
            table.append(row)
        # unmerge merge-cells
        merge_list = worksheet.merged_cells
        for merge in merge_list:
            coords = merge.bottom
            # switch to 0 index
            coords = [(i-1,j-1) for i,j in coords]
            merge_value = table[coords[0][0]][coords[0][1]]
            for i,j in coords[1:]:
                table[i][j] = merge_value
        
        # identify column index by border style, character style
        
        # rid of empty list
        table = [row for row in table if set(row)!={None} and set(row)!={''}]
        tables.append(table)
    return tables

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--associated_data_dir", type=str, help="directory of associated data")
    parser.add_argument("-t", "--target_dir", type=str, help="target directory for output")
    
    args = parser.parse_args()
    associated_data_dir = args.associated_data_dir
    target_dir = args.target_dir

    if not os.path.isdir(target_dir):
        try:
            os.makedirs(target_dir)
        except:
            print('Error occured when creating target directory')

    files = [os.path.join(associated_data_dir,i) for i in os.listdir(associated_data_dir)]

    table_2d = []
    for filepath in files:
        if filepath.endswith('xls'):
            tables = xls_read(filepath)
        if filepath.endswith('xlsx'):
            try:
                tables = xlsx_read(filepath)
            except:
                print('Error occured for file : ',filepath)
        if filepath.endswith('txt'):
            try:
                with open(filepath, 'rb') as f:
                    text = f.read()
                    text = text.decode()
            except:
                print('Error occured for file : ',filepath)
                continue
            tables = [[i.split('\t') for i in text.split('\r\n')]]
        if filepath.endswith('csv'):
            try:
                with open(filepath, 'rb') as f:
                    text = f.read()
                    text = text.decode()
            except:
                print('Error occured for file : ',filepath)
                continue
            tables = [[i.split(',') for i in text.split('\n')]]
        table_2d += tables

    table_json = {'tables':[]} 
    for table_num,t in enumerate(table_2d):
        superrow_idx = get_superrows(t)
        cur_table = table2json(t, [], [], superrow_idx, table_num, '', '')
        table_json['tables'].append(cur_table)

    basename = os.path.abspath(associated_data_dir).split('/')[-1]
    filename = '{}_associated_data.json'.format(basename)
    with open(os.path.join(target_dir,filename),'w') as f:
        json.dump(table_json,f,ensure_ascii=False)
        