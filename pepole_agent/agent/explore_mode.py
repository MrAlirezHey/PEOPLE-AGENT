from qdrant_client import QdrantClient,models
from qdrant_client.models import VectorParams, Distance ,Filter, FieldCondition, Range , MatchValue
import os
import sys
from openai import OpenAI
import openai
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.user_management import load_eval_data
qdrant_client = QdrantClient(
    url="https://38643683-3a7a-419f-a7c8-ed5df42e0513.us-east4-0.gcp.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Hvbo0Fz8I-LswSnPT2zVfkAWpfneGdsdxEa4we83e70",
)
openai=OpenAI(base_url="https://api.gapgpt.app/v1",api_key='sk-5Au1uXjPPG7Z7SirxaV56Xdcg8n61S7Yj2U7ULCppWw4ZDaD')

print(qdrant_client.get_collections())


collection_name='pepole_agent'
existing_collections = qdrant_client.get_collections()


if collection_name not in existing_collections.collections[0].name:
    print(f"Collection '{collection_name}' does not exist. Creating it...")
    qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE
        ),
    )
   
    qdrant_client.create_payload_index(
        collection_name=collection_name,
        field_name="field_of_interest",
        field_schema=models.PayloadSchemaType.KEYWORD,

    )

    qdrant_client.create_payload_index(
        collection_name=collection_name,
        field_name="score",
        field_schema=models.PayloadSchemaType.FLOAT
    )
else:
    print(f"Collection '{collection_name}' already exists.")
def upload_data(history):
    history=history[0]
    text = f"Summary: {history['summary']}\nEvaluation: {history['score_reason']}\nIssues and strengths: {history['issues_and_strengths']}\nScore: {history['score']}"
    response=openai.embeddings.create(
        model='text-embedding-3-small',
        input=text
    )
    
    
    points = [models.PointStruct(
        id= str(history.get('user_id')),
        vector= response.data[0].embedding,
        payload= {'user_id':history.get('user_id'),
            "score":float(history.get('score')),
            'field_of_interest':history.get('field_of_interest'),
            "text": text}
    )
    ]
    
    
    qdrant_client.upload_points(
    collection_name='pepole_agent',
    points=points
    )
    print('tttt')
def search_with_range_filter_and_vector(history):
    history = history[0]
    text = f"Summary: {history['summary']}\nEvaluation: {history['score_reason']}\nIssues and strengths: {history['issues_and_strengths']}\nScore: {history['score']}"
    print(history.get('field_of_interest'))
    
    response = openai.embeddings.create(
        model='text-embedding-3-small',
        input=text
    )
    query_vector = response.data[0].embedding

    filter_condition = Filter(
        must=[  
            #FieldCondition(
            #    key="score",  
            #    range=Range( 
            #        gte=0,
            #        lte=1
             #   )
           # ),
            FieldCondition(  
                key="field_of_interest",  
                match=MatchValue(
                    value=history.get('field_of_interest')
                )
            )
        ]
    )


    search_results = qdrant_client.query_points(
        collection_name='pepole_agent', 
        query=query_vector,  
        limit=50,  
        
        query_filter=Filter(
        must=[FieldCondition(key="field_of_interest", match=MatchValue(value=history.get('field_of_interest')))]
    ) ,
        with_payload=True
    )
    print(search_results.points)
    return search_results.points

    print(search_results.points[0].id)

upload_data(load_eval_data('019dfd3a-d4bf-4ac2-9242-20786f108ac8'))