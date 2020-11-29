# -*- coding: utf-8 -*-

import json
import re
import string
import logging
import sys
from collections import OrderedDict
from preprocess.PersianNormalizer import PersianNormalizer


class PolarityDetector(object):

    def __init__(self, logger=logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
                                                  stream=sys.stdout, level=logging.INFO)):
        self.__logger = logger
        self.__Normalizer = PersianNormalizer()
        self.__LoadStopwords()
        self.__LoadWordsDictionary()
        self.__POSETIVE_EMOJI = [':-)', '=)', ':)', '8)', ':]', '=]', '=>', '8-)', ':->', ':-]', ':”)', ':’)', ':-)',
                                 '=)',
                                 ':3',
                                 ':>', ':ˆ)', ':-3', '=>', ':->', ':-V', '=v',
                                 ':-1', 'ˆ', 'ˆ', 'ˆLˆ', 'ˆ)ˆ', ':*', ':-*', ';-)', ';)', ';-]', ';]', ';->', ';>',
                                 '%-}',
                                 '<3',
                                 ':-D', ':D', '=D', ':-P', '=3', 'xD', ':P', '=P',
                                 'O.o', 'o.O', ':v', 'B)', 'B-)', 'B|', '8|', ':’-)', ':!', ':-X', '=*', ':-*', ':*',
                                 '😀', '😃', '😄', '😁', '😆', '😅', '😐', '😳', '😎', '😺', '😸', '😹', '😻', '😼',
                                 '💋',
                                 '💪',
                                 '👀', '👁', '👅', '👄', '👶', '🙋', '😶', '😏', '🤣', '❤', '😂', '🙂', '🙃', '😉',
                                 '😊', '😇',
                                 '😍', '😘', '😗', '☺', '😚', '😙', '😋', '😛', '😜', '😝', '🙄', '👍', '💙', '🎀', '🌸'
                                 ]
        self.__NEGATIVE_EMOJI = ['- -', ':-(', ':(', ':[', ':-<', ':-[', '=(', ':-@', ':-&', ':-t', ':-z', ':<)', '}-(',
                                 ':o',
                                 ':O', ':-o', ':-O', ':-\\',
                                 ':-/', ':-.', ':\\', ':’(', ':, (', ':’-(', ':, -(', ':˜(˜˜', ':˜-(',
                                 '😟', '🙁', '😮', '😯', '😲', '😳', '😦', '😧', '😮', '😨', '😰', '😥', '😢', '😭',
                                 '😱',
                                 '😖', '😣', '😞', '😓', '😩', '😫', '😤', '😡', '😠', '👿', '💀', '☠', '💩', '👎',
                                 '😑']
        self.__EMOJI = [':-)', '=)', ':)', '8)', ':]', '=]', '=>', '8-)', ':->', ':-]', ':”)', ':’)', '=)', ':3', ':>',
                        ':ˆ)',
                        '=>', ':->', ':-V', '=v', ':-1', 'ˆ', 'ˆ', 'ˆLˆ', 'ˆ)ˆ', ':*', ':-*', ';-)', ';)', ';-]', ';]',
                        ';->',
                        ';>', '%-}', '<3', ':-D', ':D', '=D', ':-P', '=3', 'xD', ':P', '=P', 'O.o', 'o.O', ':v', 'B)',
                        'B-)',
                        'B|', '8|', ':’-)', ':!', ':-X', '=*', ':-*', ':*', '- -', ':-(', ':(', ':[', ':-<', ':-[',
                        '=(',
                        ':-@', ':-&', ':-t', ':-z', ':<)', '}-(', ':o', ':O', ':-o', ':-O', ':-\\', ':-/', ':-.', ':\\',
                        ':’(',
                        ':, (', ':’-(', ':, -(', ':˜(˜˜', ':˜-(', '🌴', '⭕', '😀', '💐', '😃', '😄', '🦖', '🌟', '🎂',
                        '😁',
                        '🎊', '📍', '😆', '😅', '🔪', ':', '🤣', '😂', '🙂', '❣', '🙃', '☘', '😉', '😊', '٪', '😇',
                        '🥰', '😍',
                        '🤩', '😘', '📘', '😗', '☺', '😚', '😙', '😋', '😛', '😜', '🤪', '💫', '🔔', '✅', '😝', '🤑',
                        '🤗',
                        '🤭', '🤫', '🖤', '🏽️', '🏼️', '🤔', '🤐', '🤨', '😐', '😑', '😶', '📥', '💣', '🍀', '🦋',
                        '💣', '📌',
                        '😏', '😒', '🙄', '📆', '😬', '🤥', '😌', '😔', '😪', '🤤', '🌒', '😴', '😷', '🤒', '🤕', '🤢',
                        '🤮',
                        '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🦌', '🥳', '😎', '🤓', '🧐', '😕', '🏻', '🚨', '😟',
                        '🙁',
                        '☹', '😮', '😯', '😲', '😳', '🥺', '😦', '😧', '🍒️', '🌶', '🍶', '😨', '😰', '😥', '😢', '😭',
                        '😱',
                        '😖', '😣', '😞', '😓', '😩', '😫', '💕', '😤', '😡', '😠', '🤬', '🏴', '🎥', '😈', '👿', '🔸',
                        '🌸',
                        '💀', '☠', '💩', '🤡', '👹', '👺', '👻', '👽', '👾', '☔', '🤖', '😺', '😸', '😹', '😻', '😼',
                        '😽',
                        '🙀', '😿', '😾', '💋', '👋', '🤚', '🖐', '💔', '✋', '🙈', '💚', '🖖', '👌', '✌', '🤞', '🤟',
                        '🤘',
                        '🔥', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝', '👍', '👎', '💜', '✊', '👊', '🤛', '🤜', '👏',
                        '🙌',
                        '👐', '🤲', '🤝', '🙏', '✍', '💅', '🤳', '🔰', '💪', '🦵', '🦶', '💥', '👂', '👃', '🧠', '🍂',
                        '🐥',
                        '🌸', '🌺', '🏾', '✨', '🦷', '🦴', '👀', '👁', '👅', '👄', '👶', '🧒', '👦', '👧', '🧑', '👱',
                        '👨',
                        '🧔', '👱', '👨', '👨', '👨', '👨', '👩', '👱', '👩', '👩', '👩', '👩', '🧓', '♦', '👴', '👵',
                        '🙍',
                        '🙍', '🙍', '🙎', '🙎', '🙎', '🙅', '🙅', '🙅', '🙆', '🙆', '🙆', '💁', '💁', '💁', '🙋', '🙋',
                        '🙋',
                        '🙇', '🙇', '🙇', '🤦', '🤦', '🤦', '🤷', '🤷', '🤷', '👨', '👩', '👨', '👩', '👨', '👩', '👨',
                        '👩',
                        '👨', '👩', '👨', '👩', '👨', '👩', '👨', '👩', '👨', '👩', '👨', '👩', '👨', '👩', '📲', '👨',
                        '👩',
                        '👨', '👩', '👨', '👩', '👨', '👩', '👨', '👩', '👮', '👮', '👮', '🍆', '🕵', '🕵', '🕵', '💂',
                        '💂',
                        '💂', '👷', '👷', '👷', '🤴', '👸', '👳', '👳', '👳', '👲', '🧕', '🤵', '👰', '🤰', '🌹', '⬇',
                        '♂',
                        '❤', '🤱', '👼', '🎅', '🤶', '💙', '🐍', '🦸', '🦸', '🦹', '🦹', '✏', '♀', '🦹', '🧙', '🧙',
                        '🧙',
                        '🧚', '🧚', '🧚', '🧛', '🧛', '➿', '🧛', '🧜', '🧜', '🧜', '🧝', '🧝', '🧝', '🧞', '🧞', '🧞',
                        '🧟',
                        '🧟', '🔴', '💆', '💆', '💆', '💇', '💇', '💇', '🚶', '🚶', '🚶', '🏃', '🏃', '🏃', '💃', '🕺',
                        '🕴',
                        '👯', '👯', '👯', '💢', '🏻', '🧖', '🧖', '🧘', '👭', '👫', '👬', '💏', '👨', '👩', '💑', '👨',
                        '👩',
                        '👪', '👨', '👨', '👨', '👨', '👨', '👨', '👨', '👨', '💙', '💛', '🔵', '⚫', '👨', '👨', '👩',
                        '👩',
                        '👩', '👩', '👩', '🔺', '👨', '👨', '👨', '👨', '👨', '👩', '👩', '👩', '👩', '👩', '🗣', '👤',
                        '👥',
                        '👣', '🧳', '🌂', '☂', '🧵', '🧶', '👓', '🕶', '🥽', '🥼', '👔', '👕', '👖', '🧣', '🧤', '🧥',
                        '🧦',
                        '👗', '👘', '👙', '👚', '👛', '👜', '👝', '🎒', '👞', '👟', '🥾', '🥿', '👠', '👡', '👢', '👑',
                        '👒',
                        '🎩', '🎓', '🧢', '⛑', '💄', '💍', '💼', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '۱',
                        '۲',
                        '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', ')',
                        '_',
                        '+', '=', '-', '|', '|', '}', '{', '[', ']', ':', ':', ',', '.', '<', '/', '?', '؟', '>', 'ً',
                        'ٌ',
                        '،']
        self.__AlphabetList = "ابپتتثجچحخدذرزسشصضطظعغفقکگلمنوهیآآئأؤژيپۀۀةؤيؤإأء:-) =) :) 8) :] =] => 8-) :-> :-] :”) :’) =) :3 :> :ˆ) => :-> :-V =v :-1 ˆ ˆ ˆLˆ ˆ)ˆ :* :-* ;-) ;) ;-] ;] ;-> ;> %-} <3 :-D :D =D :-P =3 xD :P =P O.o o.O :v B) B-) B| 8| :’-) :! :-X =* :-* :*- - :-( :( :[ :-< :-[ =( :-@ :-& :-t :-z :<) }-( :o :O :-o :-O :-\\:-/ :-. :\\ :’( :, ( :’-( :, -( :˜(˜˜ :˜-(🌴⭕😀💐😃😄🦖🌟🎂😁🎊📍😆😅🔪:🤣😂🙂❣🙃☘😉😊٪😇🥰😍🤩😘📘😗☺😚😙😋😛😜🤪💫🔔✅😝🤑🤗🤭🤫🖤🏽️🏼️🤔🤐🤨😐😑😶📥💣🍀🦋💣📌😏😒🙄📆😬🤥😌😔😪🤤🌒😴😷🤒🤕🤢🤮🤧🥵🥶🥴😵🤯🤠🦌🥳😎🤓🧐😕🏻🚨😟🙁☹😮😯😲😳🥺😦😧🍒️🌶🍶😨😰😥😢😭😱😖😣😞😓😩😫💕😤😡😠🤬🏴🎥😈👿🔸🌸💀☠💩🤡👹👺👻👽👾☔🤖😺😸😹😻😼😽🙀😿😾💋👋🤚🖐💔✋🙈💚🖖👌✌🤞🤟🤘🔥🤙👈👉👆🖕👇☝👍👎💜✊👊🤛🤜👏🙌👐🤲🤝🙏✍💅🤳🔰💪🦵🦶💥👂👃🧠🍂🐥🌸🌺🏾✨🦷🦴👀👁👅👄👶🧒👦👧🧑👱👨🧔👱👨👨👨👨👩👱👩👩👩👩🧓♦👴👵🙍🙍🙍🙎🙎🙎🙅🙅🙅🙆🙆🙆💁💁💁🙋🙋🙋🙇🙇🙇🤦🤦🤦🤷🤷🤷👨👩👨👩👨👩👨👩👨👩👨👩👨👩👨👩👨👩👨👩👨👩📲👨👩👨👩👨👩👨👩👨👩👮👮👮🍆🕵🕵🕵💂💂💂👷👷👷🤴👸👳👳👳👲🧕🤵👰🤰🌹⬇♂❤🤱👼🎅🤶💙🐍🦸🦸🦹🦹✏♀🦹🧙🧙🧙🧚🧚🧚🧛🧛➿🧛🧜🧜🧜🧝🧝🧝🧞🧞🧞🧟🧟🔴💆💆💆💇💇💇🚶🚶🚶🏃🏃🏃💃🕺🕴👯👯👯💢🏻🧖🧖🧘👭👫👬💏👨👩💑👨👩👪👨👨👨👨👨👨👨👨💙💛🔵⚫👨👨👩👩👩👩👩🔺👨👨👨👨👨👩👩👩👩👩🗣👤👥👣🧳🌂☂🧵🧶👓🕶🥽🥼👔👕👖🧣🧤🧥🧦👗👘👙👚👛👜👝🎒👞👟🥾🥿👠👡👢👑👒🎩🎓🧢⛑💄💍💼1234567890۱۲۳۴۵۶۷۸۹۰!@#$%^&*())_+=-||}{[]::.</?؟>ًٌ،"

    def __LoadStopwords(self):
        try:
            with open("preprocess/resources/polarity_stopword.txt", 'r', encoding='utf-8') as file_reader:
                Stopwords = file_reader.readlines()
                self.__StopWords = list()
            for word in Stopwords:
                word = word.strip()
                self.__StopWords.append(word)
        except Exception as e:
            self.__logger.error("Polarity StopWords Loading error, EX: " + str(e))

    def __LoadWordsDictionary(self):
        self.__WordsDict = dict()
        try:
            with open('preprocess/resources/polarity_dict.json', encoding='utf-8') as json_file:
                self.__WordsDict = json.load(json_file)
        except Exception as e:
            self.__logger.error("Polarity Words Dictionary Loading error, EX: " + str(e))

    def __persian_word_extractor(self, text):
        WORD = re.compile(r'\w+')
        ESentance = list()
        for word in WORD.findall(text):
            ExWord = ''
            EWord = list()
            Word = list(word)
            for Char in Word:
                if Char in self.__AlphabetList:
                    ExWord = ExWord + Char
                else:
                    if ExWord != '':
                        EWord.append(ExWord)
                    ExWord = ''
            if ExWord != '':
                EWord.append(ExWord)
            ESentance.extend(EWord)
        ESentance = [x + ' ' for x in ESentance]
        ESentance = ''.join(ESentance)
        return ESentance

    def Detect(self, text):
        polarity_lable = 'z'
        sent_score = 0
        word_count = 1
        try:
            sen = self.__Normalizer.clean_sentence(text)
            Normsen = self.__persian_word_extractor(sen)
            posetiveEmoji = [value for value in self.__POSETIVE_EMOJI if value in sen]
            posetive_count = len(posetiveEmoji)
            negativemoji = [value for value in self.__NEGATIVE_EMOJI if value in sen]
            negative_count = len(negativemoji)
            if (posetive_count > negative_count):
                sent_score = 1
            elif (posetive_count < negative_count):
                sent_score = -1
            else:
                Words = re.sub('[' + string.punctuation + ']', ' ', Normsen).split()
                CListWord = list()
                for word in Words:
                    word = "".join(OrderedDict.fromkeys(word))
                    for emoji in self.__EMOJI:
                        if emoji in word:
                            word = word.replace(emoji, '')
                            CListWord.append(emoji)
                    CListWord.append(word)
                Words = filter(lambda a: a != '', CListWord)
                for word in Words:
                    if word in self.__WordsDict and word not in self.__StopWords and not word.__contains__("http"):
                        if self.__WordsDict[word][0] > 0 or self.__WordsDict[word][1] > 0:
                            word_count = word_count + 1
                            word_sum = self.__WordsDict[word][0] + self.__WordsDict[word][1]
                            word_score = (self.__WordsDict[word][0] * 0.22 - self.__WordsDict[word][
                                1] * 0.78) / word_sum
                            sent_score = sent_score + word_score
                try:
                    sent_score = sent_score / word_count
                except:
                    sent_score = 0
            if sent_score == 0:
                polarity_lable = 'z'
            if sent_score > 0.11:
                polarity_lable = 'p'
            elif sent_score < 0.086:
                polarity_lable = 'n'
        except Exception as err:
            self.__logger.error("Polarity Detector Exception")
            self.__logger.error("Casuse: %s" % err)
        return {'lable': polarity_lable, 'score': sent_score}


if __name__ == '__main__':
    texts = ['چه حس قشنگی و زیبایی دارم امروز', 'بیخیال رفیق', 'کار بسیار خوبییه',
             'سلام من امروز حالم خیلی بده و داغونم']
    pl = PolarityDetector()
    for txt in texts:
        resp = pl.Detect(txt)
        print('Text: {}\n{}\n===========================================\n'.format(txt, resp))
