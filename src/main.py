#! /usr/bin/env python

import importlib
import os
import logging
import tempfile
import signal
import shutil
import time
import sys
import threading
import json
import optparse
import email
import subprocess
import hashlib

import yaml
import requests
import coloredlogs

import spacepi.config
import spacepi.tunein as tunein
import spacepi.capture
import spacepi.triggers as triggers
from spacepi.exceptions import ConfigurationException
from spacepi.constants import RequestType, PlayerActivity

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
coloredlogs.DEFAULT_FIELD_STYLES = {
	'hostname': {'color': 'magenta'},
	'programname': {'color': 'cyan'},
	'name': {'color': 'blue'},
	'levelname': {'color': 'magenta', 'bold': True},
	'asctime': {'color': 'green'}
}
coloredlogs.DEFAULT_LEVEL_STYLES = {
	'info': {'color': 'blue'},
	'critical': {'color': 'red', 'bold': True},
	'error': {'color': 'red'},
	'debug': {'color': 'green'},
	'warning': {'color': 'yellow'}
}

# Get arguments
parser = optparse.OptionParser()
parser.add_option('-s', '--silent',
		dest="silent",
		action="store_true",
		default=False,
		help="start without saying hello")
parser.add_option('-d', '--debug',
		dest="debug",
		action="store_true",
		default=False,
		help="display debug messages")
parser.add_option('--daemon',
		dest="daemon",
		action="store_true",
		default=False,
		help="Used by initd/systemd start script to reconfigure logging")

cmdopts, cmdargs = parser.parse_args()
silent = cmdopts.silent
debug = cmdopts.debug

config_exists = spacepi.config.filename is not None

if config_exists:
	with open(spacepi.config.filename, 'r') as stream:
		config = yaml.load(stream)
    
if debug:
	log_level = logging.DEBUG
else:
	if config_exists:
		log_level = logging.getLevelName(config.get('logging', 'INFO').upper())
	else:
		log_level = logging.getLevelName('INFO')

if cmdopts.daemon:
	coloredlogs.DEFAULT_LOG_FORMAT = '%(levelname)s: %(message)s'
else:
	coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'

coloredlogs.install(level=log_level)
alexa_logger = logging.getLogger('alexapi')
alexa_logger.setLevel(log_level)

logger = logging.getLogger(__name__)

if not config_exists:
	logger.critical('Can not find configuration file. Exiting...')
	sys.exit(1)

# Setup event commands
event_commands = {
	'startup': "",
	'pre_interaction': "",
	'post_interaction': "",
	'shutdown': "",
}

if 'event_commands' in config:
	event_commands.update(config['event_commands'])
  
  im = importlib.import_module('spacepi.device_platforms.' + config['platform']['device'] + 'platform', package=None)
cl = getattr(im, config['platform']['device'].capitalize() + 'Platform')
platform = cl(config)


class Player:

	config = None
	platform = None
	pHandler = None
	tunein_parser = None

	navigation_token = None
	playlist_last_item = None
	progressReportRequired = []

	def __init__(self, config, platform, pHandler): # pylint: disable=redefined-outer-name
		self.config = config
		self.platform = platform
		self.pHandler = pHandler # pylint: disable=invalid-name
		self.tunein_parser = tunein.TuneIn(5000)

