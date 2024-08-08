def convert_doc(document) -> dict:
    document["oid"] = str(document["_id"])
    del document["_id"]
    return document

def convert_doc_list(documents) -> list:
    return [convert_doc(doc) for doc in documents]

# document = {
#   "_id": {
#     "$oid": "66b3aa3bee6fb3d6278b70a6"
#   },
#   "project": "foo-bar2_OMT",
#   "application": "OmegaT",
#   "char_count": 3,
#   "source_lang": "en",
#   "target_lang": "zh-ZZ",
#   "mt_provider": "DeepL"
# }

# # x = convert_doc(document)

# # print(x)