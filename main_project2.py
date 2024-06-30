from boltiotai import openai
from flask import Flask, render_template_string, request
#import openai
import os

print(os.environ.get("API_KEY_o"))


# Helper function to generate health advice
def generate_health_advice(messages):
    openai.api_key = os.environ.get("API_KEY_o")
    if not openai.api_key:
        return "You have not set the OpenAI API key."

    response = openai.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=messages)
    print(response)
    if  not  response["choices"] or len(response["choices"]) == 0:
        return "Sorry, unable to provide health advice at the moment. Please try again later."

    output = response["choices"][0]["message"]["content"]
    return output


# Create a Flask web application object named app
app = Flask(__name__)

# Initialize messages
messages = [{
    "role":
    "system",
    "content":
    "You are a helpful assistant providing health-related advice. You need to interactively assist users with either diet plans or illness information based on their input."
}]


@app.route('/', methods=['GET', 'POST'])
def home():
    global messages
    user_input = ""
    response = ""

    if request.method == 'POST':
        user_input = request.form['query']
        messages.append({"role": "user", "content": user_input})

        if user_input.lower() == 'd':
            response = "Please provide your age, gender, weight, and height separated by commas (e.g., 25, male, 70kg, 175cm):"
        elif user_input.lower() == 'i':
            response = "What disease can I help with?"
        else:
            # Handle inputs for age, gender, weight, height for diet or disease details
            last_message = messages[-2]['content']
            if last_message.startswith("Please provide your age"):
                age, gender, weight, height = [
                    x.strip() for x in user_input.split(',')
                ]
                messages.append({
                    "role":
                    "user",
                    "content":
                    f"Age: {age}, Gender: {gender}, Weight: {weight}, Height: {height}"
                })
                user_input = f"I need a diet plan for a {gender} aged {age} with a weight of {weight} and height of {height}."
            elif last_message == "What disease can I help with?":
                messages.append({
                    "role": "user",
                    "content": f"Disease: {user_input}"
                })

            response = generate_health_advice(messages)

        messages.append({"role": "assistant", "content": response})

    return render_template_string('''<!DOCTYPE html>
<html>
<head>
    <title>Personal Health Assistant</title>
    <link href="{{ url_for('static', filename='css/styles.css') }}" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1 class="my-4">YOUR PERSONAL HEALTH ASSISTANT</h1>
        <div class="chat-box">
            {% for message in messages %}
                {% if message.role == 'user' %}
                <div class="user-query">
                    <div class="user-label">You:</div>
                    <div class="user-text">{{ message.content }}</div>
                </div>
                {% else %}
                <div class="assistant-response">
                    <div class="assistant-label">Assistant:</div>
                    <div class="assistant-text">{{ message.content }}</div>
                </div>
                {% endif %}
            {% endfor %}
        </div>
        <form id="health-form" method="post">
            <div class="mb-3">
                <label for="query" class="form-label">How may I help you?:</label>
                <input type="text" class="form-control" id="query" name="query" placeholder="Type your response here..." required>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</body>
</html>
''',
                                  messages=messages)


# Start the Flask application if the script is being run directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
