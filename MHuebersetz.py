# miya.host translation manager

import json
from aiogram.types import User


# Routes to localisation files.
class TDS:
    def __init__(self, u: User = None):  # type: ignore
        langstrings = json.load(open('utilities/tds.json', 'r', encoding='utf-8'))
        errorstrings = json.load(open('utilities/etds.json', 'r', encoding='utf-8'))
        additionalstrings = json.load(open('utilities/atds.json', 'r', encoding='utf-8'))
        self.ru = langstrings['ru']
        self.en = langstrings['en']
        self.de = langstrings['de']
        self.nl = langstrings['nl']
        self.uk = langstrings['uk']
        self.es = langstrings['es']
        self.it = langstrings['it']
        self.fr = langstrings['fr']
        self.lb = langstrings['lb']
        self.tt = langstrings['tt']
        self.uz = langstrings['uz']

        self.erru = errorstrings['ru']
        self.eren = errorstrings['en']
        self.erde = errorstrings['de']
        self.ernl = errorstrings['nl']
        self.eruk = errorstrings['uk']
        self.eres = errorstrings['es']
        self.erit = errorstrings['it']
        self.erfr = errorstrings['fr']
        self.erlb = errorstrings['lb']
        self.ertt = errorstrings['tt']
        self.eruz = errorstrings['uz']

        self.aru = additionalstrings['ru']
        self.aen = additionalstrings['en']
        self.ade = additionalstrings['de']
        self.anl = additionalstrings['nl']
        self.auk = additionalstrings['uk']
        self.aes = additionalstrings['es']
        self.ait = additionalstrings['it']
        self.afr = additionalstrings['fr']
        self.alb = additionalstrings['lb']
        self.att = additionalstrings['tt']
        self.azu = additionalstrings['uz']

        self.supported = ['ru', 'en', 'de', 'nl', 'uk', 'es', 'it', 'fr', 'lb', 'tt', 'uz']

        if u:
            self.standard = json.load(open('haupt.json', 'r', encoding='utf-8'))[str(u.id)]['lang']
        else:
            self.standard = 'en'

    def get(self, name: str, lang: str = '', additional_file: str = '') -> str:
        """
        Returns the translation of the specified string.
        :param name: String name.
        :param lang: Language; may be not specified.
        :param additional_file: Additional file to search for the string.
        :return: Translation of the specified string.
        """
        if not lang:
            lang = self.standard

        if lang == 'ru':
            try:
                if additional_file == 'e':
                    return self.erru[name]
                elif additional_file == 'a':
                    return self.aru[name]
                return self.ru[name]
            except KeyError:
                return 'Перевод отсутствует.'

        elif lang == 'en':
            try:
                if additional_file == 'e':
                    return self.eren[name]
                elif additional_file == 'a':
                    return self.aen[name]
                return self.en[name]
            except KeyError:
                return 'Translation is missing.'

        elif lang == 'de':
            try:
                if additional_file == 'e':
                    return self.erde[name]
                elif additional_file == 'a':
                    return self.ade[name]
                return self.de[name]
            except KeyError:
                return 'Übersetzungszeile fehlt.'

        elif lang == 'nl':
            try:
                if additional_file == 'e':
                    return self.ernl[name]
                elif additional_file == 'a':
                    return self.anl[name]
                return self.nl[name]
            except KeyError:
                return 'Vertaling ontbreekt.'

        elif lang == 'uk':
            try:
                if additional_file == 'e':
                    return self.eruk[name]
                elif additional_file == 'a':
                    return self.auk[name]
                return self.uk[name]
            except KeyError:
                return 'Переклад відсутній.'

        elif lang == 'es':
            try:
                if additional_file == 'e':
                    return self.eres[name]
                elif additional_file == 'a':
                    return self.aes[name]
                return self.es[name]
            except KeyError:
                return 'Falta la traducción.'

        elif lang == 'it':
            try:
                if additional_file == 'e':
                    return self.erit[name]
                elif additional_file == 'a':
                    return self.ait[name]
                return self.it[name]
            except KeyError:
                return 'Traduzione mancante.'

        elif lang == 'fr':
            try:
                if additional_file == 'e':
                    return self.erfr[name]
                elif additional_file == 'a':
                    return self.afr[name]
                return self.fr[name]
            except KeyError:
                return 'Traduction manquante.'
        
        elif lang == 'lb':
            try:
                if additional_file == 'e':
                    return self.erlb[name]
                elif additional_file == 'a':
                    return self.alb[name]
                return self.lb[name]
            except KeyError:
                return 'Keng Iwwersetzung.'
        
        elif lang == 'tt':
            try:
                if additional_file == 'e':
                    return self.ertt[name]
                elif additional_file == 'a':
                    return self.att[name]
                return self.tt[name]
            except:
                return 'Тәрҗемә юк.'
        
        elif lang == 'uz':
            try:
                if additional_file == 'e':
                    return self.eruz[name]
                elif additional_file == 'a':
                    return self.azu[name]
                return self.uz[name]
            except:
                return 'Tarjima yo\'q.'

        else:
            return 'No such language.'
