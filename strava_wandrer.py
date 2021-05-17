#!/usr/bin/python3
# -*-coding:Utf-8 -*

import strava_tools

import argparse
import os
import datetime
import time

from stravaweblib import DataFormat

__author__ = "Arnaud TORA"
__copyright__ = "Copyright 2020"
__credits__ = "Arnaud TORA"
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Arnaud TORA"
__status__ = "Dev"


"""
Code Python ayant pour but reuploader des seances, afin de mettre a jour le site wandred.earth

 - Téléchargement des fichiers (course, vélo, ou tous)
 - Modification des dates / types
 - Upload

"""


#################################
############ MAIN ###############
#################################



parser = argparse.ArgumentParser(description="Strava_Wandrer, reuploader des seances")
parser.add_argument('--type_act',
	type=str,
	default="All",
	choices=['Run', 'Ride', 'All'],
	help="Choix du type d'activite à reuploader (Run, Ride, ou All  (all par defaut)")

args = parser.parse_args()
type_act = args.type_act


print ("")
# creds pour read,activity:write,activity:read_all,profile:read_all,read_all
# voir https://www.youtube.com/watch?v=sgscChKfGyg&ab_channel=Franchyze923

# Client destination avec ses creds
creds_dest = strava_tools.get_creds("creds_dest.txt")
strava_tools.refresh_acces_token(creds_dest)
client_dest = strava_tools.get_client(creds_dest)
webclient_dest = strava_tools.get_webclient(creds_dest)

#strava_tools.display_athlete(client_dest)
#strava_tools.display_last_activity(client_dest)



# Clean des activites 2000 - A supprimer a la fin
after  = "2005-01-01T00:00:00Z"
before = "2010-10-01T00:00:00Z"
list_act = strava_tools.get_first_N_activity(client_dest, after, before, "All", 10000)
# for delete_act in list_act:
# 	if "_CopyForWandrer_" in delete_act.name :
# 		print(delete_id)
# 		strava_tools.delete_strava_activity(webclient_dest, delete_act)

print(list_act)
# Recherche de la derniere activite uploadee
# Pour trouver la date 'after'
print("\n\n## Recherche de la derniere activite uploadee ##")
derniere_date_ajout = datetime.datetime(2010, 1, 1)
for act in list_act:
	print (act)
	if("_CopyForWandrer_" in act.name):
		print (act.name)
		derniere_date_ajout = act.name.split("_")[2]
		annee=derniere_date_ajout.split("-")[0]
		mois=derniere_date_ajout.split("-")[1]
		jour=derniere_date_ajout.split("-")[2]
		derniere_date_ajout = datetime.datetime(int(annee), int(mois), int(jour))
		print(derniere_date_ajout)
	else:
		break

print("La derniere uploadee est")
print(derniere_date_ajout)

# Récupération des N premieres activites, du type voulu
after = derniere_date_ajout+"T00:00:00Z"
before = "2013-01-01T00:00:00Z"
list_act = strava_tools.get_first_N_activity(client_dest, after, before, type_act, 5)


# Pour toutes les activites choisis
# Filtre sur le nom, qui ne contient pas 'CopyForWandrer'
print("\n\n## Modification et envoie des activites ##")
for activity in list_act:
	print(activity)
	
	# Téléchargement des datas	
	data_filename = strava_tools.get_activity_data(webclient_dest, activity.id, DataFormat.TCX)
	print("Act initial : " + data_filename)
	date_initial = activity.start_date.strftime("%Y-%m-%d")
	print("date : " + date_initial)
	derniere_date_ajout = derniere_date_ajout + datetime.timedelta(days=1)
	date_ajout = derniere_date_ajout.strftime("%Y-%m-%d")
	data_filename_modif= "_CopyForWandrer_" + date_initial + "_" + date_ajout + "_" + data_filename.replace(".tcx", "")
	print("Nouveau nom d'activite : " + data_filename_modif)

	# Modification des dates, et type destination
	contenu_out = []
	with open(data_filename, "r") as fichier:
		contenu = fichier.readlines()
		date_a_modifier = ""
		for ligne in contenu:
			# Modification de la date
			if("<Id>" in ligne):
				date_a_modifier = ligne.split("<Id>")[1].split("T")[0]
				print("Date1 : " + date_a_modifier)
				print("Date2 : " + str(date_ajout))
				ligne = ligne.replace(date_a_modifier, date_ajout)
			elif(date_a_modifier != ""):
				ligne = ligne.replace(date_a_modifier, date_ajout)

			if('<Activity Sport="Running">' in ligne):
				ligne = ligne.replace("Running", "EBikeRide")
			contenu_out.append(ligne)

	with open(data_filename_modif, 'w') as fichier:
		for ligne in contenu_out:
			fichier.write(ligne)


	# Upload
	with open(data_filename_modif, 'rb') as fp:
		uploader = client_dest.upload_activity(fp, data_type="tcx", name=data_filename_modif, activity_type="EBikeRide", private=True)
		print (uploader.response)
		activity = uploader.wait()		
		print ("Activite upload, voir https://www.strava.com/activities/" + str(activity.id))

		# # Suppression du fichier telecharge
		# os.remove(data_filename)

	time.sleep(10)