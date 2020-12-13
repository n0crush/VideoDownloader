#!python -3


"""
#time_modify: 03:13 AM 12/13/2020
#note: 
	- incomplete:
		- decode signature(cipher)
		- signin to get private/age restricted/.etc
		- clean code


"""


__auth__ = "@n0crush"
__info__ = ["github.com/n0crush", "twitter.com/n0crush"]



import re
import sys
import json
import requests

from urllib.parse import unquote


class YoutubeBase:

	internet_required = True

	def setUrl(self, url):
		self.url = url

	def __repr__(self):
		return "Class || Youtube Base"

	# check and return correct video_id
	def checkVideoId(self, url):
		#('false', callback)	| tuple| fail	
		#('true', video_id) 	| str  | success

		reg = re.compile(r'((https://www\.youtube\.com/watch\?v=)|(https://youtu\.be/))([a-zA-Z0-9_-]{11}).*')

		check_match = reg.search(url)

		if check_match==None:
			return ('false', 'callback: _method_ object.checkVideoId()')

		return ('true', check_match.group(4))
	

	#requests and return respone text decoded
	def getRequest(self):
		#('false', callback)			| tuple| fail	
		#('false', responseTextDecoded)		| str  | success

		check_video_id = self.checkVideoId(self.url)
		if check_video_id[0]=='false':
#*
			return ('false','[!] Invalid youtube URL.', check_video_id[1])

		video_id = check_video_id[1]
		
		#customize User-Agent
		headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}

		url = "https://www.youtube.com/get_video_info?video_id="+video_id+"&el=embedded&ps=default&eurl=&gl=US&hl=en"	
		# or
		# url = url = "https://www.youtube.com/get_video_info?video_id="+video_id

		try:
			#customize timeout
			res = requests.get(url, headers=headers, timeout=3)
		except Exception as _ex:
			return ('false', str(_ex), 'callback: _method_ object.getRequest()')
		
		if res.status_code != 200:
#*
			return ('false', '[!] Request to URL failed!', str(res.status_code))

		responseTextDecoded = unquote(res.text).split("&")

		return ('true', responseTextDecoded)		#responseTextDecoded is list type	
		
	
	#extract all video information and return as dictionary
	def getInfo(self, responseTextDecoded):
		# At ----20:43 PM 12/7/2020---- always True
		
		#('false', callback)			| tuple| fail	
		#data_as_dict 				| dict | success

		data_input = ''

		for item in responseTextDecoded:
			if item.startswith('player_response='):
				data_input = item
				break
		def getPlayerResponse(data):
			reg = re.compile(r'(player_response=)({.*)')
			if reg.search(data)!=None:
				x = reg.search(data).group(2)
				return x

		response_data = getPlayerResponse(data_input)
		response_data = response_data.replace('\u0026', '&')
		data_as_dict = json.loads(response_data)

		return data_as_dict


class Youtube(YoutubeBase):
	def __init__(self):
		self.filtered_info = {}
		
	def __repr__(self):
		return "Class || Youtube"

	def clear_text(self, *args, t=False, l=False, d=False):
		# t, l, d 	= 	text, list, dictionary
		if len(args)!=1:
			return False
		obj = args[0]

		text = "Empty"

		if (t==True) and (type(obj) is str):
			text = obj.replace('+', ' ')
		elif (l==True) and (type(obj) is list):
			for i in range(len(obj)):
				obj[i] = obj[i].replace('+', ' ')
			text = ''.join(obj)
		elif d==True:		# not use
			pass

		return text


	#Info will be processed: [playabilityStatus, streamingData[formats, adaptiveFormats], videoDetails]
	def filterInfo(self, data_as_dict):						#DONE
		#('false', callback)			| tuple| fail	
		#set self.filtered_info 		| dict | success
		

		filtered_info = {
		'playabilityStatus':{},
		'streamingData':{},
		'videoDetails':{}
		}

		var_check = data_as_dict['playabilityStatus']

		available_status = ["ERROR", "LOGIN_REQUIRED", "UNPLAYABLE", "OK"]			# add more here

		status = var_check['status']

		if (status==available_status[3]):
			for info_block in filtered_info:
				filtered_info[info_block] = data_as_dict[info_block]

			mess = ('true', 'getInfo success | self.filtered_info is set')				
		else:
			error_response = var_check['errorScreen']['playerErrorMessageRenderer']

			reason = self.clear_text(error_response['reason']['simpleText'], t=True)
			filtered_info['playabilityStatus'] = {
				'status':status,
				'reason':reason
			}
			
			mess = ('false', '<status: %s> | <reason: %s>' %(status, reason))

		self.filtered_info = filtered_info

		return mess


