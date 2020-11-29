import json
import random
import re

import os

import requests
import jdatetime
import datetime
from imageProcessor import ImageAnalyzer

class AgeFinder:
    def __init__(self, **kwargs):
        self.user_data = kwargs.pop('user_data', None)
        self.education_words = {
            'کارشناسی': (18, 24), 'ارشد': (22, 25), 'Master': (26, 40), 'Bachelor': (22, 26), 'B.A': (21, 25),
            'M.A': (26, 33), 'M.s': (33, 40), 'B.sc': (18, 24), 'دکترای': (32, 45), 'دکتری': (32, 45), "دکتر": (32, 45),
            'مهندسی': (18, 25), 'مهندس': (21, 30), "دانشجوی": (18, 22),
            'متخصص': (32, 45), 'engineering': (18, 24), 'engineer': (21, 27), 'ph.D': (28, 40), 'PHD': (28, 40),
            "Chief": (35, 45)}
        self.birth_words = ('متولد', 'تولد', 'born', 'birth', 'birthday', 'day', 'month', 'year')
        self.fa_jalali_months = frozenset({
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'})
        self.en_jalali_months = frozenset({
            'farvardin', 'ordibehesht', 'khordad', 'tir', 'mordad', 'shahrivar', 'mehr', 'aban', 'azar', 'dey',
            'bahman',
            'esfand'})
        self.miladi_months = frozenset({
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
            'november',
            'december'})
        self.miladi_months_code = frozenset({
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec'})

        self.age_definer = ('years', 'old', 'year')
        self.__function_weights = {'check_username': .70, 'get_age_birth': .90, 'get_age_edu': .75,
                                   'check_month_text': .85, 'find_by_image': .40}
        self.__function_weights_posts = {'check_username': .69, 'get_age_birth': .79, 'get_age_edu': .74,
                                         'check_month_text': .84, 'find_by_image': .39}
        self.persian_numbers = ('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')

    def text_normalizer(self, text):
        normal_text = text
        for index, i in enumerate(self.persian_numbers):
            if i in text:
                normal_text = normal_text.replace(i, str(index))
        return normal_text

    def check_username(self, username):
        en_year = re.findall("[1-3][09][0-9]{2}", username)
        if en_year.__len__() > 0:
            age = self.year_to_age(en_year[0], 0)
            return age if 13 <= age < 90 else None
        else:
            fa_year = re.findall("[1][34][0-9]{2}", username)
            if fa_year.__len__() > 0:
                age = self.year_to_age(fa_year[0], 1)
                return age if 13 <= age < 90 else None
        return

    @staticmethod
    def year_to_age(year, cal_type=0):
        """ calculating age of user,type get 2 param [0,1],0 is gregorian and 1 in jalali """
        try:
            assert (cal_type in [0, 1])
            if cal_type == 0:
                age = datetime.datetime.now().year - int(year)
                return age
            else:
                age = jdatetime.datetime.now().year - int(year)
                return age
        except AssertionError:
            print('enter a valid number[0,1]!')

    def date_to_age(self, date, cal_type=0):
        """ calculating age of user,type get 2 param [0,1],0 is gregorian and 1 in jalali """
        if cal_type == 1:
            age = jdatetime.datetime.now().year - date
        else:
            age = datetime.datetime.now().year - date
        return age

    def get_age_birth(self, text):
        text = self.text_normalizer(text)
        gregorian_date_regex = {
            '%d-%m-%Y': '([0-3]{0,1}[0-9]\-[0-1]{0,1}[0-9]\-[1-3][09][0-9]{2})',
            '%d/%m/%Y': '([0-3]{0,1}[0-9]\/[0-1]{0,1}[0-9]\/[1-3][09][0-9]{2})',
            '%Y-%m-%d': '([1-3][09][0-9]{2}\-[0-1]{0,1}[0-9]\-[0-3]{0,1}[0-9])',
            '%Y/%m/%d': '([1-3][09][0-9]{2}\/[0-1]{0,1}[0-9]\/[0-3]{0,1}[0-9])',
            '%m-%d-%Y': '([0-1]{0,1}[0-9]\-[0-3]{0,1}[0-9]\-[1-3][09][0-9]{2})',
            '%m/%d/%Y': '([0-1]{0,1}[0-9]\/[0-3]{0,1}[0-9]\/[1-3][09][0-9]{2})',
            '%Y-%d-%m': '([1-3][09][0-9]{2}\-[0-3]{0,1}[0-9]\-[0-1]{0,1}[0-9])',
            '%Y/%d/%m': '([1-3][09][0-9]{2}\/[0-3]{0,1}[0-9]\/[0-1]{0,1}[0-9])'}
        jalali_date_regex = {
            '%d-%m-%Y': '([0-3]{0,1}[0-9]\-[0-1]{0,1}[0-9]\-[1][34][0-9]{2})',
            '%d/%m/%Y': '([0-3]{0,1}[0-9]\/[0-1]{0,1}[0-9]\/[1][34][0-9]{2})',
            '%Y-%m-%d': '([1][34][0-9]{2}\-[0-1]{0,1}[0-9]\-[0-3]{0,1}[0-9])',
            '%Y/%m/%d': '([1][34][0-9]{2}\/[0-1]{0,1}[0-9]\/[0-3]{0,1}[0-9])',
            '%y/%m/%d': '([0-9]{2}\/[0-1]{0,1}[0-9]\/[0-3]{0,1}[0-9])',
            '%y-%m-%d': '([0-9]{2}\-[0-1]{0,1}[0-9]\-[0-3]{0,1}[0-9])',
            '%m-%d-%Y': '([0-1]{0,1}[0-9]\-[0-3]{0,1}[0-9]\-[1][34][0-9]{2})',
            '%m/%d/%Y': '([0-1]{0,1}[0-9]\/[0-3]{0,1}[0-9]\/[1][34][0-9]{2})',
            '%Y-%d-%m': '([1][34][0-9]{2}\-[0-3]{0,1}[0-9]\-[0-1]{0,1}[0-9])',
            '%Y/%d/%m': '([1][34][0-9]{2}\/[0-3]{0,1}[0-9]\/[0-1]{0,1}[0-9])',
        }
        # if any(word in text for word in self.birth_words):
        for rx in gregorian_date_regex:
            birthday = re.findall(gregorian_date_regex[rx], text)
            if birthday:
                date = datetime.datetime.strptime(birthday[0], rx).year
                return self.date_to_age(date, cal_type=0)
        for rx in jalali_date_regex:
            birthday = re.findall(jalali_date_regex[rx], text)
            if birthday:

                if rx == '%y/%m/%d':
                    birthday = "13" + birthday[0]
                    rx = '%Y/%m/%d'
                elif rx == '%y-%m-%d':
                    birthday = "13" + birthday[0]
                    rx = '%Y-%m-%d'
                else:
                    birthday = birthday[0]
                date = datetime.datetime.strptime(birthday, rx).year
                return self.date_to_age(date, cal_type=1)

    def get_age_edu(self, text):
        for key, value in self.education_words.items():
            if key in text:
                return value
        return

    def find_year(self, text, cal_type=0):
        """ 0 if for gregorian and 1 is for jalali"""
        if cal_type == 0:
            g_year = re.findall('[1-3][09][0-9]{2}', text)
            if g_year:
                return g_year[0]
        else:
            j_year = re.findall('[1][34][0-9]{2}', text)
            if j_year:
                return j_year[0]
        return

    def find_day(self, text):
        day = re.findall('[1-3]{0,1}[0-9]', text)
        if day:
            return day[0]
        return

    def check_month_text(self, text):
        """ 1 is for jalali and 0 is for gregorian """
        text = self.text_normalizer(text)

        for month in self.miladi_months.union(self.miladi_months_code):
            if re.search(r'\b' + month + r'\b', text):
                year = self.find_year(text, cal_type=0)
                # day = self.find_day(text)
                if not year:
                    return
                return self.date_to_age(int(year), 0)
        for month in self.en_jalali_months.union(self.fa_jalali_months):
            if re.search(r'\b' + month + r'\b', text):
                year = self.find_year(text, cal_type=1)
                # day = self.find_day(text)
                if not year:
                    return
                return self.date_to_age(int(year), 1)
        return

    def find_by_image(self, image_url):
        img = requests.get(image_url, allow_redirects=True)
        f_name = 'user_images/image_1.jpg'
        open(f_name, 'wb').write(img.content)
        ia = ImageAnalyzer(f_name)
        age = ia.age_identifier()
        os.remove(f_name)
        return age

    def _check_age(self, post_caption=None):
        dict_recognized = dict()
        if not post_caption:
            age_1 = self.check_username(self.user_data['username'])
            age_2 = self.get_age_birth(self.user_data['user_bio'])
            age_3 = self.get_age_edu(self.user_data['user_bio'])
            age_4 = self.check_month_text(self.user_data['user_bio'])
        else:
            age_1 = self.check_username(post_caption)
            age_2 = self.get_age_birth(post_caption)
            age_3 = self.get_age_edu(post_caption)
            age_4 = self.check_month_text(post_caption)
        total_percent = 0
        if age_1:
            dict_recognized['check_username'] = age_1
            total_percent += self.__function_weights['check_username']
        if age_2:
            dict_recognized['get_age_birth'] = age_2
            total_percent += self.__function_weights['get_age_birth']
        if age_3:
            dict_recognized['get_age_edu'] = age_3
            total_percent += self.__function_weights['get_age_edu']

        if age_4:
            dict_recognized['check_month_text'] = age_4
            total_percent += self.__function_weights['check_month_text']
        return dict_recognized, total_percent

    def recognize_age(self):
        age_5 = list(self.find_by_image(self.user_data['image']))
        dict_recognized, total_percent = self._check_age()
        posts_keys = dict()
        if age_5.__len__() > 0 and age_5 is not "unknown":
            dict_recognized['find_by_image'] = age_5
            total_percent += self.__function_weights['find_by_image']
        for index, post in enumerate(self.user_data['posts']):
            dict_recognized_1, total_percent_2 = self._check_age(post)

            for key, value in dict_recognized_1.items():
                dict_recognized[key + str(index)] = value
                posts_keys.update({key + str(index): self.__function_weights_posts[key]})
                total_percent += total_percent_2
        avg_percent = total_percent / dict_recognized.__len__() if dict_recognized.__len__() is not 0 else 0
        values_list = []
        for key in dict_recognized.keys():
            if key[-1].isnumeric():
                values_list.append(self.__function_weights_posts[''.join([i for i in key if not i.isdigit()])])
            else:
                values_list.append(self.__function_weights[key])
        main_age = None
        if values_list.__len__() is not 0:
            max_value = max(values_list)
            for key, value in self.__function_weights.items():
                if value == max_value:
                    main_age = dict_recognized[key]
            if not main_age:
                for key, value in posts_keys.items():
                    if value == max_value:
                        main_age = dict_recognized[key]
        return main_age if main_age else "unknown", "{:.2f}".format(avg_percent * 100)

