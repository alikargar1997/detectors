import json
import random
import re
import string
import os
import gender_guesser.detector as gender
import requests
from imageProcessor import ImageAnalyzer
from emoji_extractor.extract import Extractor
from langdetect import detect
import jdatetime
import datetime
import ast


class Detector(object):
    """ Abstract class for detector classes """
    
    def detect(self):
        """
        Raises:
            AssertionError -- developer has to override this method
        """
        assert AssertionError("override this method")


class GenderFinder(Detector):
    """ Detect gender of Instagram users."""
    
    def __init__(self, **kwargs):
        """
        class initialization to predefine args and attributes.

        Keyword Args:
            **kwargs: this must contain a dict in format and vars: user_data = {'fullname':fullname ,
                            'username':username ,
                            'user_bio':user_bio ,
                            'image': profile_pic_url,
                            'posts': list of caption of the posts : ['str','str',...]
                         }
        """
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

        self.user_data = kwargs.pop('user_data', None)

    def randomString(self, stringLength=8):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def findWholeWord(self, w):
        """
        Find a single word or a string composed of multiple single words in a given string.

        Args:
            w (str): word to find in string.

        Returns:
            func: a function object with a string argument.
        """
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    def find_by_fullname(self, full_name):
        """
        Search in pre processed files and detect gender by fullname of the user.

        Args:
            full_name (str): user's fullname

        Returns:
            [str] : 'male' , 'female' or 'unknown' detected by function
        """
        if full_name is not None:
            splited_name = full_name.lower().split(' ')
            first_name = splited_name[0]
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
        """
        Normalize username by removing numbers and repetitive characters from start and end of username.

        Args:
            username (str): username of user

        Returns:
            [str]: cleaned username
        """
        while True:
            if not username.__len__() > 1:
                return
            try:
                if not username[0].isalpha() or username[0] == username[1]:
                    username = username[1:]
                if not username[-1].isalpha() or username[-1] == username[-2]:
                    username = username[:-1]
                if username[0].isalpha() and username[-1].isalpha() and \
                        not username[0] == username[1] and not username[-1] == username[-2]:
                    break
            except IndexError:
                return None
        return username

    def name_extractor(self, cleaned_username):
        """
        Compare start and end of username with pre processed names to detect gender.

        Args:
            cleaned_username (str): normalized username

        Returns:
            [str]: 'male','female' or None
        """
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
        """
        Detect gender by username.

        Args:
            username (str): user's username

        Returns:
            [str]: result of name_extractor function.

        """
        cleaned_username = self.clean_username(username)
        if not cleaned_username:
            return
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
        """
        Search in text for initialized lists of the words depended to males and females genders

        Args:
            text (str): biography, caption of posts , etc.

        Returns:
            [str]: male,female or unknown

        """
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
        """
        Detect by image of user,it downloads the image and detect by ImageAnalyzer class.

        Args:
            image_url (str): url of image.

        Returns:
            [str]: male,female or unknown.

        """
        img = requests.get(image_url, allow_redirects=True)
        f_name = 'user_images/image_1.jpg'
        open(f_name, 'wb').write(img.content)
        ia = ImageAnalyzer(f_name)
        gender = ia.gender_identifier()
        os.remove(f_name)
        return gender

    def find_by_emoji(self, text):
        """
        detect by emojies used by user in bio,post's caption,etc.
         emojies depended to the different genders are defined in initialization.

        Args:
            text (str): biography,post's caption,etc.

        Returns:
            [dict]: dict of genders with their score. ex: {'male':.2,'female':.8}
        """
        counter = Extractor().count_emoji(text)

        for key, value in counter.items():
            if key in self.female_emoji:
                self.genders_dict['female'] += value / 100
            if key in self.male_emoji:
                self.genders_dict['male'] += value / 100
        return self.genders_dict

    def detect(self):
        """
        Main detect function,
        this function collect all other function and append them to a dict,
        each key of the dict are assigned to a function of detecting functions,
        the values are also string of 'male','female' or 'unknown'.
        there is another dict that defined in initialization,
        the dict contains keys that assigned to the functions and values that are scores of each function.
        in this method gets sum of all scores of males and females seperately,and gets the max of them.
        the max value is the gender and score of trust of the operations.

        Returns:
            [tuple] (str,float): first param is 'gender' and second one in 'score of trust'.
        """
        is_male_dict = {}
        is_female_dict = {}
        gender_1 = self.find_by_fullname(self.user_data['user_full_name'])
        gender_2 = self.find_by_username(self.user_data['user_name'])
        gender_3 = self.find_by_text(self.user_data['user_bio']) if 'user_bio' in self.user_data else "unknown"
        gender_4 = list(self.find_by_image(self.user_data['user_profile_pic']))
        gender_5 = self.find_by_emoji(self.user_data['user_bio']) if 'user_bio' in self.user_data else dict()
        self.genders_dict = {"female": .0, "male": .0}

        gender_t="unknown"
        for post in self.user_data['posts']:
            if 'caption' in post:
                post = post['caption']
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
        male_total_weight = male_weight / is_male_dict.__len__() if is_male_dict.__len__() is not 0 else 0
        female_total_weight = female_weight / is_female_dict.__len__() if is_female_dict.__len__() is not 0 else 0
        try:
            male_trust_percent = male_total_weight * 100
            female_trust_percent = female_total_weight * 100
            is_male_val = "{:.2f}".format(male_trust_percent/(male_trust_percent+female_trust_percent) * 100)
            is_female_val = "{:.2f}".format(female_trust_percent/(male_trust_percent+female_trust_percent) * 100)
            if is_male_val>is_female_val:
                final_result="male"
            elif is_female_val>is_male_val:
                final_result="female"
            else:
                final_result="unknown"
            
            return "male","{:.2f}".format(male_trust_percent),is_male_val,"female","{:.2f}".format(female_trust_percent),\
                    is_female_val,final_result,gender_1,gender_2,gender_3,str(gender_4),str(gender_5),gender_t
        except ZeroDivisionError:
            return "unknown",0
    
