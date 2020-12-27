#!/usr/bin/python3
# -*-coding:Utf-8 -*

from stravalib import Client
from stravalib import model, exc, attributes, unithelper as uh

from datetime import datetime, timedelta
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"



def get_creds(chemin):
	"""
		Lecture et recuperation des identifiants de connexions
		- ID
		- SecretClient
		- Token
		- Code
		- RefreshCode	"""
	creds = {}

	with open(chemin, "r") as fichier:
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

	return (creds)



def refresh_acces_token(creds):
	"""	Refresh des tokens pour communiquer avec Strava	"""

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
	""" Mise a jour du client avec le nouveau token """

	client = Client(access_token=creds["AccesToken"])
	return client



def display_athlete(client):
	""" Affichage des informations de l'Athlete """

	athlete = client.get_athlete()
	print ("\n### Display Athlete ###")
	print("Athlete's name is {} {}, based in {}, {}".format(athlete.firstname, athlete.lastname, athlete.city, athlete.country))
	print("Photo URL " + athlete.profile)
	print("all_run_totals : " + str(athlete.stats.all_run_totals.distance))
	print("all_bike_totals : " + str(athlete.stats.all_ride_totals.distance))
	print("FTP " + athlete.ftp)



def display_activity(activity, client):
	""" 
		Affichage detaille de l'activite en parametre 
			- id
			- name
			- kudos_count
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



def display_last_activity(client):
	""" Affiche la derniere activite, de maniere detaille """

	print ("\nDisplay last activity")
	for activity in client.get_activities(limit=1):
		display_activity(activity, client)



def display_N_activity(client, n):
	""" Affichage simple des N dernieres activitees"""

	print ("\nDisplay last {} activity".format(n))
	for activity in client.get_activities(limit=n):
		print("{0.id} - {0.name} - {0.moving_time}".format(activity))



def create_manual_run(client):
	""" Creation d'une activite manuelle """

	print ("\nCreation d'une activite")
	now = datetime.now().replace(microsecond=0)
	a = client.create_activity("[fake] Test_API_Strava - Envoi via l'API Python #GEEK",
		description="Debut de l'utilisation de l'API, ça ouvre pleins de possibilite :P",
		activity_type=model.Activity.RUN,
		start_date_local=now,
		elapsed_time=str(timedelta(hours=1, minutes=4, seconds=5).total_seconds()).replace('.0', ''),
		distance=uh.kilometers(15.2))

	print ("Activite cree, voir https://www.strava.com/activities/" + str(a.id))


def upload_existing_activite(client, activity_file):
	""" Upload d'une activite existante a partir d'un fichier exporte de Strava """

	print ("\nUpload d'une activite")

	# On prend le nom du fichier comme nom d'activite
	# On recupere aussi son extension (data_type)
	activite_name, data_type = os.path.splitext(activity_file)
	data_type = data_type.replace(".", "")
	print ("activite_name : " + activite_name)
	print ("data_type     : " + data_type)

	with open(activity_file, 'rb') as fp:
		uploader = client.upload_activity(fp, data_type=data_type, name=activite_name, activity_type="VirtualRide")
		print (uploader.response)

		a = uploader.wait()		
		print ("Activite upload, voir https://www.strava.com/activities/" + str(a.id))


######## MAIN ##########
print ("")
# creds pour read,activity:write,activity:read_all,profile:read_all,read_all
# voir https://www.youtube.com/watch?v=sgscChKfGyg&ab_channel=Franchyze923
creds = get_creds("creds.txt")
refresh_acces_token(creds)
client = get_client(creds)

display_athlete(client)

display_last_activity(client)
display_N_activity(client, 20)

create_manual_run(client)

filename_download = "Ocean_lava_Cliffside_Loop.fit"
upload_existing_activite(client, filename_download)