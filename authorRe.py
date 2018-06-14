"""

regex for parsing raw author name

"""

import re

# regex elements

legal = "[a-z\s'-]"
no_space = "[a-z'-]"

illegal = "[^a-z,\s'-]"

letter = "[a-z]"      

word = "[a-z'-]{2,}"    

# regex components

legals = '{}*'.format(legal)

initials1 = "({}\s)+".format(letter)
initials = "({}\s)*".format(letter)
end_initial = letter                            

last_name_comma = "{},\s".format(word)

names1 = "({}\s)+".format(word)
names = "({}\s)*".format(word)
end_name = word

# names matches

dmatch = {
    'initials_'                          : '^{}'.format(initials1),
    '_initial_'                          : '(?<=\s){}(?=\s)'.format(letter),    

    'names_comma'                        : '^{}{}'.format(names, last_name_comma), # only for journal check
    'names_comma_names'                  : '^{}{}{}{}$'.format(names, last_name_comma, names, end_name), 
    'names_comma_initials'               : '^{}{}{}{}$'.format(names, last_name_comma, initials, end_initial),
    'names_comma_names_initials'         : '^{}{}{}{}{}$'.format(names, last_name_comma, names1, initials, end_initial),
    'names_comma_initials_names'         : '^{}{}{}{}(){}$'.format(names, last_name_comma, initials1, names, end_name),
    
    'names'                              : '.*({}(?=(\s|$|,)))+'.format(word),
    'names_'                             : '^{}{}(?=\s)'.format(names, end_name),
    'only_names'                         : '^{}{}$'.format(names, end_name),
    'only_initials'                      : '^{}{}$'.format(initials, end_initial),
    
    'names_initials'                     : '^{}{}\s{}{}$'.format(names, end_name, initials, end_initial),
    
    'initials_names'                     : '^{}{}{}$'.format(initials1, names, end_name),
    
    'names_legals_name'                  : '^{}{}{}$'.format(names1, legals, end_name), # only for journal check
    'names_initials_names'               : '^{}{}{}{}$'.format(names1, initials1, names, end_name),
    
    
    'initials_no_space'                  : '((?<=\s)[A-Z]{2,4}(?=($|\s))|(^[A-Z]{2,4}(?=\s)))', # only for journal check
    'no_lower_case'                      : '^[^a-z]{3,}$',      # only for journal check,
    
    'no_spaces'                          : '^{}+$'.format(no_space),
    'blank'                              : '^\s*$',  
    'illegal'                            : '^.*{}+.*$'.format(illegal),

}

