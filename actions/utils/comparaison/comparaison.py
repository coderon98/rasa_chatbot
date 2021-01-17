import string
import numpy as np
import pandas as pd


def create_dataframe(matrix, tokens):
    doc_names = ['doc_{i + 1}' for i, _ in enumerate(matrix)]
    df = pd.DataFrame(data=matrix, index=doc_names, columns=tokens)
    return df


def jaccard_similarity(source, cible):
    """
        On enlève la ponctuation et on met le texte en minuscule
    """
    source = source.lower()
    cible = cible.lower()
    source = ''.join([i for i in source if i not in string.punctuation])
    cible = ''.join([i for i in cible if i not in string.punctuation])
    s = set(source.split())
    c = set(cible.split())
    resultat = (float(len(s.intersection(c))) / float(len((s.union(c)))))
    return resultat


def distance_de_levenstein(source, cible):
    """
        On enlève la ponctuation et on met le texte en minuscule
    """
    source = source.lower()
    cible = cible.lower()
    source = ''.join([i for i in source if i not in string.punctuation])
    cible = ''.join([i for i in cible if i not in string.punctuation])
    if len(source) == 0 or len(cible) == 0:
        return 0
    tab = np.zeros((len(source) + 1, len(cible) + 1), dtype=int)
    cout = np.ones((len(source), len(cible)), dtype=int)

    for i in range(len(source) + 1):
        tab[i][0] = i
    for j in range(len(cible) + 1):
        tab[0][j] = j

    for i in range(len(source)):
        for j in range(len(cible)):
            if source[i] == cible[j]:
                cout[i][j] = 0
    """
        Le minimum entre ces éléments
        L’élément directement au-dessus et on ajoute 1 : tab[i-1, j] + 1. (effacement)
        L’élément directement avant et on ajoute 1 : tab[i, j-1] + 1. (insertion)
        L’élément diagonal précédent plus le coût : tab[i-1, j-1] + cout(i-1, j-1). (substitution)
    """
    for i in range(1, len(source) + 1, 1):
        for j in range(1, len(cible) + 1, 1):
            tab[i][j] = min(min((tab[i - 1][j] + 1), (tab[i][j - 1] + 1)),
                            (tab[i - 1][j - 1] + cout[i - 1][j - 1]))
    resultat = 1 - (tab[len(source)][len(cible)] / max(len(source), len(cible)))
    return resultat


def similar_text(source, cible):
    """
        On enlève la ponctuation et on met le texte en minuscule
    """
    source = source.lower()
    cible = cible.lower()
    source = ''.join([i for i in source if i not in string.punctuation])
    cible = ''.join([i for i in cible if i not in string.punctuation])
    i = j = similar = 0
    s = len(source)
    c = len(cible)
    if s > c:
        temp = source
        source = cible
        cible = temp
    while (i < s) and (j < len(cible)):
        if i < len(source) and j < len(cible):
            if source[i] == cible[j]:
                i = i + 1
                j = j + 1
                similar = similar + 1
            elif s < c:
                s = s + 1
                j = j + 1
            elif s > c:
                s = s - 1
                i = i + 1
            else:
                i = i + 1
                j = j + 1
        elif s < c:
            s = s + 1
            j = j + 1
        elif s > c:
            s = s - 1
            i = i + 1
        else:
            i = i + 1
            j = j + 1
    resultat = similar / max(s, c)
    return resultat


def cosine_similarity(source, cible):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    data = [source, cible]
    Tfidf_vect = TfidfVectorizer()
    vector_matrix = Tfidf_vect.fit_transform(data)
    tokens = Tfidf_vect.get_feature_names()
    cosine_similarity_matrix = cosine_similarity(vector_matrix)
    return create_dataframe(cosine_similarity_matrix, data).to_numpy()[0][1]


def cosine_similarity2(source, cible):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    data = [source, cible]
    count_vectorizer = CountVectorizer()
    vector_matrix = count_vectorizer.fit_transform(data)
    tokens = count_vectorizer.get_feature_names()
    cosine_similarity_matrix = cosine_similarity(vector_matrix)
    return create_dataframe(cosine_similarity_matrix, data).to_numpy()[0][1]


if __name__ == '__main__':
    print(cosine_similarity("La voiture est bleue", "La voiture est verte"))
    print(cosine_similarity2("La voiture est bleue", "La voiture est verte"))
