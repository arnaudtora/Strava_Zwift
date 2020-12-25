#!/usr/bin/python3
# -*-coding:Utf-8 -*

from stravalib import Client

from datetime import datetime, timedelta
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



######## MAIN ##########
print ("")
# creds pour read,activity:write,activity:read_all,profile:read_all,read_all
# voir https://www.youtube.com/watch?v=sgscChKfGyg&ab_channel=Franchyze923
creds = get_creds("creds.txt")
refresh_acces_token(creds)
client = get_client(creds)