## MaterialisticToBookmark
Add saved pages to firefox from the backup used in the Materialistic application (HN app), skipping already bookmarked pages.
## Usage
The software has two modes, SQL and JSON (SUGGESTED). 

With the *json* mode you can update the json backup that can be backed up from Bookmarks Page in Firefox.

With the *sql* mode you can update directly the sql database present in your profile (using linux it's usually inside /home/$USER/.mozilla/firefox/profile/places.sqlite), but the mode is not suggested because unfortunately places.sqlite DBs are not well documented and usually it causes corruption (you won't be able to delete the added bookmarks until you verify the integrity using the tool in about:support and edit the sync to "0" and changecount to "1" in the DB, but it shouldn't occur the problem with bookmarks (just with newly created folders, it doesn't happen with this script). With the *sql* mode your new bookmarks get added to the "Other Bookmarks" folder, feel free to change the *parent* variable if the folder is *id* is different from 5.
