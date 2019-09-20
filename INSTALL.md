
Install the Picture Library


Sudo Pip install virtualenv
virtualenv -p python3 --system-site-packages picLib
. piclLib/bin/activate
Pip install pycups
pip install Pillow
pip install flask
pip install flask_sqlalchemy
pip install flask-wtf
pip install passlib


Creates Database 
python createTables.py

Make Autostart as Webapplication using uswgi and nginx

https://askubuntu.com/questions/927881/running-a-flask-app-on-startup-with-systemd
https://stackoverflow.com/questions/24941791/starting-flask-server-in-background



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
#### content of picLib
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
#####content end


sudo ln -s /etc/nginx/sites-available/picLib /etc/nginx/sites-enabled/picLib

sudo vim /etc/uwsgi/apps-available/picLib.ini

## content of piclib.ini
[uwsgi]
vhost = true
socket = /tmp/picLib.sock
venv = /home/pi/pictureLibrary/picLib
chdir = /home/pi/pictureLibrary
module = app
callable = app
plugin = python3

### end of content


sudo ln -s /etc/uwsgi/apps-available/picLib.ini /etc/uwsgi/apps-enabled/picLib.ini



sudo service nginx restart
sudo service uwsgi restart

create Folder for Photobooth Backgrounds and Logos

cd ~
mkdir background
chown +777 background
mkdir logo
chown +777 logo
cd background 

## Add one Background and Logo to the folders and create the _bg or _logo symlink  

ln -s /home/pi/background/bgxxx.jpg _bg
ln -s /home/pi/logo/logoxxx.jpg _logo

## this is, if you are using those symlinks as logo/background on  the photobooth changeable from webinterface

## link to where ever your background an logo folder are located (I moved them, before they where in the photobooth location, too lazy to clean that up)
cd ~/pictureLibrary
ln -s /home/pi photob

##Printing 

sudo usermod -a -G lpadmin pi
sudo cupsctl --remote-any
sudo /etc/init.d/cups restart

create printer