def text_normalizer(text):
    """
    Normalize the text given,change the persian numbers to en
    Args:
        text (str): bio,caption,etc.

    Returns:
        [str]: normal text
    """
    persian_numbers = ('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')

    normal_text = text
    for index, i in enumerate(persian_numbers):
        if i in text:
            normal_text = normal_text.replace(i, str(index))
    return normal_text

class AgeFinder(Detector):
    """ Detect age of Instagram user """
    
    def __init__(self, **kwargs):
        """
        class initialization to predefine args and attributes.

        Keyword Args:
            **kwargs: this must contain a dict in format and vars: user_data = {'fullname':fullname ,
                            'username':username ,
                            'user_bio':user_bio ,
                            'image': profile_pic_url,
                            'posts': list of caption of the posts : ['str','str',...]
                         }
        """
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

    def check_username(self, username):
        """
        Check username if contains number of years even it's jalali year or gregorian year type
        Args:
            username (str): user's username

        Returns:
            [int]: age between 13 to 90 or None
        """
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
        """ calculating age of user

        Args:
            year (int): jalali or gregorian year
            cal_type (int):  get 2 param [0,1],0 is gregorian and 1 in jalali

        Raises:
            AssertionError -- cal_type must be 0 or 1

        Returns:
            [int]: age number
        """
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
        """ Convert jalali or gregorian date to age

        Args:
            date (str): jalali or gregorian date
            cal_type (int):  get 2 param [0,1],0 is gregorian and 1 in jalali

        Returns:
           [int]: age number

        """
        """ calculating age of user,type get 2 param [0,1],0 is gregorian and 1 in jalali """
        if cal_type == 1:
            age = jdatetime.datetime.now().year - date
        else:
            age = datetime.datetime.now().year - date
        return age

    def get_age_birth(self, text):
        """
        Find date of birth with different formats in 2 type of jalali and gregorian date in text given.

        Args:
            text (str): biography or post's captions,etc.

        Returns:
            [int]: age
        """
        text = text_normalizer(text)
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
        """
        Find educational words in text.

        Args:
            text (str): bio,caption,etc.

        Returns:
            [tuple] (int,int): first param is 'min age' and second is 'max age'
        """
        for key, value in self.education_words.items():
            if key in text:
                return value
        return

    def find_year(self, text, cal_type=0):
        """
        Check text if contains number of years even it's jalali year or gregorian year type
        Args:
            text (str): biography or post's captions,etc.
            cal_type (int):  get 2 param [0,1],0 is gregorian and 1 in jalali

        Returns:
            [int]: year
        """
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
        """
        Find day in text.

        Args:
            text: biography or post's captions,etc.

        Returns:
            [int]: day
        """
        day = re.findall('[1-3]{0,1}[0-9]', text)
        if day:
            return day[0]
        return

    def check_month_text(self, text):
        """
        Find month name or code in jalali and gregorian type in text given then find year in it if exists.

        Args:
            text (str):  biography or post's captions,etc.
        Returns:
            [int]: age or None
        """
        text = text_normalizer(text)

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
        """
        Detect by image of user,it downloads the image and detect by ImageAnalyzer class.

        Args:
            image_url (str): url of image.

        Returns:
            [str]: this str is contain a tuple in format (min_age,max_age).
        """
        img = requests.get(image_url, allow_redirects=True)
        f_name = 'user_images/image_1.jpg'
        open(f_name, 'wb').write(img.content)
        ia = ImageAnalyzer(f_name)
        age = ia.age_identifier()
        os.remove(f_name)
        return age

    def _check_age(self, post_caption=None):
        """
        Creates dict of detections results from caption of the posts if post_caption exists,
         else calculates the results of user's details.
        Args:
            post_caption: caption of a post

        Returns:
            [tuple] (dict,float): dict contains --> {'recognized_method':age,..},float is sum of each method score.
        """
        dict_recognized = dict()
        if not post_caption:
            age_1 = self.check_username(self.user_data['user_name'])
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

    def detect(self):
        """
        Main detect function,
        This function calculates the age results of user's detail recognition and user's post captions recognition,
        merge em all in a dict and sum the scores and then divide on recognized functions count to
        calculate the trust percent,then collect the score of each recognized functions and collect the max of the scores
        and results the age and score

        Returns:
            [tuple] (str,float): first parameter can be age,(min_age,max_age) or unknown ,second is percent of trust.
        """
        age_5 = list(self.find_by_image(self.user_data['user_profile_pic']))
        dict_recognized, total_percent = self._check_age()
        posts_keys = dict()
        if age_5.__len__() > 0 and age_5 is not "unknown":
            dict_recognized['find_by_image'] = age_5
            total_percent += self.__function_weights['find_by_image']
        for index, post in enumerate(self.user_data['posts']):
            post = post['caption']
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


