import json, requests, threading, time, webbrowser

api_location = "https://en.wikipedia.org/api/rest_v1/page/random/summary"

# keyword variables are used to find the relevant data in the JSON to assign to the local variables

keyword_title = "title"
keyword_question = "extract"
keyword_category = "description"

keyword_urls = "content_urls"
keyword_mode = "desktop"
keyword_url = "page"

questions = []
action = ""
current_question = -1

running = 1

def get_external_json (x):
	request = requests.get(x, allow_redirects = True)
	while request.status_code == 429:
		request = requests.get(x, allow_redirects = True)
	return json.loads(request.content.decode("utf-8"))

def create_question ():
	src = get_external_json(api_location)
	question = {}
	question["title"] = src[keyword_title].lower()
	
	location = question["title"].find("(")
	if not location == -1:
		question["title"] = question["title"][0:location].strip()
	
	question["question"] = src[keyword_question].lower()
	try:
		question["category"] = src[keyword_category].lower()
	except KeyError:
		question["category"] = "(null category)"
	question["url"] = src[keyword_urls][keyword_mode][keyword_url]
	return question

def append_question ():
	working_question = create_question()
	while len(working_question["question"]) < 200:
		working_question = create_question()
	questions.append(working_question)

def async_updater ():
	while running:
		if current_question > len(questions) - 5:
			append_question()
		time.sleep(1)

t1 = threading.Thread(target = async_updater)
t1.start()

while not (action == "stop" or action == "c" or action == "q"):
	if action == "open":
		webbrowser.open(questions[current_question]["url"])
		action = ""
	elif action == "save":
		with open(input("Enter output location: "), 'w') as outfile:
			json.dump(questions, outfile, indent = 1)
			print("\n")
		action = ""
	elif len(questions) == 0:
		pass
	else:
		current_question += 1
		print("(", current_question, "/", len(questions), "),", questions[current_question]["category"])
		print(questions[current_question]["question"].replace(questions[current_question]["title"], "???"))
		action = input("")
		print(questions[current_question]["title"])
		if action == "":
			action = input("")

running = 0
print("\nThank you for playing!")
