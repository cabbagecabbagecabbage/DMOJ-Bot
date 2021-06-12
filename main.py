import discord
import os
from discord.ext import commands
from keep_alive import keep_alive
from api_requests import *
from replit import db

HELP_MSG = '''```User Commands: 
%connect <dmoj handle> - Connects a discord id to a dmoj handle. 

%disconnect - Disconnects a discord id from a dmoj handle if it is linked.

%handle - Displays what dmoj handle the user is attached to.

%profile - Displays information about the dmoj handle that the user is connected to.

%solved - Shares a text file with all the problems that the dmoj handle linked to the user has solved.

%leaderboard <information requested> - Displays the information requested of all connected users. The information requested can be <points>, <performance_points>, or <problem_count>.

%rating_graph - Displays the rating graph of the dmoj handle connected to the user.```
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
			if handle_exists(handle):
				db['users'][str(message.author.id)] = handle
				await chnl.send(f"Successfully connected {message.author} to dmoj user {handle}")
			else:
				await chnl.send(f"{handle} does not exist on dmoj")
		else:
			await chnl.send("Invalid format")
	
	if msg.startswith("%disconnect"):
		try:
			del db['users'][str(message.author.id)]
			await chnl.send(f"{message.author} is no longer connected to {db['users'][str(message.author.id)]}")
		except Exception as e:
			print(e)
			await chnl.send(f"{message.author} is currently not connected to a handle")

	if msg.startswith("%handle"):
		if str(message.author.id) in db['users'].keys():
			await chnl.send(f"{message.author} is currently connected to {db['users'][str(message.author.id)]}")
		else:
			await chnl.send(f"{message.author} is currently not connected to a handle")
	
	if msg.startswith("%profile"):
		if len(msg.split()) == 1:
			if str(message.author.id) in db['users'].keys():
				handle = db['users'][str(message.author.id)]
				data = profile(handle)
				await chnl.send(f"Username: {data[0]}\nTotal points: {data[1]}\nPerformance Points: {data[2]}\nProblem Count: {data[3]}")
			else:
				await chnl.send(f"{message.author} is not currently connected to a handle")
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
			if str(message.author.id) in db.keys():
				handle = db['users'][str(message.author.id)]
				with open("solved.txt", "w") as file:
					for problem in solved(handle):
						file.write("https://dmoj.ca/problem/"+problem+"\n")
				with open("solved.txt", "rb") as file:
					await chnl.send("Your file is:", file=discord.File(file, "solved.txt"))
			else:
				await chnl.send(f"{message.author} is not currently connected to a handle")
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
		data = [profile(db['users'][str(user)]) for user in db['users'].keys()]
    
		reply = ''

		if len(msg.split()) == 2:
			sortby = msg.split()[1]
			if sortby == 'points':
				data.sort(key = lambda x: x[2], reverse = True)
				reply += "\n".join([f"```{d[0]} --- Total points: {d[1]}```" for d in data])
				

			elif sortby == 'performance_points':
				data.sort(key = lambda x: x[2], reverse = True)
				reply += "\n".join([f"```{d[0]} --- Performance Points: {d[2]}```" for d in data])
			

			elif sortby == 'problem_count':
				data.sort(key = lambda x: x[2], reverse = True)
				reply += "\n".join([f"```{d[0]} --- Problem Count: {d[3]}```" for d in data])
				
      if reply != '':
        await chnl.send(reply)
      
			else:
				await chnl.send("Invalid Format")
		print('test')

	if msg.startswith("%rating_graph"):
		if len(msg.split()) == 1:
			if str(message.author.id) in db.keys():
				handle = db['users'][str(message.author.id)]
				await chnl.send(rating_graph(handle))
			else:
				await chnl.send(f"{message.author} is not currently connected to a handle")
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
		handle = db["users"][str(message.author.id)]
		if len(msg.split()) == 1: 
			await chnl.send(createquestion(handle,1,50,""))
		elif len(msg.split()) == 2:
			topic = msg.split()[1]
			if topic in ALLTOPICS:
				await chnl.send(createquestion(handle,1,50,topic))
			else:
				await chnl.send(f"Invalid Format")
				
		elif len(msg.split() == 3):
			low,high = msg.split()[1],msg.split()[2]
			try:
				if (int(low) >= 1 and int(high) <= 50):
					await chnl.send(createquestion(handle,low,high,""))
			except:
				await chnl.send(f"Invalid Format")
		elif len(msg.split() == 4):
			low,high,topic = msg.split()[1:]
			try:
				if (int(low) >= 1 and int(high) <= 50 and topic in ALLTOPICS):
					await chnl.send(createquestion(handle,low,high,topic))
			except:
				await chnl.send(f"Invalid Format")


	elif msg.startswith("%get_topics"):
		await chnl.send("```"+"\n".join(ALLTOPICS)+"```")


keep_alive()

#this works
client.run("ODUzMDg3NjcyMTYzNTAwMDQz.YMQRzg.Z_xXs7Zk0qnW5eh0eQ5RhRqf0WU")

#this doesnt
# print(os.environ['TOKEN'])
# client.run(os.environ['TOKEN'])
