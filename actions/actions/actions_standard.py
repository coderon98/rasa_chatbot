# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Text, Dict, Any
import os.path
import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from utils.comparaison import comparaison

score_threshold = 0.80  # seuil de fiabilité standard
base = os.getcwd()  # os.path.abspath(os.path.join(os.getcwd(), os.pardir))
csv_path = os.path.join(os.path.join(os.path.join(base, "data"), "faq_data_csv"), "data.csv")


class ActionGetFAQAnswer(Action):
    """
        Cette classe utilise le module de comparaison
        pour trouver la bonne réponse
    """

    def name(self) -> Text:
        return "action_get_faq_answer"

    def __init__(self):
        self.csv_data = pd.read_csv(str(csv_path))
        self.response = ''
        self.confidence = 0.0
        self.ind = 0
        return

    def query_answer(self, quest):
        self.confidence = 0.0
        self.ind = 0
        for line_id, line_content in self.csv_data.iterrows():
            value1 = comparaison.similar_text(quest, line_content["question"])
            value2 = comparaison.jaccard_similarity(quest, line_content["question"])
            value3 = comparaison.distance_de_levenstein(quest, line_content["question"])
            value4 = comparaison.cosine_similarity(quest, line_content["question"])
            value5 = comparaison.cosine_similarity2(quest, line_content["question"])
            maxi = max(value5, value4, value3, value2, value1)
            if maxi > self.confidence:
                self.confidence = maxi
                self.response = line_content["response"]
                self.ind = line_id
                if self.confidence == 1.0:
                    break
        return self.confidence, self.response

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        user_question = tracker.latest_message['text']
        score, resp = self.query_answer(user_question)
        print("La question de l'utilisateur :", user_question)
        print("Compatibilité avec la question n°:{} avec la confidence: {}".format(self.ind, score))
        if score > score_threshold:
            dispatcher.utter_message(resp)
        else:
            return [SlotSet("not_found_in_faq","True")]
        return None
