from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///files.db')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload: 16 MB

# Initialize database
db = SQLAlchemy(app)

# File model
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)
    filepath = db.Column(db.String(300), nullable=False)

# Home route – list uploaded files
@app.route('/')
def index():
    files = File.query.all()
    return render_template('index.html', files=files)

# Upload route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(filepath)

            # Save record to database
            file_record = File(filename=uploaded_file.filename, filepath=filepath)
            db.session.add(file_record)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('upload.html')

# Download route
@app.route('/download/<int:file_id>')
def download(file_id):
    file = File.query.get_or_404(file_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True)

# Run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
