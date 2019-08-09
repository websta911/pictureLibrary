#!/bin/python

import os, errno
import cups
from PIL import Image
from flask import Flask, Response, request, abort, render_template_string, send_from_directory, render_template,flash, redirect, session, url_for
import StringIO
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, validators, SubmitField, HiddenField, PasswordField,TextAreaField,SelectField
from wtforms.fields.html5 import EmailField, DateField
from datetime import datetime
from functools import wraps
from passlib.hash import sha256_crypt
from tabledef import *
from urllib import urlencode, quote, unquote

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
#app.config['DATABASE']=os.path.join(app.root_path,'piclib.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'picLib.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


WIDTH = 350
HEIGHT = 350

## Config ###

##Bilderpfad
picture_basename = datetime.now().strftime("./photob/%Y-%m-%d")
path = './bilder'
path = picture_basename
photobpath = './photob'
## Veranstaltung
va = "AuC"
aEvconf = db.session.query(Event).filter_by(eactive=1).first()
va = aEvconf.eShort

## Config End

@app.route('/<path:filename>')
def image(filename):
    try:
        w = int(request.args['w'])
        h = int(request.args['h'])
    except (KeyError, ValueError):
        return send_from_directory('.', filename)

    try:
        im = Image.open(filename)
        im.thumbnail((w, h), Image.ANTIALIAS)
        io = StringIO.StringIO()
        im.save(io, format='JPEG')
        return Response(io.getvalue(), mimetype='image/jpeg')

    except IOError:
        abort(404)

    return send_from_directory('.', filename)

@app.route('/')
def index():
    images = []
    exclude = set(['src'])
    for root, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]
        for filename in [os.path.join(root, name) for name in files]:
            if not filename.endswith('.jpg'):
                continue
            im = Image.open(filename)
            #name = os.path.splitext(filename)[-1] + os.path.splitext(filename)[-2] 
            name = filename.split('/')[-1]
            w, h = im.size
            aspect = 1.0*w/h
            if aspect > 1.0*WIDTH/HEIGHT:
                width = min(w, WIDTH)
                height = width/aspect
            else:
                height = min(h, HEIGHT)
                width = height*aspect
            images.append({
                'name': name,
                'width': int(width),
                'height': int(height),
                'src': filename
            })

    return render_template('index.html', **{
        'images': sorted(images, reverse=True)
    })
	
@app.route('/subscribe/<string:filename>', methods=['GET', 'POST'])
def subscribe(filename):
    image = []
    fullPath = "%s/%s" % ( path, filename )
    im = Image.open(fullPath)
    
    w, h = im.size
    aspect = 1.0*w/h
    if aspect > 1.0*WIDTH/HEIGHT:
        width = min(w, WIDTH)
        height = width/aspect
    else:
        height = min(h, HEIGHT)
        width = height*aspect
    image.append({
        'name': filename.encode('utf8'),
        'width': int(width),
        'height': int(height),
        'src': fullPath.encode('utf8')
    })
    formu = subscribeForm(request.form)

    formu.imagesrc.data = fullPath.encode('utf8')

    if request.method == 'POST' and formu.validate():
        imagesrc =  request.form['imagesrc']
        email = request.form['email']

        print imagesrc
        print email

        subscription = Subscription(imagesrc, email, va)
        db.session.add(subscription)
        db.session.commit()
      
        flash('Wir haben die Adresse gespeichert und senden Ihnen das Foto nach der Hochzeit zu.', 'success')
        return redirect('/')
        

    #return render_template('subscribe.html', **{ 'image' : image , 'form' : formu })
    return render_template('subscribe.html', image=image, form=formu)
   


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/allSubscriptions')
@is_logged_in
def allSubscriptions():	
    subs = db.session.query(Subscription).all()

    return render_template('show_subs.html', subs=subs )

@app.route("/upload")
@is_logged_in
def upload():
    return render_template("upload.html")