if __name__ == '__main__':

	class TestRe():
		
		
		def test(self, test_name, re_string, pass_list, fail_list):
			
			
			
			
			pass_flag = True
			
			# pass 
			for s in pass_list:
				res = re.search(re_string, s)
				#print(s, res)
				if res == None:
					print('{} failed on pass {}'.format(test_name, s))
					pass_flag = False
				else: 
					#print('{} passed match "{}" on "{}"'.format(test_name, s, res.group(0)))
					pass
			
			# fail
			for s in fail_list:
				res = re.search(re_string, s)
				#print(s, res)
				if res != None:
					print('{} failed on fail {}'.format(test_name, s))
					pass_flag = False
					
				
			if pass_flag: 
				print (test_name + ' - PASS')
			else:
				print(re_string)
				print("*************")
				
			return 
					
		 
		def test_names_comma(self, re_string):
			
			# should pass if lower case names followed by a comma space        
			test_name = 'names_comma'
			pass_list = ['abc, def', 'abc def, ', 'abc def ghi, ', "a'bc, ", 'abc-def abc, ']
			fail_list = ['a, ', 'abc abc', 'ABC, ', 'Abc, ', 'a']
			self.test(test_name, re_string, pass_list, fail_list)
			
		def test_initials_no_space(self, re_string):
			
			# should pass if block of 2-4 capital letters
			test_name = 'initials_no_space'
			pass_list = ['ABCDE, ABCDE AB', 'ABCDE, ABC', "A'BCDE ABC", "ABC A'BCDE", 'AB Abc']
			fail_list = ['abcde ab', 'Abcde ab', 'ABCDE ABCDE']
			self.test(test_name, re_string, pass_list, fail_list)
			
			
		def test_no_lower_case(self, re_string):
			
			# should pass if only capitals
			test_name = 'no_lower_case'
			pass_list = ['ABCDE, ABCDE AB', 'ABCDE, ABC', "A'BCDE ABC", "ABC A'BCDE"]
			fail_list = ['abcde ab', 'Abcde ab']
			self.test(test_name, re_string, pass_list, fail_list)
	  

		def test_only_names(self, re_string):
			
			# should pass if only lower case words which are 2 or more characters long
			test_name = 'only_names'
			pass_list = ['abc', 'abc def', "a'bc", 'abc-def']
			fail_list = ['ABC DEF', 'abc, def', 'abc d ef']
			self.test(test_name, re_string, pass_list, fail_list)

			
		def test_only_initials(self, re_string):
			# should only pass if all single lower case letters with spaces with no spaces before or after
			test_name = 'only_initials'
			pass_list = ['a', 'a b c']
			fail_list = ['abc', 'abc a', 'a abc', "a'a" , ' a a' , 'a a ']
			self.test(test_name, re_string, pass_list, fail_list)
			
			
			
		def test_names_initials(self, re_string):
			# should only pass lower case names followed by lower case spaced initials
			test_name = 'names_initials'
			pass_list = ['abc a', 'abc abc a a', "a'abc a"]
			fail_list = ['a abc', 'a a', 'abc abc', 'abc a abc', 'a abc a', 'abc', 'a']
			self.test(test_name, re_string, pass_list, fail_list)        
	  

		def test_names(self, re_string):
			
			# should pass if one or more lower case names
			test_name = 'names'
			pass_list = ['abc', 'abc def', "a'bc", 'abc-def', 'a abc', 'abc a', 'abc, def', 'abc d ef']
			fail_list = ['ABC DEF', 'a', 'a a']
			self.test(test_name, re_string, pass_list, fail_list)    
			
		def test_initials_names(self, re_string):
			
			# should pass if one or more initials followed by one or more names - lower case
			test_name = 'initials_names'
			pass_list = ['a abc', 'a b c abc', 'a abc abc']
			fail_list = ['ab abc', 'abc a abc', 'abc a']
			self.test(test_name, re_string, pass_list, fail_list) 
	  

		def test_names_legals_name(self, re_string):
			
			# should pass if one or more names followed by zero or more names or initials followed by one or more names - lower case
			test_name = 'names_legals_name'
			pass_list = ['abc abc', 'abc abc abc', 'abc abc a abc abc', 'abc ab-cd abc']
			fail_list = ['a abc', 'a abc abc', 'abc a']
			self.test(test_name, re_string, pass_list, fail_list) 
			
			
		def test_no_spaces(self, re_string):
			
			# should pass if there is a lower case string of 1 or more characters with no spaces
			test_name = 'no_spaces'
			pass_list = ['a', 'ab']
			fail_list = ['a b', '', ' ', ' a', 'a ']
			self.test(test_name, re_string, pass_list, fail_list) 
			
		def test_blank(self, re_string):
			# should pass if there is nothing
			test_name = 'blank'
			pass_list = ['', ' ']
			fail_list = ['a', 'a b']
			self.test(test_name, re_string, pass_list, fail_list) 
			
		def test_names_initials_names(self, re_string):
			# should pass there are one or more names followed by one or more initials followed by one or more names - lower case
			test_name = 'names_intitials_names'
			pass_list = ['abc a abc', 'abc abc a abc abc', "abc a a'bc"]
			fail_list = ['a abc', 'abc abc']
			self.test(test_name, re_string, pass_list, fail_list)   
			
		def test_illegal(self, re_string):
			# should pass if contains illegal characters ie not a-z ' -
			test_name = 'illegal'
			pass_list = ['#', 'yfh&amp', 'afaf (dff)']
			fail_list = ['abc', 'abc, a']
			self.test(test_name, re_string, pass_list, fail_list)   
			
		def test_names_comma_names(self, re_string):
			# should pass if names followed by comma followed by names
			test_name = 'names_comma_names'
			pass_list = ['abc, abc', 'abc abc, abc abc']
			fail_list = ['abc', 'abc, a', 'abc, abc, abc']
			self.test(test_name, re_string, pass_list, fail_list)     
			
		def test_names_comma_initials(self, re_string):
			# should pass if names followed by comma followed by names
			test_name = 'names_comma_initials'
			pass_list = ['abc, a', 'abc abc, a a']
			fail_list = ['abc', 'abc, abc a', 'abc, a abc']
			self.test(test_name, re_string, pass_list, fail_list)  
			
		def test_names_comma_names_initials(self, re_string):
			# should pass if names followed by comma followed by names
			test_name = 'names_comma_names_initials'
			pass_list = ['abc, abc a', 'abc abc, abc abc a a']
			fail_list = ['abc', 'abc, a abc a', 'abc, a abc']
			self.test(test_name, re_string, pass_list, fail_list)          
			
		def test_names_comma_initials_names(self, re_string):
			# should pass if names followed by comma followed by names
			test_name = 'names_comma_initials_names'
			pass_list = ['abc, a abc', 'abc abc, a a abc abc']
			fail_list = ['abc abc', 'abc, abc a', 'abc a abc']
			self.test(test_name, re_string, pass_list, fail_list) 
			

	print('RUNNING TESTS')
	print()
			
	testRe = TestRe()

	testRe.test_names_comma_initials_names(dmatch['names_comma_initials_names'])
	testRe.test_names_comma_names_initials(dmatch['names_comma_names_initials'])
	testRe.test_names_comma_initials(dmatch['names_comma_initials'])
	testRe.test_names_comma_names(dmatch['names_comma_names'])
	testRe.test_illegal(dmatch['illegal'])
	testRe.test_names_initials_names(dmatch['names_initials_names'])
	testRe.test_blank(dmatch['blank'])
	testRe.test_no_spaces(dmatch['no_spaces'])
	testRe.test_names_legals_name(dmatch['names_legals_name'])
	testRe.test_initials_names(dmatch['initials_names'])
	testRe.test_names(dmatch['names'])
	testRe.test_names_initials(dmatch['names_initials'])
	testRe.test_only_initials(dmatch['only_initials'])
	testRe.test_only_names(dmatch['only_names'])
	testRe.test_names_comma(dmatch['names_comma'])
	testRe.test_initials_no_space(dmatch['initials_no_space'])  
	testRe.test_no_lower_case(dmatch['no_lower_case'])
	
	print()
	print('TESTS COMPLETE')
