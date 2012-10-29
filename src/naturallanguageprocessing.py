# -*- coding: utf-8 -*-

__author__="vero4ka"
__date__ ="$13.09.2010 7:29:48$"

import time
import re
import itertools
from mylowercase import to_lower


class Parser:
    def __init__(self, dict, text):
        self.dict = dict # ������-�������
        self.text = text # ������� �����
        self.sentences = []
        self.orig_sentences = []
        self.output_file = '..\\output.html'
        self.output_string = ''
        self.parse()

    def parse(self):
        file = open(self.output_file, 'w')
        self.output_string += """
            <html>
            <head>
                    <title>Parser</title>
            </head>
            <body>
        """
        self.output_string += "<h3>�������� �����:</h3>\n"
        self.output_string += '<p>' + text + '</p>\n'

        print "- noting down the time..."
        start_time = time.clock()

        # ����������� ������

        # ��������� ����� �� �����������
        self.sentences = re.split(r'\"*\)*[.?!]+[\s\n]+', self.text)
        # ��������� � ����� ������ ������ []
        # �� ��� ����� ���������:
        self.sentences = self.sentences[:-1]
        
        # ��������� ����������� �� �����
        for i in range(len(self.sentences)):
            sentence = self.sentences[i]
            # ������� �� ����������� ��� ������ � �������
            # �����, ����� - ����� (�����), �����: ����� ("�����")
            self.sentences[i] = re.split(r'\"*\)*,*\:*\s+\-*\s*\(*\"*', sentence)

        # ������������� �����������
        sent_num = 1
        for sentence in self.sentences:
            self.output_string += "<h3>����������� " + sent_num.__str__() + ":</h3>\n"
            self.parse_sentence(sentence)
            sent_num += 1   

        time_for_parsing = time.clock() - start_time
        self.output_string += "<h3>Time = " + time_for_parsing.__str__() + " seconds </h3>\n"
        print "- parsing took", time_for_parsing, "seconds"
        self.output_string += """
            </body>
            </html>
        """
        file.write(self.output_string)
        file.close()


    def parse_sentence(self, sentence):
        forms_in_sentence = []

        # ��������������� ������
        for word in sentence:
            description, all_forms = self.get_description(word)
            # ������� ����� (����������) + ��� �.�.
            self.output_string += "<b>" + word + "</b>: " + description + "<br />\n"

            # ���� ����� ��� ����� ����� ������ ����
            # ����� ���� ������ ��� ���� �� �������: ���, ����, �����, ����...
            if all_forms != None:
                # ������� � ����. ����� �����, � ���. ��� ���������
                for form in all_forms:
                    form.insert(0, word)
                forms_in_sentence.append(all_forms)
        
        # �������������� ������
        self.output_string += "<br /><i><b>�������������� ������:</b></i><br />\n"

        counter_for_versions = 1
        # ������������� ��� ��������� ��������� ���� (��������� ������������)
        list_of_all_combinations = list(itertools.product(*forms_in_sentence))
        for mf_version in list_of_all_combinations:
            forms_are_correct = True # �������� �� ��� ����� �����

            # ���� I.
            # ��������������(���� ��� ���������), ������� ����� ����������������
            # ������ ������������� � ��� �� ����, ������ � �����
            # (���� ��� ������� �� �����������, ��������� � ������� ������)

            NP_groups = [] # ������ ������� ����� ��� �������� ������ ����
            is_adj = False # ������ ��� ���������� ��������������
            adj_forms = [] # ������ ���� ������������� ��� ��������������

            # ��������� ����� ������� ������
            # (����� ����� �������� � ����� NP_groups)
            new_NP_group = []

            for form in mf_version: # ���� �� mf_version (������� ����� ����)
                # ������ form �������� ���: [ 0- ���� �����, 1- ����� ����,
                #      2- �����, 3- ���, 4- ����., 5- �����]

                # ���� �� ���������� �� ��������������
                if form[1] == '����.':
                    is_adj = True # ��������, ��� �� ��� ���������
                    # �������� ��� �������������� (�����, ���, �����)
                    adj_forms.append([form[2], form[3], form[5]])
                    new_NP_group.append(form[0]) # ��������� � ������� �����
                    continue # ��������� � ��������� form � ������
                # ���� �� ���������� �� ��������������� � ����� ��� ���� ����.
                if form[1] == '���.' and is_adj:
                    is_adj = False # �������� ��� ��������������
                    noun = [form[2], form[3], form[5]]
                    new_NP_group.append(form[0]) # ��������� � ������� �����
                    forms_match = True # ��������, ����� ���. � ����. ���������
                    for adj in adj_forms: # ��� ���� ��������������
                        # ���� ����� �� ��������� ���� �� ��� ������ ���������������
                        if not (adj[0] == noun[0] and adj[1] == noun[1] and adj[2] == noun[2]):
                            forms_match = False
                            adj_forms = []
                            break
                    adj_forms = [] # ������� ������ ��������������
                    if not forms_match: # ���� ����� �� �������
                        # �� � ��� ��������� ����� �������� �������
                        forms_are_correct = False
                        new_NP_group = [] # ������� ������� ������
                        continue
                    # ���� ��� ������, ������� ������ � ������ ������� �����
                    NP_groups.append(new_NP_group)
                    new_NP_group = []
            
            # ���� ����� �� ������ I ����, �� ��������� � ������ ������ ����
            if not forms_are_correct:
                continue

            # ���� II.
            # ���������� ���������� ������
            # ���� ����������� ������-�� ������� + ���., � ������ ����������
            # �������� ��������� � �.�. ���., �� ���
            # �������� ���������� ������
            # (���� ��� ������� �� �����������, ��������� � ������� ������)

            PP_groups = [] # ������ ���������� ����� ��� �������� ������ ����
            is_prep = False # ������ ��� ��������� �������

            # ��������� ����� ���������� ������
            # (����� ����� �������� � ����� PP_groups)
            new_PP_group = []
            prep_case = "" # �����, � ������� ����� ��������� �������

            for form in mf_version: # ���� �� mf_version (������� ����� ����)
                # ������ form �������� ���: [ 0- ���� �����, 1- ����� ����,
                #      2- �����, 3- ���, 4- ����., 5- �����]
                # ��� ��������: [ 0- ���� �����, 1- ����� ����, 2- ����� ]

                # ���� �� ���������� �� �������
                if form[1] == '�������':
                    is_prep = True # ��������, ��� �� ��� ���������
                    prep_case = form[2] # �������� ��� �����
                    new_PP_group.append(form[0]) # ��������� � ���������� �����
                    continue # ��������� � ��������� form � ������
                # ���� �� ���������� �� ��������������� � ����� ��� ��� �������
                if form[1] == '���.' and is_prep:
                    is_prep = False # �������� ��� �������
                    noun_case = form[2]
                    new_PP_group.append(form[0]) # ��������� � ������� �����
                    forms_match = True # ��������, ������ ���. � �������� ���������
                    if not prep_case == noun_case: # ���� ������ �� �������
                        # �� � ��� ��������� ����� �������� �������
                        forms_are_correct = False
                        new_PP_group = [] # ������� ���������� ������
                        continue
                    # ���� ��� ������, ������� ������ � ������ ���������� �����
                    PP_groups.append(new_PP_group)
                    new_PP_group = []

            # ���� ����� �� ������ II ����, �� ��������� � ������ ������ ����
            if not forms_are_correct:
                continue

            self.output_string += "<br /><i>������� ������� �" + counter_for_versions.__str__() + "</i>:<br />\n"
            self.output_string += self.forms_toString_V2(mf_version) + "<br />\n"

            # ��������� ������� ������
            if len(NP_groups) != 0:
                self.output_string += "<br /><i>NP groups:</i><br />"
                for group in NP_groups:
                    for word in group:
                        self.output_string += word + " "
                    self.output_string += "<br />"

            # ��������� ���������� ������
            if len(PP_groups) != 0:
                self.output_string += "<br /><i>PP groups:</i><br />"
                for group in PP_groups:
                    for word in group:
                        self.output_string += word + " "
                    self.output_string += "<br />"

            counter_for_versions += 1
            

    # ������� ������ �.�. � �������, ��������������� ����� word
    def get_forms(self, word):
        level = self.dict
        for letter in word:
            if level.get(letter):
                level = level.get(letter)
        return level.get('form')

    # �������� �.�. � ��������� ���, ��� ����� �� ����� ���� ������� �� �����
    # ��.. �������������.. ����� ������� � ��� �����
    def forms_toString(self, forms):
        res = ""
        form_num = 1
        for form in forms:
            res += "<br />" + form_num.__str__() + "). "
            for item in form:
                if item != "": res += item + ", "
            res = res[:-2] # ������ ��������� �������
            form_num += 1
        return res

    def forms_toString_V2(self, forms):
        res = ""
        form_num = 1
        for form in forms:
            res += "<br />" + form_num.__str__() + "). "
            for item in form:
                if item != "":
                    if item == "���.":
                        res += "<span style=\"color:blue\">" + item + "</span>, "
                    elif item == "����.":
                        res += "<span style=\"color:red\">" + item + "</span>, "
                    elif item == "����.":
                        res += "<span style=\"color:green\">" + item + "</span>, "
                    elif item == "�������" or item == "����":
                        res += "<span style=\"color:gray\">" + item + "</span>, "
                    else: res += item + ", "
            res = res[:-2] # ������ ��������� �������
            form_num += 1
        return res

    # �������� ��� �.�. ����� ������� + forms ��� ����. �������
    def get_description(self, word):
        description = '' # ������ �� ����� �.�. ��� ����� word

        # ������� ���� ����� � �������
        # �������������� ��������� ����� � ������ �������
        #print word, word.lower() # ����� �� ���-���� ���� ��� ����������� :(
        all_forms = self.get_forms(to_lower(word))
        if all_forms != None:
            # ��������� ��� ������������� �����
            forms = [list(x) for x in set(tuple(x) for x in all_forms)]
            description = self.forms_toString(forms)

            # ������������ ������ ���� ����� ��� ��������������� �������
            # ��� ����� ������ ���, ����, ����, ��������
            forms_for_sint = []
            form_exists = False
            for form in forms:
                if form[0] == '�������' or form[0] == '���.' or form[0] == '����.' or form[0] == '����.':
                    if form[0] == '���.' or form[0] == '����.': form.pop(-1) # ������� ��
                    forms_for_sint.append(form)
                    form_exists = True
            if not form_exists: forms_for_sint = None
            return (description, forms_for_sint)

        # ���� � ������� ��� ������� �����:

        # ���� ��� ������� (-19�C ��� 4�F)
        if re.match(r'[+-]*\d+�[CFK���]', word):
            return ("�����������", None)

        # ���� ��� ���� 12.08.1983 ��� 31/08/11
        #if re.match(r"\d{1,2}(/.-])\d{1,2}\1\d{2}", word):
        if re.match(r"[0123]\d[.\-\\/][01]\d[.\-\\/]\d{2,4}", word):
            return ("����", None)

        # ���� ��� ����� 12.8 ��� -0,1
        if re.match(r'[+-]*\d+[.,]+\d+', word):
            return ("�������������� �����", None)

        # ���� ��� ����� -12 ��� -1
        if re.match(r'[-]\d', word):
            return ("����� ������������� �����", None)

        # ���� ��� ����� 12 ��� 1
        if re.match(r'\d', word):
            return ("����������� �����", None)

        # ���� ��� ����� 12.8 ��� 0,1 ��� -18
        # (�� ������, ���� �� ������ ��� �� �����)
        if re.match(r'[+-]*\d+[.,]*\d*', word):
            return ("�����", None)

        # ���� ��� ��� �����������
        if re.match(r'[�-�][�-�]+\w+', word):
            return ("��� �����������", None)

        # ���� ��� ��� �����������
        if re.match(r'[A-Za-z]\w+', word):
            return ("����������� �����", None)

        # ���� ��� ������ � �� �����
        description = '������������'
        return (description, None)


