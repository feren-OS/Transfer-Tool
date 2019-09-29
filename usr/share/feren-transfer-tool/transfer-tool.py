#!/usr/bin/python3

import os
import gi
import subprocess
import threading
import shutil
import logging

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk, GdkPixbuf, GLib, GObject
from os.path import expanduser

import apt
cache = apt.Cache()

GLib.threads_init()
GObject.threads_init()
Gdk.threads_init()

class init():
    stepsdone = ""
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('transfer-tool.glade')
        self.win = self.builder.get_object('MainWind')
        self.win.connect('delete-event', Gtk.main_quit)
        
        self.notebook = self.builder.get_object('MainSteps')
        
        #PangoFont = Pango.FontDescription("Tahoma 12")
        #self.win.modify_font(PangoFont)
        
        self.win.set_icon_name('feren-transfer-tool')
        
        #Misc
        self.currentpage = self.builder.get_object('GUIStack')
        self.homepagepage = self.builder.get_object('HomePage')
        self.backupdatapage = self.builder.get_object('BackupData')
        self.restoredatapage = self.builder.get_object('RestoreData')
        self.processingpage = self.builder.get_object('Processing')
        self.alldonepage = self.builder.get_object('FinishPageStatus')
        self.failedfilespage = self.builder.get_object('FailedFilesList')
        
        #Home Page
        self.backupdatapagebtn = self.builder.get_object('BackupDataPageBtn')
        self.backupdatapagebtn.connect('clicked', self.goto_backupdata)
        self.restoredatapagebtn = self.builder.get_object('RestoreDataPageBtn')
        self.restoredatapagebtn.connect('clicked', self.goto_restoredata)
        
        #Toolbar
        self.backbtn = self.builder.get_object('BackBtn')
        self.backbtn.connect('clicked', self.goto_home)
        self.aboutpage = self.builder.get_object('AboutBtn')
        self.aboutpage.connect('clicked', self.goto_about)
        self.about = self.builder.get_object('AboutTransferTool')

        #Backup Data
        self.togglealtbackupsource = self.builder.get_object('ToggleAltBackupSource')
        self.togglealtbackupsource.connect('state-set', self.altbackupsource_toggled)
        self.altbackupsource = self.builder.get_object('AltBackupSource')
        self.altbackupsource.connect('file-set', self.altbackupsource_changed)
        
        self.backupselectorbox = self.builder.get_object('BackupDataSelector')

        self.backuptarget = self.builder.get_object('BackupDataLocation')
        self.backuptarget.connect('file-set', self.backuptarget_changed)
        self.beginbackup = self.builder.get_object('BeginBackup')
        self.beginbackup.connect('clicked', self.start_backup)
        
        self.togglehomebackup = self.builder.get_object('ToggleHomeBackup')
        self.togglehomebackup.connect('toggled', self.backup_home_toggled)
        
        self.toggledocsbackup = self.builder.get_object('ToggleDocumentsBackup')
        self.toggledocsbackup.connect('toggled', self.backup_docs_toggled)
        
        self.togglepicsbackup = self.builder.get_object('TogglePicturesBackup')
        self.togglepicsbackup.connect('toggled', self.backup_pics_toggled)
        
        self.togglemusicbackup = self.builder.get_object('ToggleMusicBackup')
        self.togglemusicbackup.connect('toggled', self.backup_music_toggled)
        
        self.togglevideosbackup = self.builder.get_object('ToggleVideosBackup')
        self.togglevideosbackup.connect('toggled', self.backup_videos_toggled)
        
        self.toggledownloadsbackup = self.builder.get_object('ToggleDownloadsBackup')
        self.toggledownloadsbackup.connect('toggled', self.backup_downloads_toggled)
        
        self.toggledesktopbackup = self.builder.get_object('ToggleDesktopBackup')
        self.toggledesktopbackup.connect('toggled', self.backup_desktop_toggled)
        
        self.togglepfpbackup = self.builder.get_object('ToggleAvatarBackup')
        self.togglepfpbackup.connect('toggled', self.backup_pfp_toggled)
        
        self.togglebgbackup = self.builder.get_object('ToggleBGBackup')
        self.togglebgbackup.connect('toggled', self.backup_bg_toggled)

        #Restore Data
        self.restoresource = self.builder.get_object('RestoreDataLocation')
        self.restoresource.connect('file-set', self.restoreresource_changed)
        self.beginrestore = self.builder.get_object('BeginRestore')
        self.beginrestore.connect('clicked', self.start_restore)
        
        self.restoreselectorbox = self.builder.get_object('RestorationBox')
        self.restorebackupsource = ""
        
        self.togglehomerestore = self.builder.get_object('ToggleHomeRestore')
        self.togglehomerestore.connect('toggled', self.restore_home_toggled)
        
        self.toggledocsrestore = self.builder.get_object('ToggleDocumentsRestore')
        self.toggledocsrestore.connect('toggled', self.restore_docs_toggled)
        
        self.togglepicsrestore = self.builder.get_object('TogglePicturesRestore')
        self.togglepicsrestore.connect('toggled', self.restore_pics_toggled)
        
        self.togglemusicrestore = self.builder.get_object('ToggleMusicRestore')
        self.togglemusicrestore.connect('toggled', self.restore_music_toggled)
        
        self.togglevideosrestore = self.builder.get_object('ToggleVideosRestore')
        self.togglevideosrestore.connect('toggled', self.restore_videos_toggled)
        
        self.toggledownloadsrestore = self.builder.get_object('ToggleDownloadsRestore')
        self.toggledownloadsrestore.connect('toggled', self.restore_downloads_toggled)
        
        self.toggledesktoprestore = self.builder.get_object('ToggleDesktopRestore')
        self.toggledesktoprestore.connect('toggled', self.restore_desktop_toggled)
        
        self.togglepfprestore = self.builder.get_object('ToggleAvatarRestore')
        self.togglepfprestore.connect('toggled', self.restore_pfp_toggled)
        
        self.togglebgrestore = self.builder.get_object('ToggleBGRestore')
        self.togglebgrestore.connect('toggled', self.restore_bg_toggled)
        
        #Processing
        self.operationtype = self.builder.get_object('operationtype')
        self.targetlocationtext = self.builder.get_object('targetlocationtext')
        self.sourcelocationtext = self.builder.get_object('sourcelocationtext')
        self.backupcategorytext = self.builder.get_object('backupcategorytext')
        self.copyingstatustext = self.builder.get_object('copyingstatustext')
        self.itemscopyprogress = self.builder.get_object('CopyingFilesProgress')
        self.overallprogress = self.builder.get_object('OverallProgress')
        
        self.backupstatelbl = self.builder.get_object('BackupStatusLbl')
        self.restorestatelbl = self.builder.get_object('RestoreStatusLbl')
        
        self.homecategorylblp = self.builder.get_object('HomeCategoryLblProcessing')
        self.docscategorylblp = self.builder.get_object('DocsCategoryLblProcessing')
        self.picscategorylblp = self.builder.get_object('PicsCategoryLblProcessing')
        self.musiccategorylblp = self.builder.get_object('MusicCategoryLblProcessing')
        self.videoscategorylblp = self.builder.get_object('VideosCategoryLblProcessing')
        self.downloadscategorylblp = self.builder.get_object('DownloadsCategoryLblProcessing')
        self.desktopcategorylblp = self.builder.get_object('DesktopCategoryLblProcessing')
        self.pfpcategorylblp = self.builder.get_object('PfpCategoryLblProcessing')
        self.prepcategorylblp = self.builder.get_object('PreparingLblProcessing')
        self.processinggraphic = self.builder.get_object('ProcessingGraphicImage')
        self.processinggraphic1 = self.builder.get_object('RestoreGraphic')
        self.processinggraphic2 = self.builder.get_object('BackupGraphic')
        self.processinggraphic3 = self.builder.get_object('BackupGraphicAltSource')
        
        self.builder.get_object('GoHome1').connect('pressed', self.goto_home)
        self.builder.get_object('GoHome2').connect('pressed', self.goto_home)
        self.builder.get_object('GoHome3').connect('pressed', self.goto_home)
        
        self.builder.get_object('Exit1').connect('pressed', self.quit_program)
        self.builder.get_object('Exit2').connect('pressed', self.quit_program)
        self.builder.get_object('Exit3').connect('pressed', self.quit_program)
        
        self.builder.get_object('ViewFailures1').connect('pressed', self.view_failed_files)
        self.builder.get_object('ViewFailures2').connect('pressed', self.view_failed_files)
        
        #Failed Files List
        self.liststore = self.builder.get_object('liststore1')
        self.failedlistview = self.builder.get_object('failedfileslistview')
        
        #Extra memory values
        self.homebackupenabled = False
        self.docsbackupenabled = False
        self.picsbackupenabled = False
        self.musicbackupenabled = False
        self.videobackupenabled = False
        self.downloadsbackupenabled = False
        self.desktopbackupenabled = False
        self.pfpbackupenabled = False
        self.bgbackupenabled = False
        self.altbackupsourceenabled = False
        self.altbackupsourcelocat = ""
        self.backuptargetlocat = ""
        self.restoresourcelocat = ""
        self.homerestoreenabled = False
        self.docsrestoreenabled = False
        self.picsrestoreenabled = False
        self.musicrestoreenabled = False
        self.videorestoreenabled = False
        self.downloadsrestoreenabled = False
        self.desktoprestoreenabled = False
        self.pfprestoreenabled = False
        self.bgrestoreenabled = False
        self.failedcopies = {}
        self.failedfolders={}
        self.homeprogress = 0.0
        self.docsprogress = 0.0
        self.picsprogress = 0.0
        self.musicprogress = 0.0
        self.videosprogress = 0.0
        self.downloadsprogress = 0.0
        self.desktopprogress = 0.0
        self.homefilescopied = 0
        self.docsfilescopied = 0
        self.picsfilescopied = 0
        self.musicfilescopied = 0
        self.videosfilescopied = 0
        self.downloadsfilescopied = 0
        self.desktopfilescopied = 0
        self.homefilestocopy = 0
        self.docsfilestocopy = 0
        self.picsfilestocopy = 0
        self.musicfilestocopy = 0
        self.videosfilestocopy = 0
        self.downloadsfilestocopy = 0
        self.desktopfilestocopy = 0
        
        self.changedchosendirectory = ""
        self.aboutlicensetext = ""
        
        #Localisation
        self.documentsfoldername = subprocess.run(['/usr/share/feren-transfer-tool/get-user-dirs', 'Doc'], stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")[0]
        self.picturesfoldername = subprocess.run(['/usr/share/feren-transfer-tool/get-user-dirs', 'Pi'], stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")[0]
        self.musicfoldername = subprocess.run(['/usr/share/feren-transfer-tool/get-user-dirs', 'M'], stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")[0]
        self.videosfoldername = subprocess.run(['/usr/share/feren-transfer-tool/get-user-dirs', 'V'], stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")[0]
        self.downloadsfoldername = subprocess.run(['/usr/share/feren-transfer-tool/get-user-dirs', 'Dow'], stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")[0]
        self.desktopfoldername = subprocess.run(['/usr/share/feren-transfer-tool/get-user-dirs', 'De'], stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")[0]
        
    def quit_program(self, button):
        Gtk.main_quit()
        
    #def processing_animation(self):
        #while True:
            #processinganimationstep = 0
            #while processinganimationstep < 300:
                #self.filecopyimage.xalign = processinganimationstep
                #processinganimationstep += 1
        
    def toggle_bg_options(self, value):
        #Set visibility of controls relating to BG Backup/Restore options to 'value' boolean
        self.togglebgbackup.set_visible(value)
        self.togglebgrestore.set_visible(value)
        self.togglebgrestore.set_sensitive(value)
        self.builder.get_object('ImageBGBackup').set_visible(value)
        self.builder.get_object('bgbkuplabel').set_visible(value)
        self.builder.get_object('ImageBGRestore').set_visible(value)
        self.builder.get_object('bgrestorelabel').set_visible(value)
        
    def view_failed_files_gui(self, button):
        #Clear the failed files list
        self.liststore.clear()
        #Add the failed folder creations first to the list
        for file1 in self.failedfolders:
            self.liststore.append((file1, self.failedcopies[file1],))
        #Add the failed file copies to the list
        for file1 in self.failedcopies:
            self.liststore.append((file1, self.failedcopies[file1],))
        
    def view_failed_files(self, button):
        #Go to the Failed Files List and enable 'Back' if not enabled
        self.currentpage.set_visible_child(self.failedfilespage)
        self.backbtn.set_sensitive(True)
        
    def backup_clear_checkboxes(self):
        self.togglehomebackup.set_active(False)
        self.toggledocsbackup.set_active(False)
        self.togglepicsbackup.set_active(False)
        self.togglemusicbackup.set_active(False)
        self.togglevideosbackup.set_active(False)
        self.toggledownloadsbackup.set_active(False)
        self.toggledesktopbackup.set_active(False)
        self.togglepfpbackup.set_active(False)
        self.togglebgbackup.set_active(False)
        
    def goto_backupdata(self, button):
        #Go to the 'Backup Data' page
        #If an alternative backup source is turned ON when going to this page, check the checkboxes against what is in that directory
        if self.togglealtbackupsource.get_state() == True and self.altbackupsource.get_filename() is not None:
            self.check_checkboxes_backup(self.altbackupsource.get_filename())
        elif self.togglealtbackupsource.get_state() == True:
            self.backup_clear_checkboxes()
        else:
            #Otherwise check the checkboxes against $HOME / ~
            self.check_checkboxes_backup(os.path.expanduser("~"))
        self.currentpage.set_visible_child(self.backupdatapage)
        #Enable the 'Back' button
        self.backbtn.set_sensitive(True)
        
    def restore_clear_checkboxes(self):
        #Clear all the checkboxes in Restore Data
        self.togglehomerestore.set_active(False)
        self.toggledocsrestore.set_active(False)
        self.togglepicsrestore.set_active(False)
        self.togglemusicrestore.set_active(False)
        self.togglevideosrestore.set_active(False)
        self.toggledownloadsrestore.set_active(False)
        self.toggledesktoprestore.set_active(False)
        self.togglepfprestore.set_active(False)
        self.togglebgrestore.set_active(False)
        
    def goto_restoredata(self, button):
        #If there is a chosen restore source, enable/disable the checkboxes in Restore according to what is and isn't in the backup
        if self.restoresource.get_filename() is not None and os.path.exists(self.restorebackupsource):
            self.check_checkboxes_restore(self.restorebackupsource)
        else:
            #Otherwise clear all the checkboxes in Restore
            self.restore_clear_checkboxes()
        #Go to the 'Restore Data' page and enable the 'Back' button
        self.currentpage.set_visible_child(self.restoredatapage)
        self.backbtn.set_sensitive(True)
        
    def goto_home(self, button):
        #This is the 'Back' button code - if the user is on the 'Failed Files' list page, take them back to the 'All Done' page, otherwise take them to the 'Welcome' page
        if self.currentpage.get_visible_child() == self.failedfilespage:
            self.currentpage.set_visible_child(self.alldonepage)
        else:
            self.currentpage.set_visible_child(self.homepagepage)
            self.backbtn.set_sensitive(False)
        
    def goto_about(self, button):
        #Open the About dialog
        self.about.show_all()
        result = self.about.run()
        self.about.hide()
        
    #Backup
    def check_checkboxes_backup(self, location):
        #Enable or disable checkboxes based on whether the files exist or not
        #'Home' exists regardless so enable that tickbox
        self.togglehomebackup.set_sensitive(True)
        self.togglehomebackup.set_active(True)
        #Temporary memory values for knowing the locations of each other backup part
        docslocation = (location+"/"+self.documentsfoldername)
        picslocation = (location+"/"+self.picturesfoldername)
        musiclocation = (location+"/"+self.musicfoldername)
        videoslocation = (location+"/"+self.videosfoldername)
        downloadslocation = (location+"/"+self.downloadsfoldername)
        desktoplocation = (location+"/"+self.desktopfoldername)
        #Check if backup category's applicable folder exists and enable/disable the checkbox accordingly
        if os.path.isdir(docslocation):
            self.toggledocsbackup.set_sensitive(True)
            self.toggledocsbackup.set_active(True)
        else:
            self.toggledocsbackup.set_sensitive(False)
            self.toggledocsbackup.set_active(False)
        if os.path.isdir(picslocation):
            self.togglepicsbackup.set_sensitive(True)
            self.togglepicsbackup.set_active(True)
        else:
            self.togglepicsbackup.set_sensitive(False)
            self.togglepicsbackup.set_active(False)
        if os.path.isdir(musiclocation):
            self.togglemusicbackup.set_sensitive(True)
            self.togglemusicbackup.set_active(True)
        else:
            self.togglemusicbackup.set_sensitive(False)
            self.togglemusicbackup.set_active(False)
        if os.path.isdir(videoslocation):
            self.togglevideosbackup.set_sensitive(True)
            self.togglevideosbackup.set_active(True)
        else:
            self.togglevideosbackup.set_sensitive(False)
            self.togglevideosbackup.set_active(False)
        if os.path.isdir(downloadslocation):
            self.toggledownloadsbackup.set_sensitive(True)
            self.toggledownloadsbackup.set_active(True)
        else:
            self.toggledownloadsbackup.set_sensitive(False)
            self.toggledownloadsbackup.set_active(False)
        if os.path.isdir(desktoplocation):
            self.toggledesktopbackup.set_sensitive(True)
            self.toggledesktopbackup.set_active(True)
        else:
            self.toggledesktopbackup.set_sensitive(False)
            self.toggledesktopbackup.set_active(False)
        #Check for a user picture and enable/disable tickbox accordingly
        #TODO: Find the user picture file of a Windows user in such a way where it can be used as a Linux user picture
        if os.path.isfile(location+"/.face"):
            self.togglepfpbackup.set_sensitive(True)
            self.togglepfpbackup.set_active(True)
        else:
            self.togglepfpbackup.set_sensitive(False)
            self.togglepfpbackup.set_active(False)
        #Check for a desktop background file and enable/disable tickbox accordingly
        #TODO: Support backing up Desktop Background on all supported Feren OS DEs
        if os.path.isfile(location+"/AppData/Roaming/Microsoft/Windows/Themes/TranscodedWallpaper") or os.path.isfile(location+"/AppData/Roaming/Microsoft/Windows/Themes/TranscodedWallpaper.jpg"):
            self.toggle_bg_options(True)
            self.togglebgbackup.set_active(True)
        else:
            self.toggle_bg_options(False)
            self.togglebgbackup.set_active(False)
        
    def backup_altsource_check(self, newstate):
        #Check if the Alternative Backup Source option is checked and if so make changes to the GUI accordingly
        if newstate:
            if self.altbackupsource.get_filename() is not None and os.path.exists(self.altbackupsource.get_filename()) and not self.altbackupsource.get_filename().startswith(os.path.expanduser("~")):
                #Alright, an alternative backup source has been selected, enable the selection box and check the tickbox availability for this source
                self.backupselectorbox.set_sensitive(True)
                self.check_checkboxes_backup(self.altbackupsource.get_filename())
            else:
                #No path selected yet so we'll clear the tickboxes and disable the selection box
                self.backup_clear_checkboxes()
                self.backupselectorbox.set_sensitive(False)
        else:
            #Alternative backup source isn't enabled so the selection box should be enabled
            self.backupselectorbox.set_sensitive(True)
            
    def altbackupsource_toggled(self, button, newstate):
        #When Alternative Backup source is toggled
        if newstate:
            #Enable the alternative backup source selector
            self.altbackupsource.set_sensitive(True)
            #Check that the alternative source was selected or not
            self.backup_altsource_check(newstate)
        else:
            #Disable the alternative backup source selector
            self.altbackupsource.set_sensitive(False)
            #Enable the backup options chooser if it's disabled
            self.backupselectorbox.set_sensitive(True)
            #Change the tickboxes to reflect what can be found in HOME
            self.check_checkboxes_backup(os.path.expanduser("~"))
            
            
    def check_chosen_directory(self, directory, choosercontrol):
        if not choosercontrol.get_filename == self.changedchosendirectory:
            #We will call on a Bash Script to do the handy-work for us in terms of choosing the directory in case of scenarios such as the user choosing a Windows Drive and therefore needing to let them choose which Users folder in there they'd like to backup from
            #TODO: Make this part of the main GUI instead of a Zenity-powered external script
            chosendir = subprocess.run(['/usr/share/feren-transfer-tool/fix-directory-choice', str(directory)], stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")[0]
            #Make a note of what the directory was last changed to by this script so that in future times it runs it won't do anything unless the chosen path has changed
            self.changedchosendirectory = chosendir
            #Set the chosen folder in the Alt. Backup Source folder selector box to the newly chosen folder
            choosercontrol.set_filename(chosendir)
            #Trigger another checkbox check with this change of Alt. Backup Source in mind
            self.backup_altsource_check(True)
        
    def altbackupsource_changed(self, chooser):
        #Call for when the folder selector for alternative backup source location has a new value
        self.backup_altsource_check(True)
        #Trigger the above code for the reasons mentioned in the above code
        self.check_chosen_directory(self.altbackupsource.get_filename(), self.altbackupsource)
    
    def update_status(self, progressvalue, filecopying, category, categoryprogressvalue):
        #Set the overall progress progress bar value to be the current overall progress
        self.overallprogress.set_fraction(progressvalue)
        #Set the 'Currently copying' text to the current file's path
        self.copyingstatustext.set_text(filecopying)
        #Set the 'Currently on' text to the current category being worked on
        self.backupcategorytext.set_visible_child(category)
        #Same as overallprogress.set_fraction but with the current category's progress instead
        self.itemscopyprogress.set_fraction(categoryprogressvalue)
        
    def set_window_closable(self, boolean):
        #Set whether the window is closable or not depending on variable 'boolean'
        self.win.set_deletable(boolean)
        
    def finished_process(self, fileslistcount, target):
        #...and then proceed not to use it here, ok then me... haven't checked if I did this intentionally because it caused a segfault or something yet so your guess is as good as mine
        self.win.set_deletable(True)
        #Take the user to the 'All Done' page
        self.currentpage.set_visible_child(self.alldonepage)
        #Re-enable the back button
        self.backbtn.set_sensitive(True)
        #Change page depending on self.failedcopies
        # - If nothing failed to copy, we'll show the 'Everything copied' version of this page
        # - If 10 or less files managed to copy while the rest didn't, we'll consider it a failed operation and show the 'Operation Failed' version of this page
        # - Otherwise it's the 'All Done With Errors' version of this page
        if len(self.failedcopies) == 0:
            self.alldonepage.set_visible_child(self.builder.get_object('AllDoneSuccess'))
        elif len(self.failedcopies) >= (fileslistcount - 10):
            self.alldonepage.set_visible_child(self.builder.get_object('FailedOperation'))
            GLib.idle_add(lambda: self.view_failed_files_gui(''))
            GLib.timeout_add(10, lambda: self.view_failed_files_gui(''))
        else:
            self.alldonepage.set_visible_child(self.builder.get_object('AllDoneWithErrors'))
            GLib.idle_add(lambda: self.view_failed_files_gui(''))
            GLib.timeout_add(10, lambda: self.view_failed_files_gui(''))
        
    def copy_files(self, togglehome, toggledocs, togglepics, togglemusic, togglevideos, toggledownloads, toggledesktop, togglepfp, togglebg, source, target):
        #Disable closing the window by the close button
        GLib.idle_add(lambda: self.set_window_closable(False))
        GLib.timeout_add(10, lambda: self.set_window_closable(False))
        #Change the status to 'Preparing' on the Processing screen
        GLib.idle_add(lambda: self.update_status(0.0, "", self.prepcategorylblp, 0.0))
        GLib.timeout_add(10, lambda: self.update_status(0.0, "", self.prepcategorylblp, 0.0))
        #Just some variable setting in case
        categorytype = self.prepcategorylblp
        categoryprogress = 0.0
        #Thread function to copy files
        #Empty values for later
        filestocopy = 0
        backupfileslist = {}
        #Progress Bar values for 'Copying Progress'
        self.homeprogress = 0.0
        self.docsprogress = 0.0
        self.picsprogress = 0.0
        self.musicprogress = 0.0
        self.videosprogress = 0.0
        self.downloadsprogress = 0.0
        self.desktopprogress = 0.0
        self.homefilescopied = 0
        self.docsfilescopied = 0
        self.picsfilescopied = 0
        self.musicfilescopied = 0
        self.videosfilescopied = 0
        self.downloadsfilescopied = 0
        self.desktopfilescopied = 0
        self.homefilestocopy = 0
        self.docsfilestocopy = 0
        self.picsfilestocopy = 0
        self.musicfilestocopy = 0
        self.videosfilestocopy = 0
        self.downloadsfilestocopy = 0
        self.desktopfilestocopy = 0
        #Walk through the source directory
        #TODO: Maybe warn the user that later on in the code their Home will be hosed of all broken symlinks
        
        #See what directories are in the source directory
        #Blank out these variables just in case first...
        folderstoscaninsource=[]
        filesinsource=[]
        for folder in os.listdir(source):
            #If the item in the source folder is a symlink, we'll add it to the list of files to be copied from the source folder's main folder
            if os.path.islink(source+"/"+folder) and not folder.startswith(".") and togglehome == True:
                filesinsource.append(folder)
            elif os.path.isdir(source+"/"+folder):
                #Otherwise if it's a directory, we'll do some checks to make sure unwanted folders aren't copied when doing the real transfer process
                if folder.startswith("."):
                    #Exclude hidden directories
                    pass
                elif togglehome == False and folder != (self.documentsfoldername) and folder != (self.picturesfoldername) and folder != (self.musicfoldername) and folder != (self.videosfoldername) and folder != (self.downloadsfoldername) and folder != (self.desktopfoldername):
                    #If Home Folder is turned OFF and the folder found isn't any other category's folder, exclude it
                    pass
                elif toggledocs == False and folder == (self.documentsfoldername):
                    #Exclude Documents Folder if Documents is OFF
                    pass
                elif folder == "AppData" or folder == "Searches" or folder == "Cookies":
                    #Exclude some folders including Windows User Folders
                    pass
                elif togglepics == False and folder == (self.picturesfoldername):
                    #...I think you get the point by now.
                    pass
                elif togglemusic == False and folder == (self.musicfoldername):
                    pass
                elif togglevideos == False and folder == (self.videosfoldername):
                    pass
                elif toggledownloads == False and folder == (self.downloadsfoldername):
                    pass
                elif toggledesktop == False and folder == (self.desktopfoldername):
                    pass
                elif not str(folder) in folderstoscaninsource:
                    #The last exclusion is if it's not already added to the list
                    folderstoscaninsource.append(str(source+"/"+folder))
            elif os.path.isfile(source+"/"+folder) and not folder.startswith(".") and togglehome == True and not ((folder.startswith("NTUSER.DAT") and (folder.endswith(".blf") or folder.endswith(".regtrans-ms"))) or (folder.startswith("ntuser.dat") and (folder.endswith(".blf") or folder.endswith(".regtrans-ms"))) or folder == "ntuser.dat" or folder == "ntuser.ini" or folder == "NTUSER.DAT"):
                #If it's a file, however, isn't hidden and isn't a Windows System File, add it to the list of files in the source folder to copy over
                filesinsource.append(folder)
        if togglepfp == True:
            #Add user picture if enabled to the files to copy from source folder
            filesinsource.append(".face")
        if togglehome == True or togglepfp == True:
            #Only append Source Folder contents to the backup list if Home Folder or Profile Picture are ON
            backupfileslist[source] = filesinsource
        
        #Look through the folders found in source directory
        for directory in folderstoscaninsource:
            for r, d, f in os.walk(directory, followlinks=False):                   
                backupfileslist[r] = f
                #Extra bit for adding folder symlinks
                for file1 in d:
                    if os.path.islink(r+"/"+file1):
                        backupfileslist[r].append(file1)
                #Add count of files and links found to be copied in that folder to the overall files count
                filestocopy += len(backupfileslist[r])
                if r.startswith(source+"/"+self.documentsfoldername+"/") or r == (source+"/"+self.documentsfoldername):
                    #If it's part of Documents, add the files and links found in there to the Documents files count
                    self.docsfilestocopy += len(backupfileslist[r])
                elif r.startswith(source+"/"+self.picturesfoldername+"/") or r == (source+"/"+self.picturesfoldername):
                    #...you get the idea with the rest of these.
                    self.picsfilestocopy += len(backupfileslist[r])
                elif r.startswith(source+"/"+self.musicfoldername+"/") or r == (source+"/"+self.musicfoldername):
                    self.musicfilestocopy += len(backupfileslist[r])
                elif r.startswith(source+"/"+self.videosfoldername+"/") or r == (source+"/"+self.videosfoldername):
                    self.videosfilestocopy += len(backupfileslist[r])
                elif r.startswith(source+"/"+self.downloadsfoldername+"/") or r == (source+"/"+self.downloadsfoldername):
                    self.downloadsfilestocopy += len(backupfileslist[r])
                elif r.startswith(source+"/"+self.desktopfoldername+"/") or r == (source+"/"+self.desktopfoldername):
                    self.desktopfilestocopy += len(backupfileslist[r])
                else:
                    self.homefilestocopy += len(backupfileslist[r])
                    
        #Add filesdone variable for counting done files/folders
        filesdone = 0
        
        #NOTE: r has the full directory path
        #Clear the failedcopies and failedfolders lists in case
        self.failedcopies={}
        self.failedfolders={}
        #For each folder in the overall list of folders and files to be copied over from source, make their destination folder counterpart
        for folder in backupfileslist:
            if not os.path.isdir(folder.replace(source, target)):
                #Create folders on target if they don't exist
                try:
                    os.makedirs(folder.replace(source, target))
                except Exception as e:
                    #If the folder failed to be created, store their source folder path and the reason for them failing in failedfolders for later
                    self.failedfolders[folder.replace(source, target)] = type(e).__name__
        #For each file in the overall list of folders and files to be copied over from source, copy them to their location
        for folder in backupfileslist:
            for file1 in backupfileslist[folder]:
                if not file1 == "":
                    #Update GUI Status to reflect what is being copied, etc.
                    GLib.idle_add(lambda: self.update_status((filesdone / filestocopy), (folder+"/"+file1).replace((source+"/"), ""), categorytype, categoryprogress))
                    GLib.timeout_add(10, lambda: self.update_status((filesdone / filestocopy), (folder+"/"+file1).replace((source+"/"), ""), categorytype, categoryprogress))
                    #Set srcFile to the overall source file path
                    srcFile = os.path.join(folder, file1)
                    #Set destFile to srcFile but with the destination directory instead of the source directory
                    destFile = srcFile.replace(source, target)
                    #Change status depending on category
                    if srcFile.startswith(source+"/"+self.documentsfoldername):
                        categorytype = self.docscategorylblp
                        categoryon = 1
                        categoryprogress = self.docsprogress
                    elif srcFile.startswith(source+"/"+self.picturesfoldername):
                        categorytype = self.picscategorylblp
                        categoryon = 2
                        categoryprogress = self.picsprogress
                    elif srcFile.startswith(source+"/"+self.musicfoldername):
                        categorytype = self.musiccategorylblp
                        categoryon = 3
                        categoryprogress = self.musicprogress
                    elif srcFile.startswith(source+"/"+self.videosfoldername):
                        categorytype = self.videoscategorylblp
                        categoryon = 4
                        categoryprogress = self.videosprogress
                    elif srcFile.startswith(source+"/"+self.downloadsfoldername):
                        categorytype = self.downloadscategorylblp
                        categoryon = 5
                        categoryprogress = self.downloadsprogress
                    elif srcFile.startswith(source+"/"+self.desktopfoldername):
                        categorytype = self.desktopcategorylblp
                        categoryon = 6
                        categoryprogress = self.desktopprogress
                    elif srcFile == (source+"/.face"):
                        categorytype = self.pfpcategorylblp
                        categoryon = 7
                        categoryprogress = 0.0
                    else:
                        categorytype = self.homecategorylblp
                        categoryon = 0
                        categoryprogress = self.homeprogress
                    #Delete symlinks where possible to prevent them from causing Transfer Tool to copy symlinks into symlinked folders on overwriting operations
                    try:
                        if os.path.islink(destFile):
                            try:
                                os.remove(destFile)
                            except:
                                pass
                        #Copy the file
                        shutil.copy(srcFile, destFile, follow_symlinks=False)
                    except Exception as e:
                        #If the file failed to copy, store the source file path and the reason for failing in failedcopies for later
                        self.failedcopies[srcFile] = type(e).__name__
                    #Add one to the files done count
                    filesdone += 1
                    #Do the same with the category-only files done count
                    if categoryon == 0:
                        self.homefilescopied += 1
                        if self.homefilestocopy != 0:
                            self.homeprogress = (self.homefilescopied / self.homefilestocopy)
                        else:
                            self.homeprogress = 1.0
                    elif categoryon == 1:
                        self.docsfilescopied += 1
                        if self.docsfilestocopy != 0:
                            self.docsprogress = (self.docsfilescopied / self.docsfilestocopy)
                        else:
                            self.docsprogress = 1.0
                    elif categoryon == 2:
                        self.picsfilescopied += 1
                        if self.picsfilestocopy != 0:
                            self.picsprogress = (self.picsfilescopied / self.picsfilestocopy)
                        else:
                            self.picsprogress = 1.0
                    elif categoryon == 3:
                        self.musicfilescopied += 1
                        if self.musicfilestocopy != 0:
                            self.musicprogress = (self.musicfilescopied / self.musicfilestocopy)
                        else:
                            self.musicprogress = 1.0
                    elif categoryon == 4:
                        self.videosfilescopied += 1
                        if self.videosfilestocopy != 0:
                            self.videosprogress = (self.videosfilescopied / self.videosfilestocopy)
                        else:
                            self.videosprogress = 1.0
                    elif categoryon == 5:
                        self.downloadsfilescopied += 1
                        if self.downloadsfilestocopy != 0:
                            self.downloadsprogress = (self.downloadsfilescopied / self.downloadsfilestocopy)
                        else:
                            self.downloadsprogress = 1.0
                    elif categoryon == 6:
                        self.desktopfilescopied += 1
                        if self.desktopfilestocopy != 0:
                            self.desktopprogress = (self.desktopfilescopied / self.desktopfilestocopy)
                        else:
                            self.desktopprogress = 1.0
                            
        #Copy Windows BG if turned ON
        if togglebg:
            #Use a script to get the background copied
            #If the operation is a Restore, also add an extra argument for applying the backed up BG automatically
            if target == os.path.expanduser("~"):
                #TODO: Put the script in this code instead
                subprocess.Popen(["/usr/share/feren-transfer-tool/copy-bg", str(target), str(source), "--restore"])
            else:
                subprocess.Popen(["/usr/share/feren-transfer-tool/copy-bg", str(target), str(source)])
        
        #Clean up .lnk and Thumbs.db files
        #If the operation is a Restore, also hose the home folder of broken symlinks
        if target == os.path.expanduser("~"):
            print("Lost symlinks")
            subprocess.Popen(["/usr/share/feren-transfer-tool/cleanup-target", str(target), "--clear-lost-symlinks"])
        else:
            subprocess.Popen(["/usr/share/feren-transfer-tool/cleanup-target", str(target)])
        #We're done, let's take the user to the 'All Done' page
        GLib.idle_add(lambda: self.finished_process(len(backupfileslist), target))
        GLib.timeout_add(10, lambda: self.finished_process(len(backupfileslist), target))
        
    def start_backup(self, button):
        #Go to the Processing page
        self.currentpage.set_visible_child(self.processingpage)
        #Disable the Back button
        self.backbtn.set_sensitive(False)
        #Change the Operation label to Backup
        self.operationtype.set_visible_child(self.backupstatelbl)
        #Set memory values
        self.homebackupenabled = self.togglehomebackup.get_active()
        self.docsbackupenabled = self.toggledocsbackup.get_active()
        self.picsbackupenabled = self.togglepicsbackup.get_active()
        self.musicbackupenabled = self.togglemusicbackup.get_active()
        self.videobackupenabled = self.togglevideosbackup.get_active()
        self.downloadsbackupenabled = self.toggledownloadsbackup.get_active()
        self.desktopbackupenabled = self.toggledesktopbackup.get_active()
        self.pfpbackupenabled = self.togglepfpbackup.get_active()
        self.altbackupsourceenabled = self.togglealtbackupsource.get_state()
        self.bgbackupenabled = self.togglebgbackup.get_active()
        #Set backup path accordingly
        if self.altbackupsourceenabled:
            #If Alternative Backup Source is turned on, let's change the source to the selected backup source location
            self.altbackupsourcelocat = self.altbackupsource.get_filename()
            #Change the graphic on the bottom of Processing to the HD to HD graphic
            self.processinggraphic.set_visible_child(self.processinggraphic3)
        else:
            #Otherwise, we'll set the source to the user's home folder path and change the graphic to the Feren OS to HD graphic
            self.altbackupsourcelocat = os.path.expanduser("~")
            self.processinggraphic.set_visible_child(self.processinggraphic2)
        #Set the Backup Target location to be the one selected by the user
        self.backuptargetlocat = self.backuptarget.get_filename()
        #If the folder isn't FerenTransferToolBackups, let's fix that fact
        if not self.backuptargetlocat.endswith("/FerenTransferToolBackups"):
            self.backuptargetlocat = (self.backuptargetlocat+"/FerenTransferToolBackups")
        #If the backup target location folder doesn't exist, let's create it
        if not os.path.exists(self.backuptargetlocat):
            try:
                os.makedirs(self.backuptargetlocat)
            except Exception as e:
                #If this fails, we'll just abort operation, announce 'Operation Failed' and list the folder as a 'Failed File' on the 'Operation Failed' screen before taking the user there
                #Clear the failedcopies dict.
                self.failedcopies={}
                #Append this failed folder to it and the error type
                self.failedcopies[self.backuptargetlocat] = type(e).__name__
                #Do as the top comment mentions
                GLib.idle_add(lambda: self.finished_process(1, self.backuptargetlocat))
                GLib.timeout_add(10, lambda: self.finished_process(1, self.backuptargetlocat))
                return
        #Make the Overwriting Notice visible for the next time the user goes to the 'Backup Data' screen now future backups on the current settings will overwrite their incoming backup
        self.builder.get_object('OverwritingNotice').set_visible(True)
        #Debugging information
        #print("Backup Home:", self.homebackupenabled)
        #print("Backup Docs:", self.docsbackupenabled)
        #print("Backup Pics:", self.picsbackupenabled)
        #print("Backup Music:", self.musicbackupenabled)
        #print("Backup Videos:", self.videobackupenabled)
        #print("Backup Downloads:", self.downloadsbackupenabled)
        #print("Backup Desktop:", self.desktopbackupenabled)
        #print("Backup Pfp:", self.pfpbackupenabled)
        #print("Alt source:", self.altbackupsourceenabled)
        #print("Alt source:", self.altbackupsourcelocat)
        #print("Backup target:", self.backuptargetlocat)
        #Change in-UI labels to show what the source and target locations are
        self.targetlocationtext.set_markup(self.backuptargetlocat)
        self.sourcelocationtext.set_markup(self.altbackupsourcelocat)
        
        #Initiate the copying process
        self.thread = threading.Thread(target=self.copy_files,
                                  args=(self.homebackupenabled, self.docsbackupenabled, self.picsbackupenabled, self.musicbackupenabled, self.videobackupenabled, self.downloadsbackupenabled, self.desktopbackupenabled, self.pfpbackupenabled, self.bgbackupenabled, self.altbackupsourcelocat, self.backuptargetlocat))
        self.thread.start()
        
    def check_if_backup_possible(self):
        #Call for checking if the backup is possible (aka: The user hasn't turned off every option for backup)
        if not self.togglehomebackup.get_active() == True and not self.toggledocsbackup.get_active() == True and not self.togglepicsbackup.get_active() == True and not self.togglemusicbackup.get_active() == True and not self.togglevideosbackup.get_active() == True and not self.toggledownloadsbackup.get_active() == True and not self.toggledesktopbackup.get_active() == True and not self.togglepfpbackup.get_active() == True and not self.togglebgbackup.get_active() == True:
            #We can't backup nothing - disable the backup button
            self.beginbackup.set_sensitive(False)
        elif self.backuptarget.get_filename() == None:
            #We can't backup to nothing - disable the backup button
            self.beginbackup.set_sensitive(False)
        elif self.backuptarget.get_filename() == os.path.expanduser("~"):
            self.beginbackup.set_sensitive(False)
        else:
            #Enable the backup button
            self.beginbackup.set_sensitive(True)
        
    def backuptarget_changed(self, button):
        #Call for when the backup target folder selector has a new value
        if os.path.isdir(self.backuptarget.get_filename() + "/FerenTransferToolBackups"):
            #If the chosen area already has a backups folder in it, warn the user that doing a backup will overwrite that current backup
            self.builder.get_object('OverwritingNotice').set_visible(True)
        else:
            self.builder.get_object('OverwritingNotice').set_visible(False)
        #Call earlier code in case all the checkboxes were unchecked or something during this process
        self.check_if_backup_possible()
        
    def backup_home_toggled(self, button):
        #Check if the 'Backup Data' button can be used or not now with this checkbox change in mind
        self.check_if_backup_possible()
        
    def backup_docs_toggled(self, button):
        #You get the point ^
        self.check_if_backup_possible()
        
    def backup_pics_toggled(self, button):
        self.check_if_backup_possible()
        
    def backup_music_toggled(self, button):
        self.check_if_backup_possible()
        
    def backup_videos_toggled(self, button):
        self.check_if_backup_possible()
        
    def backup_downloads_toggled(self, button):
        self.check_if_backup_possible()
        
    def backup_desktop_toggled(self, button):
        self.check_if_backup_possible()
        
    def backup_pfp_toggled(self, button):
        self.check_if_backup_possible()
        
    def backup_bg_toggled(self, button):
        self.check_if_backup_possible()
        
    #Restore      
    def check_checkboxes_restore(self, location):
        #Enable or disable checkboxes based on whether the files exist or not
        #'Home' exists regardless so enable that tickbox
        self.togglehomerestore.set_sensitive(True)
        self.togglehomerestore.set_active(True)
        #Temporary memory values for knowing the locations of each other restore part
        docslocation = (location+"/"+self.documentsfoldername)
        picslocation = (location+"/"+self.picturesfoldername)
        musiclocation = (location+"/"+self.musicfoldername)
        videoslocation = (location+"/"+self.videosfoldername)
        downloadslocation = (location+"/"+self.downloadsfoldername)
        desktoplocation = (location+"/"+self.desktopfoldername)
        #Check if restore category's applicable folder exists and enable/disable the checkbox accordingly
        if os.path.isdir(docslocation):
            self.toggledocsrestore.set_sensitive(True)
            self.toggledocsrestore.set_active(True)
        else:
            self.toggledocsrestore.set_sensitive(False)
            self.toggledocsrestore.set_active(False)
        if os.path.isdir(picslocation):
            self.togglepicsrestore.set_sensitive(True)
            self.togglepicsrestore.set_active(True)
        else:
            self.togglepicsrestore.set_sensitive(False)
            self.togglepicsrestore.set_active(False)
        if os.path.isdir(musiclocation):
            self.togglemusicrestore.set_sensitive(True)
            self.togglemusicrestore.set_active(True)
        else:
            self.togglemusicrestore.set_sensitive(False)
            self.togglemusicrestore.set_active(False)
        if os.path.isdir(videoslocation):
            self.togglevideosrestore.set_sensitive(True)
            self.togglevideosrestore.set_active(True)
        else:
            self.togglevideosrestore.set_sensitive(False)
            self.togglevideosrestore.set_active(False)
        if os.path.isdir(downloadslocation):
            self.toggledownloadsrestore.set_sensitive(True)
            self.toggledownloadsrestore.set_active(True)
        else:
            self.toggledownloadsrestore.set_sensitive(False)
            self.toggledownloadsrestore.set_active(False)
        if os.path.isdir(desktoplocation):
            self.toggledesktoprestore.set_sensitive(True)
            self.toggledesktoprestore.set_active(True)
        else:
            self.toggledesktoprestore.set_sensitive(False)
            self.toggledesktoprestore.set_active(False)
        #Check for a backed up user picture and enable/disable tickbox accordingly
        if os.path.isfile(location+"/.face"):
            self.togglepfprestore.set_sensitive(True)
            self.togglepfprestore.set_active(True)
        else:
            self.togglepfprestore.set_sensitive(False)
            self.togglepfprestore.set_active(False)
        #Check for a backed up desktop background and enable/disable tickbox accordingly
        if os.path.isfile(location+"/TransferToolBackground"):
            self.toggle_bg_options(True)
            self.togglebgrestore.set_active(True)
        else:
            self.toggle_bg_options(False)
            self.togglebgrestore.set_active(False)
        
    def restore_source_check(self):
        #Check if Restore Source exists and if so make changes to the GUI accordingly
        if self.restoresource.get_filename() is not None and os.path.exists(self.restorebackupsource) and not self.restorebackupsource == os.path.expanduser("~"):
            #Alright, an alternative restore source has been selected, enable the selection box and check the tickbox availability for this source
            self.restoreselectorbox.set_sensitive(True)
            self.check_checkboxes_restore(self.restorebackupsource)
        else:
            #No path selected yet so we'll clear the tickboxes and disable the selection box
            self.restore_clear_checkboxes()
            self.restoreselectorbox.set_sensitive(False)
        
    def restoreresource_changed(self, chooser):
        #Call for when the folder selector for alternative restore source location has a new value
        if not self.restoresource.get_filename().endswith("/FerenTransferToolBackups") and os.path.exists(self.restoresource.get_filename()+"/FerenTransferToolBackups"):
            self.restorebackupsource = (self.restoresource.get_filename()+"/FerenTransferToolBackups")
            self.restore_source_check()
        else:
            self.restorebackupsource = self.restoresource.get_filename()
            self.restore_source_check()
        
    def start_restore(self, button):
        #Go to the Processing page
        self.currentpage.set_visible_child(self.processingpage)
        self.processinggraphic.set_visible_child(self.processinggraphic1)
        #Disable the Back button
        self.backbtn.set_sensitive(False)
        #Change the Operation label to Backup
        self.operationtype.set_visible_child(self.restorestatelbl)
        #Set memory values
        self.homerestoreenabled = self.togglehomerestore.get_active()
        self.docsrestoreenabled = self.toggledocsrestore.get_active()
        self.picsrestoreenabled = self.togglepicsrestore.get_active()
        self.musicrestoreenabled = self.togglemusicrestore.get_active()
        self.videorestoreenabled = self.togglevideosrestore.get_active()
        self.downloadsrestoreenabled = self.toggledownloadsrestore.get_active()
        self.desktoprestoreenabled = self.toggledesktoprestore.get_active()
        self.pfprestoreenabled = self.togglepfprestore.get_active()
        self.bgrestoreenabled = self.togglebgrestore.get_active()
        #Set restore path accordingly
        self.restoresourcelocat = self.restorebackupsource
        self.restoretargetlocat = os.path.expanduser("~")
        #Debugging information
        #print("Restore Home:", self.homerestoreenabled)
        #print("Restore Docs:", self.docsrestoreenabled)
        #print("Restore Pics:", self.picsrestoreenabled)
        #print("Restore Music:", self.musicrestoreenabled)
        #print("Restore Videos:", self.videorestoreenabled)
        #print("Restore Downloads:", self.downloadsrestoreenabled)
        #print("Restore Desktop:", self.desktoprestoreenabled)
        #print("Restore Pfp:", self.pfprestoreenabled)
        #print("Restore Source:", self.restoresourcelocat)
        #Change in-UI labels
        self.targetlocationtext.set_markup(self.restoretargetlocat)
        self.sourcelocationtext.set_markup(self.restoresourcelocat)
        
        #Start the file copying process
        self.thread = threading.Thread(target=self.copy_files,
                                  args=(self.homerestoreenabled, self.docsrestoreenabled, self.picsrestoreenabled, self.musicrestoreenabled, self.videorestoreenabled, self.downloadsrestoreenabled, self.desktoprestoreenabled, self.pfprestoreenabled, self.bgrestoreenabled, self.restoresourcelocat, self.restoretargetlocat))
        self.thread.start()
        
    def check_if_restore_possible(self):
        #Call for checking if the restore is possible (aka: The user hasn't turned off every option for restore)
        if not self.togglehomerestore.get_active() == True and not self.toggledocsrestore.get_active() == True and not self.togglepicsrestore.get_active() == True and not self.togglemusicrestore.get_active() == True and not self.togglevideosrestore.get_active() == True and not self.toggledownloadsrestore.get_active() == True and not self.toggledesktoprestore.get_active() == True and not self.togglepfprestore.get_active() == True and not self.togglebgrestore.get_active():
            #We can't restore nothing - disable the restore button
            self.beginrestore.set_sensitive(False)
        else:
            #Enable the restore button
            self.beginrestore.set_sensitive(True)
        
    def restore_home_toggled(self, button):
        #Same thing as with backup_home_toggled, etc.
        self.check_if_restore_possible()
        
    def restore_docs_toggled(self, button):
        self.check_if_restore_possible()
        
    def restore_pics_toggled(self, button):
        self.check_if_restore_possible()
        
    def restore_music_toggled(self, button):
        self.check_if_restore_possible()
        
    def restore_videos_toggled(self, button):
        self.check_if_restore_possible()
        
    def restore_downloads_toggled(self, button):
        self.check_if_restore_possible()
        
    def restore_desktop_toggled(self, button):
        self.check_if_restore_possible()
        
    def restore_pfp_toggled(self, button):
        self.check_if_restore_possible()
        
    def restore_bg_toggled(self, button):
        self.check_if_restore_possible()

    ### SHOW APP ###
    def run(self):
        self.win.set_auto_startup_notification(True)
        self.win.show_all()
        #Hide the hidden-by-default items and immediately check all the available boxes in Backup Data depending on what exists and what doesn't in ~
        self.check_checkboxes_backup(os.path.expanduser("~"))
        self.toggle_bg_options(False)
        self.builder.get_object('OverwritingNotice').set_visible(False)
        Gtk.main()

if __name__ == '__main__':
    usettings = init()
    usettings.run()
