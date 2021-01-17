import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import BytesIO
from elasticsearch import Elasticsearch
import spacy
import pandas as pd

spacy_model = "fr_core_news_md"
nlp = spacy.load(spacy_model)


def similarity_score(source, cible):
    source = nlp(source)
    cible = nlp(cible)
    return source.similarity(cible)


def search_answer(payload="", database_path="localhost", database_name="faq_base"):
    """
        On cherche dans la base de données, tous les champs ayant
        la valeur text : champ == text
        query_body est la requête proprement dite, on définit
        result contient des dictionnaires imbriquées contenant les différents tuples
                réponses associés à la requête
        le nombre de résultats de la requête vaut : len(result[hits][hits])
        index correspond au nom de la base de données
        doc_type correspond à la table de base
    """
    esl0 = Elasticsearch(hosts=[database_path])
    query_body = \
        {
            "query": {
                "bool": {
                    "must": {
                        "match": {
                            "question": payload
                        }
                    }
                }
            }
        }
    res = esl0.search(index=database_name, body=query_body)
    if len(res["hits"]["hits"]):
        for num, doc in enumerate(res["hits"]["hits"]):
            score = similarity_score(payload, doc["_source"]["question"])
            return [score, doc["_source"]["response"]]
    return [0, ""]


def search_in_knowledge_base(database_path="localhost", database_name="knowledge_base", length=5, **kwargs):
    field_list = list()
    value_list = list()
    for field_key, field_value in kwargs.items():
        if field_value:
            field_list.append(field_key)
            value_list.append(field_value)
    request_str = " AND ".join(value_list)
    esl = Elasticsearch(hosts=[database_path])
    query_body = \
        {
            "query": {
                "query_string": {
                    "fields": field_list,
                    "query": request_str
                }
            }
        }
    res = esl.search(index=database_name, body=query_body, size=length)
    result = list()
    for num, doc in enumerate(res["hits"]["hits"]):
        result.append([doc["_score"], doc["_source"]])
    return result


def pdf2xt(path):
    pg = pd.DataFrame()
    # Le gestionnaire de ressources
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    i = 0
    length = 0
    # Convertisseur de Texte
    device = TextConverter(rsrcmgr, retstr)
    with open(path, "rb") as fop:  # open in 'rb' mode to read PDF bytes
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fop, check_extractable=True):
            interpreter.process_page(page)
            i = i + 1
            pg = pg.append(pd.DataFrame(
                [[path, i, retstr.getvalue()[length:].decode("utf-8")]],
                columns=["path", "page_num", "content"], dtype=str
            ), ignore_index=True)
            length = len(retstr.getvalue())
        device.close()
        retstr.close()
    return pg


class ElasticModel:
    def __init__(self, database_path, database_name, port):
        self.database_path = database_path
        self.database_name = database_name
        self.port = port
        self.payload = pd.DataFrame()
        self.es = Elasticsearch(hosts=[{'host': self.database_path, 'port': self.port}])
        self.data = pd.DataFrame()

    def read_pdf(self, path):
        self.payload = self.payload.append(pdf2xt(path))
        return self.payload

    def add_to_base(self):
        for line_id, line_content in self.data.iterrows():
            e = \
                {
                    "paragraph": line_content["paragraph"],
                    "topic": line_content["topic"]
                }
            self.es.index(index=self.database_name, id=line_id, body=e)
        return None

    def read_all_pdf(self, pdfdir):
        for file in os.listdir(pdfdir):
            path = os.path.join(pdfdir, file)
            self.read_pdf(path)
        return None


if __name__ == '__main__':
    eModel = ElasticModel(database_path="localhost", database_name="pdf_base", port=9201)
    eModel.read_all_pdf(os.path.join(os.getcwd(), "library"))