def add_word_to_dict(dict, word, form):
    level = dict
    for letter in word:
        if (not level.has_key(letter)):
            level[letter] = {}
        level = level[letter]
    if level.has_key('form'):
        level['form'].append(form)
    else: level['form'] = [form]

################################################################################

# ������ ������� ���������

# ������ ������ � ��������� �������:
# ���������� ����� ����; �����; ���; ��������������; �����

print "reading Zaliznyak\'s dictionary..."
start_time = time.clock()

words = []
forms = []
normal_form_noun = ""
normal_form_adj = ""
for line in open('..\\dict.txt', 'r').readlines():
    # ������ ������ �� ����������� ������� ����� ������ \n
    word, form = line.rstrip('\n').split('\t')
    form = form.split(';') # ��������, ���������� �;�.;�;��;��

    # ������� ���������� �����
    # � ����������������
    if form[0] == '�':
        # ���� ��� ���������� ����� ���������������� - �������� �
        if form[1] == '�.':
            normal_form_noun = word
            form.append("� � ���� ���������� �����")
        # ���� ��� ������������ �����, ������� � ��� ���������� :)
        else:
            form.append("�� = " + normal_form_noun)
    # � ���������������
    if form[0] == '�':
        # ���� ��� ���������� ����� ���������������� - �������� �
        if form[1] == '�.':
            normal_form_adj = word
            form.append("� � ���� ���������� �����")
        # ���� ��� ������������ �����, ������� � ��� ���������� :)
        else:
            form.append("�� = " + normal_form_adj)


    # ������������� ����������. ����� ���� ������� ������
    # ����� ����
    if form[0] != '':
        if form[0] == '�':
            form[0] = '���.'
        elif form[0] == '�':
            form[0] = '����.'
        elif form[0] == '�':
            form[0] = '����.'
    # �����
    if form[1] != '':
        if form[1] == '�.':
            form[1] = '��. �.'
        elif form[1] == '�.':
            form[1] = '���. �.'
        elif form[1] == '�.':
            form[1] = '���. �.'
        elif form[1] == '�.':
            form[1] = '���. �.'
        elif form[1] == '�.':
            form[1] = '����. �.'
        elif form[1] == '�.':
            form[1] = '�����. �.'
    # ���
    if form[2] != '':
        if form[2] == '�':
            form[2] = '���. ���'
        elif form[2] == '�':
            form[2] = '���. ���'
        elif form[2] == 'c':
            form[2] = '����. ���'
    # ��������������
    if form[3] != '':
        if form[3] == '��':
            form[3] = '����.'
        elif form[3] == '��':
            form[3] = '������.'
    # �����
    if form[4] != '':
        if form[4] == '��':
            form[4] = '��. �����'
        elif form[4] == '��':
            form[4] = '����. �����'

    words.append(word)
    forms.append(form)

