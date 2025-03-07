from os import link
from numpy import full
from regex import P
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


base_url = "https://www.opinion.com.bo"
urls = [
    "https://www.opinion.com.bo/tags/feminicidio",
    "https://www.opinion.com.bo/tags/feminicidios",
]
session = HTMLSession()

for url in urls:
    stop = True
    page = 1
    while stop:
        request_url = url + "?page={}".format(page)
        r = session.get(request_url)
        if r.status_code == 200:
            print(r.status_code)
            div_article = r.html.find("div[class = article-data]")
            for div in div_article:
                notas = div.find("h2 > a")
                link_nota = notas[0].attrs["href"]
                full_path_url = base_url + link_nota

                if (
                    ("/articulo/" in full_path_url)
                    and ("/pais/" not in full_path_url)
                    and ("/tendencias/" not in full_path_url)
                    and ("/escena-del-crimen/" not in full_path_url)
                    and ("/mundo/" not in full_path_url)
                ):
                    q = session.get(full_path_url)
                    print(full_path_url)
                    if q.status_code == 200:
                        title = q.html.find("h2")
                        title = title[0].full_text
                        title = title.replace("“", '"')
                        title = title.replace("”", '"')
                        link_nota_split = link_nota.split("/")
                        section = link_nota_split[2]
                        date_publish = link_nota_split[-1]
                        date_publish = date_publish[:8]
                        date_publish = datetime.strptime(date_publish, "%Y%m%d")

                        cuerpo_nota = q.html.find("p")
                        for c in cuerpo_nota:
                            if "Lea tamb" in c.full_text:
                                cuerpo_nota.remove(c)
                            if "" == c.full_text:
                                cuerpo_nota.remove(c)
                        body = [c.full_text.strip() for c in cuerpo_nota]
                        body = [b.replace("“", '"') for b in body]
                        body = [b.replace("”", '"') for b in body]
                        tags = q.html.find("div[class=metadata] > a[href*=tag]")
                        tags = [t.text.lower() for t in tags]
                        articulo = {
                            "url": full_path_url,
                            "title": title,
                            "body": body,
                            "tags": tags,
                            "date_published": date_publish,
                            "section": section,
                            "source": "opinion",
                        }
                        # collection.insert_one(articulo)
                        try:
                            collection.insert_one(articulo)
                        except pymongo.errors.DuplicateKeyError:
                            print("Duplicate key")
            page += 1
            time.sleep(5)
            # stop = False
        else:
            stop = False
