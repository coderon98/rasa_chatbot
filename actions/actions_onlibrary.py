# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Text, Dict, Any
import os.path
import pandas as pd
from rasa_sdk.events import AllSlotsReset

from utils.elasto.elasto import ElasticModel
from utils.topic_parser.topic_parser import lemmatizer
from utils.elasto.elasto import search_in_knowledge_base
from utils.topic_parser.topic_parser import to_filter
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

score_threshold = 0.80  # seuil de fiabilité standard
base = os.path.join(os.getcwd(), "data")  # os.path.abspath(os.path.join(os.getcwd(), os.pardir))
base_path = "localhost"
base_name = "pdf_base"
base_port = 9200


class ActionGetInLibrary(Action):
    """
        Cette classe utilise le module de comparaison
        pour trouver la bonne réponse
    """

    def name(self) -> Text:
        return "action_get_in_library"

    def __init__(self):
        self.data = pd.DataFrame()
        self.eModel = ElasticModel(database_path=base_path, database_name=base_name, port=base_port)
        self.load_data()
        self.payload = list()
        self.responses = list()
        return None

    def load_data(self):
        self.data = self.eModel.read_all_pdf(os.path.join(base, "library"))
        self.eModel.payload["topic"] = self.eModel.payload["content"].apply(
            lambda x: to_filter(pd.Series(lemmatizer(x))))
        for line_id, line_content in self.eModel.payload.iterrows():
            e = \
                {
                    "path": line_content["path"],
                    "page_num": line_content["page_num"],
                    "content": line_content["content"],
                    "topic": line_content["topic"]
                }
            self.eModel.es.index(
                index=base_name,
                id=line_id,
                body=e
            )
        return None

    def load_by_attributes(self, *args):
        for elt in self.payload:
            resp = list()
            for clef, value in elt[1].items():
                if clef in args:
                    resp.append(value)
            if resp not in self.responses:
                self.responses.append(resp)
        return None

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        user_question = lemmatizer(tracker.latest_message['text'])
        self.payload = search_in_knowledge_base(database_name=base_name, database_path=base_path,
                                                length=1, content=user_question)
        self.load_by_attributes("path", "page_num")
        if self.responses is not None:
            for elt in self.responses:
                dispatcher.utter_message(text="Cette ressource matérielle est susceptible de vous aider : ")
                result = "  à partir de la page ".join(elt)
                dispatcher.utter_message(text=result)
        else:
            dispatcher.utter_message(template='utter_out_of_scope')
            dispatcher.utter_message('Veuillez contacter directement la DSI !')
        return [AllSlotsReset()]