print "- adding prepositions..."
for line in open('..\\prepositions.txt', 'r').readlines():
    # ������ ������ �� ����������� ������� ����� ������ \n
    #word = line.rstrip('\n')
    word, form = line.rstrip('\n').split('\t')
    words.append(word)
    forms.append(["�������", form])

print "- adding conjunctions..."
for line in open('..\\conjunctions.txt', 'r').readlines():
    # ������ ������ �� ����������� ������� ����� ������ \n
    word = line.rstrip('\n')
    words.append(word)
    forms.append(["����"])

print "- adding adverbs..."
for line in open('..\\adverbs.txt', 'r').readlines():
    # ������ ������ �� ����������� ������� ����� ������ \n
    word = line.rstrip('\n')
    #form = form.split(';')
    words.append(word)
    forms.append(["�������"])

print "- geographical names..."
for line in open('..\\geographic.txt', 'r').readlines():
    # ������ ������ �� ����������� ������� ����� ������ \n
    word = line.rstrip('\n')
    #form = form.split(';')
    words.append(word)
    forms.append(["�������������� ��������"])

for line in open('..\\other.txt', 'r').readlines():
    # ������ ������ �� ����������� ������� ����� ������ \n
    word, form = line.rstrip('\n').split('\t')
    words.append(word)
    forms.append([form])

