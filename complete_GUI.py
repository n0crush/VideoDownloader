#!python -3


"""
#time_modify: 03:27 AM 12/13/2020
#note: 
	- incomplete:
		- download list, download playlist function
		- use configuration files for user customization: color, font, default folder
		- clearly log
		- clean code


"""


__auth__ = "@n0crush"
__info__ = ["github.com/n0crush", "twitter.com/n0crush"]


import requests
"""
	try:
		import requests
	except:
		pass
			os.system('pip install requests')
			print('[WARNING] An Error occured when try to import "requests".')
			sys.exit('[ RUN AGAIN ]')
"""
import re, os, sys
import logging
from datetime import datetime
from subprocess import Popen
from threading import Thread
from queue import Queue, Empty
#----------------------

from tkinter import Tk, Frame, Menu, Label, Entry, Button
from tkinter import StringVar
from tkinter import END, S, W, N, E, RIGHT
from tkinter import scrolledtext, ttk
import tkinter.messagebox as messagebox
from tkinter.filedialog import asksaveasfile, askdirectory, askopenfilename
#----------------------

from fb_temp import Facebook
from yt_temp import Youtube
#----------------------

_CWD = os.getcwd()

if not os.path.exists(os.path.join(_CWD, 'AppData')):
	os.mkdir(os.path.join(_CWD, 'AppData'))



class Base:

	current_option = {
		'fb':{
			'single':1, 'playlist':0
		},
		'yt':{
			'single':0, 'playlist':0
		}
	}


	def _current_option(self):
		crt_op = None
		if (self.current_option['fb']['single']==1) and (self.current_option['fb']['playlist']==0):
			crt_op = 'fb10'
		elif self.current_option['fb']['playlist']==1:
			crt_op = 'fb11'
		elif (self.current_option['yt']['single']==1) and (self.current_option['yt']['playlist']==0):
			crt_op = 'yt10'
		elif self.current_option['yt']['playlist']==1:
			crt_op = 'yt11'	
		return crt_op		


