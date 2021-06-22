import requests
import json
from urllib.parse import urlencode
from random import choice
from datetime import date

def handle_exists(handle): 
	response = requests.get(f"https://dmoj.ca/api/v2/user/{handle}")
	return response.status_code == 200

def profile(handle): 
	response = requests.get(f"https://dmoj.ca/api/v2/user/{handle}")
	data = response.json()["data"]["object"]
	return (str(data["username"]), str(data["points"]), str(data["performance_points"]), str(data["problem_count"]))

def solved(handle): 
	response = requests.get(f"https://dmoj.ca/api/v2/user/{handle}")
	data = response.json()["data"]["object"]
	return data["solved_problems"]

def rating_graph(handle): 
	response = requests.get(f"https://dmoj.ca/api/v2/user/{handle}")
	contests = response.json()["data"]["object"]["contests"]
	ratings = [contest["rating"] for contest in contests if contest["rating"] is not None]
	keys = [contest["key"] for contest in contests if contest["rating"] is not None]
	config = {
			"type": "line",
			"data": {
					"labels": keys,
					"datasets": [{
							"label": f"Rating of {handle}",
							"data": ratings,
					}]
			}
	}
	params = {
			'chart': json.dumps(config),
			'width': 500,
			'height': 300,
			'backgroundColor': 'white',
	}
	return 'https://quickchart.io/chart?%s' % urlencode(params)

def problem_solved(handle, link):
	response = requests.get(f"https://dmoj.ca/api/v2/user/{handle}")
	data = response.json()["data"]["object"]
	return link[link.rfind("/")+1:] in data["solved_problems"]

#get an unsolved question based on paramters

def createquestion(handle,lowbound,highbound,topic):
  #handle, lowerbound (1 if nothing), highbound (50 if nothing), topic ("" if no preference)
  a = solved(handle)
  topics = ['Ad_Hoc', 'Advanced_Math', 'Brute_Force', 'Capture_the_Flag', 'Data_Structures', 'Divide_and_Conquer', 'Dynamic_Programming', 'Game_Theory', 'Geometry', 'Graph_Theory', 'Greedy_Algorithms', 'Implementation', 'Recursion', 'Regular_Expressions', 'Simple_Math', 'Simulation', 'String_Algorithms', 'Uncategorized']
  link = f"https://dmoj.ca/api/v2/problems?point_start={lowbound}&point_end={highbound}"
  if topic != "" and topic in topics:
    topic = topic.replace('_',' ')
    link += "&type="+topic

  content = requests.get(link).json()["data"]["objects"]
  lis = []
  for prob in content:
    if not prob["code"] in a:
      lis.append(prob["code"])
  selected = choice(lis)
  return selected

def createdaily(handle):
  a = solved(handle)
  Q = []
  for i in range(min(20,len(a))):
    pt = requests.get(f"https://dmoj.ca/api/v2/problem/{a[-i]}").json()["data"]["object"]["points"]
    Q.append(pt)
  avg = int(sum(Q)/len(Q))
  return createquestion(handle,max(1,avg-2),min(50,avg+4),"")

def gettime():
  return date.today()

def randprob(p1,p2):
	p1solved = solved(p1)
	p2solved = solved(p2)
	lis = []
	content = requests.get("https://dmoj.ca/api/v2/problems").json()["data"]["objects"]
	for prob in content:
		if prob["code"] not in p1solved and prob["code"] not in p2solved:
			lis.append(prob["code"])
	selected = choice(lis)
	return selected
