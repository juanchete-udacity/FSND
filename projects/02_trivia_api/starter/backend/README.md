# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. Following the instructions in [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) is recommended, but we offer a guide if you are using WSL with Windows

First install python3-venv in your Ubuntu WSL installation
```bash
sudo apt-get install python3-venv
```
Then, create a virtual enviroment with the following command 
```bash
python3 -m venv ev    
```
Activate the venv with:

```bash
source env/bin/activate
```

Now you can insall dependences in the venv

Remember to add env folder and pip to .gitignore to avoid pushing it to the repository

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
sudo -u postgres createdb trivia
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.
Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 
Setting the `PSQL_USER` and `PSQL_PWD` variables is mandatory in order to have the database connection working.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
export PSQL_USER=your_postgresql_username
export PSQL_PWD=your_postgresql_password
flask run
```

These commands put the application in development and directs our application to use the __init__.py file in our flaskr folder. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. If running locally on Windows, look for the commands in the Flask documentation.
The application is run on http://127.0.0.1:5000/ by default and is a proxy in the frontend configuration.

## Testing

To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## API Reference

### Getting Started

* Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is * hosted at the default, http://127.0.0.1:5000/, which is set as a proxy in the frontend configuration.
* Authentication: This version of the application does not require authentication or API keys.

### Error Handling

Errors are returned as JSON objects in the following format:

```json
{
    "success": False,
    "error": 400,
    "message": "bad request"
}
```

The API will return three error types when requests fail:

400: Bad Request
404: Resource Not Found
422: Not Processable
500: Internal Server Error

**GET '/categories'**

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns:
  - A Boolean if success
  - A dictionary of categories, that contains a object of id: category_string key:value pairs.
  - A number with the total of categories

```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true,
  "total_categories": 6
}
```

**GET '/questions'**
- Fetches a list of paginated questions, with their ids, answer, category and difficulty.
- Request Arguments: *page*, with the number of pagination (established in the `QUESTIONS_PER_PAGE` variable in __init__.py)
- Returns:
  - A Dictionary of categories, with ids and texts
  - An integer with the current category
  - The list of questions
  - The total amount of questions 

```json
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_category": "ALL", 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, ...
  ],
  "total_questions": 19
```

**DELETE /questions/{question_id}**
Deletes the question of the given ID if it exists. Returns the id of the deleted question, success value, total questions, and question list based on current page number to update the frontend.

- Request Arguments: None, question_id is given in the path
- Returns: the id of the deleted question, the questions array, the number of questions remaining and the status  

```json
curl -X DELETE http://127.0.0.1:5000/questions/16?page=2
{
    "questions": [
        {
        "answer": "Apollo 13", 
        "category": 5, 
        "difficulty": 4, 
        "id": 2, 
        "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        ...
    ],
    "deleted": 16,
    "success": true,
    "total_questions": 15
}
```

**POST /questions**
Creates a new question with the body containing the fields of a question, or if search term was given, searches the question table for questions containing the term supplied

- Request Arguments: *body* with the following structure

    ```json
    {
        question: "Question text"
        answer: "Answer text"
        difficulty: 1
        category: "4"
        searchTerm?: "search term"
    }
    ```

- Returns:
  - A json with the status of success, the question created, a dictionary of all the questions and the number of total questions.

    ```json
    {
        'success': True,
        'created': {the question created},
        'questions': ...,
        'total_questions': 16
    }
    ```

**GET {/categories/<category_id>/questions}**
Retrieves the questions with the category id passed as part of the path

- Request Arguments: *page* for pagination
- Returns: the dictionary of categories, the current category type, a list of questions as the result of the query and the total number of questions for pagination

```json
curl http://127.0.0.1/categories/<category_id>/questions?page=1
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_category": "Science", 
  "questions": [
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }
  ], 
  "total_questions": 3
}
```

**POST /quizzes**

Retrieves a random question from the pool of questions or from the selected category (if any)

- Required Arguments: *body* with the following content:

```json
    {
        previous_questions: [(list of previous questions ids comma separated)],
        quiz_category: {type: "category type", id: "id of the category"}
    }
```

- Returns: A JSON with the status of success and the question that is going to be asked

```json
    {
        'success': true or false,
        'question': {...the question},
    }  
```

## Authors

Juan José Rodríguez Buleo
## Acknowledgements

Our Udacity Coach Caryn, with her videos and examples it was easy to implement and understant it!