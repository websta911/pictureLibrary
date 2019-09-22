
# Installation of the Picture Library

```
Sudo Pip install virtualenv
virtualenv -p python3 --system-site-packages picLib
. piclLib/bin/activate
Pip install pycups
pip install Pillow
pip install flask
pip install flask_sqlalchemy
pip install flask-wtf
pip install passlib
```

Creates Database with 3 tables admin user and default event.
```
python createTables.py
```
## Make Autostart as Webapplication using uswgi and nginx

Source:
```
https://askubuntu.com/questions/927881/running-a-flask-app-on-startup-with-systemd
https://stackoverflow.com/questions/24941791/starting-flask-server-in-background
```

Install uswgi and nginx
Configure both

```
sudo mkdir -p /var/www/pictureLibrary
sudo chown -R pi /var/www/pictureLibrary/

sudo apt install nginx uwsgi uwsgi-plugin-python
cd /tmp
touch picLib.sock

sudo chown www-data picLib.sock
cd /etc/nginx/sites-available/
sudo rm default

sudo touch piclib
sudo vim picLib
```

content of picLib

```
server {
        listen 80;
        server_tokens off;
        client_max_body_size     30M;
        server_name www.mysite.com mysite.com;

     location / {
         include uwsgi_params;
         uwsgi_pass unix:/tmp/picLib.sock;
     }

     location /static {
         alias /home/pi/pictureLibrary/static/;
     }

     ## Only requests to our Host are allowed
    ## if ($host !~ ^(mysite.com|www.mysite.com)$ ) {
    ##    return 444;
    ## }
}
```

Enable site
```
sudo ln -s /etc/nginx/sites-available/picLib /etc/nginx/sites-enabled/picLib
```
Create uswgi config
```
sudo vim /etc/uwsgi/apps-available/picLib.ini
```
content of piclib.ini
```
[uwsgi]
vhost = true
socket = /tmp/picLib.sock
venv = /home/pi/pictureLibrary/picLib
chdir = /home/pi/pictureLibrary
module = app
callable = app
plugin = python3
```
Enable configuration
```
sudo ln -s /etc/uwsgi/apps-available/picLib.ini /etc/uwsgi/apps-enabled/picLib.ini
```

Restart services
```
sudo service nginx restart
sudo service uwsgi restart
```
create Folder for Photobooth Backgrounds and Logos
```
cd ~
mkdir background
Mkdir background/thumbs
chown +777 background
mkdir logo
Mkdir logo/thumbs
chown +777 logo
cd background 
```

Add one Background and Logo to the folders and create the _bg or _logo symlink  
```
ln -s /home/pi/background/bgxxx.jpg _bg
ln -s /home/pi/logo/logoxxx.jpg _logo
```
this symlinks are what is changed in the webinterface

Create link to where ever your background an logo folders are located (I moved them, before they where in the photobooth location, too lazy to clean that up)
```
cd ~/pictureLibrary
ln -s /home/pi photob
```
### Enable Printing 
```
sudo usermod -a -G lpadmin pi
sudo cupsctl --remote-any
sudo /etc/init.d/cups restart
```
create printer
