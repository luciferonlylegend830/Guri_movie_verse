import pymongo

try:
    print("डेटाबेस से कनेक्ट हो रहा है...")
    uri = "mongodb://luciferonlylegend830_db_user:Gurisingh40%123@guricluster-shard-00-00.f3yt7lg.mongodb.net:27017,guricluster-shard-00-01.f3yt7lg.mongodb.net:27017,guricluster-shard-00-02.f3yt7lg.mongodb.net:27017/?ssl=true&replicaSet=atlas-shard-0&authSource=admin&retryWrites=true&w=majority"
    
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=20000)
    db = client['guri_flix']
    col = db['files']

    r1 = col.update_many({}, {"$set": {"caption": {"$replaceAll": {"input": "$caption", "find": "@AWmedia07", "replacement": "@Gurimoviesverse"}}}})
    r2 = col.update_many({}, {"$set": {"caption": {"$replaceAll": {"input": "$caption", "find": "https://t.me/AWmedia07", "replacement": "https://t.me/Gurimoviesverse"}}}})

    print(f"सफल अपडेट हो गया! कुल बदले गए डेटा: {r1.modified_count + r2.modified_count}")

except Exception as e:
    print("एरर:", e)
  
