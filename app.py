from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_default_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scholarnest.db'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploaded_resources'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt', 'pptx', 'xlsx'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Google OAuth Setup (Fixed Issue)
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uname = db.Column(db.String(200), unique=True, nullable=False)
    # semester = db.Column(db.Integer, nullable=False)
    # dob = db.Column(db.String(10), nullable=False)
    # mobile_no = db.Column(db.String(15), nullable=False)
    # email = db.Column(db.String(120), unique=True, nullable=False)
    # password = db.Column(db.String(255), nullable=False)  # No password hashing

# Resource Model
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    filename = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(200), db.ForeignKey('user.uname'), nullable=False)
    user = db.relationship('User', backref=db.backref('resources', lazy=True))

# Google OAuth Login (Fixed session issue)
@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
        email = user_info["email"]

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not registered"}), 403

        session["username"] = user.uname  # Store username in session
        return redirect(url_for("dashboard"))  # Ensure /dashboard exists

    return jsonify({"error": "Failed to log in"}), 400

@app.route("/")
def home():
    return "Welcome to ScholarNest!"




# Register User (No password hashing)
# @app.route('/register', methods=['POST'])
# def register():
#     data = request.json

#     if User.query.filter_by(email=data['email']).first():
#         return jsonify({'error': 'User already exists'}), 400

#     user = User(
#         uname=data['uname'],
#         semester=data['semester'],
#         dob=data['dob'],
#         mobile_no=data['mobile_no'],
#         email=data['email'],
#         password=data['password']  # No hashing applied
#     )

#     db.session.add(user)
#     db.session.commit()
#     return jsonify({'message': 'User registered successfully'}), 201

# Upload Resource (Fixed session issue)
@app.route('/upload', methods=['POST'])
def upload_resource():
    if 'username' not in session:
        return jsonify({'message': 'User not authenticated'}), 401

    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'message': 'Invalid file format'}), 400

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    name = request.form.get('name')
    description = request.form.get('description', '')
    subject = request.form.get('subject')
    semester = request.form.get('semester')
    course = request.form.get('course')
    username = session['username']  # Fetch username from session

    new_resource = Resource(
        name=name,
        description=description,
        filename=filename,
        subject=subject,
        course=course,
        semester=semester,
        username=username
    )
    db.session.add(new_resource)
    db.session.commit()

    return jsonify({'message': 'Resource uploaded successfully'}), 201

# Fetch user's uploaded resources (Fixed session issue)
@app.route('/my_uploads', methods=['GET'])
def my_uploads():
    if 'username' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    username = session['username']
    resources = Resource.query.filter_by(username=username).all()
    
    if not resources:
        return jsonify({'message': 'No uploads found'}), 404

    resource_list = [
        {
            'name': res.name,
            'description': res.description,
            'file_url': f"/download/{res.id}"
        }
        for res in resources
    ]

    return jsonify({'uploads': resource_list}), 200

# Download Resource (Fixed Path Issue)
@app.route('/download/<int:id>', methods=['GET'])
def download_resource(id):
    resource = Resource.query.get(id)
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], resource.filename), 200

# Helper function to check file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("google_login"))  # Redirect to login if not authenticated
    return "Welcome to ScholarNest Dashboard!"

# Initialize the database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



















# Initialize the Flask app, database, and OAuth


# OAuth Configuration (using Google as an example)
# oauth = OAuth(app)
# google = oauth.register(
#     name='google',
#     client_id='YOUR_GOOGLE_CLIENT_ID',
#     client_secret='YOUR_GOOGLE_CLIENT_SECRET',
#     authorize_url='https://accounts.google.com/o/oauth2/auth',
#     access_token_url='https://accounts.google.com/o/oauth2/token',
#     api_base_url='https://www.googleapis.com/oauth2/v1/',
#     user_info_endpoint='userinfo',
#     client_kwargs={'scope': 'openid profile email'},
# )






# # Resource model, using 'uname' (email) to link to the user
# class Resource(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), nullable=False)
#     description = db.Column(db.String(255), nullable=True)
#     filename = db.Column(db.String(120), nullable=False)
#     subject = db.Column(db.String(50), nullable=False)
#     semester = db.Column(db.String(10), nullable=False)
#     username = db.Column(db.String(200), db.ForeignKey('sch_nest.uname'), nullable=False)  # Link to email
#     user = db.relationship('SchNest', backref=db.backref('resources', lazy=True))  # Relationship to user

#     def _repr_(self):
#         return f"<Resource {self.name}>"

# Helper function to check allowed file extensions
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# # OAuth callback route, called after successful login
# @app.route('/auth')
# def auth():
#     token = google.authorize_access_token()  # Get access token from Google
#     user_info = google.parse_id_token(token)  # Parse user info

#     # Store user info in session (user email will be used to link resources)
#     session['user'] = user_info

#     # If the user doesn't exist, create a new record in the database
#     user = SchNest.query.filter_by(uname=user_info['email']).first()
#     if not user:
#         user = SchNest(uname=user_info['email'])
#         db.session.add(user)
#         db.session.commit()

#     return redirect(url_for('dashboard'))

# # Dashboard or Home route (after login)
# @app.route('/dashboard')
# def dashboard():
#     if 'user' not in session:
#         return redirect(url_for('login'))  # Redirect to login if not logged in
#     return f"Welcome, {session['user']['name']}!"









