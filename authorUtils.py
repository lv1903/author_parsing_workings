"""

utility functions for parsing author names

"""

import pandas as pd
import unicodedata
import re

from authorRe import dmatch


#### functions to normalise names

def __strip_accents(s):
    """"remove accents from string"""
    return ''.join(c for c in unicodedata.normalize('NFKD', s)
                  if unicodedata.category(c) != 'Mn')
				  
def normalise_name(s):
    """normalises string, returns lower case names, removes white spaces and dots"""
    
    s = __strip_accents(s)          # remove diacritics
    s= s.lower()                  # make lower case
                                  # follow order:
    s = s.replace('.', ' ')       # 1) remove dots from initials ? should this only be done where character . space
    s = re.sub('(\s){2,}', ' ', s)# 2) remove double spaces
    s = s.strip()                 # 3) strip white spaces
    return s
	
def normalise_df_names(df, col):
    """normalises col from dataframe, returns lower case names, removes white spaces and dots"""
    
    df['norm'] = df[col]     # string to normalise
    df.rename(index=str, columns={col: 'raw_name'}, inplace=True) # keep original string
    
    df.norm = df.norm.apply(lambda x: __strip_accents(x))  # remove diacritics
    df.norm = df.norm.str.lower()                        # make lower case
    
    df.norm = df.norm.str.replace('.', ' ')              # 1) remove dots from initials ? should this only be done where character . space
    df.norm = df.norm.str.replace('(\s){2,}', ' ')             # 2) remove double spaces    
    df.norm = df.norm.str.strip()                        # 3) strip white spacesname
	
    return df
 
 
    
#### functions for journal format

def __journal_match_list(df, field, match_string, min_match, blanks=False):
    
    # get a list of journal where the name field matchs a regex above a threshold percentage
    # if blanks = False then excludes the number blanks from the average match calculation 

    df['match'] = 0
    df.loc[df[field].str.match(match_string), 'match'] = 1    
    if blanks:
        match_df = df.groupby('journal_id').match.mean().reset_index()
    else:
        match_df = df[df[field]!=''].groupby('journal_id').match.mean().reset_index()
    return list(match_df[match_df.match>=min_match].journal_id)


def get_journal_formats_df(df, dmatch):
    
    # identify journals with troublesome name formats
    # input: 
    # data frame with normalised name, raw name and journal_id 
    # output:
    # data frame with journal id and format
    
    df['journal_format'] = '-'
    
    # identify errors
    journal_list = __journal_match_list(df, 'norm', dmatch['no_spaces'], 0.5)
    df.loc[df.journal_id.isin(journal_list), 'journal_format'] += '-error_no_spaces'
    
    journal_list = __journal_match_list(df, 'norm', dmatch['blank'], 0.5, blanks=True)
    df.loc[df.journal_id.isin(journal_list), 'journal_format'] += '-error_blank'
    
    # identify last_names_comma
    journal_list = __journal_match_list(df, 'norm', dmatch['names_comma'], 0.7)
    df.loc[df.journal_id.isin(journal_list), 'journal_format'] += '-last_names_comma'
    
    # identify all caps
    journal_list = __journal_match_list(df, 'raw_name', dmatch['no_lower_case'], 0.7)
    df.loc[df.journal_id.isin(journal_list), 'journal_format'] += '-no_lower_case'
    
    # identify initials_no_spaces
    journal_list = __journal_match_list(df, 'raw_name', dmatch['initials_no_space'], 0.3)
    df.loc[df.journal_id.isin(journal_list), 'journal_format'] += '-initials_no_space'
    
    return df[['journal_id', 'journal_format']].drop_duplicates()
    
    
    
    
#### split name functions

def __get_name_format(norm, raw, known_error_list):   

        """identitfy the format of a name"""
        
        # check for errors
        
        if re.match(dmatch['blank'], raw): 
            return 'error.blank'
        elif re.match(dmatch['no_spaces'], norm): 
            return 'error.no_spaces'
        elif re.match(dmatch['illegal'], norm): 
            return 'error.illegal_character'
                ## only initials
        elif re.match(dmatch['only_initials'], norm): 
            return  'error.only_initials'
        elif len(norm) > 100: ## todo check good length
            return 'error.too_long' 
        elif norm in known_error_list:
            return 'error.list'
        
        ## todo?? double comma???
        
        # difficult formats
        
        elif re.match(dmatch['names_comma_initials_names'], norm):
            return 'unknown.names_comma_initials_names'        
        
        # check known formats
        
        else:
            name_formats = [
                'names_initials_names',
                'initials_names',
                'only_names',
#                 '_initials_names',
                'names_initials',
                
                'names_comma_names',
                'names_comma_names_initials',
                
                
            ]
            
            for name_format in name_formats:                
                if re.match(dmatch[name_format], norm): return name_format
        
        
        
        # if none of the above match
        return 'error.unknown_format'

    
