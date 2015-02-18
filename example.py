#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Vera Mazhuga http://vero4ka.info
import os

from parser import Parser

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def main():
	# читаем исходный файл с текстом
	file = open(os.path.join(BASE_DIR, 'input.txt'), 'r')
	text = file.read().decode('utf8')
	file.close()

	# в конце текста должен быть пробел или конец строки,
	# иначе не сможем распознать последнее предложение :(
	text += u" "
	text = text.replace(u"ё", u"е")
	text = text.replace(u"—", u"-")

	# непосредственно анализ...
	print "starting Parser..."
	my_parser = Parser()
	my_parser.parse(text)

if __name__ == "__main__":
    main()