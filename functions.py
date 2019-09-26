"""
Custom data goals:
1 {#} of campaigns raising more than {persons amount} have been successful
2 {#}% of campaigns in {persons category} are successful
3 campaigns in {persons category} raise an average of {$$$} successfully
4 successful campaigns raising over {persons amount} have an average duration of {##} days
5 campaigns raising (persons amount) have an average number of {####} backers
6 successful campaigns in {persons category} raise an average of {$$$$} above their goal
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

def predict_proba(model, df):
    positive_class = 'successful'
    positive_class_index = 1 

    # Call model for prediction
    pred = model.predict(df)
    predict = pred[0]
    
    # Get predicted probability
    pred_proba = model.predict_proba(df)[0,positive_class_index]

    probability = pred_proba * 100

    probability = round(probability)

    # Return prediction and probability
    # output1 = f'State is {probability:.0f}% likely to be successful'

    return probability


# Functions for querying custom stats
def get_query(query, cursor):
    cursor.execute(query)
    return(cursor.fetchall()[0][0])


def custom_stats(category, goal, cursor):
    # Create queries for each data goal

    goal_1 = f'SELECT COUNT(*) FROM clean_data WHERE target = "successful" AND monetaryGoal > "{goal}";'

    goal_2 = f'SELECT COUNT(*) / (SELECT COUNT(*) FROM clean_data WHERE categories = "{category}") FROM clean_data WHERE target = "successful" AND categories = "{category}";'

    goal_3 = f'SELECT AVG(usd_pledged) FROM clean_data WHERE target = "successful" AND categories = "{category}";'
    
    goal_4 = f'SELECT AVG(duration) FROM clean_data WHERE target = "successful" AND monetaryGoal > "{goal}";'

    goal_min = goal * 0.9
    goal_max = goal * 1.1
    goal_5 = f'SELECT AVG(backers_count) FROM clean_data WHERE target = "successful" AND (monetaryGoal > "{goal_min}" AND monetaryGoal < "{goal_max}");'

    # Similar to number 3, consider revising 3 to another stat
    goal_6 = f'SELECT AVG(usd_pledged - monetaryGoal) AS diff FROM clean_data WHERE target = "successful" AND categories = "{category}";'

    queries = [goal_1, goal_2, goal_3, goal_4, goal_5, goal_6]

    results = []
    for query in queries:
        x = get_query(query, cursor)
        results.append(x)
    
    return results


def nlp_df(data_df):
    
    df = data_df.copy()
    
    df['name_description'] = df['campaignName'].apply(lambda x: ' '.join(x.split('-'))) + ' ' + df.description
    
    features = ['name_description', 'categories', 'duration'
            , 'monetaryGoal', 'country']
    
    df = df[features]
    
    # vectorizer
    tfidf_vector = TfidfVectorizer(stop_words='english', max_features=5000)

    # tokenize name
    train_text = df['name_description']
    train_text = tfidf_vector.fit_transform(train_text)
    
    # create name matrix
    train_text_matrix = train_text.todense()
    
    # create df from name matrix
    train_text_matrix_df = pd.DataFrame(train_text_matrix, columns=tfidf_vector.get_feature_names())

    # add id for merge
    df['id'] = list(range(len(df)))
    train_text_matrix_df['id'] = list(range(len(df)))

    # merge train with name matrix
    df_merged = df.merge(train_text_matrix_df, on='id', how='inner')
    
    # drop unnecessary columns
    df_merged = df.drop(columns=['name_description', 'id'])
    
    assert len(df_merged) == len(data_df)
    
    return df_merged





