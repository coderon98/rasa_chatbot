from abc import ABC


class Step:
    """
        Cette classe définit les étapes de la discussion,
         Dans datatype on peut avoir des :
        - intent
        - action
        - checkpoint
        - ...
    """

    def __init__(self, datatype, value):
        self.datatype = datatype
        self.value = value
        self.payload = self.datatype + ": " + self.value
        return

    def __str__(self):
        return "{0}".format(self.payload)


class AbstractSet(ABC):
    """
        Classe abstraite permettant de configurer les dialogues
        payload contiendra le résultat à stocker sous la forme d'une châine de caractères
        setOfStep est la liste qui contiendra les différents step(étape du dialogue)
        title: est un commentaire pour expliquer rapidement le scénario
    """

    def __init__(self):
        self.title = "None"
        self.payload = "None"
        self.setOfStep = list()
        return

    def add(self, step):
        pass

    def erase(self, step):
        pass


class Story(AbstractSet):
    """
        Cette classe permet de configurer les potentiels schémas de discussions
        Sa priorité est faible par rapport aux rules.
    """

    def __init__(self, title):
        AbstractSet.__init__(self)
        self.title = title
        return

    def add(self, step):
        self.setOfStep.append(step.payload)
        return True

    def erase(self, step):
        self.setOfStep.remove(step.payload)
        return True

    def __str__(self):
        result = "- story: {0}\n  steps:\n".format(self.title)
        for elt in self.setOfStep:
            result += "  - " + elt + "\n"
        return result


class Rule(AbstractSet):
    """
        Cette classe permet de configurer les potentiels schémas de discussions
        Sa priorité est forte  par rapport aux stories.
        Elle est dépédante d'une condition (Objet Step)
    """

    def __init__(self, title, condition="None"):
        AbstractSet.__init__(self)
        self.title = title
        self.condition = condition
        return

    def add(self, step):
        self.setOfStep.append(step.payload)
        return True

    def erase(self, step):
        self.setOfStep.remove(step.payload)
        return True

    def __str__(self):
        result = "- rule: {0}\n  steps:\n".format(self.title)
        for elt in self.setOfStep:
            result += "  - " + elt + "\n"
        return result


class Intent:
    """
        Cette classe définit les intents avec le niveau de précision nécessaire aux NLU
    """

    def __init__(self, name):
        self.name = name
        self.examples = list()
        return

    def add(self, example):
        self.examples.append(example)
        return True

    def erase(self, example):
        self.examples.remove(example)
        return True

    def __str__(self):
        result = "- intent: {0}\n  examples: |\n".format(self.name)
        for elt in self.examples:
            result += "   - " + elt + "\n"
        return result


class Lookup:
    """
        Cette classe définit les lookups avec le niveau de précision nécessaire aux NLU
    """

    def __init__(self, name):
        self.name = name
        self.examples = list()
        return

    def add(self, example):
        self.examples.append(example)
        return True

    def erase(self, example):
        self.examples.remove(example)
        return True

    def __str__(self):
        result = "- lookup: {0}\n  examples: |\n".format(self.name)
        for elt in self.examples:
            result += "   - " + elt + "\n"
        return result


class Synonym:
    """
        Cette classe définit les intents avec le niveau de précision nécessaire aux NLU
    """

    def __init__(self, name):
        self.name = name
        self.examples = list()
        return

    def add(self, example):
        self.examples.append(example)
        return True

    def erase(self, example):
        self.examples.remove(example)
        return True

    def __str__(self):
        result = "- synonym: {0}\n  examples: |\n".format(self.name)
        for elt in self.examples:
            result += "   - " + elt + "\n"
        return result


class Regex:
    """
        Cette classe définit les intents avec le niveau de précision nécessaire aux NLU
    """

    def __init__(self, name):
        self.name = name
        self.examples = list()
        return

    def add(self, example):
        self.examples.append(example)
        return True

    def erase(self, example):
        self.examples.remove(example)
        return True

    def __str__(self):
        result = "- regex: {0}\n  examples: |\n".format(self.name)
        for elt in self.examples:
            result += "   - " + elt + "\n"
        return result


class Nlu:
    """
        C'est la classe qui stocke les données de compréhension du langage naturel
  nlu:
  - intent: greet
  examples: |
    - hey
    - bonjour
    - salut
    - bonjour par ici
    setOfX stocke des objets
    - intent
    - synonym
    - regex
    - lookup
    """

    def __init__(self):
        self.setOfX = list()
        return

    def add(self, obj):
        self.setOfX.append(obj)
        return True

    def erase(self, obj):
        self.setOfX.remove(obj)
        return True

    def __str__(self):
        result = ""
        for elt in self.setOfX:
            result += str(elt)
        return result


class Utterance:
    """
       Eléments de réponses associées indirectement à un sujet de conversion donné(intent)
    """

    def __init__(self, name):
        self.name = name
        self.examples = list()
        return

    def add(self, example):
        self.examples.append(example)
        return True

    def erase(self, example):
        self.examples.remove(example)
        return True

    def __str__(self):
        result = "  {0}:\n".format(self.name)
        for elt in self.examples:
            result += "  - text: \"" + elt + "\"\n"
        return result


class Response:
    def __init__(self):
        self.setOfUtterance = list()
        return

    def add(self, obj):
        self.setOfUtterance.append(obj)
        return True

    def erase(self, obj):
        self.setOfUtterance.remove(obj)
        return True

    def __str__(self):
        result = "responses:\n"
        for elt in self.setOfUtterance:
            result += str(elt)
        return result


class Field:
    """
       Cette classe sert à stocker un champ de formulaire
    """

    def __init__(self, name, field_type, entity):
        self.name = name
        self.field_type = field_type
        self.entity = entity
        return

    def __str__(self):
        resultat = "    " + self.name + ":\n"
        resultat += "      - type: " + self.field_type + "\n"
        resultat += "        entity: " + self.entity + "\n"
        return resultat


class Form:
    """
        Cette classe sert à manipulier un seul formulaire
        Le formulaire est constitué de plusieurs champs
    """

    def __init__(self, name):
        self.name = name
        self.setOfField = list()
        return

    def add(self, field):
        self.setOfField.append(field)
        return True

    def erase(self, field):
        self.setOfField.remove(field)
        return

    def __str__(self):
        result = "  " + self.name + ":\n"
        for elt in self.setOfField:
            result += str(elt)
        return result


class Forms:
    """
        Cette classe stocke l'ensemble des formulaires
    """

    def __init__(self):
        self.setOfForm = list()
        return

    def add(self, form):
        self.setOfForm.append(form)
        return True

    def erase(self, form):
        self.setOfForm.remove(form)
        return True

    def __str__(self):
        result = "forms:\n"
        for elt in self.setOfForm:
            result += str(elt)
        return result


class Slot:
    """
        Cette classe stocke les slots dans le bon format
    """
    def __init__(self, name, slot_type):
        self.name = name
        self.slot_type = slot_type
        return

    def __str__(self):
        result = "  "+self.name+":\n"
        result += "    type: "+self.slot_type+"\n"
        return result
