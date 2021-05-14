#!/usr/bin/python3
# -*-coding:Utf-8 -*

import strava_tools

import argparse
import os

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



# Clean des activites 2000
after = "2000-01-01T00:00:00Z"
before = "2001-10-01T00:00:00Z"
list_act = strava_tools.get_first_N_activity(client_dest, after, before, "All", 10000)
for delete_id in list_act:
	print(delete_id)
	strava_tools.delete_strava_activity(webclient_dest, delete_id)


# Récupération des N premieres activites, du type voulu
after = "2012-09-01T00:00:00Z"
before = "2013-01-01T00:00:00Z"
list_act = strava_tools.get_first_N_activity(client_dest, after, before, type_act, 5)


#Pour toutes les activites choisis

# Filtre sur le nom, qui ne contient pas 'CopyForWandrer'
for activity in list_act:
	print(activity)
	
	# Téléchargement des datas	
	data_filename = strava_tools.get_activity_data(webclient_dest, activity, DataFormat.TCX)

	# Modification des dates, et type destination

	# Upload
	# strava_tools.upload_existing_activite(client_dest, data_filename, type_ride)

# if is_delete_actity_source:
# 	strava_tools.delete_strava_activity(webclient_source, last_activite_source)

# # Suppression du fichier telecharge
# os.remove(data_filename)
