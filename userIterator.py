import datetime
import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler

import pysolr
# from gender_word_finder import GenderFinder, AgeFinder
import requests
import json
import time
import xlwt
from xlwt import Workbook
from xlrd import open_workbook
from xlutils.copy import copy
from preprocess.PersianNormalizer import PersianNormalizer
from preprocess.Dict_Taging import PolarityDetector
from Detector import AgeFinder, GenderFinder, LocationFinder, AudienceTypeFinder
import statistics


class SessionEndException(Exception):
    pass


def _excel_writer(func):
    def wrapper(self, *args, **kwargs):
        # pass
        rb = open_workbook('test_sheet.xls', formatting_info=True)

        wb = copy(rb)
        sheet = wb.get_sheet("test_sheet")
        
        # wb = Workbook()
        # sheet = wb.add_sheet("test_sheet")
        sheet.write(0, 0, "username")
        sheet.write(0, 1, "gender")
        sheet.write(0, 2, "algorithm_truth")
        sheet.write(0, 3, "gender ratio")
        sheet.write(0, 4, "gender")
        sheet.write(0, 5, "algorithm_truth")
        sheet.write(0, 6, "gender ratio")
        sheet.write(0, 7, "final_result")
        sheet.write(0, 8, "find_by_fullname")
        sheet.write(0, 9, "find_by_username")
        sheet.write(0, 10, "find_by_text")
        sheet.write(0, 11, "find_by_image")
        sheet.write(0, 12, "find_by_emoji")
        sheet.write(0, 13, "gender_by_posts_words")
        

        result = func(self, *args, **kwargs)
        if not result:
            return
        r_sheet = rb.sheet_by_index(0)
        r = r_sheet.nrows
        print(result)
        row_counter=1
        sheet.write(r,0,result[-1])
        
        for value in result[:-1]:
            sheet.write(r,row_counter,value)
            row_counter+=1
        # sheet.write(r, 0, result['username'])
        # sheet.write(r, 1, str(result['detect_entity']))
        # sheet.write(r, 2, str(result['trust_avg_percent']) + "%")
        # sheet.write(r, 3, str(result['engagement_ratio']) + "%")
        wb.save("test_sheet.xls")

    return wrapper


