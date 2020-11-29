import json

import re

from langdetect import detect

import ast


class LocationFinder(object):
    def __init__(self, **kwargs):
        self.user_bio = kwargs.pop('user_bio', None)
        self.posts = kwargs.pop('posts', None)
        self.phoneRegex = re.compile(
            r'''(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})''', re.VERBOSE)
        self.persian_numbers = ('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
        with open("preprocess/prefix_country_phone.json", 'r') as fp:
            self.country_codes = json.load(fp)['country_codes']
        self.locations_list_dict = {'country': dict(), 'state': dict(), 'city': dict(), 'district': dict(),
                                    'location': dict()}
        self.geo_tags = []
        self.locations_list = []

    def text_normalizer(self, text):
        normal_text = text
        for index, i in enumerate(self.persian_numbers):
            if i in text:
                normal_text = normal_text.replace(i, str(index))
        return normal_text

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
        if not text or text.__len__() == 0:
            return
        text = self.text_normalizer(text)
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

        # print({"state": state, 'city': city1, "district": district})
        # if state or city1 or district:
        #     yield {"state": state, 'city': city1, "district": district}
        #     print(44444444444444444444)
        # return

        # a = geograpy.get_place_context(text=text)
        # a = geograpy.Extractor(text=text)
        # print(a.find_entities())
        # a=geograpy.Extractor(text=text)
        # a.find_entities()
        # places = GeoText(text)
        # return a

    def find_by_phone(self, text):
        location = dict()
        phones = self.phoneRegex.findall(self.text_normalizer(text))
        for phone in phones:
            for key, value in self.country_codes:
                if phone.startswith(value):
                    location.update({'country': key})
        return

    def __places_dict_maker(self, obj_generator):
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
        mys = set()
        for item in self.locations_list:
            mys.add(tuple(item.items()))
        print(mys)
        # print(11111111111111111111111111)
        # print(Counter(self.locations_list))
        # print(11111111111111111111111111)

    # def find_user_location(self):
    #         while True:
    #             bio_place =
    #
    #     for post in user_posts.docs:
    #         post_places = self.find_by_place(post['caption'])
    #         if post_places:
    #             for key, value in post_places.items():
    #                 locations_list_dict[key] += value
    #         if 'location' in post and post['location']:
    #             locations_list_dict['location'].append(post['location'])
    #
    #     print(locations_list_dict)