class WidgetActivity(Base):
	def __init__(self, widget):
		self.widget = widget
		self.FB = Facebook()
		self.YT = Youtube()

	def _sgl_fb_getlink(self, url):
		self.FB.__init__()			#this is neccessary whenever make a new getlink

		file_format = [None]

		do = self.FB.getLink(url)
		#log here

		main_log.log(logging.WARNING, do)
		gl_log.log(logging.WARNING, do)

		sample = {'hd_src':'HD', 'sd_src':'no HD', 'sd_src_no_ratelimit':'no HD(full speed)'}
		duma = 'sd_src_no_ratelimit'

		if self.FB.getLink_status=="Success":
			for k in self.FB.origin_link.keys():
				file_format.insert(-1, sample[k])

				if len(sample[k])<len(sample[duma]):
					duma = k
	
			self.widget.original_url_value.set(self.FB.origin_link[duma])

			now = sample[duma]
		else:
			now = None

		self.widget.cbx2['value'] = list(file_format)
		self.widget.cbx2.current(file_format.index(now))

	def _sgl_yt_getlink(self, url):
		self.YT.__init__()			#this is neccessary whenever make a new getlink

		self.widget.file_quality = {'MP4a':{'None':'None'}, 'MP4':{'None':'None'}, 'MP3':{'None':'None'}, 'None':{'None':'None'}}

		self.YT.setUrl(url)
		res = self.YT.getRequest()

		if res[0]=='false':			#request fail
			self.widget._set_cbx_none()

			main_log.log(logging.ERROR, res[1])
			gl_log.log(logging.ERROR, res[1])

			return

		#get data success
		data_as_dict = self.YT.getInfo(res[1])

		filter_info = self.YT.filterInfo(data_as_dict)

		#video links unavailable
		if filter_info[0]=='false':
			main_log.log(logging.ERROR, filter_info[1])
			gl_log.log(logging.ERROR, filter_info[1])

			self.widget._set_cbx_none()

			title = "(Error)|Video unavailable"
			message = filter_info
			#log here

			messagebox.showinfo(title=title, message=message)

			return

		#else format look like:
		'''
			sample_itag_formats = {
			'MP4a': {'360p': 18},
			'MP4': {'1080p': 248, '720p': 398, '360p': 38},
			'MP3': {'AUDIO_QUALITY_MEDIUM': 251, 'AUDIO_QUALITY_LOW': 250}
			}
		'''
		itag_formats = self.YT.getListQualityLabel()

		for k in itag_formats.keys():
			itag_formats[k].setdefault("None", "None")
		itag_formats['None'] = {'None':'None'}

		temp = "Get link successfully ---------- Type: %s" %(str(list(itag_formats.keys())))

		main_log.log(logging.INFO, "Get link successfully")

		self.widget.original_url_value.set(temp)

		"""
		#file_quality sample
		{
			'None': ['None'],
			'MP4a': ['360p', 'None'],
			'MP4': ['1080p', '720p', '480p', '360p', '240p', '144p', 'None'],
			'MP3': ['AUDIO_QUALITY_MEDIUM', 'AUDIO_QUALITY_LOW', 'None']
		}
		"""
		file_format = list(itag_formats.keys())
		
		self.widget.file_format = file_format
		self.widget.file_quality = itag_formats

		self.widget._updateEmbdedFrame(1000)	#integral

	def _getforget(self):
		option = self.widget._current_option()

		self.widget._set_cbx_none()

		url = self.widget.url_value.get()

		#log 'url entry'
		main_log.log(logging.INFO, ('Url: \"%s\"' %url))
		gl_log.log(logging.INFO, ('Url: \"%s\"' %url))

		if option=='fb10':
			self._sgl_fb_getlink(url)
		elif option=='yt10':
			self._sgl_yt_getlink(url)

	def getlink(self):
		#---------------

		crt_op = self._current_option()

		logger.warning(str("current option: \"%s\"" %crt_op))

		if (crt_op=='fb11') or (crt_op=='yt11'):
			logger.log(logging.ERROR, "Function interrupted cause fb11/yt11 feature")
			main_log.log(logging.ERROR, "Options>>Facebook>>Single file   or  Options>>Youtube>>Single file")
			return
		#---------------

		logger.info("Create getLink thread")
		gl_log.info("Create getLink thread")
		Thread(target=self._getforget).start()

	#---------------------------------------------------------------------------
	def _sgl_fb_download(self, quality, path):	#certain 
		sample = {'hd_src':'HD', 'sd_src':'no HD', 'sd_src_no_ratelimit':'no HD(full speed)'}

		for k in sample.keys():
			if sample[k]==quality:
				key_link = k
				break
		url = self.FB.origin_link[key_link]

		main_log.log(logging.INFO, ('Originlink: \"%s\"' %url))
		dl_log.log(logging.INFO, ('Originlink: \"%s\"' %url))

		return self.FB.download(url, folder=self.widget.folder_value.get(), absolute_path=path)

	def _sgl_yt_download(self, now_cbx1, now_cbx2, files_ex):	#uncertain
		sound = 0

		if now_cbx1=='MP4a':
			sound = 1

		itag = self.widget.file_quality[now_cbx1][now_cbx2]

		find_url = self.YT.returnUrlByItag(itag, sound=sound)

		if find_url[0]=='false':
			dl_log.log(logging.ERROR, find_url[1])

			messagebox.showinfo(title="From \"returnUrlByItag\" function", message=find_url[1])
			return

		url = find_url[1]

		#loghere
		main_log.log(logging.INFO, ('itag: \"%s\"' %(str(itag))))
		main_log.log(logging.INFO, ('url: \"%s\"' %url))
		dl_log.log(logging.INFO, ('itag: \"%s\"' %(str(itag))))
		dl_log.log(logging.INFO, ('url: \"%s\"' %url))

		if (now_cbx1=='MP4a'):
			ask = asksaveasfile(filetypes=(files_ex[0], files_ex[3]), defaultextension=files_ex[0])
		elif (now_cbx1=='MP4'):
			ask = asksaveasfile(filetypes=(files_ex[1], files_ex[3]), defaultextension=files_ex[1])
		else:
			ask = asksaveasfile(filetypes=(files_ex[2], files_ex[3]), defaultextension=files_ex[2])

		if ask!=None:
			path = ask.name		
			result = self.YT.downloadVideo(url, path)
			return result
		else:
			#loghere
			dl_log.log(logging.CRITICAL, 'save file fail because of asking file is None')
			main_log.log(logging.CRITICAL, 'Download fail because of asking file is None')
			return "ask is None"

	def _downfordown(self):
		#download in separate thread

		files = [
			("Video files (Sound)", "*.mp4"),
			("Video files (NO Sound)", "*.webm"),
			("Audio files (Audio)", "*.mp3"),
			("All files (.*)", "*.*")
		]

		now_cbx1 = self.widget.cbx1.get()
		now_cbx2 = self.widget.cbx2.get()
		option = self.widget._current_option()

		if ((now_cbx1=='None') or (now_cbx2=='None')):
			title = "None is selected"
			message = ("Invalid file format/file quality: %s | %s" %(now_cbx1, now_cbx2))

			dl_log.log(logging.ERROR, message)
			main_log.log(logging.ERROR, message)

			messagebox.showinfo(title=title, message=message)
			
			return (-1,"[<Download status: Failed>")

		if option=='fb10':
			ask = asksaveasfile(filetypes=(files[0], files[3]), defaultextension=files[0])
			if ask!=None:
				main_log.log(logging.WARNING, "Downloading ....................")
				dl_log.log(logging.WARNING, "Downloading ....................")

				path = ask.name
				result = self._sgl_fb_download(now_cbx2, path)
				
				#log here
				main_log.log(logging.WARNING, str("%s|%s -- Download result: %s" %('MP4a', now_cbx2, str(result))))
				dl_log.log(logging.WARNING, str("%s|%s -- Result: %s" %('MP4a', now_cbx2, str(result))))
			else:
				#loghere
				main_log.log(logging.CRITICAL, 'Download fail because of asking file is None')
				dl_log.log(logging.CRITICAL, 'Download fail because of asking file is None')

				return (-1,"[<Download status: Failed>")
		elif option=='yt10':
			main_log.log(logging.WARNING, "Downloading ....................")
			dl_log.log(logging.WARNING, "Downloading ....................")

			result = self._sgl_yt_download(now_cbx1, now_cbx2, files)
			#loghere
			main_log.log(logging.WARNING, str("%s|%s -- Download result: %s" %(now_cbx1, now_cbx2, str(result))))
			dl_log.log(logging.WARNING, str("%s|%s -- Download result: %s" %(now_cbx1, now_cbx2, str(result))))

	def download(self):
		logger.log(logging.INFO, 'Create Download thread')
		dl_log.log(logging.INFO, 'Create Download thread')
		
		Thread(target=self._downfordown).start()
	
	#---------------------------------------------------------------------------

	def selectfolder(self):
		folder = askdirectory()+'/'
		self.widget.folder_value.set(folder)

		#loghere
		main_log.log(logging.INFO, ('Selected folder: %s' %(folder)))

	def show_process(self, message):	#notused
		pass

	def clear_process(self):			#notused
		pass

	def update_status(self):			#notused
		self.widget._update_vs_option(50)
		print(self.widget.current_option)
		self.widget.master.after(1000, self.update_status)


