
# Installation of the Picture Library

## Pre reqs

```
sudo apt install libcups2-dev cups
sudo apt install nginx uwsgi uwsgi-plugin-python3
sudo Pip install virtualenv
```

create Folder for Photobooth backgrounds and logos mine are located in /home/pi aka. ~ 
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
this symlinks are what is changed later in the webinterface

## get the picturelibrary code


Since we are creating a webinterface it makes sense to put that in /var/www 

```
sudo mkdir -p /var/www/pictureLibrary
sudo chown -R pi /var/www/pictureLibrary/

```

To get the code in there I have no idea how to do that properly but you could try something like that:
clone the repository and copy the content of the folder into the www/picturelibrary location you created before.

```
cd ~ 
git clone https://github.com/websta911/pictureLibrary
cp -r pictureLibrary/* /var/www/pictureLibrary/.
```

Create Virtualenvironment and install python modules

```
cd /var/www/pictureLibrary
virtualenv -p python3 --system-site-packages .venv
source .venv/bin/activate
pip install pycups Pillow flask flask_sqlalchemy flask-wtf passlib
```

Create link "photob" to where ever your background an logo folders are located and "Pictures" to where the Pictures of the Photobox are located. Expected to find folders with foldername in form "%Y-%m-%d"
```
cd /var/www/pictureLibrary
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
create a socket file for nginx to communicate with uwsgi
```
cd /tmp
touch picLib.sock
sudo chown www-data picLib.sock
```
Add configuration for nginx and uwsgi.
Delete default configuration for nginx and the link in sites-enabled if exists
```
cd /etc/nginx/sites-available/
sudo rm default
sudo rm /etc/nginx/sites-enabled/default
```
Create a configuration file picLib ... 
```
sudo vim picLib
```

with the following content:

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
         alias /var/www/pictureLibrary/static/;
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
venv = /var/www/pictureLibrary/.venv
chdir = /var/www/pictureLibrary
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
