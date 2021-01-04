#!/usr/bin/python3
# -*-coding:Utf-8 -*

from stravalib import Client
from stravalib import model, exc, attributes, unithelper as uh
from stravaweblib import WebClient, DataFormat

from datetime import datetime, timedelta
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


__author__ = "Arnaud TORA"
__copyright__ = "Copyright 2020"
__credits__ = "Arnaud TORA"
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Arnaud TORA"
__status__ = "Dev"


auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"


def get_creds(creds_file):
	"""
	Lecture et recuperation des identifiants de connexions
		- ID
		- SecretClient
		- Token
		- Code
		- RefreshCode
		- Email
		- Password

	:param creds_file: Le fichier de credentials
	:type creds_file: str

	:return: Un dictionnaire des credentials
	:rtype: dict
	"""
	creds = {}

	with open(creds_file, "r") as fichier:
		contenu = fichier.readlines()
		for ligne in contenu:
			ligne = ligne.replace(" ", "")
			ligne = ligne.replace("\n", "")
			ligne = ligne.replace("\r", "")
			if ligne.startswith("ID"):
				creds["id"] = int(ligne.rsplit(":")[1])
			if ligne.startswith("SecretClient"):
				creds["SecretClient"] = ligne.rsplit(":")[1]
			if ligne.startswith("Token"):
				creds["Token"] = ligne.rsplit(":")[1]
			if ligne.startswith("Code"):
				creds["Code"] = ligne.rsplit(":")[1]
			if ligne.startswith("RefreshCode"):
				creds["RefreshCode"] = ligne.rsplit(":")[1]
			if ligne.startswith("Email"):
				creds["Email"] = ligne.rsplit(":")[1]
			if ligne.startswith("Password"):
				creds["Password"] = ligne.rsplit(":")[1]

	return (creds)


def refresh_acces_token(creds):
	"""	
	Refresh des tokens pour communiquer avec Strava	

	:param creds: Le dictionnaire de credentials
	:type creds: dict
	"""
	payload = {
		'client_id': creds["id"],
		'client_secret': creds["SecretClient"],
		'refresh_token': creds["RefreshCode"],
		'grant_type': "refresh_token",
		'f': 'json'
	}

	print ("Requesting Token...")
	res = requests.post(auth_url, data=payload, verify=False)
	access_token = res.json()['access_token']
	expiry_ts = res.json()['expires_at']
	creds["AccesToken"] = access_token

	print("Access Token = {}".format(creds["AccesToken"]))
	print("New token will expire at: ",end='\t')
	print(datetime.utcfromtimestamp(expiry_ts).strftime('%Y-%m-%d %H:%M:%S'))


def get_client(creds):
	""" 
	Mise a jour du client avec le nouveau token 

	:param creds: Le dictionnaire de credentials
	:type creds: dict

	:return: La structure client
	:rtype: :class:`stravalib.client`
	"""

	client = Client(access_token=creds["AccesToken"])
	return client


def display_athlete(client):
	""" 
	Affichage des informations de l'Athlete 

	:param client: La structure client
	:type client: :class:`stravalib.client`
	"""
	athlete = client.get_athlete()
	print ("\n### Display Athlete ###")
	print("Athlete's name is {} {}, based in {}, {}".format(athlete.firstname, athlete.lastname, athlete.city, athlete.country))
	print("Photo URL " + athlete.profile)
	print("all_run_totals : " + str(athlete.stats.all_run_totals.distance))
	print("all_bike_totals : " + str(athlete.stats.all_ride_totals.distance))


def display_activity(activity, client):
	""" 
		Affichage detaille de l'activite en parametre 
			- id
			- name
			- kudos_count

	:param activity: L'activite a afficher
	:type activity: :class:`stravalib.model.Activity`

	:param client: La structure client
	:type client: :class:`stravalib.client`
	"""

	data = {}
	data['id'] = activity.id
	data['name'] = activity.name
	data['kudos'] = activity.kudos_count
	data['gear_id'] = activity.gear_id
	# activity['start_date_local'] = activity['start_date_local']
	# activity['type'] = activity['type']
	# activity['distance'] = activity['distance']
	# activity['elapsed_time'] = activity['elapsed_time']
	print ("La derniere activite retrouvee est :")
	print (data)
	print ("Materiel : {}".format(client.get_gear(activity.gear_id)))


def get_last_activity(client):
	""" 
	Affiche la derniere activite, de maniere detaille 
	
	:param client: La structure client
	:type client: :class:`stravalib.client`

	:return: La derniere activite
	:rtype: :class:`stravalib.model.Activity`
	"""
	print ("\nDisplay last activity")
	for activity in client.get_activities(limit=1):
		return activity


def display_last_activity(client):
	""" 
	Affiche la derniere activite, de maniere detaille 

	:param client: La structure client
	:type client: :class:`stravalib.client`
	"""
	print ("\nDisplay last activity")
	for activity in client.get_activities(limit=1):
		display_activity(activity, client)


def display_N_activity(client, n):
	""" 
	Affichage simple des N dernieres activitees

	:param client: La structure client
	:type client: :class:`stravalib.client`

	:param n: Le nombre d'activite maximum
	:type n: int
	"""

	print ("\nDisplay last {} activity".format(n))
	for activity in client.get_activities(limit=n):
		print("{0.id} - {0.name} - {0.moving_time}".format(activity))


