from flask import Flask, jsonify, render_template, redirect, Response, session, url_for, request
from flask_compress import Compress
from werkzeug.exceptions import BadRequest
from hashlib import sha256
import time
from typing import Union, Tuple
from pymongo import MongoClient


MONGO_HOST = "mongo"    # This is specifically for the docker stack
MONGO_PORT = 27017      # This is for if the port needs to be changed later easily
DEBUG = False           # Switch for a few print statements.


def create_app() -> Flask:
    # Flask app initialization
    app = Flask(__name__)
    app.config['SECRET_KEY'] = sha256(time.localtime().__str__().encode("utf-8")).__str__()
    Compress(app)

    # Setting up the database
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db_base = client["notes"]
    db = db_base["notes"]

    # Fix for session expiry
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index.html', methods=['GET', 'POST'])
    def main_page() -> Union[str, Response]:
        """
        Main page of the application with a list of notes.
        """
        # Try to access the DB
        try:
            titles = [note.get("Title", "None") for note in db.find()]
        # Exception thrown when the DB is uninitialized
        except AttributeError:
            titles = []
        # (Server side) Render the home page
        return render_template("index.html", titles=titles)

    @app.route('/notes', methods=['GET', 'POST'])
    def notes() -> Union[str, Tuple[Response, int]]:
        """
        Notes page. Renders most of the page, with the client side finishing the markdown.
        """
        # Try to get data from a request
        try:
            title = request.args.get('data')
            # If there is data, we will use that
            if title:
                # This returns None if there is no entry in the database
                note = db.find_one({"Title": title})
            # If the request was empty, default to an untitled note.
            else:
                note = {"Title": "Untitled", "Content": ""}
        # Exception thrown when the DB is uninitialized
        except AttributeError:
            note = {"Title": "Untitled", "Content": ""}
        # Exception thrown from accessing missing parameters
        except BadRequest:
            return jsonify({'error': 'Invalid JSON data in request body'}), 400
        # Handler for the DB returning None
        if not note:
            note = {"Title": "Untitled", "Content": ""}
        # Partially render the page and hand it off to the client
        return render_template("note.html", note=note)

    @app.route('/save', methods=['POST'])
    def save() -> Union[str, Tuple[Response, int]]:
        """
        Endpoint for saving notes.
        :returns: "Ok"
        """
        # Try to save the note
        try:
            # We can only save it if we were sent it
            if request.data:
                # Grab the JSON data from the front end
                json_data = request.json
                if DEBUG:
                    print(json_data)
                # If the title is in the DB, replace the data that is there to prevent duplication
                if db.find_one({"Title": json_data["Title"]}):
                    db.replace_one({"Title": json_data["Title"]}, json_data)
                # If it's new, insert it
                else:
                    db.insert_one(json_data)
            # No data was sent, send error 400 (Bad Request)
            else:
                if DEBUG:
                    print("No data")
                return jsonify({'error': 'Invalid JSON data in request body'}), 400
        # Exception thrown when decoding bad request data
        except BadRequest:
            print("Bad request sent")
            return jsonify({'error': 'Invalid JSON data in request body'}), 400
        # Return something
        return "Ok"

    @app.route('/delete', methods=['POST'])
    def delete() -> Union[str, Tuple[Response, int]]:
        """
        Endpoint for deleting notes.
        :returns: "Ok"
        """
        # Try to get the title sent from the front end
        try:
            if request.data:
                # Try to delete it
                db.delete_one(request.json)
                if DEBUG:
                    print(request.json)
            # No data was sent that can be deleted
            else:
                if DEBUG:
                    print("No data")
                return jsonify({'error': 'Invalid JSON data in request body'}), 400
        # Exception thrown from accessing missing parameters
        except BadRequest:
            print("Bad request sent")
            return jsonify({'error': 'Invalid JSON data in request body'}), 400
        # Return something
        return "Ok"

    @app.route('/health', methods=['GET'])
    def health() -> str:
        """
        Docker Health check
        :return: "Healthy: OK"
        """
        return "Healthy: OK"

    return app


if __name__ == '__main__':
    MONGO_HOST = "10.8.0.5"
    # Create and run the app for development
    app_create: Flask = create_app()
    app_create.run()
