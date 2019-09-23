# Main application and routing logic
from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle

# Create the app
app = Flask(__name__)

# Load in the baseline model
filename = open('model_rf_sat.pkl', 'rb')
model = pickle.load(filename)


# Test data
test_data = {
            "name": "Test_Project_1",
            "category": 5,
            "blurb": "Put the decription here and bla bla bla.",
            "goal_usd": 100000,
            "campaign_duration_days": 30,
            "country": 3
}


# Create routes to post the prediction
@app.route('/')
@app.route('/', methods=['POST'])
def predict(data=None):
    # data = request.get_json(force=True)
    data=test_data

    # Change json to dataframe
    data.update((x, [y]) for x, y in data.items())
    data_df = pd.DataFrame.from_dict(data)

    drop_columns = ['name', 'blurb']

    data_df.drop(columns = drop_columns, inplace=True)

    result = model.predict(data_df)

    output = {'results': int(result[0])}

    return jsonify(results=output)

if __name__ == '__main__':
    app.run(debug=True)