import re
import string
import random
from urlparse import urljoin
from flask import request, url_for, session, flash, redirect, render_template
from functools import wraps

#add
import os
from werkzeug import secure_filename
from os import listdir
from os.path import isfile, join
UPLOAD_FOLDER = 'static/files/'

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif', 'zip'])

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


def extract_tags(tags):
    whitespace = re.compile('\s')
    nowhite = whitespace.sub("", tags)
    tags_array = nowhite.split(',')

    cleaned = []
    for tag in tags_array:
        if tag not in cleaned and tag != "":
            cleaned.append(tag)

    return cleaned


def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = random_string()
    return session['_csrf_token']


def make_external(url):
    return urljoin(request.url_root, url)


def login_required():
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not session.get('user'):
                flash('You must be logged in..', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

class FileActions():
    def allowed_file(self,filename):
            return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    def upload_file(self):
        if request.method == 'POST':
            files = request.files.getlist('file[]')
            responses={}
            for file in files:
                responses.update(self.handle_file(file))
            return render_template('upload.html',responses=responses,user=self)
        return render_template('upload.html',user=self)

    def handle_file(self,file):
        folder = UPLOAD_FOLDER
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(folder, filename))
            response={filename: 1}
            return response
        else:
            response={file.filename: 0}
            return response

    def fetch_files(self):
        folder = UPLOAD_FOLDER
        allfiles = [f for f in listdir(folder) if isfile(join(folder, f)) if not f.startswith('.')]
        if allfiles:
            return allfiles

    def delete_file(self,filename):
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        return redirect('/upload/')