def __find_prefix(a, p):
    # returns index of first recognised prefix else return -1 for very last name 
    # doesn't include very first name
    i = 1
    while i < len(a):
        if a[i] in p:
            return i
        i+=1
    return -1
    
def __get_initials(forenames):
    """get the initials from forenames"""
    
    return ' '.join([n[0] for n in forenames.split()])
    
        
def __parse_name(norm, raw, name_format, prefix_list):

    """apply the appropriate parser for the name format"""
    
    forenames = ''
    initials = ''
    last_names = ''

    if name_format == 'names_initials_names':
        # get the initials and then parts before and after
        initials = ' '.join(re.findall(dmatch['_initial_'], norm))
        forenames = re.match("^.*(?=\s{})".format(initials), norm).group(0)
        last_names = norm[len(initials + forenames) + 2:]
        initials = __get_initials(forenames) + ' ' + initials
    
    elif name_format == 'initials_names':
        # get the initials and then parts before and after
        initials = re.match(dmatch['initials_'], norm).group(0).strip()
        last_names = norm[len(initials) + 1:]
        
    elif name_format == 'only_names':
        
        a = norm.split()
        i = __find_prefix(a, prefix_list)
        forenames = ' '.join(a[:i])
        initials = __get_initials(forenames)
        last_names = ' '.join(a[i:])
        
    elif name_format == 'names_initials':
        
        last_names = re.match(dmatch['names_'], norm).group(0)
        initials = norm[len(last_names) + 1:]
        
    
    elif name_format == 'names_comma_names':
        # get the parts before and after the comma
        a = norm.split(',')
        forenames = a[1].strip()
        initials = __get_initials(forenames)
        last_names = a[0].strip()
        
    elif name_format == 'names_comma_names_initials':        
        #reveres the order and call the function with the new name_format
        a = norm.split(',')
        norm = a[1] + ' ' + a[0]
        forenames, initials, last_names = __parse_name(norm, None, 'names_initials_names', prefix_list)
        
    elif name_format == 'names_comma_initials_names':
        print(norm)
    
    return forenames, initials, last_names
    

def split_name(norm, raw, journal_format=None, prefix_list=[], known_error_list=[]):
    
    """get the name format and then parses the name, returns strings for forenames, all initials (first and middle) and last names"""
    
    forenames = ''
    initials = ''
    last_names = ''
    name_format = 'unknown'
    
    name_format = __get_name_format(norm, raw, known_error_list)
    
    # if an error return 
    if re.match('error', name_format):
        #print(name_format)
        return forenames, initials, last_names, name_format
    
    #print(name_format)
    forenames, initials, last_names  = __parse_name(norm, raw, name_format, prefix_list)  
    
    return forenames, initials, last_names, name_format    
    
    
def test_split_name(prefix_list, known_error_list):

    test_array = [
        
        # to check
        [('def, a abc', 'def, a abc', None), ('unknown', 'unknown', 'unknown', 'unknown.names_comma_initials_names')],
        
        
        [('def def a b c', 'def def a b c', None), ('unknown', 'a b c', 'def def', 'names_initials')],
        [('abc def ghi jkl', 'abc def ghi jkl', None), ('abc def ghi', 'a d g', 'jkl', 'only_names')],
        [('abc der van def', 'abc der van def', None), ('abc', 'a', 'der van def', 'only_names')],
        [('a b c def', ' a b c def', None), ('unknown', 'a b c', 'def', 'initials_names')],
        [('fgh, abc d e', ' fgh, abc d e', None), (' abc', 'a d e', 'fgh', 'names_comma_names_initials')],
        [('abc abc d e fgh', 'abc abc d e fgh', None), ('abc abc', 'a a d e', 'fgh', 'names_initials_names')],
        [('def def, abc abc', 'Def Def, abc abc', None), ('abc abc', 'a a', 'def def', 'names_comma_names')],
        [('abc, acb, abc', 'abc, acb, abc', None), ('unknown', 'unknown', 'unknown', 'error.unknown_format')],
        [('', '', None), ('unknown', 'unknown', 'unknown', 'error.blank')],
        [('', ' ', None), ('unknown', 'unknown', 'unknown', 'error.blank')],
        [('abc', 'abc', None), ('unknown', 'unknown', 'unknown', 'error.no_spaces')],
        [('abc:', 'abc:', None), ('unknown', 'unknown', 'unknown', 'error.illegal_character')],
        [('et al', 'et al', None), ('unknown', 'unknown', 'unknown', 'error.list')],
        [('a b c', 'a b c', None), ('unknown', 'unknown', 'unknown', 'error.only_initials')],
        [('abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc', 'ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ', None), ('unknown', 'unknown', 'unknown', 'error.too_long')]
    #     [('mark jones', 'Mark Jones', None), ('mark', 'm', 'jones', 'names')]
    ]

    print('TESTING split_names')

    pass_flag = True

    for t in test_array:
        intuple = t[0]
        outtuple = t[1]
        #print([intuple, outtuple])
        restuple = split_name(intuple[0], intuple[1], intuple[2], prefix_list, known_error_list)
        if restuple != outtuple:
            pass_flag = False
            print('FAIL')
            print(intuple)
            print('gave')
            print(restuple)
            print('should be')
            print(outtuple)
            print("*************")
        else:
    #         print("PASS")
    #         print("*************")
            pass

    if pass_flag:
        print('PASS split_names')
    else:
        print('TESTING COMPLETE ERRORS')
        
        