class WidgetGUI(Base):
	'''
		label, entry, button, text		

		label: change text
		entry: set, get
		button: check, enable, disable
		text: clear, insert, writelast change, autoscroll
	'''

	option_flag=''
	cbx1_flag=''

	def _set_cbx_none(self):
		self.cbx2['value'] = ['None']
		self.cbx2.current(0)
		self.original_url_value.set('None')

	def _update_vs_option(self, speed):
		option = self._current_option()

		cbx1_current = self.cbx1.get()
		cbx2_current = self.cbx2.get()

		if option!=self.option_flag:
			self._set_cbx_none()

			self.option_flag=option

		self.embed_frame.after(speed, lambda:self._update_vs_option(speed))

	def _updateEmbdedFrame(self, speed):
		option = self._current_option()
		cbx1_current = self.cbx1.get()
		cbx2_current = self.cbx2.get()

		if option!=self.option_flag:
			self.cbx2.current(0)
			self.option_flag=option
			self.embed_frame.after(speed, lambda:self._updateEmbdedFrame(speed))

		#continue set cbx1 when facebook is choosen here
		# if (option=='fb10') or (option=='fb11'):
		# 	self.cbx1['value'] = ['MP4a', 'None']
		# 	self.cbx1.current(0)
		# 	self.embed_frame.after(speed, lambda:self._updateEmbdedFrame(speed))

		if option=='yt10':
			lst_value = list(self.file_quality[cbx1_current].keys())
			
			self.cbx2['value'] = lst_value

			#set 'None' for cbx2 whenever other file_format is selected
			if cbx1_current!=self.cbx1_flag:
				self.cbx1_flag = cbx1_current
				now_index = lst_value.index('None')
				self.cbx2.current(now_index)

			self.embed_frame.after(speed, lambda:self._updateEmbdedFrame(speed))

	def __init__(self, master):
		#--------variables
		self.url_value	= StringVar()
		self.original_url_value = StringVar()
		self.folder_value = StringVar()

		self.cbx1_value = StringVar()
		self.cbx2_value = StringVar()

		self.file_format = ('MP4', 'MP4a', 'MP3', 'None')
		self.file_quality = {'MP4a':{'None':'None'}, 'MP4':{'None':'None'}, 'MP3':{'None':'None'}, 'None':{'None':'None'}}
		
		#--------
		# master is a Frame
		self.master = master

		self.activity = WidgetActivity(self)

		self.container = {}
		#container is dict of components

		self.initWidget()
		self._update_vs_option(50)
		#?
		lg = ShowLog(self.container['text']['process'])

	def initWidget(self):
		label_background = '#c7ffda'
		bodercolor = '#4aff88'
		boderthickness = 0.5
		button_background_color = bodercolor

		#------------------------
		# Label
		self.main_label = Label(self.master, background=label_background, text="Facebook", font=("Times", 40))

		self.url_label = Label(self.master, text="   URL", background=label_background, font=("Times", 15))
		self.originurl_label = Label(self.master, text="Origin URL", background=label_background, font=("Times", 15))
		self.filename_label = Label(self.master, text="  Filename\n/Folder", background=label_background, font=("Times", 15))

		self.process_label = Label(self.master, text="Process", background=label_background, font=("Times", 20))

		#------------------------
		# Entry
		self.url_entry = Entry(self.master, highlightbackground=bodercolor, highlightcolor=bodercolor, highlightthickness=boderthickness, textvariable=self.url_value)
		self.originurl_entry = Entry(self.master, highlightbackground=bodercolor, highlightcolor=bodercolor, highlightthickness=boderthickness, textvariable=self.original_url_value)
		self.filename_entry = Entry(self.master, highlightbackground=bodercolor, highlightcolor=bodercolor, highlightthickness=boderthickness, textvariable=self.folder_value)

		#------------------------
		# Button
		self.getlink_button = Button(self.master, text="Get link", command=lambda:self.activity.getlink(), font=("Times", 15), background=button_background_color)
		self.select_button = Button(self.master, text=" Select  ", command=self.activity.selectfolder, font=("Times", 15), background=button_background_color)
		self.download_button = Button(self.master, text="Download", font=("Times", 20), background=button_background_color)

		#------------------------
		# Text
		self.process_text = scrolledtext.ScrolledText(
			self.master,
			highlightbackground=bodercolor,
			highlightcolor=bodercolor,
			highlightthickness=boderthickness,
			foreground='#000000',
			height=10
		)

		#------------------------

		self.container = {
			'label':{
				'type':self.main_label,
				'url':self.url_label,
				'original_url':self.originurl_label,
				'filename':self.filename_label,
				'process':self.process_label
			},
			'entry':{
				'url':self.url_entry,
				'original_url':self.originurl_entry,
				'filename':self.filename_entry
			},
			'button':{
				'getlink':self.getlink_button,
				'select':self.select_button,
				'download':self.download_button,
			},
			'text':{
				'process':self.process_text
			}
		}

		#nested frame
		#----------------------------
		embed_color = label_background
		self.embed_frame = Frame(self.master, width=800, height=40, bg=embed_color)
		self.embed_frame.grid(column=1, row=5, sticky=(N, S, E, W))
		embed_sticky = (W, E)

		e_l = Label(self.embed_frame, text=('File Format:'+' '*5), font=('Times', 15), background=embed_color)
		e_l.grid(column=1, row=0, sticky=(E, W))

		self.cbx1 = ttk.Combobox(self.embed_frame, justify=RIGHT, state='readonly', textvariable=self.cbx1_value) # not used
		self.cbx1.grid(column=3, row=0, sticky=(W, E))
		self.cbx1['value'] = self.file_format
		self.cbx1.current(2)

		self._add_emptylabel(self.embed_frame, c=4, r=0, text=(' '*5), sticky=embed_sticky, background=embed_color)

		self.cbx2 = ttk.Combobox(self.embed_frame, width=20, justify=RIGHT, state='readonly', textvariable=self.cbx2_value) # not used
		self.cbx2.grid(column=5, row=0, sticky=(W, E))
		self.cbx2['value'] = (None,)
		self.cbx2.current(0)

		self._add_emptylabel(self.embed_frame, c=6, r=0, text=(' '*5), sticky=embed_sticky, background=embed_color)

		e_b = Button(self.embed_frame, text='Download', command=self.activity.download, font=('Times', 15), background=button_background_color)
		e_b.grid(column=7, row=0)

		self.embed_frame.columnconfigure(0, weight=1)
		self.embed_frame.columnconfigure(8, weight=1)
		#----------------------------

		self.master.grid(column=0, row=0, padx=2, pady=2, sticky=(N, S, E, W))

		self.container['label']['type'].grid(column=1, row=1, pady=20, sticky=(E, W))
		self.container['label']['url'].grid(column=0, row=2, padx=5, pady=15, sticky=(S, W))
		self.container['label']['original_url'].grid(column=0, row=3, padx=15, pady=5, sticky=(S, W))
		self.container['label']['filename'].grid(column=0, row=4, padx=5, pady=15, sticky=(S, W))
		self.container['label']['process'].grid(column=0, row=7)

		self.container['entry']['url'].grid(column=1, row=2, padx=5, pady=15, sticky=(E, W))
		self.container['entry']['original_url'].grid(column=1, row=3, padx=5, pady=15, sticky=(E, W))
		self.container['entry']['filename'].grid(column=1, row=4, padx=5, pady=15, sticky=(E, W))

		self.container['button']['getlink'].grid(column=2, row=3, padx=5, pady=5)
		self.container['button']['select'].grid(column=2, row=4, padx=5, pady=5)

		#
		self._add_emptylabel(self.master, c=2, r=5, background=label_background)
		self._add_emptylabel(self.master, c=2, r=6, background=label_background)
		#----------------------------

		self.container['text']['process'].grid(column=1, row=7, sticky=(S, N, W, E))
		#----------------------------
		
		self._add_emptylabel(self.master, c=1, r=8, background=label_background)
		self._add_emptylabel(self.master, c=2, r=8, background=label_background)

		#
		self.master.columnconfigure(1, weight=1)
		self.master.rowconfigure(7, weight=1)
		#self.master.rowconfigure(6, weight=1)
		#

	def _add_emptylabel(self, master, c=0, r=0, text='', background=None, sticky=()):
		empty_label = Label(master, background=background, text=text)
		empty_label.grid(column=c, row=r, sticky=sticky)

	def into_process(self, message):
		self.container['text']['process'].insert(END, (str(datetime.now())[:-7]+':\t'+message+'\n'))
		self.container['text']['process'].yview(END)

	def updateWidget(self):
		pass
		

