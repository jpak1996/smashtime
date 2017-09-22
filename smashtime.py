from collections import OrderedDict
from twilio.rest import TwilioRestClient
import challonge
import time
import string

jank = raw_input("\nTournament url? [excluding \'http://challonge.com/\']:\n\n\tFor example, if url is \'http://challonge.com/melee_singles_09\',\n\ttype in \'melee_singles_09\'\n")

CHALLONGE_CREDS = open('creds/challonge_creds.txt', 'r').readline()
challonge.set_credentials("canigetapak", CHALLONGE_CREDS)

tournament = challonge.tournaments.show(jank)

participants = challonge.participants.index(tournament["id"])
num_entrants = len(participants)


class PlayerObject:

	def __init__(self, players):
		self.players = players
		for x in range(0,num_entrants):
			phone_string = participants[x]["display-name-with-invitation-email-address"]
			index1 = phone_string.find('<') + 1
			index2 = phone_string.find('@')
			phone_substr = phone_string[index1:index2]
			phone_len = index2 - index1

			if phone_len!=10 and phone_len!=11 :
				print("Janky phone number for entrant: " + self.players[x]['name'])
				print("Either that or there is a '<' or '@' character in their tag >:|")
			
			self.players.append({'name': participants[x]['name'], 'id': participants[x]['id'], 'number':phone_substr, 'flag': -1})

	def players_return_id(self,x):
		return self.players[x]['id']

	def players_return_number(self,x):
		return self.players[x]['number']

	def players_return_name(self,x):
		return self.players[x]['name']

	def players_return_flag(self,x):
		return self.players[x]['flag']

	def players_set_flag(self,x,f):
		self.players[x]['flag'] = f

twilio_file = open('creds/twilio_creds.txt', 'r')
ACCOUNT_SID = string.strip(twilio_file.readline())
AUTH_TOKEN = string.strip(twilio_file.readline())
FROM_NUM = string.strip(twilio_file.readline())
print ACCOUNT_SID
print AUTH_TOKEN
print FROM_NUM
def main2():
	
	client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

	tournament = challonge.tournaments.show(jank)

	matches = challonge.matches.index(tournament["id"])
	num_matches = len(matches)

	players = []
	PO = PlayerObject(players)

	print tournament["state"]

	#tournament state possibilities
	#pending
	#underway
	#awaiting_review
	#complete

	if tournament["state"] == "pending":
		print "Please start the tournament."
		exit()

	while(tournament["state"]=="underway"):

		tournament = challonge.tournaments.show(jank)
		print tournament["state"]

		matches = challonge.matches.index(tournament["id"])

		if tournament["state"]!="underway":
			break
		#first match_id vs second match_id
		#PO could have a match_id field storing the last match they played to be compared with a constantly updated match_id
		for x in range(0,num_matches):
			if matches[x]["state"] == "open":
				player1_id = matches[x]["player1-id"]
				player2_id = matches[x]["player2-id"]
				counter = -1
				for elem in range(0,num_entrants):

					if PO.players_return_id(elem) == player1_id:
						#for round 1 players
						if PO.players_return_flag(elem) == -1:
							PO.players_set_flag(elem,matches[x]["id"])
							player1_name = PO.players_return_name(elem)
							player1_number = PO.players_return_number(elem)
							counter+=1
						elif PO.players_return_flag(elem) == matches[x]["id"]:
							#for when the match has not finished
							counter+=0
						else:
							#for new matches
							PO.players_set_flag(elem,matches[x]["id"])
							player1_name = PO.players_return_name(elem)
							player1_number = PO.players_return_number(elem)
							counter+=1
						
					elif PO.players_return_id(elem) == player2_id:
						if PO.players_return_flag(elem) == -1:
							PO.players_set_flag(elem,matches[x]["id"])
							player2_name = PO.players_return_name(elem)
							player2_number = PO.players_return_number(elem)
							counter+=1
						elif PO.players_return_flag(elem) == matches[x]["id"]:
							counter+=0
						else:
							PO.players_set_flag(elem,matches[x]["id"])
							player2_name = PO.players_return_name(elem)
							player2_number = PO.players_return_number(elem)
							counter+=1
					if counter==1:
						msg = player1_name + ', please report to the TO for your match with ' + player2_name + '.'
						client.messages.create(
							to = player1_number,
							from_ = FROM_NUM,
							body = msg,
						)
						print(msg)

						msg = player2_name + ', please report to the TO for your match with ' + player1_name + '.'
						client.messages.create(
							to = player2_number,
							from_ = FROM_NUM,
							body = msg,
						)
						print(msg)
						counter = -1
						
						break


		time.sleep(10)
	
	print "Props to the winner."

main2()
