from flask import Flask, request, jsonify, render_template
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

app = Flask(__name__)

# Load Q&A database
try:
    with open('qa_database.json') as f:
        qa_data = json.load(f)
except FileNotFoundError:
    print("Error: 'qa_database.json' not found. Ensure the file is in the same directory.")
    qa_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/ask', methods=['POST'])
def ask():
    if not request.is_json:
        return jsonify({'error': 'Invalid content type, expected application/json'}), 415
    data = request.json
    if 'message' not in data:
        return jsonify({'error': 'Missing "message" key in JSON payload'}), 400
    user_input = data['message']
    response = get_response(user_input)
    return jsonify({'response': response})

def get_response(user_input):
    user_input = preprocess_input(user_input)  # Normalize the input

    # Use fuzzy matching to find the most similar question in the database
    best_match = process.extractOne(user_input, [qa_pair['question'] for qa_pair in qa_data], scorer=fuzz.partial_ratio)

    if best_match:
        question, score = best_match
        if score >= 70:  # Adjust the score threshold as necessary (e.g., 70%)
            # Find the answer corresponding to the matched question
            for qa_pair in qa_data:
                if qa_pair['question'].lower() == question.lower():
                    return qa_pair['answer']
        else:
            return "Sorry, I didn't quite catch that. Could you rephrase your question?"

    return "Sorry, I don't have an answer for that."

def preprocess_input(input):
    # Normalize input: convert to lowercase, remove unnecessary punctuation, etc.
    return input.strip().lower()

if __name__ == '__main__':
    app.run(debug=True, port=5000)