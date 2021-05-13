#!/usr/bin/python3
# -*-coding:Utf-8 -*

import strava_tools

import argparse
import os

__author__ = "Arnaud TORA"
__copyright__ = "Copyright 2020"
__credits__ = "Arnaud TORA"
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Arnaud TORA"
__status__ = "Dev"


"""
Code Python ayant pour but de transférer une activité Strava d'un compte A vers un compte B

 - Option de vérification du nom de l'activité source
 - Option de suppression de l'activité source

Nécessite les credentials A et B (surtout sur l'origin est privée)
"""


#################################
############ MAIN ###############
#################################



parser = argparse.ArgumentParser(description="Strava_Zwift, pour transférer une activite d'un compte Strava vers un autre")
parser.add_argument('--delete', 
	action='store_true',
	default=False,
	help="Option pour supprimer l'activite source")
parser.add_argument('--type_ride',
	type=str,
	default="VirtualRide",
	choices=['VirtualRide', 'Ride'],
	help="Choix du type d'activite (VirtualRide par defaut)")

args = parser.parse_args()
is_delete_actity_source = args.delete
type_ride = args.type_ride


print ("")
# creds pour read,activity:write,activity:read_all,profile:read_all,read_all
# voir https://www.youtube.com/watch?v=sgscChKfGyg&ab_channel=Franchyze923

# Client source avec ses creds
creds_source = strava_tools.get_creds("creds_source.txt")
strava_tools.refresh_acces_token(creds_source)
client_source = strava_tools.get_client(creds_source)
webclient_source = strava_tools.get_webclient(creds_source)

# Client destination avec ses creds
creds_dest = strava_tools.get_creds("creds_dest.txt")
strava_tools.refresh_acces_token(creds_dest)
client_dest = strava_tools.get_client(creds_dest)
webclient_dest = strava_tools.get_webclient(creds_dest)

#display_athlete(client_source)
#strava_tools.display_athlete(client_dest)

#display_last_activity(client_source)
#display_N_activity(client_source, 20)

# Test creation et suppression d'une activite
#activity_create = create_manual_run(client_dest)
#time.sleep(10)
#delete_strava_activity(webclient_dest, activity_create)


# Recuperation de la dernière activite renseignee, et upload sur le 2nd compte
last_activite_source = strava_tools.get_last_activity(client_source)
print ("Derniere activite = " + last_activite_source.name + " --- " + str(last_activite_source.id))

data_filename = strava_tools.get_activity_data(webclient_source, last_activite_source)

strava_tools.upload_existing_activite(client_dest, data_filename, type_ride)

if is_delete_actity_source:
	strava_tools.delete_strava_activity(webclient_source, last_activite_source)

# Suppression du fichier telecharge
os.remove(data_filename)
