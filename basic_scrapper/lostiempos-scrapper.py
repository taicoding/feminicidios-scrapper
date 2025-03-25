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

base_url = "https://www.lostiempos.com"
urls = [
    "https://www.lostiempos.com/etiqueta/feminicidio",
    "https://www.lostiempos.com/etiqueta/feminicidios",
]
session = HTMLSession()


for url in urls:
    stop_count = 0
    stop = True
    page = 0
    while stop:
        request_url = url + "?page={}".format(page)
        print(request_url)
        r = session.get(request_url)
        if r.status_code == 200:
            print(r.status_code)
            div_result = r.html.find("div[class *= view-etiquetas]")[0]
            div_article = div_result.find("div[class *= views-field-title]")

            for div in div_article:
                notas = div.find("a")
                link_nota = notas[0].attrs["href"]
                full_path_url = base_url + link_nota

                if (
                    ("/economia/" not in full_path_url)
                    and ("/opinion/" not in full_path_url)
                    and ("/tendencias/" not in full_path_url)
                    and ("/mundo/" not in full_path_url)
                ):
                    print(full_path_url)
                    q = session.get(full_path_url)
                    if q.status_code == 200:
                        title = q.html.find("h1")
                        title = title[0].full_text.strip()
                        title = title.replace("“", '"')
                        title = title.replace("”", '"')
                        link_nota_split = link_nota.split("/")
                        section = link_nota_split[2]
                        date_publish = link_nota_split[3]
                        date_publish = datetime.strptime(date_publish, "%Y%m%d")
                        cuerpo_nota = q.html.find("p")
                        for c in cuerpo_nota:
                            if "Más en" in c.full_text:
                                cuerpo_nota.remove(c)
                            if " " == c.full_text:
                                cuerpo_nota.remove(c)
                            if "" == c.full_text:
                                cuerpo_nota.remove(c)
                        body = [
                            c.full_text.replace("\xa0", "").strip() for c in cuerpo_nota
                        ]
                        body = [b.replace("“", '"') for b in body]
                        body = [b.replace("”", '"') for b in body]
                        tags = q.html.find("ul[class=field-items] > li > a")
                        tags = [t.text.lower() for t in tags]
                        articulo = {
                            "url": full_path_url,
                            "title": title,
                            "body": body,
                            "tags": tags,
                            "date_published": date_publish,
                            "section": section,
                            "source": "lostiempos",
                        }
                        try:
                            collection.insert_one(articulo)
                        except pymongo.errors.DuplicateKeyError:
                            print("Duplicate key")
                            stop_count += 1
            page += 1
            time.sleep(5)
            # stop = False
        else:
            if stop_count > 5:
                stop = False

            stop = False
