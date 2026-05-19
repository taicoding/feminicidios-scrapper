from mongoengine import (
    Document,
    ObjectIdField,
    StringField,
    DateTimeField,
    ListField,
    BooleanField,
)

from datetime import datetime


class News(Document):
    meta = {"collection": "feminicidio"}
    title = StringField(required=True)
    url = StringField(required=True, unique=True)
    body = ListField(StringField(), required=True)
    tags = ListField(StringField(), required=True)
    source = StringField(required=True)
    section = StringField(required=True)
    published_at = DateTimeField(required=True)
    llm_processed = BooleanField(default=False)
    llm_model = StringField(default="")
    flagged = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
