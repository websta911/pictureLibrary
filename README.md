# pictureLibrary
webpage to display pictures taken by a photobooth, where people can subscribe to get the pictures sent via email

But it is a little bit more. I built this initially for the first version of mr. Reuterbals photobooth. I wanted the attendees of the wedding to be able to get their pictures also in a digital version.
I did not want the people to block the Photobooth while entering their email address.
So I made an website where all the pictures are displayed and you can enter your email address to get the picture sent some time after the wedding.
Since it went really well I integrated the background and logo settings of the first version of the Photobooth when there was no settings gui.

### contains currently:
- display all pictures in a folder
- subscribe/order specific pictures by providing email address
- some form of event 
- user management
- upload of background and logo files
- manage backgrounds and logos for photobooth
- upload and print of random pictures



### Some kind of explanation:

I am not a developer, so the quality of the code is not that great.
Everything is in app.py there are even some unused functions in there where I tried some things.
In the first few lines are some folder settings.
Some of them are based on symlinks in the project folder.

There are a few symlinks involved which need to be present to be able to start it.
- photob: points to the location where the background and the logo folder are located 
- _logo: the chosen logo in the logo folder
- _bg: the chosen background in the background folder.

I am planning of adding to that and eventually clean some things up but that will not happen in the near future.

One feature I really would like to create is a layoutcreator for the photobooth. Where you can create layouts by placing picture and logo placeholder. But I have no idea how to do that, how and in what form to save the layout and the booth needs the corresponding function to use that.
So this will take a long time to get there if ever.

