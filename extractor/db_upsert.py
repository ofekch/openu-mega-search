import asyncio
import os
import json
from elasticsearch import AsyncElasticsearch
from extractor import async_list_dir

HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
PORT = os.getenv('ELASTICSEARCH_PORT', '9200')
USERNAME = os.getenv('ELASTICSEARCH_USERNAME', 'elastic')
PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')
# Connect to Elasticsearch
es = AsyncElasticsearch(f"https://{HOST}:{PORT}",
                        http_auth=(USERNAME, PASSWORD),
                        verify_certs=False,
                        ssl_show_warn=False)

INDEX_MAPPING ={
    "mappings": {
        "properties": {
            "timestamp": {"type": "date"},
            "course_id": {"type": "text"},
            "hash": {"type": "text"},
            "path": {
                "type": "text",
                "fields": {
                    "hebrew": {
                        "type": "text",
                        "analyzer": "hebrew_path_analyzer"
                    }
                }
            },
            "text_heb": {
                "type": "text",
                "fields": {
                    "hebrew": {
                        "type": "text",
                        "analyzer": "hebrew"
                    }
                }
            },
            "text_heb_eng": {
                "type": "text",
                "fields": {
                    "hebrew": {
                        "type": "text",
                        "analyzer": "hebrew"
                    }
                }
            }
        }
    },
    "settings": {
        "analysis": {
            "analyzer": {
                "hebrew": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding"]
                },
                "hebrew_path_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding"]
                }
            }
        }
    }
}

async def create_index(index_name):
    if not await es.indices.exists(index=index_name):
        await es.indices.create(index=index_name, body=INDEX_MAPPING)
        print(f"Index '{index_name}' created successfully with specified mappings.")
    else:
        print(f"Index '{index_name}' already exists.")

async def upsert_doc_with_retry(index_name, doc_id, doc, retries=3):
    try:
        await es.update(index=index_name, id=doc_id, body={
            "doc": doc, "doc_as_upsert": True})
    except Exception as e:
        if retries > 0:
            await upsert_doc_with_retry(index_name, doc_id, doc, retries-1)
        else:
            raise e

async def upsert_file_to_elasticsearch(course_id, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            await upsert_doc_with_retry(course_id, data["hash"], data)
    except Exception as e:
        print(f"Failed to upsert file {file_path}", e)


async def upsert_to_elasticsearch(index_name, path):
    await create_index(index_name)
    files = await async_list_dir(path)
    print(f"Upserting {len(files)} to elastic")
    coroutines = []
    for file in files:
        coroutines.append(upsert_file_to_elasticsearch(index_name, f'{path}/{file}'))
    await asyncio.gather(*coroutines)
    await es.close()
    print(f"Finished upserting to elastic")