class FileMenu(Menu):
	def logdata(self):
		#open notepad.exe
		a = Popen(['notepad.exe', os.path.join(_CWD, 'AppData/log.log')])
		logger.log(logging.WARNING, 'Open log file')

	def exit(self):
		logger.log(logging.CRITICAL, 'Quit program\n*End logging*')
		sys.exit()
		

class OptionMenu(Menu):
	def setWidget(self, widget):
		self.widget = widget

	def login(self, target=None, container={}):
		title = "Login"
		message = "--- Login feature is unavailable right now ---"
		
		#loghere
		logger.log(logging.ERROR, 'Login function')

		messagebox.showwarning(title=title, message=message)

		return

	def download_playlist(self):
		#loghere
		logger.log(logging.ERROR, 'Download playlist function')
		main_log.log(logging.ERROR, 'Download playlist function is not available right now!\nUsing \"Single file\"')

		return

	def download_list(self):
		#loghere
		logger.log(logging.ERROR, 'Download playlist function')
		main_log.log(logging.ERROR, 'Download list function is not available right now!\nUsing \"Single file\"')

		return


class SettingMenu(Menu):
	def setWidget(self, widget):
		self.widget = widget

	def set_defaultfolder(self):
		folder = askdirectory()+'/'
		self.widget.folder_value.set(folder)
		
		#loghere
		logger.log(logging.INFO, ("Set folder: %s" %folder))

	def user_define(self):
		pass


