import json
import random
import re
import string
import os
import gender_guesser.detector as gender
import requests
import jdatetime
import datetime
from imageProcessor import ImageAnalyzer
from emoji_extractor.extract import Extractor


class GenderFinder:
    def __init__(self, user_data):
        self.female_words = (
            'دختر', 'دختران', 'زن', 'زنان', 'ملکه', 'خانوم', 'girl', 'girls', 'women', 'queen', 'dokhtar', 'zan',
            'بانو',
            'banoo', 'بانوان', 'khanoom', 'dokhtaran', 'zan', 'zanan', 'malake')
        self.male_words = (
            'مرد', 'پسر', 'پسران', 'مردان', 'پادشاه', 'king', 'boys', 'man', 'آقا', 'agha', 'mard', 'padeshah', 'shah',
            'pesar', 'pesaran', 'mardan', 'aqa')
        self.gender_detector = gender.Detector()
        self.api_url = "https://genderapi.io/api/?name={0}&key={1}"
        self.api_key = '5ee72d41756fae68974f3bc2'
        self.female_emoji = frozenset({
            "😘", "🙅", "🙆", "🙋", "🙍", "🙎", "☔", "🍑", "🍓", "👄", "👗", "👙", "👚", "👛", "👝", "👠", "👡", "👢",
            "👧", "👩", "👩", "👯", "👰", "👵", "👸", "💁", "💃", "💄", "💅", "💆", "💇", "💋", "💖", "💕", "😊",
            "🌷🌷", "🌸", "🌹", "🌺", "🌻", "🌼", "❤", "♥"
        })
        self.male_emoji = frozenset({
            "😤", "🙇", "🚶", "🎅", "🏃", "👕", "👦", "👨", "👮", "👱", "👲", "👳", "👴", "👷", "👺", "👿", "💂", "🔪",
            "🔧", "🔫", "👑", "👔", "🔥", "💣"
        })
        self.__function_weights = {'find_by_fullname': .90, 'find_by_username': .85, 'find_by_text': .65,
                                   'find_by_image': .50, 'find_by_emoji': .07, 'posts_text': .40}

        self.genders_dict = {"female": .0, "male": .0}

        self.user_data = user_data

    def randomString(self, stringLength=8):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def findWholeWord(self, w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    def find_by_fullname(self, full_name):
        if full_name is not None:
            splited_name = full_name.lower().split(' ')
            first_name = splited_name[0]
            # last_name = splited_name[1].capitalize()
            gender = self.gender_detector.get_gender(first_name)
            fem_list = []
            mal_list = []
            if gender is 'unknown':
                with open('preprocess/female_persian_names', 'r') as f:
                    for line in f:
                        name = line.strip()
                        if self.findWholeWord(name)(full_name.lower()):
                            fem_list.append(name)
                with open('preprocess/female_finglish_names', 'r') as f:
                    for line in f:
                        name = line.strip()
                        if self.findWholeWord(name)(full_name.lower()):
                            fem_list.append(name)
                with open('preprocess/male_persian_names', 'r') as f:
                    for line in f:
                        name = line.strip()
                        if self.findWholeWord(name)(full_name.lower()):
                            mal_list.append(name)
                with open('preprocess/male_finglish_names', 'r') as f:
                    for line in f:
                        name = line.strip()
                        if self.findWholeWord(name)(full_name.lower()):
                            mal_list.append(name)
                if fem_list.__len__() is not 0 or mal_list.__len__() is not 0:
                    return "male" if ''.join(fem_list).__len__() < ''.join(mal_list).__len__() else 'female'
        return "unknown"

    def find_by_name_api(self, name):
        try:
            splited_name = name.split(' ')
            first_name = splited_name[0].capitalize()
            return json.loads(requests.get(url=self.api_url.format(first_name, self.api_key)).text)['gender']
        except:
            pass

    @staticmethod
    def clean_username(username):
        while True:
            if not username.__len__() > 1:
                return
            if not username[0].isalpha() or username[0] == username[1]:
                username = username[1:]
            if not username[-1].isalpha() or username[-1] == username[-2]:
                username = username[:-1]
            if username[0].isalpha() and username[-1].isalpha() and \
                    not username[0] == username[1] and not username[-1] == username[-2]:
                break
        return username

    def name_extractor(self, cleaned_username):
        fem_name, mal_name = str(), str()
        with open('preprocess/female_finglish_names', 'r') as f:
            for line in f:
                name = line.strip()
                if cleaned_username and cleaned_username.startswith(name):
                    fem_name = name
                elif cleaned_username and cleaned_username.endswith(name):
                    fem_name = name
        with open('preprocess/male_finglish_names', 'r') as f:
            for line in f:
                name = line.strip()
                if cleaned_username and cleaned_username.startswith(name):
                    mal_name = name
                elif cleaned_username and cleaned_username.endswith(name):
                    mal_name = name
        if not fem_name and not mal_name:
            return
        return "female" if fem_name.__len__() != 0 else "male"

    def find_by_username(self, username):
        cleaned_username = self.clean_username(username)
        gen = self.name_extractor(cleaned_username)
        if not gen:
            regex = re.compile('[^a-zA-Z]')
            username_list = regex.split(cleaned_username)
            for name in username_list:
                gen = self.name_extractor(self.clean_username(name))
                if gen:
                    return gen
            return
        return gen

    def find_by_username_old(self, username):
        regex = re.compile('[^a-zA-Z]')
        cleaned_username = regex.sub('', username)
        fem_list = []
        mal_list = []
        with open('preprocess/female_finglish_names', 'r') as f:
            for line in f:
                name = line.strip()
                if name in cleaned_username:
                    fem_list.append(name)
        with open('preprocess/male_finglish_names', 'r') as f:
            for line in f:
                name = line.strip()
                if name in cleaned_username:
                    mal_list.append(name)

                    return 'male'
        if fem_list.__len__() is not 0 or mal_list.__len__() is not 0:
            return "male" if ''.join(fem_list).__len__() < ''.join(mal_list).__len__() else 'female'
        return "unknown"

    def find_by_text(self, text):
        for word in self.female_words:
            fem_w = re.search(word, text)
            if fem_w and fem_w.lastgroup:
                return 'female'
        for word in self.male_words:
            ma_w = re.search(word, text)
            if ma_w and ma_w.lastgroup:
                return 'male'
        else:
            return 'unknown'

    def find_by_image(self, image_url):
        img = requests.get(image_url, allow_redirects=True)
        f_name = 'user_images/image_1.jpg'
        open(f_name, 'wb').write(img.content)
        ia = ImageAnalyzer(f_name)
        gender = ia.gender_identifier()
        os.remove(f_name)
        return gender

    def find_by_emoji(self, text):
        counter = Extractor().count_emoji(text)

        for key, value in counter.items():
            if key in self.female_emoji:
                self.genders_dict['female'] += value / 100
            if key in self.male_emoji:
                self.genders_dict['male'] += value / 100
        return self.genders_dict

    def recognize_gender(self):
        is_male_dict = {}
        is_female_dict = {}
        gender_1 = self.find_by_fullname(self.user_data['fullname'])
        gender_2 = self.find_by_username(self.user_data['username'])
        gender_3 = self.find_by_text(self.user_data['user_bio'])
        gender_4 = list(self.find_by_image(self.user_data['image']))
        gender_5 = self.find_by_emoji(self.user_data['user_bio'])
        self.genders_dict = {"female": .0, "male": .0}

        for post in self.user_data['posts']:
            if post:
                gender_t = self.find_by_text(post)
                self.find_by_emoji(post)
                if gender_t is not "unknown":
                    self.genders_dict[gender_t] += 0.20

        if gender_1 == 'male':
            is_male_dict['find_by_fullname'] = 'male'
        elif gender_1 == 'female':
            is_female_dict['find_by_fullname'] = 'female'

        if gender_2 == 'male':
            is_male_dict['find_by_username'] = 'male'
        elif gender_2 == 'female':
            is_female_dict['find_by_username'] = 'female'

        if gender_3 == 'male':
            is_male_dict['find_by_text'] = 'male'
        elif gender_3 == 'female':
            is_female_dict['find_by_text'] = 'female'

        if 'Male' in gender_4:
            is_male_dict['find_by_image'] = 'male'
        elif 'Female' in gender_4:
            is_female_dict['find_by_image'] = 'female'
        for key, value in gender_5.items():
            if value is not 0:
                if key == 'male':
                    is_male_dict['find_by_emoji'] = key
                else:
                    is_female_dict['find_by_emoji'] = key
        male_weight = sum(
            [self.__function_weights[m_key] for m_key in is_male_dict.keys()] + [self.genders_dict['male']])
        female_weight = sum(
            [self.__function_weights[m_key] for m_key in is_female_dict.keys()] + [self.genders_dict['female']])
        male_total_weight = male_weight / is_male_dict.__len__()
        female_total_weight = female_weight / is_female_dict.__len__()
        if male_total_weight > female_total_weight:
            return "male", "{:.2f}".format(male_total_weight * 100)
        elif female_total_weight > male_total_weight:
            return "female", "{:.2f}".format(female_total_weight * 100)
        else:
            return "unknown", 0

        # total_weight = male_weight - female_weight
        # if total_weight > 0:
        #     return "male", male_weight / is_male_dict.__len__()
        # elif total_weight < 0:
        #     return "female", female_weight / is_female_dict.__len__()


class AgeFinder:
    def __init__(self, user_data):
        self.user_data = user_data
        self.education_words = {
            'کارشناسی': (18, 24), 'ارشد': (22, 25), 'Master': (26, 40), 'Bachelor': (22, 26), 'B.A': (21, 25),
            'M.A': (26, 33), 'M.s': (33, 40), 'B.sc': (18, 24), 'دکترای': (32, 45), 'دکتری': (32, 45),"دکتر":(32,45),
            'مهندسی': (18, 25), 'مهندس': (21, 30), "دانشجوی": (18, 22),
            'متخصص': (32,45), 'engineering': (18, 24), 'engineer': (21, 27), 'ph.D': (28, 40), 'PHD': (28, 40),"Chief":(35,45 )}
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


# print(a.__str__())
imh = "https://instagram.fgbb2-2.fna.fbcdn.net/v/t51.2885-19/s320x320/91151258_1928462067287897_4041720699784527872_n.jpg?_nc_ht=instagram.fgbb2-2.fna.fbcdn.net&_nc_ohc=-YgQPhBZVF0AX-XnbY9&oh=719f12270f6eb5fb36b299ae6da8c189&oe=5F2350E4"
user_data = {'fullname': 'علی.کارگر',
             'username': '__r_aali_kargarrrrr_97',
             'user_bio': "svsdv 76-01-01 saaaaaa",
             'image': imh, 'posts': {"کارشناسی", "پادشاه دنیا"}
             }
# a = GenderFinder(user_data)
# print(a.recognize_gender())
# b = AgeFinder(user_data)
# print(b.get_age_birth())
# print(b.recognize_age())
# print(a.find_by_fullname("بهنام خالندی"))
# print(a.find_by_fullname("بهنام خالندی"))
# print(a.find_by_username("behnam.khalandi9538"))
# print(a.find_by_emoji('\ud83d\udeb6\ud83d\udeb6'))
# ay=a.find_by_username(username="alikargar_1357")
# print("\ud83d\udc97Basketball \n.\n.\n.\n\u062d\u0627\u0635\u0644 \u0627\u062e\u0631\u06cc\u0646 \u062f\u0631\u06af\u06cc\u0631\u06cc \u0642\u0644\u0628\u0648\ud83d\udc99\n\u0645\u063a\u0632 \ud83d\udeb7\u0645\u0646\n\u06cc\u0647 \u0627\u0634\u062a\u0628\u0627\u0647 \u062e\u0648\u0628 \u0628\u0648\u062f \ud83d\udcab\n.\n.\n.\n.\n.#021_")
# # print(a.year_to_age(ay[0], ay[1]))
# title = '''Welcome to my page
# 25.january.2000. #bahman
# computer engineering student at Lu'''
#
# print(a.get_age_birth('20-10-1376 تولد'))
