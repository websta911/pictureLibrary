# pictureLibrary
webpage to display pictures taken by a photobooth, where people can subscribe to get the pictures sent via email

But it is a little bit more. I built this initially for the first version of mr. Reuterbals photobooth. I wanted the attendees of the wedding to be able to get their pictures also in a digital version.
I did not want the people to block the Photobooth while entering their email address.
 which had no settings gui.
So I incorporated it in this Webinterface.
I still kept it though because of the ability to upload and choose the logos and background and not to have to remember what the file was called.
There is also some kind of Event attempt in there which is not that awesome but since the subscriptions are added in the database with the active event is good for sorting through that and you can stage the background and logo for the event and activate it.
The logo and background selection is based on symlinks in the background or logos folder and the Photobooth is using those symlinks as background and logo.



Some kind of explanation:

There are a few symlinks involved which need to be present to be able to start it.
- Photob: points to the location where the background and the logo folder are located 
- _logo: the chosen logo in the logo folder
- _bg: the chosen background in the background folder

