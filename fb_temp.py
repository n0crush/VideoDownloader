#!python -3


"""
#time_modify: 03:13 AM 12/13/2020
#note:
	- incomplete:
		- signin to get private videos
		- convert to mp3
		- clean code

"""


__auth__ = "@n0crush"
__info__ = ["github.com/n0crush", "twitter.com/n0crush"]



import re, os
import requests
from datetime import datetime


class Facebook:
	def __init__(self):
		self.getLink_status = 'Error'
		self.download_status = 'Failed'
		self.video_size = None
		self.origin_link = {}
		self.extra_code = {"getLink":0, "download":0}

	def __repr__(self):
		return "Download Public Videos on Facebook - @n0crush"

	#00:45 AM 11/7/2020	
	def _reinit(self):
		self.__init__()
		return True

	def getLink(self, url):		#DONE
		#set getLink_status="Success"	|None| success
		#set origin_link				|None| success
		#return message					|str | fail

		prefix = "https://www.facebook.com/"
		#add fb.com/

		if not url.startswith(prefix):
			return ("[!] Invalid URL. Check again! -- Hint: \"%s...\"" %(prefix))

		try:
			#customize timeout for request
			res = requests.get(url, timeout=3)
		except Exception as _ex:
			return str(_ex)

		if res.status_code != 200:
			return "[!] Invalid URL. Check again!"
		if not "Set-Cookie" in res.headers.keys():
			return "You must signin to get the original link of this video!"	#future
		else:
			self.getLink_status = "Success"

		#21:53 PM 11/6/2020--------------
		reg_for_all = re.compile(r'(hd_src|sd_src|sd_src_no_ratelimit):"(.+?)"')
		
		self.origin_link = dict(reg_for_all.findall(res.text))

		if self.origin_link=={}:
			return("no such link found")
		else:
			return("%d link found" %(len(self.origin_link)))
		#--------------------------------

	def _getSize(self, raw_size):		#raw_size is str type
		result = ''
		x = len(raw_size)

		if x>=10:
				result = str(round(int(raw_size)/(1024**3), 1))+" MB"
		elif x>=7:
				result = str(round(int(raw_size)/(1024**2), 1))+" MB"
		elif x>=4:
				result = str(round(int(raw_size)/(1024)))+" Kb"
		elif x<=3:
				result = str(int(raw_size)/(1024**3))+" bytes"

		return result
		#self.video_size = result
		
	def _handleFileName(self, folder, video_name):
		if not (os.path.exists(folder)):
			folder = os.path.join(os.path.expanduser('~'), "Downloads")	#Windows OS
			#print("[!] Using default folder: ", folder)		-- for display

		incorrect_video_name = False

		for i in "\\/:*?\"<>|":
			if i in video_name:
				incorrect_video_name = True
				break

		if ((video_name=="") or (incorrect_video_name==True)):
			#print("[!] Video name invalid. Used 'facebook_video_' as name.")	-- for display
			duma = str(datetime.now())[:19].replace(':', "_")
			duma = duma.replace(" ", "_")
			duma = duma.replace('-', "_")

			video_name = 'facebook_video_'+duma

		if not video_name.endswith('.mp4'):		
			video_name += ".mp4"

		save_path = os.path.join(folder,video_name)#.replace('/','\\')

		return save_path

	def download(self, url, folder="", video_name="", absolute_path=""):
		#return message		|None| fail/success

		if self.origin_link=={}:
			return (-1,"[<Download status: %s>, <Path: %s>]" %(self.download_status, "None"),)

		if os.path.exists(absolute_path):
			path = absolute_path
		else:
			path = self._handleFileName(folder, video_name)

		res = requests.get(url, allow_redirects=False)
		self.download_status="Success"
		self.video_size = self._getSize(res.headers['Content-Length'])

		with open(path, 'wb') as data:
			data.write(res.content)
		return (0,"[<Download status: %s>, <Path: %s>, <Size: %s>]" %(self.download_status, path, self.video_size))


"""
	some random url:

	normal: https://www.facebook.com/dienvienXuanNghi/videos/1540467796135334/
	normal: https://www.facebook.com/5min.crafts/videos/2659654504350429/
	normal: https://www.facebook.com/lethamduong.edu.vn/videos/289976458872123
	normal: https://www.facebook.com/ctrlkill/videos/213960092713660
	private: https://www.facebook.com/le.nguen.794/videos/206149947224826/
"""

