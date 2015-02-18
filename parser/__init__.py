#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Vera Mazhuga http://vero4ka.info
import os
import time
import re
import itertools
from mylowercase import to_lower

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class Parser:
    def __init__(self, dict, text):
        self.dict = dict # дерево-словарь
        self.text = text # сходный текст
        self.sentences = []
        self.orig_sentences = []
        self.output_file = os.path.join(BASE_DIR, '..', 'output.html')
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
        self.output_string += "<h3>Исходный текст:</h3>\n"
        self.output_string += '<p>' + text + '</p>\n'

        print "- noting down the time..."
        start_time = time.clock()

        # Лексический анализ

        # разделить текст на предложения
        self.sentences = re.split(r'\"*\)*[.?!]+[\s\n]+', self.text)
        # оставляет в конце пустой список []
        # но это можно исправить:
        self.sentences = self.sentences[:-1]
        
        # разделить предложения на слова
        for i in range(len(self.sentences)):
            sentence = self.sentences[i]
            # удалить из предложения все скобки и запятые
            # слово, слово - слово (слово), слово: слово ("слово")
            self.sentences[i] = re.split(r'\"*\)*,*\:*\s+\-*\s*\(*\"*', sentence)

        # анализировать предложения
        sent_num = 1
        for sentence in self.sentences:
            self.output_string += "<h3>Предложение " + sent_num.__str__() + ":</h3>\n"
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

        # Морфологический анализ
        for word in sentence:
            description, all_forms = self.get_description(word)
            # вывести слово (жирненьким) + его М.Х.
            self.output_string += "<b>" + word + "</b>: " + description + "<br />\n"

            # если формы для этого слова вообще есть
            # формы есть только для слов из словаря: сущ, глаг, предл, союз...
            if all_forms != None:
                # добавим к кажд. форме слово, к кот. она относится
                for form in all_forms:
                    form.insert(0, word)
                forms_in_sentence.append(all_forms)
        
        # Синтаксический анализ
        self.output_string += "<br /><i><b>Синтаксический анализ:</b></i><br />\n"

        counter_for_versions = 1
        # просматриваем все возможные сочетания форм (декартово произведение)
        list_of_all_combinations = list(itertools.product(*forms_in_sentence))
        for mf_version in list_of_all_combinations:
            forms_are_correct = True # подходит ли нам такая форма

            # Этап I.
            # прилагательные(одно или несколько), стоящие перед существительными
            # должны согласоваться с ним по роду, пажеду и числу
            # (если это условие не выполняется, переходим к другому набору)

            NP_groups = [] # список именных групп для текущего набора форм
            is_adj = False # раньше нам попадалось прилагательное
            adj_forms = [] # список форм встретившихся нам прилагательных

            # формируем новую именную группу
            # (чтобы потом добавить в общую NP_groups)
            new_NP_group = []

            for form in mf_version: # идем по mf_version (текущий набор форм)
                # каждая form выглядит так: [ 0- само слово, 1- часть речи,
                #      2- падеж, 3- род, 4- одуш., 5- число]

                # если мы наткнулись на прилагательное
                if form[1] == 'прил.':
                    is_adj = True # запомним, что мы его встретили
                    # запомним его характеристики (падеж, род, число)
                    adj_forms.append([form[2], form[3], form[5]])
                    new_NP_group.append(form[0]) # добавляем в именную групу
                    continue # переходим к следующей form в списке
                # если мы наткнулись на существительное и перед ним было прил.
                if form[1] == 'сущ.' and is_adj:
                    is_adj = False # забываем про прилагательное
                    noun = [form[2], form[3], form[5]]
                    new_NP_group.append(form[0]) # добавляем в именную групу
                    forms_match = True # допустим, формы сущ. и прил. совпадают
                    for adj in adj_forms: # для всех прилагательных
                        # если формы не совпадают хотя бы для одного прилагательного
                        if not (adj[0] == noun[0] and adj[1] == noun[1] and adj[2] == noun[2]):
                            forms_match = False
                            adj_forms = []
                            break
                    adj_forms = [] # очистим список прилагательных
                    if not forms_match: # если формы не совпали
                        # то и все остальные формы смотреть незачем
                        forms_are_correct = False
                        new_NP_group = [] # очистим именную группу
                        continue
                    # если все хорошо, добавим группу в список именных групп
                    NP_groups.append(new_NP_group)
                    new_NP_group = []
            
            # если фромы не прошли I Этап, то переходим к новому набору форм
            if not forms_are_correct:
                continue

            # Этап II.
            # Распознаем предложные группы
            # если встречается послед-ть предлог + сущ., и модель управления
            # предлога совпадает с М.Х. сущ., то они
            # образуют предложную группу
            # (если это условие не выполняется, переходим к другому набору)

            PP_groups = [] # список предложных групп для текущего набора форм
            is_prep = False # раньше нам попадался предлог

            # формируем новую предложную группу
            # (чтобы потом добавить в общую PP_groups)
            new_PP_group = []
            prep_case = "" # падеж, в котором стоит найденный предлог

            for form in mf_version: # идем по mf_version (текущий набор форм)
                # каждая form выглядит так: [ 0- само слово, 1- часть речи,
                #      2- падеж, 3- род, 4- одуш., 5- число]
                # для предлога: [ 0- само слово, 1- часть речи, 2- падеж ]

                # если мы наткнулись на предлог
                if form[1] == 'предлог':
                    is_prep = True # запомним, что мы его встретили
                    prep_case = form[2] # запомним его падеж
                    new_PP_group.append(form[0]) # добавляем в предложную групу
                    continue # переходим к следующей form в списке
                # если мы наткнулись на существительное и перед ним был предлог
                if form[1] == 'сущ.' and is_prep:
                    is_prep = False # забываем про пердлог
                    noun_case = form[2]
                    new_PP_group.append(form[0]) # добавляем в именную групу
                    forms_match = True # допустим, падежи сущ. и предлога совпадают
                    if not prep_case == noun_case: # если падежи не совпали
                        # то и все остальные формы смотреть незачем
                        forms_are_correct = False
                        new_PP_group = [] # очистим предложную группу
                        continue
                    # если все хорошо, добавим группу в список предложных групп
                    PP_groups.append(new_PP_group)
                    new_PP_group = []

            # если фромы не прошли II Этап, то переходим к новому набору форм
            if not forms_are_correct:
                continue

            self.output_string += "<br /><i>Вариант разбора №" + counter_for_versions.__str__() + "</i>:<br />\n"
            self.output_string += self.forms_toString_V2(mf_version) + "<br />\n"

            # напчатать именные группы
            if len(NP_groups) != 0:
                self.output_string += "<br /><i>NP groups:</i><br />"
                for group in NP_groups:
                    for word in group:
                        self.output_string += word + " "
                    self.output_string += "<br />"

            # напчатать предложные группы
            if len(PP_groups) != 0:
                self.output_string += "<br /><i>PP groups:</i><br />"
                for group in PP_groups:
                    for word in group:
                        self.output_string += word + " "
                    self.output_string += "<br />"

            counter_for_versions += 1
            

    # находит список М.Х. в словаре, соответствующих слову word
    def get_forms(self, word):
        level = self.dict
        for letter in word:
            if level.get(letter):
                level = level.get(letter)
        return level.get('form')

    # приводит М.Х. в приличный вид, так чтобы их можно было вывести на экран
    # ну.. пронумеровать.. через запятую и все такое
    def forms_toString(self, forms):
        res = ""
        form_num = 1
        for form in forms:
            res += "<br />" + form_num.__str__() + "). "
            for item in form:
                if item != "": res += item + ", "
            res = res[:-2] # удалим последнюю запятую
            form_num += 1
        return res

    def forms_toString_V2(self, forms):
        res = ""
        form_num = 1
        for form in forms:
            res += "<br />" + form_num.__str__() + "). "
            for item in form:
                if item != "":
                    if item == "сущ.":
                        res += "<span style=\"color:blue\">" + item + "</span>, "
                    elif item == "глаг.":
                        res += "<span style=\"color:red\">" + item + "</span>, "
                    elif item == "прил.":
                        res += "<span style=\"color:green\">" + item + "</span>, "
                    elif item == "предлог" or item == "союз":
                        res += "<span style=\"color:gray\">" + item + "</span>, "
                    else: res += item + ", "
            res = res[:-2] # удалим последнюю запятую
            form_num += 1
        return res

    # получить все М.Х. одной строкой + forms для синт. анализа
    def get_description(self, word):
        description = '' # строка со всеми М.Х. для слова word

        # сначала ищем форму в словаре
        # предварительно перевести слово в нижний регистр
        #print word, word.lower() # какая же все-таки БЯКА эти кодировочки :(
        all_forms = self.get_forms(to_lower(word))
        if all_forms != None:
            # исключить все повторяющиеся формы
            forms = [list(x) for x in set(tuple(x) for x in all_forms)]
            description = self.forms_toString(forms)

            # сформировать список форм слова для синтаксического анализа
            # нам нужны только сущ, прил, глаг, предлоги
            forms_for_sint = []
            form_exists = False
            for form in forms:
                if form[0] == 'предлог' or form[0] == 'сущ.' or form[0] == 'глаг.' or form[0] == 'прил.':
                    if form[0] == 'сущ.' or form[0] == 'прил.': form.pop(-1) # удалить НФ
                    forms_for_sint.append(form)
                    form_exists = True
            if not form_exists: forms_for_sint = None
            return (description, forms_for_sint)

        # если в словаре нет данного слова:

        # если это градусы (-19°C или 4°F)
        if re.match(r'[+-]*\d+°[CFKСФК]', word):
            return ("температура", None)

        # если это дата 12.08.1983 или 31/08/11
        #if re.match(r"\d{1,2}(/.-])\d{1,2}\1\d{2}", word):
        if re.match(r"[0123]\d[.\-\\/][01]\d[.\-\\/]\d{2,4}", word):
            return ("дата", None)

        # если это число 12.8 или -0,1
        if re.match(r'[+-]*\d+[.,]+\d+', word):
            return ("действительное число", None)

        # если это число -12 или -1
        if re.match(r'[-]\d', word):
            return ("целое отрицательное число", None)

        # если это число 12 или 1
        if re.match(r'\d', word):
            return ("натуральное число", None)

        # если это число 12.8 или 0,1 или -18
        # (на случай, если мы раньше его не нашли)
        if re.match(r'[+-]*\d+[.,]*\d*', word):
            return ("число", None)

        # если это имя собственное
        if re.match(r'[А-Я][а-я]+\w+', word):
            return ("имя собственное", None)

        # если это имя собственное
        if re.match(r'[A-Za-z]\w+', word):
            return ("иностранное слово", None)

        # если так ничего и не нашли
        description = 'неубивайменя'
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

