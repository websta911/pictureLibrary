
# Installation of the Picture Library

```
sudo apt install libcups2-dev cups
sudo Pip install virtualenv
virtualenv -p python3 --system-site-packages picLib
source piclLib/bin/activate
pip install pycups Pillow flask flask_sqlalchemy flask-wtf passlib
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

Create link photob to where ever your background an logo folders are located and Pictures to where the Pictures of the Photobox are located. Expected to find folders with foldername in form "%Y-%m-%d"
```
cd ~/pictureLibrary
ln -s /home/pi photob
ln -s /home/pi Pictures Pictures
```

Creates Database with 3 tables admin user and default event.
```
python createTables.py
chmod 777 picLib.db
```

## Make Autostart as Webapplication using uswgi and nginx

Source:
```
https://stackoverflow.com/questions/24941791/starting-flask-server-in-background
```

Install uswgi and nginx
Configure both


```
sudo mkdir -p /var/www/pictureLibrary
sudo chown -R pi /var/www/pictureLibrary/

sudo apt install nginx uwsgi uwsgi-plugin-python3
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

### Enable Printing 
```
sudo usermod -a -G lpadmin pi
sudo cupsctl --remote-any
sudo /etc/init.d/cups restart
```
create printer