# ��� ��� �������� ���-�� ���:
#words = ['mama', 'milk', 'moon', 'makes', 'make', 'mood', 'moon']
#forms = [ [1], [2], ['3a'], [4], [5], [6], ['3b'] ]
#{'m': {'a': {'k': {'e': {'s': {'form': [[4]]}, 'form': [[5]]}}, 'm': {'a': {'form': [[1]]}}}, 'i': {'l': {'k': {'form': [[2]]}}}, 'o': {'o': {'d': {'form': [[6]]}, 'n': {'form': [['3a'], ['3b']]}}}}}

print "creating a Tree..."
dict = {} # ���� ������
for word, form in zip(words, forms):
        add_word_to_dict(dict, word, form)

print "it took", time.clock() - start_time, "seconds"

################################################################################

# ����� � JSON

#file = open('..\\mytree.txt', 'w')
#text = file.write(dict.__str__())
#file.close()

#file = open('..\\mytree.json', 'w')
##res = json.loads(dict)
#text = file.write(json.dumps(dict.__str__().encode("utf-8")))
#file.close()

#file = open('..\\mytree.json', 'r')
#text = file.read()
##text = text.decode('utf-8')
#new_dict = json.loads(text)
#print type(new_dict)
#file.close()

# ����� � pickle

#output = open('..\\dict.pkl', 'wb')
#pickle.dump(dict, output)
#output.close()

#pkl_file = open('..\\dict.pkl', 'rb')
#dict1 = pickle.load(pkl_file)
#pkl_file.close()

################################################################################

# ������ �������� ���� � �������
file = open('..\\input.txt', 'r')
text = file.read()
file.close()

# � ����� ������ ������ ���� ������ ��� ����� ������,
# ����� �� ������ ���������� ��������� ����������� :(
text += " "
text = text.replace("�", "�")
text = text.replace("�", "-")
################################################################################

# ��������������� ������...
print "starting Parser..."
my_parser = Parser(dict, text)

#input()