class HelpMenu(Menu):
	def show_about(self):
		#show dialog
		title = "About tool"
		message = "https://github.com/n0crush/"
		messagebox.showinfo(title=title, message=message)

#
class FbMenu(OptionMenu):
	pass
class YtMenu(OptionMenu):
	pass
class UserDefine:
	#intended to be used by config file
	pass
#


class MenuGUI(Base): # OK
	def __init__(self, master, widget):

		self.playlist_flag = 0

		# master is a Menu
		# widget is a Widget

		self.master = master
		self.widget = widget

		self.container = {}

		self.initMenu()
		
	def initMenu(self):
		fb_checked = StringVar()
		yt_checked = StringVar()
		yt_playlist = StringVar()

		fb_checked.set("Single file")
		#------------------

		def set_state(state):
			if state=='enable':
				self.widget.container['label']['original_url'].config(state='normal')
				self.widget.container['entry']['original_url'].config(state='normal')
			if state=='disable':
				self.widget.container['label']['original_url'].config(state='disable')
				self.widget.container['entry']['original_url'].config(state='disable')

		def _curent_option(op: str, invoked=False)->str:
			if op=='fb':
				self.current_option['fb']['single']=1
				self.current_option['yt']['single']=0
				self.current_option['yt']['playlist']=0

				set_state('enable')

				yt_checked.set(None)
				yt_playlist.set(None)
				self.playlist_flag = 0

				fb_checked.set('Single file')

				#loghere
				logger.log(logging.INFO, "Switch to Facebook")

				self.widget.container['label']['type'].config(text="Facebook")

			if op=='yt':
				fb_checked.set(None)
				self.current_option['fb']['single']=0

				#loghere
				logger.log(logging.INFO, "Switch to Youtube")

				self.widget.container['label']['type'].config(text="Youtube")
				self.current_option['yt']['single']=1

				if self.playlist_flag==1:
					yt_playlist.set(None)
				
				if invoked==True:
					self.current_option['yt']['playlist']=1
				else:
					self.current_option['yt']['playlist']=0
					set_state('enable')

				yt_checked.set('Single file')

			return op

		#menu gui
		m_file = FileMenu(self.master, tearoff=0)
		m_file.add_command(label="Log data", command=m_file.logdata)
		m_file.add_command(label="Exit", command=m_file.exit)


		m_option = Menu(self.master, tearoff=0)
		#-----
		fb_menu = FbMenu(m_option, tearoff=0)
		fb_menu.setWidget(self.widget)

		#facebook-----------------------------------------------
		fb_menu.add_radiobutton(label="Single file", command=lambda:_curent_option('fb'), variable=fb_checked)#		fb_menu.add_separator()
		fb_menu.add_separator()
		fb_menu.add_command(label='Login', command=fb_menu.login)
		fb_menu.add_separator()
		fb_menu.add_command(label='Download List', command=(fb_menu.download_list))
		#facebook-----------------------------------------------

		#youtube-----------------------------------------------
		yt_menu = YtMenu(m_option, tearoff=0)
		yt_menu.setWidget(self.widget)		#necessery

		def yt_extension():
			if self.playlist_flag==1:
				_curent_option('yt', invoked=False)
				
				yt_playlist.set(None)

				set_state('enable')
				
				self.current_option['yt']['playlist']=0			

				self.playlist_flag=0
			else:
				_curent_option('yt', invoked=True)

				yt_menu.download_playlist()
				yt_playlist.set('Download Playlist')

				set_state('disable')

				self.current_option['yt']['playlist']=1			

				self.playlist_flag = 1

			#loghere

			#fordebug
			#logger.log(logging.INFO, str(self.current_option))

		yt_menu.add_radiobutton(label="Single file", command=lambda:_curent_option('yt'), variable=yt_checked)#

		yt_menu.add_separator()		
		yt_menu.add_command(label='Login', command=yt_menu.login)
		yt_menu.add_separator()
		yt_menu.add_command(label='Download List', command=yt_menu.download_list)
		yt_menu.add_radiobutton(label='Download Playlist', command=yt_extension, variable=yt_playlist)
		#youtube-----------------------------------------------

		m_option.add_cascade(label='Facebook', menu=fb_menu)
		m_option.add_cascade(label='Youtube', menu=yt_menu)

		#---------------------------------------------------
		m_setting = SettingMenu(self.master, tearoff=0)
		m_setting.setWidget(self.widget)
		m_setting.add_command(label='Set folder', command=m_setting.set_defaultfolder)

		usr_dfn = Menu(m_setting, tearoff=0)
		usr_dfn.add_command()
		#---------------------------------------------------

		#---------------------------------------------------
		m_help = HelpMenu(self.master, tearoff=0)	#
		m_help.add_command(label='About', command=m_help.show_about)
		#---------------------------------------------------

		container = {'Files':m_file, 'Options':m_option, 'Setting':m_setting, 'Help':m_help }		

		for key, value in container.items():
			value.cursor = True
			self.master.add_cascade(label=key, menu=value)

		self.container = container

	def add_menu(self, name, menu):		#notused
		if isinstance(menu, Menu):
			self.container[name] = menu
			return menu
		else:
			return ( '%s is not a Menu' %(str(menu)) )

	def delete_menu(self, name):		#notused
		if name in self.container.keys():
			del (self.container[name])
		else:
			return '%s is not exist.' %(name)

	def updateChange(self):				#notused
		self.master.after(1000, self.updateChange)