#### get name variant regex

def _initials_regex(a):

    """construct regex for variants of initals, takes array of initials and returns regex string"""

    s = '({}$'.format(a[0]) 
    i = 1
    while i < len(a):
        i+=1
        s += '|' + ' '.join(a[0:i]) + '$'
    s += '|' + ' '.join(a)+ ' .*$'
    s += ')'
    return s


def _forenames_regex(a):

    """construct regex for variants of forenames, takes array of forenames and returns regex string"""

    s= '($|\s$'
    try:
        s += '|{}$'.format(a[0], a[0])
        i = 1
        while i < len(a):
            i+=1
            s += '|'+ ' '.join(a[0:i]) + '$'
        s += '|' + ' '.join(a)+ ' .*$'
    except:
        s += '|.*'
    s += ')'
    return s


def _last_names_regex(a):

    """construct regex for variants of last names, takes array of last names and returns regex string"""
    
    s = '({}$'.format(a[-1], a[-1])
    i = 1
    while i < len(a):
        i+=1
        s += '|' + ' '.join(a[-1*i:]) + '$'
    s += '|.* ' + ' '.join(a) + '$'
    s += ')'    
    return s

def get_names_regex(forenames, initials, last_names):

    """get regex strings for variants of forenames, initals and last names"""
    
    f_re = _forenames_regex(forenames.split())
    i_re = _initials_regex(initials.split())
    l_re = _last_names_regex(last_names.split())
    
    return f_re, i_re, l_re
     

def match_variants(forenames, initials, last_names, df):

    """returns dataframe with variants of the input name"""

    f_re, i_re, l_re = get_names_regex(forenames, initials, last_names)
    
    # faster to run 3 seperate filters rather than one filter with &
    f_df = df[df.forenames.str.match(f_re)]   
    i_df = f_df[f_df.initials.str.match(i_re)]    
    res  = i_df[i_df.last_names.str.match(l_re)]
    
    return res
 
 
def match(raw, df, prefix_list=[], known_error_list=[]):

    """takes raw name and df and returns filtered dataframe on name variants"""

    norm = normalise_name(raw)
    forenames, initials, last_names, name_format = split_name(norm, raw, prefix_list, known_error_list)
    res = match_variants(forenames, initials, last_names, df)
    return res

 
        
if __name__ == '__main__':

    import sys
    
    try: 
        pf_filepath = sys.argv[1]
        prefix_list = list(pd.read_csv(pf_filepath, header=None, encoding = 'ISO-8859-1')[0])
    except:        
        try:
            prefix_list = list(pd.read_csv('name_prefixes.csv', header=None, encoding = 'ISO-8859-1')[0])     
        except:
            prefix_list = []
            print('no prefix_list.csv')
    
    try:
        em_filepath = sys.argv[2]
        known_error_list = list(pd.read_csv('error_match.csv', header=None, encoding = 'ISO-8859-1')[0]) 
    except:
        try: 
            known_error_list = list(pd.read_csv('error_match.csv', header=None, encoding = 'ISO-8859-1')[0]) 
        except:
            known_error_list = []
            print('no error_match.csv')
    


    test_split_name(prefix_list, known_error_list) 