class UserDetail:
    def __init__(self, Detector, *args, **kwargs):
        wb = Workbook()
        wb.add_sheet("test_sheet")
        wb.save("test_sheet.xls")
        self.Detector = Detector
        self.solr_cursor = 2020
        self.solr_index = "http://46.102.143.5:8998/solr/insta_users/"
        self.base_url = "https://www.instagram.com/"
        self.solr_index_user_complete = "http://46.102.143.5:8998/solr/insta_users_complete"
        self.solr_index_post = "http://46.102.143.5:8998/solr/insta_general"
        # self.age_finder = AgeFinder()
        # self.gender_finder = GenderFinder()
        self.session = requests.Session()
        self.sessions = {
                "job03test": "31616657788:4vGadBxK2S3D1a:2",
                "zanatest05": "31945622304:YlWjDruyLsc0ZJ:15",
                "edrispapi06": "31601499986:NPYKuecwKeglI7:18",
                "atijob03": "31998551964:yWb9GiFFw93x1u:3",
                "atidegaran": "32417797865:BtTmjusfKXelAr:20",
                "amirmohammad_sotoodeh": "7918058904:cMmk3CIWY1wNdn:21",
                "shayan_malihi9990": "38112860861:k1D2PRCXRdEDhp:25",
                "shila_bahador": "38318739065:hDShwol9vwOFFS:22",
                "zanatest03": "31613778476:Aa1tUpc1iL1F5z:25",
                "zanatest04": "31798409816:A57s27LSmu5OgD:14",
                "imannafisi66": "44043848863:fZ0c7OCikHDlTK:9",
                "atijob02": "32177432735:QJJqorViyrjBCZ:20",
                "sara_yasini021": "38512523466:fRcnwDQZJkZqvN:21",

        }

        self.__LogFilePath = "log.log"
        self.script_path = os.path.abspath(__file__)  # return absolute path of file
        root_path = self.script_path.replace('copyCalculator.py', '')  # replace 'CrawlerScheduler.py' with ''
        log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s %(message)s')
        logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
                            stream=sys.stdout)
        handler = RotatingFileHandler(root_path + self.__LogFilePath, mode='a', maxBytes=2 * 1024 * 1024, backupCount=2)
        handler.setFormatter(log_formatter)
        handler.setLevel(logging.INFO)
        self.logger = logging.getLogger('root')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.normalizer = PersianNormalizer()
        self.Polarity = PolarityDetector(logger=self.logger)
        self.__Language = "fa"
        self.utc_format = '%Y-%m-%dT%H:%M:%SZ'
        self.indx_row = 0
        self.ses_index = 0
        self.session.headers.update({
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"})
        self.solr_post = pysolr.Solr(self.solr_index_post, auth=('solr', 'Solr@123'), timeout=15)

    def users_generator(self, solr_index, rows=100):
        solr = pysolr.Solr(solr_index, auth=('solr', 'Solr@123'), timeout=15)
        rows = rows
        while True:
            results = solr.search('*:*', rows=rows, start=self.solr_cursor)
            self.solr_cursor += rows
            if results.docs.__len__() > 0:
                yield results
            else:
                break

    def extract_user_fields(self, user_json):
        try:
            is_private = user_json['is_private']
            user_name = user_json['username']
            external_url = ''
            if external_url in user_json:
                external_url = user_json['external_url']
            user_id = user_json['id']
            following_count = user_json['edge_follow']['count']
            follower_count = user_json['edge_followed_by']['count']
            media_count = user_json['edge_owner_to_timeline_media']['count']
            user_doc = {
                'user_id': user_id,
                'user_name': user_name,
                'user_full_name': self.normalizer.clean_sentence(user_json['full_name']),
                'user_is_private': is_private,
                'user_is_verified': user_json['is_verified'],
                'user_profile_pic': user_json['profile_pic_url_hd'],
                'user_bio': self.normalizer.clean_sentence(user_json['biography']),
                'external_url': external_url,
                'user_following': following_count,
                'user_followers': follower_count,
                'user_posts': media_count,
                'user_language': self.__Language
            }
            self.SolrCommit([user_doc], self.solr_index_user_complete)
            user_doc['highlight_reel_count'] = user_json['highlight_reel_count']
            return user_doc
        except Exception as err:
            print(err)

    def extract_posts_fields(self, user_json):
        documents = []
        media = user_json['edge_owner_to_timeline_media']
        user_id = user_json['id']
        user_name = user_json['username']
        posts = media['edges']
        counter = 0
        for pst in posts:
            try:
                post = pst['node']
                date = post['taken_at_timestamp']
                type = 'image'
                if post['__typename'] == 'GraphVideo':
                    type = 'video'
                elif post['__typename'] == 'GraphSidecar':
                    type = 'carousel'
                Extra_Data = {}
                if post['is_video'] or post['comments_disabled']:
                    try:
                        Extra_Data = self.getCommentsText(user_name, post['shortcode'], post['is_video'])
                    except Exception as err:
                        self.logger.error('getCommentsText Error')
                        self.logger.error("Casuse: %s" % err)
                cpt = post['edge_media_to_caption']['edges']
                caption = ''
                if len(cpt) > 0:
                    caption = self.normalizer.clean_sentence(cpt[0]['node']['text'])
                comments_count = 0
                if len(post['edge_media_to_comment']) > 0:
                    comments_count = post['edge_media_to_comment']['count']
                likes_count = 0
                if len(post['edge_liked_by']) > 0:
                    likes_count = post['edge_liked_by']['count']
                now = datetime.datetime.now().timestamp()
                elapsed_time = now - date
                engagment_rate = 0
                if (elapsed_time) < 129600:
                    elapsed_time /= 3600
                    engagment_rate = (likes_count / (440 * elapsed_time)) + (comments_count / (60 * elapsed_time))
                doc = {
                    'id': post['id'],
                    'post_code': post['shortcode'],
                    'hashtags': list(self.__ExtractHashtags(caption)),
                    'comment_disabled': post['comments_disabled'],
                    'user_id': user_id,
                    'user_name': user_name,
                    'type': type,
                    'date': self.__utc_to_local(date).strftime(self.utc_format),
                    'image_url': post['display_url'],
                    'caption': caption,
                    'comments_count': comments_count,
                    'like_count': likes_count,
                    'influence': engagment_rate
                }

                polar = self.Polarity.Detect(caption)
                doc['polarity_lable'] = polar['lable']
                doc['polarity_score'] = polar['score']
                doc.update(Extra_Data)
                documents.append(doc)
            except Exception as err:
                self.logger.error("Extract Post Fields Exception")
                self.logger.error("Casuse: %s" % err)
        self.logger.info('{}: {}'.format(user_name, counter))
        self.SolrCommit(documents, self.solr_index_post)
        return documents

    def __ExtractHashtags(self, input):
        if input is None:
            return set()
        return set(re.findall(r"#(\w+)", input))

    def __utc_to_local(self, utc_dt):
        return datetime.datetime.fromtimestamp(utc_dt)

    def get_additional_data(self, url=''):
        try:
            resp = self.session.get('https://www.instagram.com/' + url)
            print(resp.status_code)
            if resp.status_code == 200 and '__additionalDataLoaded' in resp.text:
                response = resp.text.split("window.__additionalDataLoaded(")[1].split(',', 1)[1].split(");</script>")[0]
                return json.loads(response)
            return
        except Exception as err:
            self.logger.error("error while getting additional data")
            self.logger.error("Casuse: %s" % err)

    def getCommentsText(self, user_name, post_code, is_video):
        url = 'p/' + post_code + '/?taken-by=' + user_name
        Extra_Data = {'location': ''}
        try:
            resp = self.session.get('https://www.instagram.com/' + url)
            shared_data = resp.text.split("window._sharedData = ")[1].split(";</script>")[0]
            post_data = json.loads(shared_data)
            # print(post_data)
            post = post_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
        except:
            post_data = self.get_additional_data(url)
            if post_data:
                post = post_data['graphql']['shortcode_media']
            else:
                post = None
            if post:
                if is_video:
                    Extra_Data['video_url'] = post['video_url'],
                    Extra_Data['video_views'] = post['video_view_count']
                Extra_Data['location'] = str(post['location'])
        return Extra_Data

    @staticmethod
    def user_field_extractor(user_json):
        try:
            user_posts = []
            if not user_json['is_private']:
                posts = user_json['edge_owner_to_timeline_media']['edges']
                for post in posts:
                    post = post['node']
                    cpt = post['edge_media_to_caption']['edges']
                    caption = ''
                    if len(cpt) > 0:
                        caption = cpt[0]['node']['text']
                    user_posts.append(caption)
            user_data = {'fullname': user_json['full_name'],
                         'username': user_json['username'],
                         'user_bio': user_json['biography'] if 'biography' in user_json else '',
                         'image': user_json['profile_pic_url'], 'posts': user_posts
                         }
            return user_data

        except Exception as err:
            print(err)

    @_excel_writer
    def __evaluate_detection(self, user):
        # try:
        fq = "user_name:{0}".format(user['user_name'])
        if 'posts' not in user:
            user_posts = self.solr_post.search('*:*', fq=fq, fl='caption',
                                               rows=12,
                                               sort="date asc",
                                               )
            user['posts'] = user_posts
        # print(user)
        # result_tup= self.Detector(user_data=user).detect()
        # detect_entity, trust_avg_percent, engagement_ratio = self.Detector(user_data=user).detect()
        self.indx_row += 1
        return self.Detector(user_data=user).detect().__add__((user['user_name'],))
        # return {'indx_row': self.indx_row, 'username': user['user_name'], 'detect_entity': result_tup[0],
        #         'trust_avg_percent': result_tup[1], 'engagement_ratio': result_tup[2] if result_tup.__len__()==3 else ""}
        # except Exception as err:
        #     print(err)

    def solr_user_iter(self):
        users = self.users_generator(self.solr_index_user_complete)
        while True:
            try:
                for user in users.__next__():
                    self.__evaluate_detection(user)
            except StopIteration:
                break

    def __change_session(self):
        if self.ses_index == self.sessions.__len__():
            raise SessionEndException
        time.sleep(1)
        self.session.cookies.set("sessionid", list(self.sessions.values())[self.ses_index])
        self.ses_index += 1
        self.logger.info("sessions changed")
        time.sleep(3)

    def get_user_json(self, username):
        while True:
            resp = self.session.get(self.base_url + username)
            if resp.status_code == 429:
                try:
                    self.__change_session()
                    continue
                except SessionEndException:
                    self.logger.info('end of sessions,sleep for 2 hrs')
                    time.sleep(2 * 60 * 60)
            # else:
            #     break
            if resp.status_code == 404:
                self.logger.info('This user not found in Instagram.')
                return
            try:
                shared_data = resp.text.split("window._sharedData = ")[1].split(";</script>")[0]

                data = json.loads(shared_data)
                print(json.dumps(data))

                if 'graphql' in data['entry_data']['ProfilePage'][0]:
                    user_json = data['entry_data']['ProfilePage'][0]['graphql']['user']
                else:
                    user_json = self.get_additional_data(username)['graphql']['user']

                if user_json is None:
                    self.logger.info('This user not found in Instagram.')
                    return
                user_doc = self.extract_user_fields(user_json)
                post_docs = self.extract_posts_fields(user_json)
                user_doc['posts'] = post_docs
                return user_doc
            except Exception as err:
                print("error occurred while getting user json")
                print(err)
                try:
                    self.__change_session()
                except SessionEndException:
                    self.logger.info('end of sessions,sleep for 2 hrs')
                    time.sleep(2 * 60 * 60)

    @_excel_writer
    def user_iter(self,limit=None):
        users = self.users_generator(self.solr_index)
        counter = 0
        indx_row = 0
        has_perm = True
        while has_perm:
            try:
                for user in users.__next__():
                    # try:
                    if counter==limit:
                        has_perm=False
                        break
                    if counter % 150 == 0:
                        try:
                            self.__change_session()
                        except SessionEndException:
                            self.logger.info('end of sessions,sleep for 2 hrs')
                            time.sleep(2 * 60 * 60)
                    counter += 1
                    try:
                        user_doc = self.get_user_json(user['user_name'])
                    except SessionEndException:
                        break
                    if not user_doc:
                        continue
                    print(self.__evaluate_detection(user_doc))
                    indx_row += 1
                    print(indx_row)
                    print("-" * 100)
                    # except Exception as err:
                    #     print(err)

                    # except Exception as err:
                    #     print(err)

            except StopIteration:
                break

    def extract_models(self):
        counter = 0
        user_counter, file_counter = 0, 0
        final_data_list = []

        for filename in os.listdir("preprocess/users"):
            print(filename)
            final_data_list.append({filename: []})
            with open("preprocess/users_data.JSON", 'r+') as f:
                if os.stat("preprocess/users_data.JSON").st_size > 0:
                    data = json.load(f)
                    data['data'].append({filename: []})

                    with open("preprocess/users_data.JSON", 'w') as fw:
                        json.dump(data, fw)
                        fw.flush()
            with open("preprocess/users/" + filename, 'r') as file:
                for line in file:
                    print(line.strip() == '')
                    username = line.strip()
                    user_data_dict = dict()
                    file_data_list = []
                    if username is not '':
                        if counter % 150 == 0:
                            time.sleep(1)
                            if self.ses_index == self.sessions.__len__():
                                break
                            self.session.cookies.set("sessionid", list(self.sessions.values())[self.ses_index])
                            time.sleep(1)
                            print("session changed")
                            self.ses_index += 1
                        counter += 1
                        try:
                            user_doc = self.get_user_json(username)
                        except SessionEndException:
                            break
                        user_data_dict[username] = {"followers": user_doc['user_followers'],
                                                    "following": user_doc['user_following']}
                        print(user_data_dict)
                        posts_dicts = []
                        for post in user_doc['posts']:
                            post_data = {'like': post['like_count'], 'comment': post['comments_count']}
                            posts_dicts.append(post_data)
                        user_data_dict[username]["posts"] = posts_dicts
                        if os.stat("preprocess/users_data.JSON").st_size == 0:
                            file_data_list.append(user_data_dict)
                            data = {"data": [{filename: file_data_list}]}

                        else:
                            with open("preprocess/users_data.JSON", 'r') as f:
                                data = json.load(f)
                                data['data'][file_counter][filename].append(user_data_dict)
                        with open("preprocess/users_data.JSON", 'w') as f:

                            json.dump(data, f)
                            f.flush()
                    else:
                        break
                file_counter += 1

    def SolrCommit(self, documents, solr_address):
        solr = pysolr.Solr(solr_address, auth=('solr', 'Solr@123'), timeout=35)
        solr.add(documents, commit=False, softCommit=True)
        self.logger.info('Solr {} documents Commited'.format(solr_address))

    def cal_user_ratio(self):
        with open("preprocess/users_data.JSON", 'r') as f:
            model_json = json.load(f)
            data = model_json['data']
            final_dict = {}
            for objects in data:
                for cat, value in objects.items():
                    cat = cat.replace("k", "000")
                    cat = int(cat.replace("mil", "000000"))
                    print("Category : %s" % cat)
                    final_dict[cat] = {'like': 0.0, 'comment': 0.0, 'standard_dev': 0.0, 'first_quarter': 0.0,
                                       'third_quarter': 0.0}
                    cat_likes_avgs = []
                    cat_comments_avgs = []

                    for item in value:
                        for user, user_data in item.items():
                            print("Username : %s " % user)
                            print("\tFollowers count : %s " % user_data['followers'])
                            posts_likes = 0
                            posts_comments = 0
                            posts = user_data['posts']
                            print("\tPosts count : %s " % posts.__len__())

                            for post in posts:
                                posts_likes += post['like']
                                posts_comments += post['comment']
                            likes_engagement = float(
                                "%.2f" % ((posts_likes / posts.__len__() / user_data['followers']) * 100))
                            comments_engangement = float("%.2f" % (
                                    (posts_comments / posts.__len__() / user_data['followers']) * 100))
                            print("\t" + str(likes_engagement))
                            cat_likes_avgs.append(likes_engagement)
                            cat_comments_avgs.append(comments_engangement)
                    print("\t" + str(cat_likes_avgs))
                    # print(cat_comments_avgs)
                    tot_like_avg = float("%.2f" % (sum(cat_likes_avgs) / cat_likes_avgs.__len__()))
                    print("Category like avg : %s " % tot_like_avg)
                    print("#" * 100)

                    tot_comment_avg = float("%.2f" % (sum(cat_comments_avgs) / cat_comments_avgs.__len__()))
                    final_dict[cat].update({'like': tot_like_avg})
                    final_dict[cat].update({'comment': tot_comment_avg})
                    like_stdev = float("%.2f" % statistics.stdev(cat_likes_avgs))
                    final_dict[cat].update({'standard_dev': like_stdev})
                    final_dict[cat].update({'first_quarter': float("%.2f" % (tot_like_avg - like_stdev))})
                    final_dict[cat].update({'third_quarter': float("%.2f" % (tot_like_avg + like_stdev))})

            print(final_dict)
            #     print("\tPost likes all : %s " % posts_likes)
            #     print("\tFinal engagement of likes percent : %s " % likes_engagement)
            #     print("\tFinal engagement of comments percent : %s " % comments_engangement)
            # print("-" * 100)
            # print("#" * 100)

            # for user in values


if __name__ == '__main__':
    ud = UserDetail(LocationFinder)
    # ud.cal_user_ratio()
    ud.user_iter(102)
    # ud.solr_user_iter()
    # ud.extract_models()
    # with open("preprocess/users_data.JSON", 'r') as n:
    #     # if not n.readline() == '':
    #     # print(n.read())
    #     m = json.load(n)
    #     m['data'].append({"filename": []})