class GUI:
	def __init__(self, parent):
		#parent is an instance of tkinter

		self.parent = parent

		self.mainframe = Frame(self.parent, background='#c7ffda', highlightbackground='#4aff88', highlightthickness=0)	#sync here

		self.widget = WidgetGUI(self.mainframe)

		#self.widget.updateWidget()
		#
		self.parent.columnconfigure(0, weight=1)
		self.parent.rowconfigure(0, weight=1)
		#
		self.mainmenu = MenuGUI(Menu(self.mainframe), self.widget)

		self.parent.config(menu=self.mainmenu.master)

	def change_menu_when_update(self):
		def ex():
			sys.exit()
		self.mainmenu.container['Files'].add_command(label="Exit", command=ex)

	def updateGUI(self):		#notused
		self.widget.updateWidget()


class IO:			#notused
	def __init__(self, master):
		self.master = master
	def get_in(self):
		pass
	def set_out(self):
		pass
	def process(self):
		pass


class QueueHandler(logging.Handler):
	def __init__(self, log_queue):
		super().__init__()
		self.log_queue = log_queue

	def emit(self, record):
		self.log_queue.put(record)


class ShowLog:
	def __init__(self, text_widget):
		self.text_widget = text_widget
		self.text_widget.tag_config('INFO', foreground='#000000')
		self.text_widget.tag_config('ERROR', foreground='#ff0000')
		self.text_widget.tag_config('WARNING', foreground='#ff7b00')
		self.text_widget.tag_config('CRITICAL', foreground='#018c27')	#f*ck color picker

		#--------------

		self.log_queue = Queue()
		self.queue_handler = QueueHandler(self.log_queue)
		self.queue_handler.setFormatter(logging.Formatter(('%(asctime)s -- : %(message)s')))

		main_log.addHandler(self.queue_handler)

		self.text_widget.frame.after(100, self.poll_to_queue)

	def display(self, record):
		message = self.queue_handler.format(record)

		self.text_widget.configure(state="normal")
		self.text_widget.insert(END, message + '\n', record.levelname)
		#self.text_widget.configure(state="disable")  		#optional allow to modify scrolledtext
		self.text_widget.yview(END)

	def poll_to_queue(self):
		while 1:
			try:
				record = self.log_queue.get(block=False)
			except Empty:
				break
			else:
				self.display(record)
		self.text_widget.frame.after(100, self.poll_to_queue)


logging.basicConfig(
	level=logging.DEBUG,
	format='%(asctime)s -- <%(levelname)-8s> -- <%(name)-10s> <%(filename)-s:%(funcName)s:%(lineno)s>: %(message)s',
	filename='AppData/log.log',
	filemode='a'
)

main_log = logging.getLogger("MainThread")		#ScrolledText log | log to: file, scrolledtext

gl_log = logging.getLogger("GetLink      ")		#sub log 		| log to: file
dl_log = logging.getLogger("Download  ")		#sub log 		| log to: file

logger = logging.getLogger("OKMan      ")		#root log 		| log to: file


def main():
	_excute_time = datetime.now()

	logging.info(('\n%s\n' %('-'*30))+"*Start logging*")

	root = Tk()
	root.title("Video Downloader | @n0crush")

	root.configure(bg='#4aff88')
	x = GUI(root)

	root.mainloop()


if __name__ == '__main__':
	main()

