import yaml
import json

from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import tool


# read the json file at OpenAPIspecs/petstore.json with normal python libs
with open('OpenAPIspecs/petstore.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

pets = {
  1: {"id": 1, "name": "Bluey", "Tag": "heeler"},
  2: {"id": 2, "name": "Bingo", "Tag": "heeler"},
  3: {"id": 3, "name": "Chilli", "Tag": "heeler"},
  4: {"id": 3, "name": "Bandit", "Tag": "heeler"},
}

@tool("GetAPet")
def get_a_pet(id) -> str:
  """Returns the details of a pet with the given ID."""
  return json.dumps(pets[id])

@tool("GetAllPets")
def get_all_pets() -> str:
  """Returns the details of a pet with the given ID."""
  return json.dumps(pets)

bs = """
"Slow down and take a deep breath and lets work through this step by step"
"You are an expiremental AI acting as one end of an API who can translate JSON to natural language."
"You can answer specific questions about the API Spec, provide examples of how to use the API, and summarize the API Spec in natural language."

Your API Spec:
"""
bs = bs + yaml.dump(data)


#print(bs)
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    #model="gemini-1.5-pro-latest",
    #convert_system_message_to_human=True,
    verbose=True,
    streaming=False,
    temperature=0.2,
)


requester = Agent(
  role='Requester',
  goal='Request Responses',
  verbose=True,
  backstory=(
    "Slow down and take a deep breath and lets work through this step by step"
    "You are an expiremental AI that can talk to another AI."
    "you don't know what they are are capable of, but you can ask them questions to find out."
  ),
  tools=[],
  allow_delegation=True,
  llm=llm
)

summarizer = Agent(
  role='Responder',
  goal='Respond to informative or summary requests',
  verbose=True,
  backstory=bs,
  tools=[],
  allow_delegation=True,
  llm=llm
)

agents = []

for path, verb in data['paths'].items():
  for v, content in verb.items():

    c = str(content)
    bs = "Path: " + path + " Verb: " + v + " Content: " + c
    p = Agent(
      role=f"Responder for {v} on {path}",
      goal='Respond to requests',
      verbose=True,
      backstory= bs,
      tools=[get_a_pet, get_all_pets],
      allow_delegation=True,
      llm=llm,
    )
    
    agents.append(p)

user_input = input("What do you want to know about the API? ")

Request_task = Task(
  description=(
    user_input
  ),
  expected_output="",
  tools=[],
  agent=requester,
)

def log_step(input):
  print(input)

crew = Crew(
  agents=[requester, summarizer] + agents,
  tasks=[Request_task],
  process=Process.sequential,  # Optional: Sequential task execution is default
  full_output=True,
  step_callback=log_step,
)

# Starting the task execution process with enhanced feedback
result = crew.kickoff()
#print(result)
#print(crew.agents)