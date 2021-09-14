import json
import os

import flask
from flask import Flask, jsonify, send_from_directory, Response, make_response
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'sql6.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql6436112'
app.config['MYSQL_PASSWORD'] = 'dxQH1qb931'
app.config['MYSQL_DB'] = 'sql6436112'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

# Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)


def create_tables():
    tables_to_create = {
        "annotation_users": "CREATE TABLE annotation_users ( id INTEGER NOT NULL AUTO_INCREMENT, username VARCHAR(30) NOT NULL, password VARCHAR(30) NOT NULL, project VARCHAR(30) NOT NULL, PRIMARY KEY (id));",
        "annotation_images": "CREATE TABLE annotation_images ( id INTEGER NOT NULL AUTO_INCREMENT, user_id INTEGER NOT NULL, image_name VARCHAR (60) NOT NULL, PRIMARY KEY (id))",
        "annotation_annotations": "CREATE TABLE annotation_annotations ( id INTEGER NOT NULL AUTO_INCREMENT, image_id INTEGER NOT NULL, annotation_data TEXT, PRIMARY KEY (id))"
    }
    cur = mysql.connection.cursor()

    # get existing tables
    cur.execute('''SHOW TABLES''')
    table_list = ()
    for table_list_item in cur.fetchall():
        table_list = table_list + tuple(table_list_item.values())

    # create tables if not already exists
    for table in tables_to_create.keys():
        if table not in table_list:
            cur.execute(tables_to_create[table])

    cur.close()


with app.app_context():
    create_tables()


def get_user(username):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM annotation_users WHERE username="{0}"'''.format(username))
    users_details = cur.fetchall()
    cur.close()
    return users_details


def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM annotation_users WHERE id="{0}"'''.format(user_id))
    users_details = cur.fetchall()
    cur.close()
    return users_details


def get_user_images(user_id):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM annotation_images WHERE user_id={0}'''.format(user_id))
    user_images = cur.fetchall()
    cur.close()
    return user_images


def get_image_by_id(image_id):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM annotation_images WHERE id={0}'''.format(image_id))
    image = cur.fetchall()
    cur.close()
    return image


def get_image_annotations(image_id):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM annotation_annotations WHERE image_id={0}'''.format(image_id))
    annotations = cur.fetchall()
    cur.close()
    return annotations


def get_all_annotated_image_ids():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT image_id FROM annotation_annotations''')
    annotated_images = cur.fetchall()
    cur.close()
    return annotated_images


def create_user(user_details):
    cur = mysql.connection.cursor()
    cur.execute('''INSERT INTO annotation_users (username ,password ,project ) VALUES ("{0}", "{1}", "{2}")'''.format(
        user_details['username'], user_details['password'], user_details['project']))
    mysql.connection.commit()
    cur.close()
    return get_user(user_details['username'])


def create_image(image_details):
    cur = mysql.connection.cursor()
    cur.execute('''INSERT INTO annotation_images (user_id ,image_name ) VALUES ("{0}", "{1}")'''.format(
        image_details['userId'], image_details['imageName']))
    mysql.connection.commit()
    cur.close()


def create_annotation(image_id, annotation_data):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT id FROM annotation_annotations WHERE image_id={0}'''.format(image_id))
    existing_annotates = cur.fetchall()
    if len(existing_annotates) > 0:
        cur.execute("UPDATE annotation_annotations SET annotation_data=%s WHERE image_id=%s",
                    (annotation_data, image_id))
        mysql.connection.commit()
    else:
        cur.execute("INSERT INTO annotation_annotations (image_id ,annotation_data ) VALUES (%s,%s)",
                    (image_id, annotation_data))
        mysql.connection.commit()
    cur.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def get_file_destination(project):
    file_destination = os.path.join(app.config['UPLOAD_FOLDER'], project)
    if not os.path.isdir(file_destination):
        os.mkdir(file_destination)
    return file_destination


@app.route('/register', methods=["POST"])
def register():
    register_request_details = flask.request.get_json()

    if len(get_user(register_request_details['username'])) > 0:
        return jsonify({"errorMessage": "Username already exists!"}), 409
    else:
        return create_user(register_request_details)[0], 200


@app.route('/login', methods=['POST'])
def login():
    login_request_details = flask.request.get_json()
    db_user = get_user(login_request_details['username'])
    if len(db_user) > 0 and db_user[0]['password'] == login_request_details['password']:
        return db_user[0], 200
    else:
        return jsonify({"errorMessage": "Username or Password is incorrect!"}), 401


@app.route("/upload", methods=["POST"])
def upload():
    file_status = {"success": [], "failed": []}
    for f in flask.request.files.getlist("imgCollection"):
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            destination_file = os.path.join(get_file_destination(flask.request.form.get("project")), filename)
            f.save(destination_file)
            create_image({'userId': flask.request.form.get("id"), 'imageName': filename})
            file_status['success'].append(f.filename)
        else:
            file_status['failed'].append(f.filename)
    return jsonify(file_status), 200


@app.route("/images", methods=['POST'])
def get_images():
    current_user = flask.request.get_json()
    return jsonify(get_user_images(current_user['id'])), 200


@app.route("/image/<project>/<image_name>", methods=['GET'])
def get_image(project, image_name):
    return send_from_directory(get_file_destination(project), image_name)


@app.route("/annotate/<image_id>", methods=['GET', 'POST'])
def get_annotation_image(image_id):
    if flask.request.method == 'POST':
        annotation_data = flask.request.get_json()
        create_annotation(image_id, json.dumps(annotation_data))
        return jsonify({}), 200
    elif flask.request.method == 'GET':
        return jsonify(get_image_by_id(image_id)[0]), 200


@app.route("/myannotates", methods=['POST'])
def get_user_annotated_images():
    current_user = flask.request.get_json()
    user_images = get_user_images(current_user['id'])
    all_annotated_image_ids = [image['image_id'] for image in get_all_annotated_image_ids()]
    user_annotated_images = [image for image in user_images if image['id'] in all_annotated_image_ids]
    return jsonify(user_annotated_images), 200


@app.route("/checkannotate/<image_id>", methods=['GET'])
def get_user_image_annotations(image_id):
    annotations = json.loads(get_image_annotations(image_id)[0]['annotation_data'])
    return jsonify(annotations), 200


@app.route("/download/<image_id>", methods=['POST'])
def download_annotations_csv(image_id):
    csv_data = []
    user_image_data = flask.request.get_json()
    annotations = json.loads(get_image_annotations(image_id)[0]['annotation_data'])
    for annotation in annotations:
        geometry = annotation['geometry']
        csv_data.append({
            'image': user_image_data['project'] + "/" + user_image_data['image_name'],
            'x': geometry['x'],
            'y': geometry['y'],
            'w': geometry['width'],
            'h': geometry['height']
        })
    return jsonify(csv_data), 200


if __name__ == '__main__':
    app.run()
