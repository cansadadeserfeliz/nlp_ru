# -*- coding: utf-8 -*-
import re
def to_lower(s):
    new_s = ""
    if re.match(r'[À-ß]', s):
        for i in range(len(s)):
            if s[i] == 'À':
                new_s += 'à'
                continue
            if s[i] == 'Á':
                new_s += 'á'
                continue
            if s[i] == 'Â':
                new_s += 'â'
                continue
            if s[i] == 'Ã':
                new_s += 'ã'
                continue
            if s[i] == 'Ä':
                new_s += 'ä'
                continue
            if s[i] == 'Å':
                new_s += 'å'
                continue
            if s[i] == '¨':
                new_s += '¸'
                continue
            if s[i] == 'Æ':
                new_s += 'æ'
                continue
            if s[i] == 'Ç':
                new_s += 'ç'
                continue
            if s[i] == 'È':
                new_s += 'è'
                continue
            if s[i] == 'Ê':
                new_s += 'ê'
                continue
            if s[i] == 'Ë':
                new_s += 'ë'
                continue
            if s[i] == 'Ì':
                new_s += 'ì'
                continue
            if s[i] == 'Í':
                new_s += 'í'
                continue
            if s[i] == 'Î':
                new_s += 'î'
                continue
            if s[i] == 'Ï':
                new_s += 'ï'
                continue
            if s[i] == 'Ð':
                new_s += 'ð'
                continue
            if s[i] == 'Ñ':
                new_s += 'ñ'
                continue
            if s[i] == 'Ò':
                new_s += 'ò'
                continue
            if s[i] == 'Ó':
                new_s += 'ó'
                continue
            if s[i] == 'Ô':
                new_s += 'ô'
                continue
            if s[i] == 'Õ':
                new_s += 'õ'
                continue
            if s[i] == 'Ö':
                new_s += 'ö'
                continue
            if s[i] == 'Ö':
                new_s += 'ö'
                continue
            if s[i] == 'Ø':
                new_s += 'ø'
                continue
            if s[i] == 'Ù':
                new_s += 'ù'
                continue
            if s[i] == 'Ý':
                new_s += 'ý'
                continue
            if s[i] == 'Þ':
                new_s += 'þ'
                continue
            if s[i] == 'ß':
                new_s += 'ÿ'
                continue
            new_s += s[i]
        return new_s

    return s