def create_manual_run(client):
	""" 
	Creation d'une activite manuelle 

	:param client: La structure client
	:type client: :class:`stravalib.client`
	"""

	print ("\nCreation d'une activite")
	now = datetime.now().replace(microsecond=0)
	a = client.create_activity("[fake] Test_API_Strava - Envoi via l'API Python #GEEK",
		description="Debut de l'utilisation de l'API, ça ouvre pleins de possibilite :P",
		activity_type=model.Activity.RUN,
		start_date_local=now,
		elapsed_time=str(timedelta(hours=1, minutes=4, seconds=5).total_seconds()).replace('.0', ''),
		distance=uh.kilometers(15.2))

	print ("Activite cree, voir https://www.strava.com/activities/" + str(a.id))


def get_webclient(creds):
	"""
	Log into the website with WebClient

	:param creds: Les donnees de credentials
	:type creds: dict

	:return: La structure WebClient
	:rtype: :class:`WebClient`
	"""

	# Log in (requires API token and email/password for the site)
	webclient = WebClient(access_token=creds["AccesToken"], email=creds["Email"], password=creds["Password"])
	print ("WebClient : ")
	print (webclient)

	return webclient


def get_activity_data(webclient, activity):	
	""" 
	Recuperation du fichier de l'activite voulue en utilisant WebClient 

	:param webclient: The Webclient class
	:type webclient: :class:`WebClient`

	:param activity: L'activite voulue.
	:type activity: :class:`stravalib.model.Activity`

	:return: Le `filename` du fichier recupere et cree
	:rtype: str
	"""
	activity_id = activity.id

	# Get the filename and data stream for the activity data
	data = webclient.get_activity_data(activity_id, fmt=DataFormat.ORIGINAL)

	# Save the activity data to disk using the server-provided filename
	with open(data.filename, 'wb') as f:
		for chunk in data.content:
			if not chunk:
				break
			f.write(chunk)

	return data.filename


def upload_existing_activite(client, activity_file, is_HomeTrainer):
	""" 
	Upload d'une activite existante a partir d'un fichier exporte de Strava 

	:param client: La structure client
	:type client: :class:`stravalib.client`

	:param activity_file: Le nom du fichier a envoyer a Strava
	:type activity_file: str

	:param is_HomeTrainer: Definit si l'activite est de type HomeTrainer (VirtualRide) ou non (Ride)
	:type is_HomeTrainer: bool
	"""
	print ("\nUpload d'une activite")

	# On prend le nom du fichier comme nom d'activite
	# On recupere aussi son extension (data_type)
	activite_name, data_type = os.path.splitext(activity_file)
	activite_name = activite_name.replace("_", " ")
	data_type = data_type.replace(".", "")

	print ("activite_name : " + activite_name)
	print ("data_type	 : " + data_type)


	with open(activity_file, 'rb') as fp:
		if is_HomeTrainer:
			uploader = client.upload_activity(fp, data_type=data_type, name=activite_name, activity_type="VirtualRide")
		else:
			uploader = client.upload_activity(fp, data_type=data_type, name=activite_name, activity_type="Ride")
		print (uploader.response)

		activity = uploader.wait()		
		print ("Activite upload, voir https://www.strava.com/activities/" + str(activity.id))


		if is_HomeTrainer:
			# Update de l'activite cree avec le bon velo
			# Recuperation de l'ID du velo nomme HomeTrainer ou HT
			bikes = client.get_athlete().bikes
			for bike in bikes:
				if "HT" in bike.name or "Home Trainer" in bike.name:
					print ("Update de l'activite avec le velo " + bike.name + " " + str(bike.id))
					client.update_activity(activity.id, gear_id=bike.id)
					break


def delete_activity(client, webclient, activity):
	"""
	Suppression de l'activite definit par son id

	:param client: La structure client
	:type client: :class:`stravalib.client`

	:param webclient: The Webclient class
	:type webclient: :class:`WebClient`

	:param activity: L'activite voulue.
	:type activity: :class:`stravalib.model.Activity`
	"""
	# Delete the activity
	print ("Suppression de l'activite : " + activity.name + " --- " +  str(activity.id))
	client.delete_activity(activity.id)

######## MAIN ##########
print ("")
# creds pour read,activity:write,activity:read_all,profile:read_all,read_all
# voir https://www.youtube.com/watch?v=sgscChKfGyg&ab_channel=Franchyze923

# Client source avec ses creds
creds_source = get_creds("creds_source.txt")
refresh_acces_token(creds_source)
client_source = get_client(creds_source)
webclient_source = get_webclient(creds_source)

# Client destination avec ses creds
creds_dest = get_creds("creds_dest.txt")
refresh_acces_token(creds_dest)
client_dest = get_client(creds_dest)

#display_athlete(client_source)
#display_athlete(client_dest)

#display_last_activity(client_source)
#display_N_activity(client_source, 20)

#create_manual_run(client_dest)

# Recuperation de la dernière activite renseignee, et upload sur le 2nd compte
last_activite_source = get_last_activity(client_source)
print ("Derniere activite = " + str(last_activite_source.id))

data_filename = get_activity_data(webclient_source, last_activite_source)

is_HomeTrainer = False
upload_existing_activite(client_dest, data_filename, is_HomeTrainer)

is_delete_actity_source = False
if is_delete_actity_source:
	delete_activity(client_source, webclient_source, last_activite_source)