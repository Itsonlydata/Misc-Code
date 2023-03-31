import pandas as pd
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, MiniBatchNMF, LatentDirichletAllocation

f_name = r"C:\Users\Stefan\Documents\MiscWorkProjects\Textual Information_Ning_UTD.csv"
df = pd.read_csv(f_name)

df_a1 = df['attention_1']
df_a2 = df['attention_2']
df_pbe = df['pbe_2']
df_know = df['knowledge_1']

data = df_a1

data.dropna(inplace=True)

topics = list(range(1, 10, 1))
topwords = 3

tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english')
tfidf = tfidf_vectorizer.fit_transform(data)

tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english')
tf = tf_vectorizer.fit_transform(data)

for i in topics:
    print("")
    print(f"Top Five Terms for {i} Topic(s).")
    lda = LatentDirichletAllocation(
        n_components=i,
        max_iter=5,
        learning_method="online",
        learning_offset=50.0,
        random_state=0,
    )

    lda.fit(tf)
    tf_feature_names = tf_vectorizer.get_feature_names_out()

    for topic_idx, topic in enumerate(lda.components_):
        top_features_ind = topic.argsort()[: -topwords -1 : -1]
        top_features = [tf_feature_names[i] for i in top_features_ind]
        print(top_features)