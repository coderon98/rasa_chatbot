import spacy
import torch
import numpy as np
import pandas as pd
from spacy import displacy
from transformers import *
from nltk.stem.snowball import SnowballStemmer

fr = "french"
stemmer = SnowballStemmer(language=fr)
spacy_model = "fr_core_news_md"
nlp = spacy.load(spacy_model)

test = "Bouygues a eu une coupure de réseau à Marseille"
test_2 = "Le réseau sera bientot rétabli à Marseille"
test_3 = "La panne réseau affecte plusieurs utilisateurs de l'opérateur"
test_4 = "Il fait 18 degrés ici"
r = [test_2, test_3, test_4]


def return_token(sentence):
    # Tokeniser la phrase
    doc = nlp(sentence)
    # Retourner le texte de chaque token
    return [X.text for X in doc]


def return_token_sent(sentence):
    # Tokeniser la phrase
    doc = nlp(sentence)
    # Retourner le texte de chaque phrase
    return [X.text for X in doc.sents]


def return_stem(sentence):
    doc = nlp(sentence)
    return [stemmer.stem(X.text) for X in doc]


def return_ner(sentence):
    # Tokeniser la phrase
    doc = nlp(sentence)
    # Retourner le texte et le label pour chaque entité
    return [(X.text, X.label_) for X in doc.ents]


def return_pos(sentence):
    # Tokeniser la phrase
    doc = nlp(sentence)
    # Retourner les étiquettes de chaque token
    return [(X, X.pos_) for X in doc]


def return_word_embedding(sentence):
    # Tokeniser la phrase
    doc = nlp(sentence)
    # Retourner le vecteur lié à chaque token
    return [X.vector for X in doc]


def return_mean_embedding(sentence):
    # Tokeniser la phrase
    doc = nlp(sentence)
    # Retourner la moyenne des vecteurs pour chaque phrase
    return np.mean([X.vector for X in doc], axis=0)


def return_euclid_distance(source, cibles):
    result = list()
    for elt in cibles:
        # result.append(np.linalg.norm(return_mean_embedding(source) - return_mean_embedding(elt)))
        result.append(nlp(source).similarity(nlp(elt)))
    return result


def visualize_text(text):
    doc = nlp(text)
    displacy.serve(doc, style="dep")
    return None


def visualize_paragraph(paragraph):
    paragraph = str(paragraph)
    doc = nlp(paragraph)
    sentence_spans = list(doc.sents)
    displacy.serve(sentence_spans, style="dep")
    return None


def is_chain(source, cible):
    # Tokeniser, Model
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    model = BertForNextSentencePrediction.from_pretrained('bert-base-multilingual-cased')
    # model.eval()
    # Texte tokenisé
    tokenized_text = tokenizer.tokenize(source)
    tgt = tokenizer.tokenize(cible)
    segments_ids = [i - i for i in range(len(tokenized_text))]
    second = [j - j + 1 for j in range(len(tgt))]
    tokenized_text.extend(tgt)
    # Convertir le texte en indexs
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    print(indexed_tokens)
    segments_ids.extend(second)
    print(segments_ids)
    # Transformer en tenseurs
    tokens_tensor = torch.tensor([indexed_tokens])
    segments_tensors = torch.tensor([segments_ids])
    predictions = model(tokens_tensor, segments_tensors)
    if np.argmax(predictions) == 0:
        return True
    else:
        return False


def is_chain2(source, cible):
    import tensorflow as tf
    from transformers import BertTokenizer, TFBertForNextSentencePrediction
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = TFBertForNextSentencePrediction.from_pretrained('bert-base-uncased')
    encoding = tokenizer(source, cible, return_tensors='tf')
    logs = model(encoding['input_ids'], token_type_ids=encoding['token_type_ids'])
    print(logs)


def lemmatizer(t):
    t = t.lower()
    doc = nlp(t)
    return " ".join(
        [token.lemma_ for token in doc if token.pos_ in ["NOUN", "VERB", "PROPN", "AUX"]])


def to_filter(dtf, number_of_topics=3):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    # the vectorizer object will be used to transform text to vector form
    vectorizer = CountVectorizer(min_df=1, max_df=10)
    # apply transformation
    tf = vectorizer.fit_transform(dtf).toarray()
    # tf_feature_names tells us what word each column in the matric represents
    tf_feature_names = vectorizer.get_feature_names()
    model = LatentDirichletAllocation(n_components=number_of_topics, random_state=0)
    model.fit(tf)
    return " ".join(tf_feature_names)


def to_filter2(dtf, number_of_topics=3):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import NMF
    # the vectorizer object will be used to transform text to vector form
    vectorizer = CountVectorizer(min_df=1, max_df=10)
    # apply transformation
    tf = vectorizer.fit_transform(dtf).toarray()
    # tf_feature_names tells us what word each column in the matric represents
    tf_feature_names = vectorizer.get_feature_names()
    model = NMF(n_components=number_of_topics, random_state=0, alpha=.1, l1_ratio=.5, max_iter=1000)
    model.fit(tf)
    return " ".join(tf_feature_names)


if __name__ == '__main__':
    text = """
        Nous avons couvert dans cet article de nombreuses applications 
        de Traitement Automatique du Langage Naturel en Français. Bien 
        que de très nombreuses ressources existent exclusivement en Anglais,
        il existe tout de même des outils intéressants pour le Français, 
        que votre problème de TAL concerne une classification de texte 
        par Tf-IdF, ou une approche par Deep Learning ou Transformers.
        """
    # p = lemmatizer(text)
    # p = to_filter(pd.Series(p))
    is_chain2("N'utilisez pas de parenthèses pour appeler assert comme une fonction",
              "C'est une instruction")