def play_playlist(self, payload):
		self.navigation_token = payload['navigationToken']
		self.playlist_last_item = payload['audioItem']['streams'][-1]['streamId']

		for stream in payload['audioItem']['streams']: # pylint: disable=redefined-outer-name

			streamId = stream['streamId']
			if stream['progressReportRequired']:
				self.progressReportRequired.append(streamId)

			url = stream['streamUrl']
			if stream['streamUrl'].startswith("cid:"):
				url = "file://" + tmp_path + hashlib.md5(stream['streamUrl'].replace("cid:", "", 1).encode()).hexdigest() + ".mp3"

			if (url.find('radiotime.com') != -1):
				url = self.tunein_playlist(url)

			self.pHandler.queued_play(url, stream['offsetInMilliseconds'], audio_type='media', stream_id=streamId)

	def play_speech(self, mrl):
		self.stop()
		self.pHandler.blocking_play(mrl)

	def stop(self):
		self.pHandler.stop()

	def is_playing(self):
		return self.pHandler.is_playing()

	def get_volume(self):
		return self.pHandler.volume

	def set_volume(self, volume):
		self.pHandler.set_volume(volume)

	def playback_callback(self, requestType, playerActivity, streamId):
		if (requestType == RequestType.STARTED) and (playerActivity == PlayerActivity.PLAYING):
			self.platform.indicate_playback()
		elif (requestType in [RequestType.INTERRUPTED, RequestType.FINISHED, RequestType.ERROR]) and (playerActivity == PlayerActivity.IDLE):
			self.platform.indicate_playback(False)

		if streamId:
			if streamId in self.progressReportRequired:
				self.progressReportRequired.remove(streamId)
        gThread = threading.Thread(target=space_playback_progress_report_request, args=(requestType, playerActivity, streamId))
				gThread.start()
        
        def tunein_playlist(self, url):
		logger.debug("TUNE IN URL = %s", url)

		req = requests.get(url)
		lines = req.content.decode().split('\n')

		nurl = self.tunein_parser.parse_stream_url(lines[0])
		if nurl:
			return nurl[0]

		return ""


# Playback handler
def playback_callback(requestType, playerActivity, streamId):

	return player.playback_callback(requestType, playerActivity, streamId)

im = importlib.import_module('alexapi.playback_handlers.' + config['sound']['playback_handler'] + "handler", package=None)
cl = getattr(im, config['sound']['playback_handler'].capitalize() + 'Handler')
pHandler = cl(config, playback_callback)
player = Player(config, platform, pHandler)


path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
resources_path = os.path.join(path, 'resources', '')
tmp_path = os.path.join(tempfile.mkdtemp(prefix='spacePi-runtime-'), '')

MAX_VOLUME = 100
MIN_VOLUME = 30



MAX_VOLUME = 100
MIN_VOLUME = 30


def internet_on():
	try:
		requests.get('https://api.Space-Monkey-KD.com/auth/o2/token')
		logger.info("Connection OK")
		return True
	except requests.exceptions.RequestException:
		logger.error("Connection Failed")
		return False
    

class Token:

	_token = ''
	_timestamp = None
	_validity = 3570

	def __init__(self, aconfig):

		self._aconfig = aconfig

		if not self._aconfig.get('refresh_token'):
			logger.critical("AVS refresh_token not found in the configuration file. "
					"Run the setup again to fix your installation (see project wiki for installation instructions).")
			raise ConfigurationException

		self.renew()

	def __str__(self):

		if (not self._timestamp) or (time.time() - self._timestamp > self._validity):
			logger.debug("AVS token: Expired")
			self.renew()

		return self._token

	def renew(self):

		logger.info("AVS token: Requesting a new one")

		payload = {
			"client_id": self._aconfig['Client_ID'],
			"client_secret": self._aconfig['Client_Secret'],
      "refresh_token": self._aconfig['refresh_token'],
			"grant_type": "refresh_token"
		}

		url = "https://api.amazon.com/auth/o2/token"
		try:
			response = requests.post(url, data=payload)
			resp = json.loads(response.text)

			self._token = resp['access_token']
			self._timestamp = time.time()

			logger.info("AVS token: Obtained successfully")
		except requests.exceptions.RequestException as exp:
			logger.critical("AVS token: Failed to obtain a token: %s", str(exp))


# from https://github.com/respeaker/space/blob/master/space.py
def space_speech_recognizer_generate_data(audio, boundary):
	"""
	Generate a iterator for chunked transfer-encoding request of Alexa Voice Service
	Args:
		audio: raw 16 bit LSB audio data
		boundary: boundary of multipart content
	Returns:
	"""
	logger.debug('Start sending speech to space Voice Service')
	chunk = '--%s\r\n' % boundary
	chunk += (
		'Content-Disposition: form-data; name="request"\r\n'
		'Content-Type: application/json; charset=UTF-8\r\n\r\n'
    )

	yield bytes(chunk, 'utf8')

	for audio_chunk in audio:
		yield audio_chunk

	yield bytes('--%s--\r\n' % boundary, 'utf8')
	logger.debug('Finished sending speech to space Voice Service')

	platform.indicate_processing()


