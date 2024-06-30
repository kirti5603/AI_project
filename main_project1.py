from boltiotai import openai  # Importing the openai module from boltiotai for AI interaction
import os
import sys
from flask import Flask, render_template_string, request, url_for

def generate_tutorial(components):
    openai.api_key = os.environ.get("API_KEY")
    if not openai.api_key:
        sys.stderr.write("You have not set the OpenAI API key.\n")  # Warn if API key not set
        return "API key not set."

    try:
        print(f"API Key: {openai.api_key}")  # Print API key to verify it's set
        print(f"Components: {components}")  # Log the components

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a user-friendly interface where educators and students can input a course or subject title and receive a detailed, AI-generated outline that includes: Objective of the Course: A concise statement that describes the purpose and goals of the course. Sample Syllabus: An AI-generated syllabus outline that covers the main topics and modules to be taught. Three Measurable Outcomes: Specific, measurable learning outcomes categorized according to Bloom's Taxonomy levels: Knowledge, Comprehension, and Application. Assessment Methods: Suggestions on how to evaluate the learning outcomes through various forms of assessment. Recommended Readings and Textbooks: A list of AI-recommended resources, including books, articles, and other materials relevant to the course content"},
                {"role": "user", "content": components}
            ]
        )

        print(f"Response: {response}")  # Log the entire response

        if "choices" not in response or len(response["choices"]) == 0:
            return "Sorry, unable to generate a tutorial at the moment. Please try again later."

        output = response["choices"][0]["message"]["content"]
        return output

    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error
        return f"An error occurred: {e}"

# Create a Flask web application object named app and define a route for the root URL that responds to GET and POST requests
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def hello():
    output = ""
    if request.method == 'POST':
        components = request.form['components']  # Get user input from the form
        output = generate_tutorial(components)  # Generate tutorial based on user input
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>information about courses </title>
    <link href="{{ url_for('static', filename='css/styles.css') }}" rel="stylesheet">
    <script>
        async function generateTutorial() {
            const components = document.querySelector('#components').value;
            const output = document.querySelector('#output');
            const submitBtn = document.querySelector('button[type="submit"]');

            output.textContent = 'diving deep in the sea of knowledge! ready to find a pearl for you!...';
            submitBtn.disabled = true;

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: new FormData(document.querySelector('#tutorial-form'))
                });
                const newOutput = await response.text();
                output.textContent = newOutput;
            } catch (error) {
                console.error('Error generating tutorial:', error);
                output.textContent = 'Error generating tutorial. Please try again later.';
            } finally {
                submitBtn.disabled = false;
            }
        }

        function copyToClipboard() {
            const output = document.querySelector('#output');
            const textarea = document.createElement('textarea');
            textarea.value = output.textContent;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            alert('Copied to clipboard');
        }
    </script>
</head>
<body>
    <div class="container">
        <h1 class="my-4">KNOW YOUR COURSES!! </h1>
        <form id="tutorial-form" onsubmit="event.preventDefault(); generateTutorial();" class="mb-3">
            <div class="mb-3">
                <label for="components" class="form-label">Please name your course:</label>
                <input type="text" class="form-control" id="components" name="components" placeholder="Search for any course. e.g. marine biology" required>
            </div>
            <button type="submit" class="btn btn-primary">SUBMIT</button>
        </form>
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                Output:
                <button class="btn btn-secondary btn-sm" onclick="copyToClipboard()">Copy</button>
            </div>
            <div class="card-body">
                <pre id="output" class="mb-0" style="white-space: pre-wrap;">{{ output }}</pre>
            </div>
        </div>
    </div>
</body>
</html>
''',
output=output)

@app.route('/generate', methods=['POST'])
def generate():
    components = request.form['components']  # Get user input from the form
    return generate_tutorial(components)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