class LocationFinder(Detector):
    """ Detect location of Instagram users """
    
    def __init__(self, **kwargs):
        """
        class initialization to predefine args and attributes.

        Keyword Args:
            **kwargs: this must contain a dict in format and vars: user_data = {'fullname':fullname ,
                            'username':username ,
                            'user_bio':user_bio ,
                            'image': profile_pic_url,
                            'posts': {'caption':list of caption of the posts : ['str','str',...],
                                      'location':list of location of the posts}
                         }


        """
        self.user_data = kwargs.pop('user_data')
        self.user_bio = self.user_data.get('user_bio', None)
        self.posts = self.user_data.get('posts', None)
        self.phoneRegex = re.compile(
            r'''(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})''', re.VERBOSE)
        self.persian_numbers = ('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
        with open("preprocess/prefix_country_phone.json", 'r') as fp:
            self.country_codes = json.load(fp)['country_codes']
        self.locations_list_dict = {'country': dict(), 'state': dict(), 'city': dict(), 'district': dict(),
                                    'location': dict()}
        self.geo_tags = []
        self.locations_list = []

    def language_detector(self, text):
        lang_code = detect(text)
        with open("preprocess/language_codes.json", 'r') as f:
            iso_codes = json.load(f)
            for item in iso_codes['iso_codes']:
                if list(item.values())[0][1] == lang_code:
                    return {"nationality": list(item.keys())[0]}
        return

    def country_code_detect(self, text):
        with open("preprocess/language_codes.json", 'r') as f:
            iso_codes = json.load(f)
            for item in iso_codes['iso_codes']:
                if re.search(r'\b' + list(item.values())[0][2] + r'\b', text):
                    return {"nationality": list(item.keys())[0]}
        return

    def find_by_place(self, text):
        """
        
        Args:
            text (str): biography, caption of posts , etc.

        Yields:
            [dict]: dict of partial location {'state': state, 'city': city, 'district': district}

        """
        if not text or text.__len__() == 0:
            return
        text = text_normalizer(text)
        state, city1, district = None, None, None
        with open("preprocess/iranstates.json") as jsfile:
            loc_json = json.load(jsfile)
            for loc in loc_json['states']:

                for city in loc['cities']:
                    if re.search(r'\b' + city['name'] + r'\b', text):
                        state = loc['name']
                        city1 = city['name']
                        if "district" in city:
                            for dist in city['district']:
                                if re.search(r'\b' + dist + r'\b', text):
                                    state = loc['name']
                                    city1 = city['name']
                                    district = dist
                                    yield {"state": state, 'city': city1, "district": district}
                                    state, city1, district = None, None, None
                        else:
                            yield {"state": state, 'city': city1, "district": district}
                            state, city1, district = None, None, None
                if re.search(r'\b' + loc['name'] + r'\b', text):
                    state = loc['name']
                    yield {"state": state, 'city': city1, "district": district}

    def find_by_phone(self, text):
        location = dict()
        phones = self.phoneRegex.findall(text_normalizer(text))
        for phone in phones:
            for key, value in self.country_codes:
                if phone.startswith(value):
                    location.update({'country': key})
        return

    def __places_dict_maker(self, obj_generator):
        """Create dictionary of locations and repeatation number of them

        Args:
            obj_generator (Generator): Generator that contains a dict({"state": state, 'city': city, "district": district})
        """        
        if obj_generator:
            obj_place_counter = 0
            while True:
                try:
                    ob_dict = obj_generator.__next__()
                    self.locations_list.append(ob_dict)
                    obj_place_counter += 1
                    for key, value in ob_dict.items():
                        if value:
                            b_counter = self.locations_list_dict[key][value] if value in self.locations_list_dict[
                                key] else 0
                            self.locations_list_dict[key].update({value: b_counter + 1})
                except StopIteration:
                    break

    def _generate_place(self):
        """Finds the locations in bio or posts caption,geo tags in posts and if geo tags exists add them to
        the final dict and count them.

        Returns:
            locations_dict[dict]: returns dict of locations and states in type of: 
            {'country': {"country":count_of_repeatation}, 'state': {"state":count_of_repeatation},
            'city': {"city":count_of_repeatation},'district': {"district":"count_of_repeatation"},
            'location': {"location":count_of_repeatation}}
        """        
        bio_places_generator = self.find_by_place(self.user_bio)
        if bio_places_generator:
            self.__places_dict_maker(bio_places_generator)
        for post in self.posts:
            if 'caption' in post:
                post_places_generator = self.find_by_place(post['caption'])
                if post_places_generator:
                    self.__places_dict_maker(post_places_generator)
            if 'location' in post and post['location'] is not '' and post['location'] is not 'None':
                self.geo_tags.append(post['location'])
        for geo_tag in self.geo_tags:
            geo = json.loads(json.dumps(ast.literal_eval(geo_tag)))
            if geo:
                geo_name = geo['name'].split(',')[0].lower()
                b_counter = self.locations_list_dict['location'][geo_name] if geo_name in self.locations_list_dict[
                    'location'] else 0
                self.locations_list_dict['location'].update({geo_name: b_counter + 1})
        print(self.locations_list_dict)
        # mys = set()
        # for item in self.locations_list:
        #     mys.add(tuple(item.items()))
        # print(mys)
        return self.locations_list_dict

    def detect(self):
        """Final detection of locations

        Returns:
            [tuple]: (dict of locations and states in type of: 
            {'country': {"country":count_of_repeatation}, 'state': {"state":count_of_repeatation},
            'city': {"city":count_of_repeatation},'district': {"district":"count_of_repeatation"},
            'location': {"location":count_of_repeatation}}, None(to be in format of tuple))
        """        
        return str(self._generate_place()),None

def posts_iterator(func):
    """Decorator to itter posts of a user,concat the likes and comments counts

    Args:
        func ([function]): call the function that using post iteration.
    """    
    def wrapper(self, *args, **kwargs):
        likes_count = 0
        comments_count = 0
        if self.posts:
            for post in self.posts:
                likes_count += post['like_count']
                comments_count += post['comments_count']
        kwargs['tot_likes'] = likes_count
        kwargs['tot_comments'] = comments_count
        return func(self, *args, **kwargs)

    return wrapper

class AudienceTypeFinder(Detector):
    """Detect users audience type"""    
    def __init__(self, **kwargs):
        """
        class initialization to predefine args and attributes.

        Keyword Args:
            **kwargs: this must contain a dict in format and vars: user_data = 
                        {   
                            'fullname':fullname ,
                            'user_is_verified':user_is_verified,
                            'user_followers':user_followers,
                            'user_following':user_following,
                            'user_is_private':user_is_private,
                            'highlight_reel_count':highlight_reel_count
                            'username':username ,
                            'user_bio':user_bio ,
                            "date":date,
                            'image': profile_pic_url,
                            'posts': list of dictionaries for posts : [{"like_count":int(),"comments_count":int()}]
                         }
        """
        self.user_data = kwargs.pop('user_data', None)
        if self.user_data:
            self.followers_count = self.user_data['user_followers']
            self.followings_count = self.user_data['user_following']
            self.bio = self.user_data['user_bio']
            self.posts_count = self.user_data['user_posts']
            self.is_verified = self.user_data['user_is_verified']
            self.is_private = self.user_data['user_is_private']
            self.profile_picture = self.user_data['user_profile_pic']
            self.full_name = self.user_data['user_full_name']
            self.posts = self.user_data['posts']
            self.highlight_reel_count = self.user_data['highlight_reel_count']
            self.user_name = self.user_data['user_name']
        self.__real_users_ratio = {500000: {'like': 11.06, 'comment': 0.67, 'standard_dev': 4.26, 'first_quarter': 6.8,
                                            'third_quarter': 15.32},
                                   3000: {'like': 10.7, 'comment': 1.01, 'standard_dev': 7.1, 'first_quarter': 3.6,
                                          'third_quarter': 17.8},
                                   2000: {'like': 12.63, 'comment': 1.68, 'standard_dev': 8.38, 'first_quarter': 4.25,
                                          'third_quarter': 21.01},
                                   8000: {'like': 5.62, 'comment': 0.26, 'standard_dev': 3.57, 'first_quarter': 2.05,
                                          'third_quarter': 9.19},
                                   100: {'like': 35.09, 'comment': 2.83, 'standard_dev': 24.59, 'first_quarter': 10.5,
                                         'third_quarter': 59.68},
                                   50000: {'like': 9.35, 'comment': 0.42, 'standard_dev': 6.33, 'first_quarter': 3.02,
                                           'third_quarter': 15.68},
                                   300000: {'like': 11.48, 'comment': 0.6, 'standard_dev': 7.64, 'first_quarter': 3.84,
                                            'third_quarter': 19.12},
                                   10000: {'like': 7.08, 'comment': 0.63, 'standard_dev': 3.68, 'first_quarter': 3.4,
                                           'third_quarter': 10.76},
                                   1: {'like': 24.98, 'comment': 1.85, 'standard_dev': 9.83, 'first_quarter': 15.15,
                                       'third_quarter': 34.81},
                                   100000: {'like': 9.85, 'comment': 0.43, 'standard_dev': 4.79, 'first_quarter': 5.06,
                                            'third_quarter': 14.64},
                                   1000: {'like': 12.47, 'comment': 0.84, 'standard_dev': 6.6, 'first_quarter': 5.87,
                                          'third_quarter': 19.07},
                                   80000: {'like': 16.43, 'comment': 1.32, 'standard_dev': 11.06, 'first_quarter': 5.37,
                                           'third_quarter': 27.49},
                                   5000: {'like': 9.91, 'comment': 0.38, 'standard_dev': 5.99, 'first_quarter': 3.92,
                                          'third_quarter': 15.9},
                                   1000000: {'like': 6.23, 'comment': 0.2, 'standard_dev': 4.56, 'first_quarter': 1.67,
                                             'third_quarter': 10.79},
                                   500: {'like': 19.62, 'comment': 1.43, 'standard_dev': 11.01, 'first_quarter': 8.61,
                                         'third_quarter': 30.63},
                                   20000: {'like': 6.44, 'comment': 0.33, 'standard_dev': 4.93, 'first_quarter': 1.51,
                                           'third_quarter': 11.37}}

        self.fl_status = self.find_fl_status()

    def __count_username_digits(self):
        """Counts the username's digits

        Returns:
            [int]: count of digits in username
        """        
        counter = 0
        for i in self.user_name:
            if i.isdigit():
                counter += 1
        return counter

    def __count_username_alpha(self):
        """Counts username's alphabets

        Returns:
            [int]: count of username's alphabets
        """        
        counter = 0
        for i in self.user_name:
            if i.isalpha():
                counter += 1
        return counter

    def __cal_username_ratio(self):
        """Calculates username's ratio of number of digits to username's alphabets.

        Returns:
            [bool]:  if result is more than 60 percent returns True,else False
        """        
        return True if self.__count_username_digits() / self.user_name.__len__() > .60 else False

    def find_real_people(self):
        """Check if user is real by looking for the distance of following/followers counts,private accounts,fullname,
        profile picture,verified users,bio,highlighted stories,posts count.
        assigned an score to every parameter.

        Returns:
            [float]: returns total score of parameters
        """        
        total_score = 0
        if self.followings_count - self.followers_count < 3000:
            total_score += 0.30
        if self.is_private:
            total_score += .10
        if self.full_name and self.full_name.__len__() > 0:
            total_score += .10
        if "YW5vbnltb3VzX3Byb2ZpbGVfcGlj.2" not in self.profile_picture:
            total_score += .10
        if self.is_verified:
            return 1
        if self.bio and self.bio is not '':
            total_score += .10
        if self.highlight_reel_count and self.highlight_reel_count > 0:
            total_score += .20
        # if self.__cal_username_ratio():
        #     total_score -= .30
        total_score += self.posts_count * 0.10

        return total_score if total_score < 1 else 1

    def find_fake_user(self):
        """Find if user is fake by calculating distance of following/follower parameters

        Returns:
            [int]: 1 if fake else 0
        """        
        if (self.followings_count - self.followers_count) > 3500:
            if self.fl_status == 'bad':
                return 1
        return 0

    def find_mass_follower(self):
        """Find if user has mass follower by checking following and followers

        Returns:
            [int]: 1 if has mass follower else 0
        """        
        if self.followings_count > 1500 and 10000 > self.followers_count > 5000 and not self.has_fake_follower:
            return 1
        return 0

    def find_bot(self):
        """Find if user is bot by checking followers count,posts count, username ratio and profile picture.

        Returns:
            [float]: score of bot user
        """        
        total_score = 0
        if self.followers_count ==0:
            total_score += .50
        if self.posts_count == 0:
            total_score += .20
        if self.__cal_username_ratio():
            total_score += .20
        if "YW5vbnltb3VzX3Byb2ZpbGVfcGlj.2" in self.profile_picture:
            total_score += .10
        return total_score

    def find_stolen_account(self):
        """Find if account is stolen or deactivated by checking last post datetime

        Returns:
            [bool]: True if is stolen else False
        """        
        if self.posts:
            last_post_time = datetime.datetime.strptime(self.posts[0]['date'], "%Y-%m-%dT%H:%M:%SZ")
            if (datetime.datetime.now() - last_post_time).days > 365:
                return True
        return False

    @posts_iterator
    def _calculate_lf_ratio(self, **kwargs):
        """Calculates ratio of posts likes to follower

        Returns:
            [float]: returns ratio or None for division by zero
        """        
        try:
            return float("%.2f" % float(kwargs.get('tot_likes') / self.posts.__len__() / self.followers_count)) * 100
        except ZeroDivisionError:
            return None

    def find_influencer(self):
        """Check if user is influencer by looking for more than 10000 followers counts.

        Returns:
            [int]: 1 for True and 0 for False
        """        
        if self.followers_count > 10000:
            return 1
        return 0

    def find_fl_status(self):
        """find status of posts like to follower situation depended to real users ratio

        Returns:
            [string]: unknown,bad,normal,good,excellent
        """        
        if self.is_private or self.posts_count == 0:
            return "unknown"
        for key in list(sorted(self.__real_users_ratio.keys()).__reversed__()):
            if self.followers_count > key:
                user_engagement_ratio = self._calculate_lf_ratio()
                if user_engagement_ratio is None:
                    return "unknown"
                first_quarter = self.__real_users_ratio[key]['first_quarter']
                third_quarter = self.__real_users_ratio[key]['third_quarter']
                norm_avg = self.__real_users_ratio[key]['like']
                if user_engagement_ratio < first_quarter:
                    return 'bad'
                elif first_quarter < user_engagement_ratio <= norm_avg:
                    return 'normal'
                elif norm_avg < user_engagement_ratio < third_quarter:
                    return 'good'
                else:
                    return 'excellent'
        return "unknown"

    @posts_iterator
    def calculate_engagement(self, **kwargs):
        """calculate total engagement of latest 12 posts of user 

        Returns:
            [float]: ratio of total likes count + total comments to posts count,or None for division by zero.
        """        
        try:
            return float("%.2f" % ((((kwargs.get('tot_likes') + kwargs.get(
                'tot_comments')) / self.followers_count) / self.posts.__len__()) * 100))
        except ZeroDivisionError:
            return None

    def detect(self):
        """Categories and generates final results into suspicious,influencer and real accounts,
        by checking methods points and results

        Returns:
            [tuple]: (type,engagement status,engagement ratio)
        """        
        engagement_ratio = self.calculate_engagement()
        engagement_ratio = engagement_ratio if engagement_ratio else "unknown"
        print(engagement_ratio)
        final_res = {'is_real': 0.0, 'is_fake': self.find_fake_user(), 'is_bot': self.find_bot(), 'stolen': 0.0,
                     'influencer': self.find_influencer(), 'engagement_status': self.fl_status}
        if final_res['is_bot'] > .50:
            return 'suspicious', 'is_bot', engagement_ratio
        if final_res['is_fake']:
            return 'suspicious', 'is_fake', engagement_ratio

        is_real = self.find_real_people()
        if is_real > .50:
            if self.find_stolen_account():
                return 'suspicious', 'stolen', engagement_ratio
            if self.find_influencer():
                return 'influencer', self.fl_status, engagement_ratio
            return 'real', self.fl_status, engagement_ratio
        return 'unknown', is_real, engagement_ratio

if __name__ == '__main__':
    au = AudienceTypeFinder()
    # au.calculate_engagement()
    # au.find_engagment_status()