# читаем словарь словоформ

# Каждая статья в следующем формате:
# словоформа часть речи; падеж; род; одушевленность; число

print "reading Zaliznyak\'s dictionary..."
start_time = time.clock()

words = []
forms = []
normal_form_noun = ""
normal_form_adj = ""
print BASE_DIR, os.path.join(BASE_DIR, '..', 'dict.txt')
for line in open(os.path.join(BASE_DIR, '..', 'dict.txt'), 'r').readlines():
    # читаем строки за исключением символа конца строки \n
    word, form = line.rstrip('\n').split('\t')
    form = form.split(';') # например, вентиляция с;и.;ж;но;ед

    # добавим нормальную форму
    # к существительному
    if form[0] == 'с':
        # если это нормальная форма существительного - запомним её
        if form[1] == 'и.':
            normal_form_noun = word
            form.append("я и есть нормальная форма")
        # если это ненормальная форма, добавим к ней нормальную :)
        else:
            form.append("НФ = " + normal_form_noun)
    # к прилагательному
    if form[0] == 'п':
        # если это нормальная форма существительного - запомним её
        if form[1] == 'и.':
            normal_form_adj = word
            form.append("я и есть нормальная форма")
        # если это ненормальная форма, добавим к ней нормальную :)
        else:
            form.append("НФ = " + normal_form_adj)


    # переобозначим сокращения. чтобы было удобнее читать
    # часть речи
    if form[0] != '':
        if form[0] == 'с':
            form[0] = 'сущ.'
        elif form[0] == 'г':
            form[0] = 'глаг.'
        elif form[0] == 'п':
            form[0] = 'прил.'
    # падеж
    if form[1] != '':
        if form[1] == 'и.':
            form[1] = 'им. п.'
        elif form[1] == 'р.':
            form[1] = 'род. п.'
        elif form[1] == 'в.':
            form[1] = 'вин. п.'
        elif form[1] == 'д.':
            form[1] = 'дат. п.'
        elif form[1] == 'т.':
            form[1] = 'твор. п.'
        elif form[1] == 'п.':
            form[1] = 'предл. п.'
    # род
    if form[2] != '':
        if form[2] == 'м':
            form[2] = 'муж. род'
        elif form[2] == 'ж':
            form[2] = 'жен. род'
        elif form[2] == 'c':
            form[2] = 'сред. род'
    # одушевленность
    if form[3] != '':
        if form[3] == 'од':
            form[3] = 'одуш.'
        elif form[3] == 'но':
            form[3] = 'неодуш.'
    # число
    if form[4] != '':
        if form[4] == 'ед':
            form[4] = 'ед. число'
        elif form[4] == 'мн':
            form[4] = 'множ. число'

    words.append(word)
    forms.append(form)

