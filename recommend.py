from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split


def recommend(userprofile):
    client = MongoClient('mongodb://localhost:27017')
    db = client['bigdata']
    collection = db['job_vectors']
    klist = []
    embeddinglist = []
    for document in collection.find():
        klist.append(document['job_description'])
        embeddinglist.append(document['job_vector'])

    #model搞一个
    model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
    #encode一下user数据变成向量
    sentence_embedding = model.encode(userprofile)
    #valuelist变成向量
    embeddinglist = [np.array(v, dtype=object) for v in embeddinglist]
    #find similiarity
    similarity_matrix = cosine_similarity([sentence_embedding] , embeddinglist).flatten()
    #panda去sort
    df=pd.DataFrame({"sentence":klist,"similarityscore":similarity_matrix})
    result_list = df.sort_values(by=["similarityscore"], ascending=False).head(10)["sentence"].tolist()

    ans=[]
    for collection_name in db.list_collection_names() :
        if collection_name =='job_vectors': continue
        collection = db[collection_name]
        cursor = collection.find()

        # Iterate through all documents in the collection
        for document in cursor:
            # Extract job description field
            if document.get('job_description', None) in result_list:
                ans.append((document.get('job_title', None),document.get('job_publisher', None),document.get('job_id', None),document.get('employer_name', None),document.get('job_posted_at_timestamp', None),document.get('job_employment_type', None),document.get('job_job_title', None),document.get('job_city', None),document.get('job_state', None)))
    return json.dumps(list(set(ans)))
#print(recommend("researcher  new york"))
# svm recommend

X_train = np.tile(job_vectors, (8, 1))
y_train = user_interactions[:8].flatten()

X_test = np.tile(job_vectors, (2, 1))
y_test = user_interactions[8:].flatten()

clf = SVC(probability=True)
clf.fit(X_train, y_train)

recommendations = clf.predict_proba(X_test)[:, 1]
recommendations = recommendations.reshape(2, -1)

for i in range(2):
    recommended_jobs = np.argsort(recommendations[i])[::-1]
    print(f"Recommended jobs for user {i+9}: {recommended_jobs}")
