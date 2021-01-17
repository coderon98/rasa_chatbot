# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import typing
import os.path
import pandas as pd
from pandas.errors import EmptyDataError
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from elasticsearch import Elasticsearch
from utils.elasto import elasto

score_threshold = 0.80  # seuil de fiabilité standard
base = os.getcwd()  # os.path.abspath(os.path.join(os.getcwd(), os.pardir))
csv_path = os.path.join(os.path.join(base, "data"), "faq_data_csv")
base_path = "localhost"


class ActionGetFAQAnswer(Action):
    """
        Cette classe utilise le module de comparaison
        pour trouver la bonne réponse
    """

    def name(self) -> typing.Text:
        return "action_get_faq_answer"

    def __init__(self):
        self.es = Elasticsearch(hosts=[base_path])
        for file in os.listdir(csv_path):
            path = os.path.join(csv_path, file)
            try:
                self.csv_data = pd.read_csv(str(path), sep=';')
            except EmptyDataError:
                print("Veuillez vérifier la validité de vos fichiers csv !")
                print("Le séparateur utilisé ici est le point-virgule ';'.")
            else:
                self.load_data()
        return

    def load_data(self):
        for line_id, line_content in self.csv_data.iterrows():
            e = \
                {
                    "question": line_content["question"],
                    "response": line_content["response"]
                }
            self.es.index(index='faq_base', id=line_id, body=e)
        return

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
                  domain: typing.Dict[typing.Text, typing.Any]):
        user_question = tracker.latest_message['text']
        score, resp = elasto.search_answer(payload=user_question, database_path=base_path)
        if score > score_threshold:
            dispatcher.utter_message(resp)
        else:
            return [SlotSet("not_found_in_faq", "True")]
        return [SlotSet("not_found_in_faq", "False")]