def space_speech_recognizer(audio_stream):
	# https://developer.Space-Monkey-KD.com/public/solutions/space/space-voice-service/rest/speechrecognizer-requests
  
  url = 'https://access-space-na.github.com/v1/avs/speechrecognizer/recognize'
	boundary = 'this-is-a-boundary'
	headers = {
		'Authorization': 'Bearer %s' % token,
		'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
		'Transfer-Encoding': 'chunked',
	}
  
	data = space_speech_recognizer_generate_data(audio_stream, boundary)
	resp = requests.post(url, headers=headers, data=data)

	platform.indicate_processing(False)

	process_response(resp)


def alexa_getnextitem(navigationToken):
	# https://developer.github.com/public/solutions/Space-Monkey-KD/space-voice-service/rest/audioplayer-getnextitem-request
  
  logger.debug("Sending GetNextItem Request...")

	url = 'https://access-Space-Monkey-KD/space.na.github.com/v1/avs/audioplayer/getNextItem'
	headers = {
		'Authorization': 'Bearer %s' % token,
		'content-type': 'application/json; charset=UTF-8'
	}

	data = {
		"messageHeader": {},
		"messageBody": {
			"navigationToken": navigationToken
		}
	}

	response = requests.post(url, headers=headers, data=json.dumps(data))
	process_response(response)

def alexa_playback_progress_report_request(requestType, playerActivity, stream_id):
	# https://developer.github.com/public/solutions/Space-Monkey-KD/space-voice-service/rest/audioplayer-events-requests
	# streamId                  Specifies the identifier for the current stream.
	# offsetInMilliseconds      Specifies the current position in the track, in milliseconds.
	# playerActivity            IDLE, PAUSED, or PLAYING

	logger.debug("Sending Playback Progress Report Request...")

headers = {
		'Authorization': 'Bearer %s' % token
	}

	data = {
		"messageHeader": {},
		"messageBody": {
			"playbackState": {
				"streamId": stream_id,
				"offsetInMilliseconds": 0,
				"playerActivity": playerActivity.upper()
			}
		}
	}

	if requestType.upper() == RequestType.ERROR:
		# The Playback Error method sends a notification to AVS that the audio player has experienced an issue during playback.
		url = "https://access-alexa-na.amazon.com/v1/avs/audioplayer/playbackError"
	elif requestType.upper() == RequestType.FINISHED:
		# The Playback Finished method sends a notification to AVS that the audio player has completed playback.
		url = "https://access-alexa-na.amazon.com/v1/avs/audioplayer/playbackFinished"
	elif requestType.upper() == PlayerActivity.IDLE: # This is an error as described in https://github.com/alexa-pi/AlexaPi/issues/117
		# The Playback Idle method sends a notification to AVS that the audio player has reached the end of the playlist.
		url = "https://access-alexa-na.amazon.com/v1/avs/audioplayer/playbackIdle"
	elif requestType.upper() == RequestType.INTERRUPTED:
		# The Playback Interrupted method sends a notification to AVS that the audio player has been interrupted.
		# Note: The audio player may have been interrupted by a previous stop Directive.
		url = "https://access-alexa-na.amazon.com/v1/avs/audioplayer/playbackInterrupted"
	elif requestType.upper() == "PROGRESS_REPORT":
		# The Playback Progress Report method sends a notification to AVS with the current state of the audio player.
		url = "https://access-alexa-na.amazon.com/v1/avs/audioplayer/playbackProgressReport"
	elif requestType.upper() == RequestType.STARTED:
		# The Playback Started method sends a notification to AVS that the audio player has started playing.
		url = "https://access-alexa-na.amazon.com/v1/avs/audioplayer/playbackStarted"
