from mongoengine import Document, ObjectIdField, StringField, DateTimeField, ListField

from datetime import datetime


class News(Document):
    meta = {"collection": "feminicidio"}
    _id = ObjectIdField(primary_key=True)
    title = StringField(required=True)
    url = StringField(required=True, unique=True)
    body = ListField(StringField(), required=True)
    tags = ListField(StringField(), required=True)
    source = StringField(required=True)
    section = StringField(required=True)
    published_at = DateTimeField(required=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
