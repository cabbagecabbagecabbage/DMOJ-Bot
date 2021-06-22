import discord
import os
from discord.ext import commands
from keep_alive import keep_alive
from api_requests import *
from replit import db
from datetime import date

HELP_MSG = '''```User Commands: 


%connect <dmoj handle> - Connects a discord id to a dmoj handle. 

%disconnect - Disconnects a discord id from a dmoj handle if it is linked.

%handle - Displays what dmoj handle the user is attached to.

%profile - Displays information about the dmoj handle that the user is connected to.

%profile <handle> - Displays information about the dmoj handle provided.

%solved - Shares a text file with all the problems that the dmoj handle linked to the user has solved.

%leaderboard <information requested> - Displays the information requested of all connected users. The information requested can be <points>, <performance_points>, or <problem_count>.

%rating_graph - Displays the rating graph of the dmoj handle connected to the user.

%rating_graph <handle> - Displays the rating graph of the dmoj handle provided.





Problem Commands:


%get_question <minimum points> <maximum points> <problem type> - Chooses a random problem based on the range and problem type entered by the user. The range and problem type are both optional parameters. Ex.

%get_question <minimum points> <maximum points>

%get_question <problem type>

%daily_problem - Sends one new problem everyday.



Dueling Commands:


%duel @<someone> - challenges someone to a duel

%acceptduel @<someone> - accept the duel from someone

%forfeitduel - forfeit your ongoing duel

%done - inform the bot that you've solved the problem



Topics:
'Ad_Hoc', 'Advanced_Math', 'Brute_Force', 'Capture_the_Flag', 'Data_Structures', 'Divide_and_Conquer', 'Dynamic_Programming', 'Game_Theory', 'Geometry', 'Graph_Theory', 'Greedy_Algorithms', 'Implementation', 'Recursion', 'Regular_Expressions', 'Simple_Math', 'Simulation', 'String_Algorithms', 'Uncategorized'

```
'''

ALLTOPICS = ['Ad_Hoc', 'Advanced_Math', 'Brute_Force', 'Capture_the_Flag', 'Data_Structures', 'Divide_and_Conquer', 'Dynamic_Programming', 'Game_Theory', 'Geometry', 'Graph_Theory', 'Greedy_Algorithms', 'Implementation', 'Recursion', 'Regular_Expressions', 'Simple_Math', 'Simulation', 'String_Algorithms', 'Uncategorized']

client = discord.Client()

