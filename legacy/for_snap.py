from matplotlib.pyplot import title
from requests_html import HTMLSession
from pymongo import MongoClient
import pymongo
import time
from datetime import datetime
import os

client = MongoClient(
    os.getenv("MONGO_URI")
)
db = client[os.getenv("DB_NAME")]
collection = db[os.getenv("COLLECTION_NAME")]
try:
    collection.create_index([("url", pymongo.ASCENDING)], unique=True)
except Exception as e:
    print(e)

base_url = "https://www.la-razon.com"
urls = [
    "https://www.la-razon.com/tags/feminicidio/",
    "https://www.la-razon.com/tags/feminicidios/",
]
session = HTMLSession()

for url in urls:
    stop = True
    page = 1
    while stop:
        request_url = url + "page/{}/".format(page)
        print(request_url)
        request_url ="https://www.la-razon.com/tags/feminicidio/"
        r = session.get(request_url)
        if r.status_code == 200:
            print(r.status_code)
            div_block = r.html.find("div[class = articles-list]")[0]
            div_article = div_block.find("div[class = article-meta]")
            for div in div_article:
                notas = div.find("a")
                link_nota = notas[0].attrs["href"]
                link_nota = link_nota

                if (
                    ("/lr-article/" not in link_nota)
                    and ("/mundo/" not in link_nota)
                    and ("/voces/" not in link_nota)
                    and ("/la-revista/" not in link_nota)
                ):
                    q = session.get(link_nota)
                    print(link_nota)
if q.status_code == 200:
    title = q.html.find("h1[class = title]")
    title = title[0].full_text
    div_cuerpo = q.html.find("div[class=article-body]")[0]
    cuerpo_nota = div_cuerpo.find("p")
    body = [c.full_text.strip() for c in cuerpo_nota]
    
                        div_tags = q.html.find("div[class=lr-tags-cloud-block]")[0]
                        tags = div_tags.find("a[href*=tag]>li")
                        tags = [t.full_text.lower() for t in tags]
                        link_nota_split = link_nota.split("/")
                        section = link_nota_split[3]
                        date_publish = (
                            link_nota_split[4] + link_nota_split[5] + link_nota_split[6]
                        )
                        date_publish = datetime.strptime(date_publish, "%Y%m%d")
articulo = {
    "url": link_nota,
    "title": title,
    "body": body,
    "tags": tags,
    "date_published": date_publish,
    "section": section,
    "source": "larazon",
}
collection.insert_one(articulo)

try:
    
except pymongo.errors.DuplicateKeyError:
    print("Duplicate key")
            page += 1
            time.sleep(5)
            # stop = False
        else:
            stop = False

db = client["feminicidios"]
collection = db["news"]
cursor = collection.find()
df = pd.DataFrame(list(cursor))

import spacy
import pymongo
from pymongo import MongoClient
import pandas as pd
from spacy.lang.es.stop_words import STOP_WORDS

nlp_alpha = spacy.load("es_dep_news_trf")
nlp_beta = spacy.load("es_core_news_lg")

df["title_lower"] = df["title"].apply(lambda x: x.lower())
df['ents_list'] = df["title"].apply(lambda x: [e  for e in nlp_beta(x).ents])
df['ents_loc'] = df["title"].apply(lambda x: [e.text.lower()  for e in nlp_beta(x).ents if e.label_=='LOC'])
df['nouns'] = df["title"].apply(lambda x: [w.text.lower()  for w in nlp_alpha(x).noun_chunks])

df_title_data["clean_ent_loc"] = df_title_data.apply(lambda x: clean_loc(x.nouns,x.ents_loc),axis=1)


def title_key(title_lower, list_nouns, list_loc):
    clean_title = dict()
    title_lower_aux= deepcopy(title_lower)
    for n in list_nouns:
        if n not in stopwords:
            if title_lower.find(n) >-1:
                clean_title[title_lower.find(n)] = n
                title_lower=title_lower.replace(n,"")
    free_words = dict()
    for w in title_lower:
        free_words[title_lower_aux.find(w)] = w
    
    clean_list = {**free_words, **clean_title}
    clean_list = clean_list.items()
    sorted_clean = dict(sorted(clean_list))
    

    title_keys = []
    for k,c in sorted_clean.items():
        if c in list_loc:
            title_keys.append(c)
        else:
            p = c.split(" ")
            for w in p:
                if w in stopwords:
                    p.remove(w)
            p= " ".join(p)
            title_keys.append(p)
    
    return title_keys