# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from __future__ import print_function
import typing
import os.path
import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
# from rasa.shared.core.events import Restarted, AllSlotsReset
from rasa_sdk.events import Restarted, AllSlotsReset
from elasticsearch import Elasticsearch
from utils.elasto import elasto

base = os.getcwd()  # os.path.abspath(os.path.join(os.getcwd(), os.pardir))
json_path = os.path.join(os.path.join(os.path.join(base, "data"), "faq_data_json"), "data.json")
database_path = "localhost"
base_name = "knowledge_database"


class ActionGetKnowledge(Action):
    """
        Cette classe utilise la base de connaissance
    """

    def name(self) -> typing.Text:
        return "action_get_knowledge"

    def __init__(self):
        self.es = Elasticsearch(hosts=[database_path])
        self.json_data = pd.read_json(str(json_path))
        self.payload = list()
        self.responses = list()
        self.load_data()
        return

    def load_data(self):
        for line_id, line_content in self.json_data.iterrows():
            for elt in range(len(line_content.values)):
                self.es.index(index=base_name, id=line_id, body=line_content.values[elt])
        return

    def load_by_attributes(self, *args):
        for elt in self.payload:
            resp = list()
            for clef, value in elt[1].items():
                if clef in args:
                    resp.append(value)
            if resp not in self.responses:
                self.responses.append(resp)
        return None

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: typing.Dict[typing.Text, typing.Any]):
        self.responses.clear()
        self.payload = elasto.search_in_knowledge_base(database=database_path,
                                                       database_name=base_name,
                                                       name=tracker.get_slot("name"),
                                                       price_range=tracker.get_slot("price_range"),
                                                       breakfast_included=tracker.get_slot("breakfast_included"),
                                                       city=tracker.get_slot("city"),
                                                       free_wifi=tracker.get_slot("free_wifi"),
                                                       star_rating=tracker.get_slot("star_rating"),
                                                       swimming_pool=tracker.get_slot("")
                                                       )
        self.load_by_attributes("name", "city")
        i = 0
        for elt in self.responses:
            i = i + 1
            result = " basé à ".join(elt)
            result = str(i) + ". " + result
            dispatcher.utter_message(text=result)
        return None


class ActionRestarted(Action):
    def name(self):
        return "action_restarted"

    def run(self, dispatcher, tracker, domain):
        return [Restarted()]


class ActionSlotReset(Action):
    def name(self):
        return "action_slot_reset"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]
