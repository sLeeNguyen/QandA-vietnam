# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#     Copyright 2020 QandA-vietnam.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import logging
from elasticsearch import Elasticsearch

LOGGER = logging.getLogger(__name__)

es = Elasticsearch([{"host": "localhost", "port": 9200, "timeout": 60}])

default_settings = {
    "index": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
    },
    "analysis": {
        "analyzer": {
            "my_analyzer": {
                "type": "custom",
                "tokenizer": "vi_tokenizer",
                "filter": [
                    "lowercase",
                    "vi_stop",
                    "asciifolding"
                ]
            }
        }
    }
}

question_index_settings = {
    "settings": default_settings,
    "mappings": {
        "properties": {
            "question_id": {"type": "integer"},
            "title": {"type": "text", "analyzer": "my_analyzer"},
            "content": {"type": "text", "analyzer": "my_analyzer"},
            "date_create": {"type": "date"},
            "tags": {"type": "keyword"},
            "owner_id": {"type": "keyword"},
        }
    }
}

answer_index_settings = {
    "settings": default_settings,
    "mappings": {
        "properties": {
            "answer_id": {"type": "integer"},
            "content": {"type": "text", "analyzer": "my_analyzer"},
            "date_create": {"type": "date"},
            "owner_id": {"type": "keyword"},
        }
    }
}

reputation_score_index_settings = {
    "settings": default_settings,
    "mappings": {
        "properties": {
            "points_received": {"type": "integer"},
            "date_received": {"type": "date"},
            "owner_id": {"type": "keyword"},
            "username": {"type": "keyword"},
            "type_received": {"type": "keyword"}
        }
    }
}


def init():
    if not es.indices.exists(index='question'):
        es.indices.create(index='question', body=question_index_settings)
    if not es.indices.exists(index='answer'):
        es.indices.create(index='answer', body=answer_index_settings)
    if not es.indices.exists(index='reputation'):
        es.indices.create(index='reputation', body=reputation_score_index_settings)


def question_index(question_id,
                   title,
                   content,
                   date_create,
                   tags,
                   owner_id):
    """
    Create an document and save to elasticsearch.
    Document's id will be set to question_id.
    """
    body = {
        "question_id": question_id,
        "title": title,
        "content": content,
        "date_create": date_create,
        "tags": tags,
        "owner_id": owner_id
    }
    return index_document('question', document=body, doc_id=question_id)


def answer_index(answer_id,
                 content,
                 date_create,
                 owner_id):
    """
    Create an document and save to elasticsearch.
    Document's id will be set to answer_id.
    """
    body = {
        "answer_id": answer_id,
        "content": content,
        "date_create": date_create,
        "owner_id": owner_id
    }
    return index_document(index_name='answer', document=body, doc_id=answer_id)


def reputation_index(points_received,
                     date_received,
                     owner_id,
                     username,
                     type_received):
    body = {
        "points_received": points_received,
        "date_received": date_received,
        "owner_id": owner_id,
        "username": username,
        "type_received": type_received
    }
    return index_document(index_name='reputation', document=body)


def index_document(index_name, document, doc_id):
    return es.index(index=index_name, body=document, id=doc_id)


def search(query):
    pass


def question_update(question_id,
                    title,
                    content,
                    tags):
    """
    Partial update document with id is 'question_id' in 'question' index
    """
    body = {
        "script": {
            "source": "ctx._source.title=params.title;"
                      "ctx._source.content=params.content;"
                      "ctx._source.tags=params.tags",
            "params": {
                "title": title,
                "content": content,
                "tags": tags
            }
        }
    }
    return es.update(index='question', id=question_id, body=body)


def answer_update(answer_id,
                  content):
    """
    Partial update document with id is 'answer_id' in 'answer' index
    """
    body = {
        "script": {
            "source": "ctx._source.content=params.content;",
            "params": {
                "content": content
            }
        }
    }
    return es.update(index='question', id=answer_id, body=body)


def question_delete(question_id):
    """
    Delete document with id is 'question_id'
    """
    return es.delete(index='question', id=question_id)


def answer_delete(answer_id):
    """
    Delete document with id is 'answer_id'
    """
    return es.delete(index='answer', id=answer_id)