#from here, only get videoDetail if streamingData is not empty
	def getListQualityLabel(self):
		#('false', callback)							| str  | fail
		#('true', [itag_formats:list(tuple), itag_adaptiveFormats:list(tuple)])	| list | success

		#sample of label, currently
		qualityName = [
			(3840, 2160, "2160p | 4k"),
			(2560, 1440, "1440p | 2k"),
			(1920, 1080, "1080p | HD"),
			(1280, 720, "720p | HD"),
			(854, 480, "480p"),
			(640, 360, "360p"),
			(426, 240, "240p"),
			(256, 144, "144p")]

		itag_formats = {'MP4a':{}, 'MP4':{}, 'MP3':{}}

		for d in self.filtered_info['streamingData']['formats']:			#with itag have mp4a
			if 'qualityLabel' in d.keys():
				itag_formats['MP4a'][d['qualityLabel']] = d['itag']		#append each tuple

		for d in self.filtered_info['streamingData']['adaptiveFormats']:
			if 'qualityLabel' in d.keys():	#mp4 only
				itag_formats['MP4'][d['qualityLabel']] = d['itag']
#				itag_adaptiveFormats.setdefault((d['itag'], d['qualityLabel'],))	#append each tuple
			if 'audioQuality' in d.keys():	#audio only
				itag_formats['MP3'][d['audioQuality']] = d['itag']
		'''
			itag_formats sample:
			[
				{'360p': 18, '720p': 22},
				{'1080p': 248, '1080p60': 399},
				{'AUDIO_QUALITY_MEDIUM':28}
			]
		'''
		return itag_formats

	def _getBestQualityLabel(self, tup_list):
		#('false', callback)			| tuple | fail
		#('true', the_best_itag:int)		| tuple	| success

		#tup_list: [('360p', 18), ('720p', 22)]
		#pattern: [(18, '360p'), (22, '720p')]

		the_best_itag = 0

		for t in tup_list:
			label = t[0]
			as_number = int(label[:label.index('p')])
			if as_number>=the_best_itag:
				the_best_itag = t[1]

		return the_best_itag

	def returnUrlByItag(self,itag, sound=1):
		#('true', url:str) 				| tuple	| success, given by itag
		#('false', 'cipher' ,'unknow')			| tuple	| ciphered
		#('false', callback)				| tuple	| fail

		def f_find(ld):	#ld is a list dictionarys
			temp = ('false', 'not found', 'unknown')		
			for d in ld:
				lst_key = d.keys()
				flag = 1
				for k in lst_key:
					#ciphered --> break task
					if ('cipher' in lst_key) or ('signatureCipher' in lst_key):
						flag = 0
						temp = ('false', 'cipher', 'unknown')
						break
				if flag==0:
					break
				if d['itag']==itag:
					return ('true', d['url'])
			return temp

		#mp4+audio	: 'streamingData'>'formats'
		#mp4 only, mp3	: 'streamingData'>'adaptiveFormats'
		if sound:
			f_formats = f_find(self.filtered_info['streamingData']['formats'])
		else:
			f_formats = f_find(self.filtered_info['streamingData']['adaptiveFormats'])

		if f_formats[0]=='true':
				return ('true', f_formats[1])			
		elif f_formats[1]=='cipher':
			#url has been ciplered by browser signature
			return ('false', 'Url has been ciphered')
		else:
			return ('false', 'Url not found!')

	def downloadVideo(self, url, path):
		try:
			#specify timeout argument here
			res = requests.get(url, allow_redirects=False)
		except Exception as _ex:
			return str(_ex)

		#problem occur when used open method( 0kb written)
		# with open(path, 'wb') as temp:
		# 	temp.write(res.content)

		_open = open(path, 'wb')

		_open.write(res.content)

		_open.close()

		return "Download successfully!"

"""
	#--------
	sample url		

	#y1 = YoutubeDownload("https://www.youtube.com/watch?v=4paY_pxFvcw")	#normal
	#y1 = YoutubeDownload("https://www.youtube.com/watch?v=-IgirY6Kmjw")	#normal
	#y1 = YoutubeDownload("https://youtu.be/oppFGatt6cA")			#unplayable
	#y1 = YoutubeDownload("https://youtu.be/OulN7vTDq1I")			#cipher
	#y1 = YoutubeDownload("https://www.youtube.com/watch?v=_mUP9wDRZqY")	#error
	#y1 = YoutubeDownload("https://www.youtube.com/watch?v=viexJiVIf6c")	#private
	#y1 = YoutubeDownload("https://www.youtube.com/watch?v=LXb3EKWsInQ")	#4k
	#y1 = YoutubeDownload("https://www.youtube.com/watch?v=KWvvRaoWkoc")	#2k
	#url = "https://www.youtube.com/watch?v=gFygl4fP3MY&t=71s"		#unplayable
"""



