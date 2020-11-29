from bs4 import BeautifulSoup
import requests

# html_doc = requests.get(
#     url='https://fa.wikipedia.org/wiki/%D9%81%D9%87%D8%B1%D8%B3%D8%AA_%D9%86%D8%A7%D9%85%E2%80%8C%D9%87%D8%A7%DB%8C_%D8%A7%DB%8C%D8%B1%D8%A7%D9%86%DB%8C')
# soup = BeautifulSoup(html_doc.text, 'html.parser')
# with open("persian_names.txt",'w') as f:
#     for ul in soup.find_all('div', attrs={'class': 'column-count-۶'}):
#         # soup1 = BeautifulSoup(ul,'html.parser')
#         for li in ul.find_all('li'):
#
#             f.write(li.text.split('[')[0].split('(')[0].strip()+'\n')
# namesets = set()
# with open("persian_names.txt", 'r') as f:
#     for name in f.readlines():
#         namesets.add(name.strip().encode('utf8').decode('utf8'))
#
# with open("preprocess/female_persian_names", 'w') as f:
#     for i in namesets:
#         f.write(i + "\n")
# html_doc = requests.get(
#     url='https://gahar.ir/%D8%A7%D8%B3%D9%85-%D8%AF%D8%AE%D8%AA%D8%B1-%D8%AC%D8%AF%DB%8C%D8%AF-%D8%8C-%D8%A7%D8%B3%D9%85-%D8%AF%D8%AE%D8%AA%D8%B1-%D8%A7%DB%8C%D8%B1%D8%A7%D9%86%DB%8C-%D8%A8%D8%A7%DA%A9%D9%84%D8%A7%D8%B3/')
# soup = BeautifulSoup(html_doc.text, 'html.parser')
# with open("persian_names.txt",'w') as f:
#     for p in soup.find_all('p'):
#         # soup1 = BeautifulSoup(ul,'html.parser')
#         name =p.find('strong')
#         if name and not "اسم دختر ایرانی" in name.text:
#             f.write(name.text.replace(":","").strip() + '\n')

mtlist = []
with open("preprocess/male_emojies", 'r') as f:
    for line in f:
        mtlist.append("\\u"+line.strip().lower().replace(" ", '\\u'))
with open("preprocess/male_emojies", 'w') as f:

    for i in mtlist:
        f.write(i+"\n")
