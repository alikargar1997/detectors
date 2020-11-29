import pysolr

solr = pysolr.Solr("http://185.211.59.9:9988/solr/insta_users_complete/", auth=('crawler_instagram', '1nst@gr@m'),
                   timeout=15)
cur = 0


def writer(file, user_name):
    with open("preprocess/users/{}".format(file), 'a') as f:
        f.write(user_name + '\n')
        f.flush()


while True:
    results = solr.search('*:*',
                          rows=100,
                          sort="_version_ asc",
                          start=cur)
    cur += 100
    if results.docs.__len__()==0:
        break
    for result in results.docs:
        if result['user_posts'] > 0 and result['user_is_private'] is not True:
            if 500000 < result['user_followers'] < 1000000:
                writer('500k', result['user_name'])

            if 300000 < result['user_followers'] < 500000:
                writer('300k', result['user_name'])

            if 100000 < result['user_followers'] < 300000:
                writer('100k', result['user_name'])

            if 80000 < result['user_followers'] < 100000:
                writer('80k', result['user_name'])

            if 50000 < result['user_followers'] < 80000:
                writer('50k', result['user_name'])

            if 20000 < result['user_followers'] < 50000:
                writer('20k', result['user_name'])

            if 10000 < result['user_followers'] < 20000:
                writer('10k', result['user_name'])

            if 8000 < result['user_followers'] < 10000:
                writer('8k', result['user_name'])

            if 5000 < result['user_followers'] < 8000:
                writer('5k', result['user_name'])

            if 3000 < result['user_followers'] < 5000:
                writer('3k', result['user_name'])

            if 2000 < result['user_followers'] < 3000:
                writer('2k', result['user_name'])

            if 1000 < result['user_followers'] < 2000:
                writer('1k', result['user_name'])

            if 500 < result['user_followers'] < 1000:
                writer('500', result['user_name'])
            if 100 < result['user_followers'] < 500:
                writer('100', result['user_name'])
            if result['user_followers'] < 100:
                writer('1', result['user_name'])

