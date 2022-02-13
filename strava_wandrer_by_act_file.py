#!/usr/bin/python3
# -*-coding:Utf-8 -*

import strava_tools

import argparse
import os
import datetime
import time
import shutil

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
parser.add_argument('--file_id',
	type=str,
	required=True,
	help="Nom du fichier contenant les id a telecharger et envoyer")

args = parser.parse_args()
file_id = args.file_id


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
after  = "1990-01-01T00:00:00Z"
before = "2000-10-01T00:00:00Z"
list_act = strava_tools.get_first_N_activity(client_dest, after, before, "All", 10000)
# for delete_act in list_act:
# 	if "_CopyForWandrer_" in delete_act.name :
# 		strava_tools.delete_strava_activity(webclient_dest, delete_act)

# Recherche de la derniere activite uploadee
# Pour trouver la date 'after'
print("\n\n## Recherche de la derniere activite uploadee ##")
derniere_date_recuperation = datetime.datetime(2012, 8, 9)
derniere_date_ajout = datetime.datetime(1990, 1, 1)
for act in list_act:
	print (act)
	if("_CopyForWandrer_" in act.name):
		derniere_date_recuperation = act.name.split("_")[2]
		annee_recup=derniere_date_recuperation.split("-")[0]
		mois_recup=derniere_date_recuperation.split("-")[1]
		jour_recup=derniere_date_recuperation.split("-")[2]
		derniere_date_recuperation = datetime.datetime(int(annee_recup), int(mois_recup), int(jour_recup))

		derniere_date_ajout = act.name.split("_")[3]
		annee_ajout=derniere_date_ajout.split("-")[0]
		mois_ajout=derniere_date_ajout.split("-")[1]
		jour_ajout=derniere_date_ajout.split("-")[2]
		derniere_date_ajout = datetime.datetime(int(annee_ajout), int(mois_ajout), int(jour_ajout))

	else:
		break

print("La derniere date d'activite uploadee est")
print(derniere_date_recuperation)
print("La derniere activitite a ete uploadee en fake le ")
print(derniere_date_ajout)


# Lecture du fichier des ID a recuperer et envoyer
shutil.copyfile(file_id, file_id+"_save.txt")
list_id_act=[]
print(file_id)
with open(file_id, "r") as fichier:
	contenu = fichier.readlines()
	id = 0
	for line in contenu:
		line = line.replace("\n","")
		if( (line.startswith("__DEJA_AJOUTEE_"))):
			continue
		elif( line.startswith("https://www.strava.com/activities") ):
			id = line.split("/")[-1:][0]
		elif( line.isdigit() ):
			id = line
		else:
			print("Attention : format d'id non respecte : " + line)
			continue
		list_id_act.append(id)


print("###########################")
print("Les " + str(len(list_id_act)) +" activite qui vont être envoyées sont:")
for id in list_id_act:
	print ("ID a ajouter : '" + str(id) + "'")
print("###########################")


for id in list_id_act:
	print("\n\n")
	print("###########################")
	print ("ID a ajouter : '" + str(id) + "'")

	
	# Téléchargement des datas	
	print("Telechargement des data")
	data_filename = strava_tools.get_activity_data(webclient_dest, id, DataFormat.TCX)


	# Modification des dates, et type destination
	contenu_out = []
	date_a_modifier = ""

	derniere_date_ajout = derniere_date_ajout + datetime.timedelta(days=1)
	date_ajout = derniere_date_ajout.strftime("%Y-%m-%d")

	with open(data_filename, "r") as fichier:
		contenu = fichier.readlines()
		for ligne in contenu:
			# Modification de la date
			if("<Id>" in ligne):
				date_a_modifier = ligne.split("<Id>")[1].split("T")[0]
				ligne = ligne.replace(date_a_modifier, date_ajout)
			elif(date_a_modifier != ""):
				ligne = ligne.replace(date_a_modifier, date_ajout)

			if('<Activity Sport="Running">' in ligne):
				ligne = ligne.replace("Running", "EBikeRide")
			contenu_out.append(ligne)


	data_filename_modif= "_CopyForWandrer_" + date_a_modifier + "_" + date_ajout + "_" + data_filename.replace(".tcx", "")
	print("Nouveau nom d'activite : " + data_filename_modif)

	with open(data_filename_modif, 'w') as fichier:
		for ligne in contenu_out:
			fichier.write(ligne)


	# Upload
	with open(data_filename_modif, 'rb') as fp:
		uploader = client_dest.upload_activity(fp, data_type="tcx", name=data_filename_modif, activity_type="EBikeRide", private=True)
		print (uploader.response)
		activity = uploader.wait()		
		print ("Activite upload, voir https://www.strava.com/activities/" + str(activity.id))


	# Fin d'upload OK, on met a jour le fichier en ajoutant __DEJA_AJOUTEE__ a la ligne contenant l'id d'activite
	contenu_file_out = []
	with open(file_id, "r") as fichier:
		contenu = fichier.readlines()
		for line in contenu:
			if(id in line):
				line = "__DEJA_AJOUTEE__ " + line
			contenu_file_out.append(line)

	with open(file_id, 'w') as fichier:
		for ligne in contenu_file_out:
			fichier.write(ligne)



	# Suppression du fichier telecharge
	os.remove(data_filename)
	os.remove(data_filename_modif)

	time.sleep(90)