@app.route("/uploading", methods=["POST"])
def uploading():
    target = os.path.join(basedir, 'images/')
    # target = os.path.join(APP_ROOT, 'static/')
    print(target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accept incoming file:", filename)
        print ("Save it to:", destination)
        upload.save(destination)

    # return send_from_directory("images", filename, as_attachment=True)
    return render_template("complete_display_image.html", image_name=filename)

@app.route('/uploading/<filename>')
@is_logged_in
def send_image(filename):
    return send_from_directory("images", filename)


@app.route('/print/<string:filename>')
@is_logged_in
def cups_print(filename):
    target = os.path.join(basedir, 'images/')
    fullPath = "/".join([target, filename])
    print("fullpath:", fullPath)
    CupsPrinting(fullPath)
    flash('Druckauftrag abgesendet.', 'success')
    return render_template("complete_display_image.html", image_name=filename)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

class createUserForm(Form):
    username = StringField('Username', [validators.Length(min=1, max = 10)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/createUser', methods=['GET','POST'])
@is_logged_in
def createUser():
    form = createUserForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        newUser = User(username, password)
        db.session.add(newUser)
        db.session.commit()

        flash('Neuer User angelegt', 'success')

        redirect(url_for('index'))
    return render_template('createUser.html', form=form)

class changePWForm(Form):
    password_old = PasswordField('old Password', [validators.DataRequired()])
    password = PasswordField('new password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords dont match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/manageUser')
@is_logged_in
def manageUser():
    
    all = db.session.query(User).all()
    return render_template('manageUser.html', **{
        'user' : all
    })

@app.route('/deleteUser/<string:id>', methods=['POST'])
@is_logged_in
def deleteUser(id):
    
    remUser = db.session.query(User).filter_by(id=id).first()
    uname = remUser.username
         
    
    #remUser = User('admin', 'admin@example.com')
    db.session.delete(remUser)
    db.session.commit()
    flash('deleted {}'.format(uname),'success')
    return redirect(url_for('manageUser'))


@app.route('/resetUserpw/<string:id>', methods=['POST'])
@is_logged_in
def resetUserpw(id):
    
    resUser = db.session.query(User).filter_by(id=id).first()
    uname = resUser.username
    pw = pwgen(8)
    pwc = sha256_crypt.encrypt(str(pw))
    resUser.password = pwc
    db.session.add(resUser)
    db.session.commit()
    flash('reset PW for {} to {}'.format(uname,pw ),'success')
    return redirect(url_for('manageUser'))


def pwgen(length):
    
    if not isinstance(length, int)or length < 4:
        error = 'Passwort zur kurz'
    
    chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789abcdefghijkmnpqrstuvwxyz!-_"
    from os import urandom
    return "".join(chars[ord(c) % len(chars)] for c in urandom(length))
    #alphabet = string.ascii_letters + string.digits
    #password = ''.join(secrets.choice(alphabet) for i in range(6))
    #return password


@app.route('/changePW', methods=['POST','GET'])
@is_logged_in
def changePW():
    form = changePWForm(request.form)
    username = session['username']
   
    if request.method == 'POST' and form.validate():
        oldpw = form.password_old.data
        password_candidate = sha256_crypt.encrypt(str(form.password.data))

        query = db.session.query(User).filter_by(username = username)
        print query
        result = query.first()
        print result
        if result:
            password = result.password

            if sha256_crypt.verify(oldpw, password):
                result.password = password_candidate
                db.session.add(result)
                db.session.commit()
                flash('Passwort geaendert','success')
            else:
                flash('Altes Passwort stimmt nicht', 'danger')
                return render_template('changePW.html', form=form)
        
        redirect(url_for('dashboard'))
    
    return render_template('changePW.html', form=form)

def getImgList(asset):
    bgPath = os.path.join(photobpath, 'background')
    bgSL = os.readlink(bgPath + '/_bg')
    logoPath = os.path.join(photobpath, 'logo')
    logoSL = os.readlink(logoPath + '/_logo')
    bgImages = []
    for root, dirs, files in os.walk(bgPath, topdown=True):
        for filename in [os.path.join(root, name) for name in files]:
            if not (filename.endswith('.jpg') or filename.endswith('.png')) :
                continue
            name = filename.split('/')[-1]
            bgImages.append((filename, name))
    logoImages = []
    for root, dirs, files in os.walk(logoPath, topdown=True):
        for filename in [os.path.join(root, name) for name in files]:
            if not (filename.endswith('.jpg') or filename.endswith('.png')) :
                continue
            name = filename.split('/')[-1]
            logoImages.append((filename,name))
    if asset == 'Bg':
        return bgImages
    elif asset == 'Logo':
        return logoImages


    
class EventForm(Form):
    event = StringField('Veranstaltung', [validators.Length(min=4, max=30)])
    eDate = DateField('VeranstaltungsDatum', format='%Y-%m-%d')
    eShort = StringField('Kurzform',[validators.Length(min=2, max=8)])
    eDesc = TextAreaField('Beschreibung')
    eBg = SelectField('Hintergrund', choices=getImgList("Bg"))
    eLogo = SelectField('Logo', choices=getImgList("Logo"))

@app.route('/newEvent', methods=['GET', 'POST'])
@is_logged_in
def newEvent():
    
    form = EventForm(request.form)

    #form.eBg.choices = [(bg['name']) for bg in bgImages ]

    if request.method == 'POST' and form.validate():
        event = form.event.data
        eDate = form.eDate.data
        eDesc = form.eDesc.data
        eShort = form.eShort.data
        eBg = form.eBg.data
        eLogo = form.eLogo.data
        eactive = 0

        newEvent = Event(event, eDate, eDesc, eBg, eLogo, eShort, eactive )
        db.session.add(newEvent)
        db.session.commit()
        flash ('Event wurde angelegt', 'success')
        return redirect(url_for('manageEvents'))
    return render_template('newEvent.html', form=form)

@app.route('/newEvent1', methods=['GET', 'POST'])
@is_logged_in
def newEvent1():
    
    bgPath = os.path.join(photobpath, 'background')
    bgSL = os.readlink(bgPath + '/_bg')
    logoPath = os.path.join(photobpath, 'logo')
    logoSL = os.readlink(logoPath + '/_logo')

    if request.method == 'POST':
        event = request.form['event']
        eDate = request.form['eDate']
        eDesc = request.form['eDesc']
        eShort = request.form['eShort']
        eBg = request.form['eBg']
        eLogo = request.form['eLogo']

        newEvent = Event(event, eDate, eDesc, eBg, eLogo, eShort )
        db.session.add(newEvent)
        db.session.commit()
        flash ('Event wurde angelegt', 'success')
        return redirect(url_for('manageEvents'))

        
    
    bgImages = []
    for root, dirs, files in os.walk(bgPath, topdown=True):
        for filename in [os.path.join(root, name) for name in files]:
            if not (filename.endswith('.jpg') or filename.endswith('.png')) :
                continue

            name = filename.split('/')[-1]
            bgImages.append({
                'name': name,
                'src': filename
            })
    
    logoImages = []
    for root, dirs, files in os.walk(logoPath, topdown=True):
        for filename in [os.path.join(root, name) for name in files]:
            if not (filename.endswith('.jpg') or filename.endswith('.png')) :
                continue

            name = filename.split('/')[-1]
            logoImages.append({
                'name': name,
                'src': filename
            })


    return render_template('newEvent.1.html', **{
        'bgImages': sorted(bgImages),
        'logoImages': sorted(logoImages),
        'aBg': bgSL,
        'aLogo':logoSL
    })



@app.route('/manageEvents')
@is_logged_in
def manageEvents():
    all = db.session.query(Event).all()
    return render_template('manageEvents.html', **{
        'events' : all
    })

@app.route('/editEvent/<string:id>', methods=['GET','POST'])
@is_logged_in
def editEvent(id):
    edEv = db.session.query(Event).filter_by(id=id).first()
    print datetime.strptime(edEv.eDate,'%Y-%m-%d').strftime('%m/%d/%Y')
    #print edEv.eDate.strftime('%Y-%m-%d')

    form = EventForm(request.form)
    form.event.data = edEv.event
    form.eDate.data = datetime.strptime(edEv.eDate,'%Y-%m-%d')
    form.eDesc.data = edEv.eDesc
    form.eShort.data = edEv.eShort
    form.eBg.data = edEv.eBg
    form.eLogo.data = edEv.eLogo

    eactive = edEv.eactive

    if request.method == 'POST':
        edEv.event = request.form['event']
        edEv.eDate = request.form['eDate']
        edEv.eDesc = request.form['eDesc']
        edEv.eShort = request.form['eShort']
        edEv.eBg = request.form['eBg']
        edEv.eLogo = request.form['eLogo']

        
        db.session.add(edEv)
        db.session.commit()
        flash ('Event wurde geaendert', 'success')
        return redirect(url_for('manageEvents'))
    return render_template('editEvent.html', form = form)


@app.route('/deleteEvent/<string:id>', methods=['POST'])
@is_logged_in
def deleteEvent(id):
    
    remEv = db.session.query(Event).filter_by(id=id).first()
    event = remEv.event
    db.session.delete(remEv)
    db.session.commit()
    flash('deleted {}'.format(event),'success')
    return redirect(url_for('manageEvents'))

@app.route('/setEventactive/<string:id>', methods=['POST','GET'])
def setEventactive(id):
    
    aEv = db.session.query(Event).filter_by(eactive=1).all()

    for ev in aEv:
        ev.eactive = 0
        db.session.add(ev)
    
    cEv = db.session.query(Event).filter_by(id=id).first()
    cEv.eactive = 1
    evname = cEv.event
    db.session.add(cEv)
    db.session.commit()

    bgPath = os.path.join(photobpath, 'background')
    bgSL = os.readlink(bgPath + '/_bg')
    logoPath = os.path.join(photobpath, 'logo')
    logoSL = os.readlink(logoPath + '/_logo')

    logo = cEv.eLogo
    img = cEv.eBg
    
    if bgSL == img:
        print 'all good bgwise'
    else:
        os.remove(bgPath + '/_bg')
        os.symlink(img, bgPath + '/_bg')
        flash("set new background to {}".format(img), 'success')
        bgSL = os.readlink(bgPath + '/_bg')
    
    if logoSL == logo:
            print 'all good logowise'
    else:
        os.remove(logoPath + '/_logo')
        os.symlink(logo, logoPath + '/_logo')
        flash("set new logo to {}".format(logo), 'success')
        logoSL = os.readlink(logoPath + '/_logo')

    va = cEv.eShort

    flash('{} ist nun aktiv'.format(evname),'success')
    return redirect(url_for('manageEvents'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login_username = request.form['username']
        password_candidate =request.form['password']

        query = db.session.query(User).filter_by(username = login_username)
        print query
        result = query.first()
        print result
        if result:
            password = result.password

            # if password == password_candidate:
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = login_username
                flash('You are now logged in', 'success')
                return redirect(url_for('index'))

            #session['logged_in'] = True
            else:
                flash('wrong password!', 'danger')
            
        else:
            error = 'Invalid Credentials. Please try again.'
            
    return render_template('login.html', error=error)   


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

def CupsPrinting(BPicture):
    conn = cups.Connection()
    printers = conn.getPrinters()
    printer_name = printers.keys()[0]
    cups.setUser('pi')
    print_id = conn.printFile(printer_name, BPicture, "Photo Booth",{})
    

class subscribeForm(Form):
    imagesrc = HiddenField('imagesrc')
    email = EmailField('email', [validators.DataRequired(), validators.Email()])

@app.route('/photobox')
def photobox():
    logo_filename = os.path.join(photobpath, 'logo/_logo')
    bg_filename = os.path.join(photobpath, 'background/_bg')
    return render_template("photobox.html", logo_img = logo_filename, bg_img = bg_filename)
    #return render_template('photobox.html')        

@app.route('/photobox1', methods=['GET', 'POST'])
def photobox1():
    
    bgPath = os.path.join(photobpath, 'background')
    bgSL = os.readlink(bgPath + '/_bg')
    logoPath = os.path.join(photobpath, 'logo')
    logoSL = os.readlink(logoPath + '/_logo')

    if request.method == 'POST':
        bgchoice = request.form['bgoptions']
        logochoice = request.form['logooptions']
        print bgchoice
        print logochoice

        if bgSL == bgchoice:
            print 'all good gbwise'
        else:
            os.remove(bgPath + '/_bg')
            os.symlink(bgchoice, bgPath + '/_bg')
            flash("set new background")
            bgSL = os.readlink(bgPath + '/_bg')

        if logoSL == logochoice:
                print 'all good logowise'
        else:
            os.remove(logoPath + '/_bg')
            os.symlink(logochoice, logoPath + '/_bg')
            flash("set new logo")
            logoSL = os.readlink(logoPath + '/_logo')

        
    
    bgImages = []
    for root, dirs, files in os.walk(bgPath, topdown=True):
        for filename in [os.path.join(root, name) for name in files]:
            if not (filename.endswith('.jpg') or filename.endswith('.png')) :
                continue

            name = filename.split('/')[-1]
            bgImages.append({
                'name': name,
                'src': filename
            })
    
    logoImages = []
    for root, dirs, files in os.walk(logoPath, topdown=True):
        for filename in [os.path.join(root, name) for name in files]:
            if not (filename.endswith('.jpg') or filename.endswith('.png')) :
                continue

            name = filename.split('/')[-1]
            logoImages.append({
                'name': name,
                'src': filename
            })


    return render_template('photobox1.html', **{
        'bgImages': sorted(bgImages),
        'logoImages': sorted(logoImages),
        'aBg': bgSL,
        'aLogo':logoSL
    })
            

@app.route("/setStandard", methods=['GET'])
def setStandard():
    bgPath = os.path.join(photobpath, 'background')
    bgSL = os.readlink(bgPath + '/_bg')
    logoPath = os.path.join(photobpath, 'logo')
    logoSL = os.readlink(logoPath + '/_logo')

    
    asset = request.args.get('asset')
    img = request.args.get('img')
    print asset
    print img

    if asset =='bg':
        
        if bgSL == img:
            print 'all good gbwise'
        else:
            os.remove(bgPath + '/_bg')
            os.symlink(img, bgPath + '/_bg')
            flash("set new background to {}".format(img), 'success')
            bgSL = os.readlink(bgPath + '/_bg')
    elif asset == 'logo':
        if logoSL == img:
                print 'all good logowise'
        else:
            os.remove(logoPath + '/_logo')
            os.symlink(img, logoPath + '/_logo')
            flash("set new logo to {}".format(img), 'success')
            logoSL = os.readlink(logoPath + '/_logo')

    return redirect(url_for('photobox1'))
        

@app.route("/PBupload", methods=['GET', 'POST'])
@is_logged_in
def PBupload():
    
    
    if request.method == 'POST':
        asset = request.form['Asset']    
        target = os.path.join(photobpath, asset)
    # target = os.path.join(APP_ROOT, 'static/')
        print(target)
        if not os.path.isdir(target):
            print 'missing target'
        else:
            print("Couldn't create upload directory: {}".format(target))
        #print(request.files.getlist("file"))
        for upload in request.files.getlist("file"):
            print(upload)
            print("{} is the file name".format(upload.filename))
            filename = upload.filename
            destination = "/".join([target, filename])
            print ("Accept incoming file:", filename)
            print ("Save it to:", destination)
            upload.save(destination)
            flash('Uploaded to {}'.format(destination),'success')
            return redirect(url_for('photobox1'))
    else:
        return render_template("PBupload.html")         

#not used
def confirmation_required(desc_fn):
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.args.get('confirm') != '1':
                desc = desc_fn()
                return redirect(url_for('confirm', 
                    desc=desc, action_url=quote(request.url)))
            return f(*args, **kwargs)
        return wrapper
    return inner
#not used
@app.route('/confirm')
def confirm():
    desc = request.args['desc']
    action_url = unquote(request.args['action_url'])

    return render_template('_confirm.html', desc=desc, action_url=action_url)
#not used
def you_sure():
    return "Are you sure?"


@app.route('/deleteFile/<string:id>', methods=['POST'])
@is_logged_in
def deleteFile(id):
    print 'was here'
    asset = request.form['asset']
    
    workdir = os.path.join(photobpath, asset)
    todelete = os.path.join(workdir, id)

    print todelete  
    os.remove(todelete)
    flash('Deleted {}'.format(id),'success')
    return redirect(url_for('photobox1'))





@app.route('/changeLink/<link>', methods=['GET', 'POST'])
def changeLink(link):
    target = link
    print target
    if(link == 'bg_img'):
        sPath = os.path.join(photobpath, 'background')
        print "change link for bg"
        bgSL = os.readlink(sPath + '/_bg')
        
    elif(link == 'logo_img'):
        sPath = os.path.join(photobpath, 'logo')
        print "change link for logo"
        logoSL = os.readlink(sPath + '/_logo')


    if request.method == 'POST':
        choice = request.form['options']
        print choice

        setBG = os.path.join(sPath, choice)
        print setBG
        flash("set background to {choice}")

        
    else :    

        images = []
        for root, dirs, files in os.walk(sPath, topdown=True):
            for filename in [os.path.join(root, name) for name in files]:
                if not filename.endswith('.jpg'):
                    continue
            
            #name = os.path.splitext(filename)[-1] + os.path.splitext(filename)[-2] 
                name = filename.split('/')[-1]
            
                images.append({
                    'name': name,
                    'src': filename
                })

        return render_template('changeLink.html', **{
            'images': sorted(images, reverse=True)
        })
    return redirect(url_for('photobox'))

@app.route('/setLink')
def setLink():
     return redirect(url_for('photobox'))


def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError, e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e


""" class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    imagesrc = db.Column(db.String(255))
    email =  db.Column(db.String(255))
    va = db.Column(db.String(255))
    
    def __init__(self, imagesrc, email, va):
        self.imagesrc = imagesrc
        self.email = email
        self.va = va

class Users(db.Model):
    """"""
    __tablename__ = "users"
 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
 
    #----------------------------------------------------------------------
    def __init__(self, username, password):
        """"""
        self.username = username
        self.password = password
 """

if __name__ == '__main__':
  app.run(debug=True, host='::')
