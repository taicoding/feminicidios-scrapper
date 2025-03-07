from matplotlib.pyplot import title
from requests_html import HTMLSession
from pymongo import MongoClient
import pymongo
import time
from datetime import datetime
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db[os.getenv("COLLECTION_NAME")]
try:
    collection.create_index([("url", pymongo.ASCENDING)], unique=True)
except Exception as e:
    print(e)

base_url = "https://www.eldiario.net/"
urls = [
    "https://elpais.bo/tags/view/Feminicidio?page={}",
]
"""
query = {"source": "elpais"}
d = collection.delete_many(query)
print(d.deleted_count, " documents deleted !!")
"""
session = HTMLSession()
for url in urls:
    stop_count = 0
    stop = True
    page = 1
    while stop:
        request_url = url.format(page)
        # print(request_url)
        r = session.get(request_url)
        if r.status_code == 200:
            # print(r.status_code)
            div_article = r.html.find("a[class = link-news]")
            for div in div_article:
                link_nota = div.attrs["href"]
                full_path_url = link_nota
                # print(full_path_url)
                q = session.get(full_path_url)
                if q.status_code == 200:
                    title = q.html.find("h1")
                    title = title[0].full_text.strip()
                    title = title.replace("“", '"')
                    title = title.replace("”", '"')
                    link_nota_split = link_nota.split("/")
                    date_publish = link_nota_split[4][:8]
                    date_publish = datetime.strptime(date_publish, "%Y%m%d")
                    section = link_nota_split[3]
                    div_cuerpo = q.html.find("div[class*=note-body]")[0]

                    cuerpo_nota = div_cuerpo.find("p")
                    body = [c.full_text.strip() for c in cuerpo_nota]
                    body = [b.replace("“", '"') for b in body]
                    body = [b.replace("”", '"') for b in body]
                    if body == []:
                        body = [div_cuerpo.full_text.strip()]

                    div_tags = q.html.find("div[class=ep_post_tags]")[0]

                    tags = div_tags.find("li > a")
                    tags = [t.full_text.lower().replace("#", "") for t in tags]

                    articulo = {
                        "url": full_path_url,
                        "title": title,
                        "body": body,
                        "tags": tags,
                        "date_published": date_publish,
                        "section": section,
                        "source": "elpais",
                    }
                    try:
                        collection.insert_one(articulo)
                    except pymongo.errors.DuplicateKeyError:
                        print("Duplicate key")
                    # time.sleep(2)
            page += 1
            time.sleep(3)
            # stop = False
        else:
            stop = False