@client.event
async def on_ready():
  print('Bot is ready')

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	msg = message.content
	chnl = message.channel
	if msg.startswith("%help"):
		await chnl.send(HELP_MSG)

	### USER COMMANDS ###
	if msg.startswith("%connect"):
		if len(msg.split()) == 2:
			handle = msg.split()[1]
			if str(message.author.id) in db['users'].keys():
				await chnl.send(f"You are already connected to the account {db['users'][str(message.author.id)]['handle']}")
			elif handle_exists(handle):      
				db['users'][str(message.author.id)] = {}
				db['users'][str(message.author.id)]['handle'] = handle
				db['users'][str(message.author.id)]['dueling'] = False
				db['users'][str(message.author.id)]['pending duels'] = []
				db['users'][str(message.author.id)]['duel problem'] = ""
				db['users'][str(message.author.id)]['duel opponent'] = ""
				db['users'][str(message.author.id)]['lastchecked'] = date.today().strftime("%d/%m/%Y")
				db['users'][str(message.author.id)]["curstreak"] = 0
				db['users'][str(message.author.id)]['longeststreak'] = 0
				db['users'][str(message.author.id)]['firsttime'] = 1
				db['users'][str(message.author.id)]['question'] = ''
				await chnl.send(f"Successfully connected {message.author} to dmoj handle {handle}")
			else:
				await chnl.send(f"{handle} does not exist on dmoj")
		else:
			await chnl.send("Invalid format")
	
	if msg.startswith("%disconnect"):
		try:
			await chnl.send(f"Successfully disconnected {message.author} from dmoj handle {db['users'][str(message.author.id)]['handle']}")
			del db['users'][str(message.author.id)]
		except:
			await chnl.send(f"{message.author} is currently not connected to a handle")

	if msg.startswith("%handle"):
		if str(message.author.id) in db['users'].keys():
			await chnl.send(f"{message.author} is currently connected to {db['users'][str(message.author.id)]['handle']}")
		else:
			await chnl.send(f"{message.author} is currently not connected to a handle")
	
	if msg.startswith("%profile"):
		if len(msg.split()) == 1:
			if str(message.author.id) in db['users'].keys():
				handle = db['users'][str(message.author.id)]['handle']
				data = profile(handle)
				await chnl.send(f"Username: {data[0]}\nTotal points: {data[1]}\nPerformance Points: {data[2]}\nProblem Count: {data[3]}")
			else:
				await chnl.send(f"{message.author} is currently not connected to a handle")
		elif len(msg.split()) == 2:
			handle = msg.split()[1]
			if handle_exists(handle):
				data = profile(handle)
				await chnl.send(f"Username: {data[0]}\nTotal points: {data[1]}\nPerformance Points: {data[2]}\nProblem Count: {data[3]}")
			else:
				await chnl.send(f"The handle {handle} does not exist")
		else:
			await chnl.send(f"Invalid Format")
	
	if msg.startswith("%solved"):
		if len(msg.split()) == 1:
			if str(message.author.id) in db['users'].keys():
				handle = db['users'][str(message.author.id)]['handle']
				with open("solved.txt", "w") as file:
					for problem in solved(handle):
						file.write("https://dmoj.ca/problem/"+problem+"\n")
				with open("solved.txt", "rb") as file:
					await chnl.send("Your file is:", file=discord.File(file, "solved.txt"))
			else:
				await chnl.send(f"{message.author} is currently not connected to a handle")
		elif len(msg.split()) == 2:
			handle = msg.split()[1]
			if handle_exists(handle):
				with open("solved.txt", "w") as file:
					for problem in solved(handle):
						file.write("https://dmoj.ca/problem/"+problem+"\n")
				with open("solved.txt", "rb") as file:
						await chnl.send("Your file is:", file=discord.File(file, "solved.txt"))
			else:
				await chnl.send(f"The handle {handle} does not exist")
		else:
			await chnl.send(f"Invalid Format")
	
	if msg.startswith("%leaderboard"):
		data = [profile(db['users'][str(user)]['handle']) for user in db['users'].keys()]
    
		reply = ''
		fixed = 25
		if len(msg.split()) == 2:
			sortby = msg.split()[1]
			if sortby == 'points':
				data.sort(key = lambda x: float(x[1]), reverse = True)
				reply += "\n".join([d[0] + (fixed-len(d[0]))*" " + d[1] for d in data])
				

			elif sortby == 'performance_points':
				data.sort(key = lambda x: float(x[2]), reverse = True)
				reply += "\n".join([d[0] + (fixed-len(d[0]))*" " + d[2] for d in data])
			

			elif sortby == 'problem_count':
				data.sort(key = lambda x: float(x[3]), reverse = True)
				reply += "\n".join([d[0] + (fixed-len(d[0]))*" " + d[3] for d in data])
				
			if reply != '': 
				await chnl.send('```' + reply + '```')

			else:
				await chnl.send("Invalid Format")

	if msg.startswith("%rating_graph"):
		if len(msg.split()) == 1:
			if str(message.author.id) in db['users'].keys():
				handle = db['users'][str(message.author.id)]['handle']
				await chnl.send(rating_graph(handle))
			else:
				await chnl.send(f"{message.author} is currently not connected to a handle")
		elif len(msg.split()) == 2:
			handle = msg.split()[1]
			if handle_exists(handle):
				await chnl.send(rating_graph(handle))
			else:
				await chnl.send(f"The handle {handle} does not exist")
		else:
			await chnl.send(f"Invalid Format")

	### PROBLEM COMMANDS ###


	if msg.startswith("%get_question"):
		if str(message.author.id) in db['users'].keys():
			handle = db["users"][str(message.author.id)]['handle']
			if len(msg.split()) == 1: 
				await chnl.send("https://dmoj.ca/problem/"+createquestion(handle,1,50,""))
			elif len(msg.split()) == 2:
				topic = msg.split()[1]
				if topic in ALLTOPICS:
					await chnl.send("https://dmoj.ca/problem/"+createquestion(handle,1,50,topic))
				else:
					await chnl.send(f"Invalid Format")
					
			elif len(msg.split()) == 3:
				low,high = msg.split()[1],msg.split()[2]
				try:
					if (int(low) >= 1 and int(high) <= 50):
						await chnl.send("https://dmoj.ca/problem/"+createquestion(handle,low,high,""))
				except:
					await chnl.send(f"Invalid Format")
			elif len(msg.split()) == 4:
				low,high,topic = msg.split()[1],msg.split()[2],msg.split()[3]
				try:
					if (int(low) >= 1 and int(high) <= 50 and topic in ALLTOPICS):
						await chnl.send("https://dmoj.ca/problem/"+createquestion(handle,low,high,topic))
				except:
					await chnl.send(f"Invalid Format")
		else:
				await chnl.send(f"{message.author} is currently not connected to a handle") 	

	if msg.startswith("%daily_problem"):
		if (len(msg.split()) == 1):
			td = date.today().strftime("%d/%m/%Y")
			aut = str(message.author.id)
			dic = db['users'][aut]
			if aut in db['users'].keys():
				handle = dic['handle']
				if td != dic['lastchecked'] or dic['firsttime']:
					dic['lastchecked'] = td
					#check if they did their previous daily question
					if (dic['question'] in solved(handle) or dic['firsttime']):
						if (not dic['firsttime']):
							dic['curstreak'] += 1
							dic['longeststreak'] = max(dic['longeststreak'],dic['curstreak'])
							await chnl.send(f"Good job {message.author}! We have already updated your streak. Your current streak is {dic['curstreak']}")
					dic['question'] = createdaily(handle)
					dic['firsttime'] = 0

				await chnl.send(f"Your daily challenge problem is {'https://dmoj.ca/problem/'+dic['question']}")

				db['users'][aut] = dic
          
				
	### DUELING COMMANDS ###
	if msg.startswith("%duel"):
		if len(msg.split()) != 2:
			await chnl.send("Invalid Format")
		else:
			p1 = str(message.author.id)
			p2 = msg.split()[1][3:-1]
			if p1 in db['users'].keys() and p2 in db['users'].keys():
				if not db['users'][p1]['dueling'] and not db['users'][p2]['dueling']:
					db['users'][p2]["pending duels"].append(p1)
					await chnl.send("Duel proposed!")
				else:
					await chnl.send("You must wait until neither of you are in a duel.")
			else:
				await chnl.send("Both you and the person you duel must be connected.")

	if msg.startswith("%acceptduel"):
		if len(msg.split()) != 2:
			await chnl.send("Invalid Format")
		else:
			p2 = str(message.author.id)
			p1 = msg.split()[1][3:-1]
			if p1 in db['users'][p2]["pending duels"] and db['users'][p2]["dueling"] == False:
				db['users'][p2]["pending duels"].remove(p1)
				db['users'][p2]["dueling"] = True
				db['users'][p1]["dueling"] = True
				db['users'][p2]["duel opponent"] = p1
				db['users'][p1]["duel opponent"] = p2
				problem = randprob(db['users'][p1]['handle'],db['users'][p2]['handle'])
				db['users'][p1]['duel problem'] = problem
				db['users'][p2]['duel problem'] = problem
				await chnl.send(f"The duel will now begin. Problem: https://dmoj.ca/problem/{problem}")
			else:
				await chnl.send("That person has not challenged you to a duel or they are in a duel right now.")
	
	if msg.startswith("%forfeitduel"):
			p1 = str(message.author.id)
			if db['users'][p1]["dueling"] == True:
				db['users'][db['users'][p1]["duel opponent"]]["dueling"] = False
				db['users'][p1]["dueling"] = False
				await chnl.send(f"{db['users'][p1]['handle']} has forfeited. {db['users'][db['users'][p1]['duel opponent']]['handle']} wins.")
				db['users'][db['users'][p1]["duel opponent"]]["duel opponent"] = ""
				db['users'][p1]["duel opponent"] = ""
				db['users'][db['users'][p1]["duel opponent"]]["duel problem"] = ""
				db['users'][p1]['duel problem'] = ""
			else:
				await chnl.send("You are currently not in a duel.")

	if msg.startswith("%done"):
		p1 = str(message.author.id)
		if db['users'][p1]["dueling"] == True:
			if problem_solved(db['users'][p1]['handle'], db['users'][p1]['duel problem']):
				db['users'][db['users'][p1]["duel opponent"]]["dueling"] = False
				db['users'][p1]["dueling"] = False
				await chnl.send(f"{db['users'][p1]['handle']} has solved the problem. {db['users'][p1]['handle']} wins.")
				db['users'][db['users'][p1]["duel opponent"]]["duel opponent"] = ""
				db['users'][p1]["duel opponent"] = ""
				db['users'][db['users'][p1]["duel opponent"]]["duel problem"] = ""
				db['users'][p1]['duel problem'] = ""
			else:
				await chnl.send(f"You have not solved the problem yet.")
		else:
			await chnl.send("You are currently not in a duel.")


keep_alive()

my_secret = os.environ['TOKEN']

client.run(my_secret)