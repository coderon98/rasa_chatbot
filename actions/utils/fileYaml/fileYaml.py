from abc import ABC
from utils.container import container


class FileYaml(ABC):
    """
        Cette classe sert de structure de base pour les fichiers yaml
        plus précisement les fichiers data et les fichiers domain
    """

    def __init__(self):
        """

        :rtype: FileYaml
        """
        self.version = "2.0"
        self.payload = "None"
        return

    def parse(self, filename):
        pass


class FileYamlData(FileYaml):
    """
        Cette classe sert à créer les objets servant à entraîner
        le modèle à la compréhension du langage naturel
    """

    def __init__(self):
        FileYaml.__init__(self)
        self.nlu = list()
        self.stories = list()
        self.rules = list()
        return

    def parse(self, filename):
        """
            Cette fonction analyse un fichier data et charge
             son contenu dans l'objet self
        :param filename:
        :return:
        """
        import ruamel.yaml as ryaml
        ryaml = ryaml.YAML()
        with open(filename, 'r') as input_stream:
            content = ryaml.load(input_stream)
        self.version = content['version']
        """
            Traitement des données de type NLU
        """
        obj = None
        if 'nlu' in content:
            for elt in content['nlu']:
                for key, value in elt.items():
                    if key == "intent":
                        obj = container.Intent(name=value)
                        continue
                    elif key == "regex":
                        obj = container.Regex(name=value)
                        continue
                    elif key == "lookup":
                        obj = container.Lookup(name=value)
                        continue
                    elif key == "synonym":
                        obj = container.Synonym(name=value)
                        continue
                    elif key == "examples":
                        liste = str(value).replace("- ", "").split("\n")
                        obj.examples = liste[:len(liste) - 1]
                        self.nlu.append(obj)
        """
            Traitement des données de type Story 
        """
        if 'stories' in content:
            for elt in content["stories"]:
                for key, value in elt.items():
                    if key == "story":
                        obj = container.Story(value)
                        continue
                    elif key == "steps":
                        for elt2 in value:
                            for cle, valeur in elt2.items():
                                s = container.Step(datatype=cle, value=valeur)
                                obj.add(s)
                        self.stories.append(obj)
        """
            Traitement des données de type Rule
        """
        if 'rules' in content:
            for elt in content["rules"]:
                for key, value in elt.items():
                    if key == "rule":
                        obj = container.Rule(value)
                        continue
                    elif key == "steps":
                        for elt2 in value:
                            for cle, valeur in elt2.items():
                                s = container.Step(datatype=cle, value=valeur)
                                obj.add(s)
                        self.rules.append(obj)
            return

    def add_story(self, story):
        self.stories.append(story)
        return True

    def erase_story(self, story):
        self.stories.remove(story)
        return True

    def add_rule(self, rule):
        self.rules.append(rule)
        return True

    def erase_rule(self, rule):
        self.rules.remove(rule)
        return True

    def add_nlu(self, nlu):
        self.nlu.append(nlu)
        return True

    def erase_nlu(self, nlu):
        self.nlu.remove(nlu)
        return True

    def __str__(self):
        result = "version: \"2.0\"\n"
        result += "\nnlu:\n"
        for elt in self.nlu:
            result += str(elt)
        result += "\nstories:\n"
        for elt in self.stories:
            result += str(elt)
        result += "\nrules:\n"
        for elt in self.rules:
            result += str(elt)
        return result


class FileYamlDomain(FileYaml):
    """
        Cette classe sert à configurer les fichiers de domain
        C'est une sorte de fichier d'entête qui stocke les listes d'éléments
    """

    def __init__(self, responses=None, forms=None):
        FileYaml.__init__(self)
        self.intents = list()
        self.actions = list()
        self.entities = list()
        self.slots = list()
        self.sessions_config = ['session_expiration_time: 60', 'carry_over_slots_to_new_session: true']
        self.responses = responses
        if self.responses is None:
            self.responses = container.Response()
        self.forms = forms
        if self.forms is None:
            self.forms = container.Forms()
        return

    def parse(self, filename):
        import ruamel.yaml as ryaml
        ryaml = ryaml.YAML()
        with open(filename, 'r') as input_stream:
            content = ryaml.load(input_stream)
        if "version" in content:
            self.version = content['version']
        """
            Traitement de la liste d'intents
                                   d'entities
                                   d'actions
                                   de session_config
        """
        if "intents" in content:
            self.intents = content["intents"]
        if "entities" in content:
            self.entities = content["entities"]
        if "actions" in content:
            self.actions = content["actions"]
        """
            Traitement des session_config
             
        for key, value in content["session_config"].items():
            self.sessions_config.append(key+": "+str(value))
        """
        """
            Traitement des slots
        """
        s = container.Slot(name="None", slot_type="None")
        if "slots" in content:
            for key, value in content["slots"].items():
                for cle, valeur in value.items():
                    if cle == "type":
                        s = container.Slot(name=key, slot_type=valeur)
                self.add_slot(s)
        """
            Traitement des responses
        """
        if "responses" in content:
            for key, value in content["responses"].items():
                utter = container.Utterance(name=key)
                for elt in value:
                    utter.add(elt["text"])
                self.responses.add(utter)
        return

    def add_slot(self, slot):
        self.slots.append(slot)
        return True

    def erase_slot(self, slot):
        self.slots.remove(slot)
        return True

    def add_action(self, action):
        self.actions.append(action)
        return True

    def erase_action(self, action):
        self.actions.remove(action)
        return True

    def add_entity(self, entity):
        self.entities.append(entity)
        return True

    def erase_entity(self, entity):
        self.entities.remove(entity)
        return True

    def add_intent(self, intent):
        self.intents.append(intent)
        return True

    def erase_intent(self, intent):
        self.intents.remove(intent)
        return True

    def add_session_config(self, session_config):
        self.sessions_config.append(session_config)
        return True

    def erase_session_config(self, session_config):
        self.sessions_config.remove(session_config)
        return True

    def __str__(self):
        result = "version: \"2.0\"\n"
        result += "\nintents:\n"
        for elt in self.intents:
            result += "  - " + elt + "\n"
        result += "\nactions:\n"
        for elt in self.actions:
            result += "  - " + elt + "\n"
        result += "\nentities:\n"
        for elt in self.entities:
            result += "  - " + elt + "\n"
        result += "\nslots:\n"
        for elt in self.slots:
            result += str(elt)
        result += "\n" + str(self.responses)
        result += "\nsession_config:\n"
        for elt in self.sessions_config:
            result += "  " + elt + "\n"
        return result