print "- adding prepositions..."
for line in open(os.path.join(BASE_DIR, '..', 'prepositions.txt'), 'r').readlines():
    # читаем строки за исключением символа конца строки \n
    #word = line.rstrip('\n')
    word, form = line.rstrip('\n').split('\t')
    words.append(word)
    forms.append(["предлог", form])

print "- adding conjunctions..."
for line in open(os.path.join(BASE_DIR, '..', 'conjunctions.txt'), 'r').readlines():
    # читаем строки за исключением символа конца строки \n
    word = line.rstrip('\n')
    words.append(word)
    forms.append(["союз"])

print "- adding adverbs..."
for line in open(os.path.join(BASE_DIR, '..', 'adverbs.txt'), 'r').readlines():
    # читаем строки за исключением символа конца строки \n
    word = line.rstrip('\n')
    #form = form.split(';')
    words.append(word)
    forms.append(["наречие"])

print "- geographical names..."
for line in open(os.path.join(BASE_DIR, '..', 'geographic.txt'), 'r').readlines():
    # читаем строки за исключением символа конца строки \n
    word = line.rstrip('\n')
    #form = form.split(';')
    words.append(word)
    forms.append(["географическое название"])

for line in open(os.path.join(BASE_DIR, '..', 'other.txt'), 'r').readlines():
    # читаем строки за исключением символа конца строки \n
    word, form = line.rstrip('\n').split('\t')
    words.append(word)
    forms.append([form])

# все это выглядит как-то так:
#words = ['mama', 'milk', 'moon', 'makes', 'make', 'mood', 'moon']
#forms = [ [1], [2], ['3a'], [4], [5], [6], ['3b'] ]
#{'m': {'a': {'k': {'e': {'s': {'form': [[4]]}, 'form': [[5]]}}, 'm': {'a': {'form': [[1]]}}}, 'i': {'l': {'k': {'form': [[2]]}}}, 'o': {'o': {'d': {'form': [[6]]}, 'n': {'form': [['3a'], ['3b']]}}}}}

print "creating a Tree..."
dict = {} # наше дерево
for word, form in zip(words, forms):
        add_word_to_dict(dict, word, form)

print "it took", time.clock() - start_time, "seconds"

# читаем исходный файл с текстом
file = open(os.path.join(BASE_DIR, '..', 'input.txt'), 'r')
text = file.read()
file.close()

# в конце текста должен быть пробел или конец строки,
# иначе не сможем распознать последнее предложение :(
text += " "
text = text.replace("ё", "е")
text = text.replace("—", "-")
################################################################################

# непосредственно анализ...
print "starting Parser..."
my_parser = Parser(dict, text)
