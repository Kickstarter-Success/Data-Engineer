# Main application and routing logic
from flask import Flask, render_template, request, jsonify
from decouple import config
from functions import get_query, custom_stats
from visualizations import make_visuals
from mysql.connector.cursor import MySQLCursorPrepared
import os
import pandas as pd
import mysql.connector
import pickle

# Remove later ##
flipped = {0: 'Space Exploration',
 1: 'Wearables',
 2: 'Hardware',
 3: 'Software',
 4: 'Web',
 5: 'Sound',
 6: "Children's Books",
 7: 'Calendars',
 8: 'Art Books',
 9: 'Fiction',
 10: 'Nature',
 11: 'People',
 12: 'Letterpress',
 13: 'Literary Journals',
 14: 'Nonfiction',
 15: 'Footwear',
 16: 'Jewelry',
 17: 'Pet Fashion',
 18: 'Ready-to-wear',
 19: 'Apparel',
 20: 'Animation',
 21: 'Comedy',
 22: 'Documentary',
 23: 'Action',
 24: 'Textiles',
 25: 'Sculpture',
 26: 'Public Art',
 27: 'Performance Art',
 28: 'Crafts',
 29: 'DIY',
 30: 'Woodworking',
 31: 'Knitting',
 32: 'Candles',
 33: 'Quilts',
 34: 'Glass',
 35: 'Embroidery',
 36: 'Crochet',
 37: 'Pottery',
 38: 'Product Design',
 39: 'Graphic Design',
 40: 'Design',
 41: 'Typography',
 42: 'Interactive Design',
 43: 'Civic Design',
 44: 'Architecture',
 45: 'Shorts',
 46: 'Narrative Film',
 47: 'Film & Video',
 48: 'Webseries',
 49: 'Thrillers',
 50: 'Family',
 51: 'Experimental',
 52: 'Science Fiction',
 53: 'Fantasy',
 54: 'Music Videos',
 55: 'Horror',
 56: 'Movie Theaters',
 57: 'Drama',
 58: 'Romance',
 59: 'Television',
 60: 'Festivals',
 61: 'Food',
 62: 'Small Batch',
 63: "Farmer's Markets",
 64: 'Restaurants',
 65: 'Farms',
 66: 'Drinks',
 67: 'Events',
 68: 'Food Trucks',
 69: 'Cookbooks',
 70: 'Vegan',
 71: 'Spaces',
 72: 'Community Gardens',
 73: 'Bacon',
 74: 'Fashion',
 75: 'Accessories',
 76: 'Couture',
 77: 'Childrenswear',
 78: 'Places',
 79: 'Digital Art',
 80: 'Flight',
 81: 'Graphic Novels',
 82: 'Dance',
 83: 'R&B',
 84: 'Performances',
 85: 'Gaming Hardware',
 86: 'Mobile Games',
 87: 'Gadgets',
 88: 'Young Adult',
 89: 'Illustration',
 90: 'Translations',
 91: 'Zines',
 92: 'Weaving',
 93: 'Ceramics',
 94: 'Radio & Podcasts',
 95: 'Immersive',
 96: 'Technology',
 97: 'Blues',
 98: 'DIY Electronics',
 99: 'Jazz',
 100: 'Electronic Music',
 101: 'Apps',
 102: 'Camera Equipment',
 103: 'Robots',
 104: '3D Printing',
 105: 'Workshops',
 106: 'Poetry',
 107: 'Photobooks',
 108: 'Photography',
 109: 'World Music',
 110: 'Mixed Media',
 111: 'Residencies',
 112: 'Fine Art',
 113: 'Classical Music',
 114: 'Printing',
 115: 'Webcomics',
 116: 'Animals',
 117: 'Publishing',
 118: 'Kids',
 119: 'Academic',
 120: 'Periodicals',
 121: 'Anthologies',
 122: 'Indie Rock',
 123: 'Comic Books',
 124: 'Games',
 125: 'Tabletop Games',
 126: 'Installations',
 127: 'Conceptual Art',
 128: 'Playing Cards',
 129: 'Puzzles',
 130: 'Metal',
 131: 'Video Games',
 132: 'Photo',
 133: 'Pop',
 134: 'Rock',
 135: 'Country & Folk',
 136: 'Print',
 137: 'Video',
 138: 'Latin',
 139: 'Faith',
 140: 'Art',
 141: 'Painting',
 142: 'Video Art',
 143: 'Makerspaces',
 144: 'Hip-Hop',
 145: 'Music',
 146: 'Stationery',
 147: 'Punk',
 148: 'Fabrication Tools',
 149: 'Chiptune',
 150: 'Musical',
 151: 'Theater',
 152: 'Comics',
 153: 'Plays',
 154: 'Journalism',
 155: 'Audio',
 156: 'Literary Spaces',
 157: 'Live Games',
 158: 'Taxidermy'}

# Create the app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


# Load in the baseline model
filename = open('model_rf_thurs.pkl', 'rb')
model = pickle.load(filename)


# Create routes to post the prediction
@app.route('/', methods=['POST'])
def predict():
    """
    Uses randomforest/NLP to classify if the user's input
    will succeed or not and adds to the json dict output.
    """

    # User input from front-end
    data = request.get_json(force=True)

    # Change json to dataframe
    data.update((x, [y]) for x, y in data.items())
    data_df = pd.DataFrame.from_dict(data)

    # If user input contains anything the model doesn't
    drop_columns = ['campaignName', 'description']
    data_df.drop(columns = drop_columns, inplace=True)

    # Results for RF/NLP model
    model_result = model.predict(data_df)
    
    # --------------------------------------------------------------

    # Create connection and cursor for querying custom/general stats
    mydb = mysql.connector.connect(
        host = config('hostname'),
        user = config('username'),
        passwd = config('password'),
        db = config('database_name'),
        use_pure=True
    )
    cursor = mydb.cursor(cursor_class=MySQLCursorPrepared)
    
    # Filter out category and monetaryGoal from user data
    category = data_df['categories'].map(flipped)[0]
    goal = int(data_df['monetaryGoal'][0])


    # Custom stats
    custom_results = custom_stats(category, goal, cursor)

    # --------------------------------------------------------------

    # Final output dict
    output = {'results': int(model_result[0]),
            'custom_stats': {
                'raising_more_success' : custom_results[0],
                'category_success' : custom_results[1],
                'category_average' : custom_results[2],
                'average_duration' : custom_results[3],
                'average_backers' : custom_results[4],
                'average_over' : custom_results[5]
            }
    }
    return jsonify(output)


@app.route('/visualizations', methods=['POST'])
def visualizations():
    # User input from front-end
    data = request.get_json(force=True)

    # Change json to dataframe
    data.update((x, [y]) for x, y in data.items())
    data_df = pd.DataFrame.from_dict(data)

    # If user input contains anything the model doesn't
    drop_columns = ['campaignName', 'description']
    data_df.drop(columns = drop_columns, inplace=True)

    return make_visuals(data_df)


if __name__ == "__main__":
    app.run(debug=True)