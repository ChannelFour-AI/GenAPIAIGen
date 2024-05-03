import yaml
import json

from crewai import Agent, Task, Crew, Process
from langchain.agents import Tool
from crewai_tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_google_vertexai import VertexAI

from langchain_community.agent_toolkits import FileManagementToolkit

# read the json file at OpenAPIspecs/petstore.json with normal python libs
with open('OpenAPIspecs/petstore.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

pets = {
  1: {"id": 1, "name": "Bluey", "Tag": "heeler"},
  2: {"id": 2, "name": "Bingo", "Tag": "heeler"},
  3: {"id": 3, "name": "Chilli", "Tag": "heeler"},
  4: {"id": 3, "name": "Bandit", "Tag": "heeler"},
}


tools = FileManagementToolkit(
    root_dir="python_functions/",
    selected_tools=["write_file"],
).get_tools()
write_tool = tools[0]

#move to vertexAI for better quota
llm = VertexAI(
  model="gemini-1.5-pro-preview-0409",
  temperature=.5,
  max_tokens=1024,
  streaming = False,
)

@tool("GetAPet")
def get_a_pet(id) -> str:
  """Returns the details of a pet with the given ID."""
  return json.dumps(pets[id])

@tool("GetAllPets")
def get_all_pets() -> str:
  """Returns the details of a pet with the given ID."""
  return json.dumps(pets)

@tool("Write File with content")
def write_file(filename, data):
  """Writes the given data to the file with the given name."""
  with open("python_functions/"+filename, "w") as f:
      f.write(data)

python_repl = PythonREPL()


# You can create the tool to pass to an agent
repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print()`.",
    func=python_repl.run,
)

def process_input(user_input):
  bs = """
  "You are an expiremental AI acting as one end of an API who can translate YAML to natural language."
  "You can answer specific questions about the API Spec, provide examples of how to use the API, and summarize the API Spec in natural language."

  Your API Spec:
  """
  bs = bs + yaml.dump(data)

  requester = Agent(
    role='Requester',
    goal='Request Responses',
    verbose=True,
    backstory=(
      "You are an expiremental AI that can talk to another AI."
      "you don't know what they are are capable of, but you can ask them questions to find out."
    ),
    tools=[],
    allow_delegation=True,
    llm=llm
  )

  summarizer = Agent(
    role='Responder',
    goal='Respond to informative or summary requests. If you do not have a tool for the request, ask the developer to make a function for the request that conforms to the API spec',
    verbose=True,
    backstory=bs,
    tools=[],
    allow_delegation=True,
    llm=llm
  )

  #read current python file
  with open(__file__, 'r') as f:
    current_code = f.read()

  #convert to string
  current_code = str(current_code)

  dev_bs = f"""
  You are a python developer who is responsible for developing a function.
  Once you have generated the python, use the repl_tool to print the output.
  """
  bs = bs + yaml.dump(data)

  developer = Agent(
    role='Developer',
    goal='Develop the API',
    verbose=True,
    backstory=dev_bs,
    tools=[repl_tool],
    allow_delegation=True,
    llm=llm
  )

  dev_task = Task(
      description="""write necessary python function to respond for the missing functionality to the requested path""",
      expected_output="python function",
      agent=developer,
    tools=[repl_tool],
  )

  agents = []

  for path, verb in data['paths'].items():
    for v, content in verb.items():

      c = str(content)
      bs = "Path: " + path + " Verb: " + v + " Content: " + c
      p = Agent(
        role=f"Responder for {v} on {path}",
        goal='Respond to requests. If you do not have a tool for the request, ask the developer to make one',
        verbose=True,
        backstory= bs,
        #tools=[get_a_pet, get_all_pets],
        tools=[get_a_pet],
        allow_delegation=True,
        llm=llm,
        max_iter=2
      )
      
      agents.append(p)

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
    tasks=[Request_task, dev_task],
    process=Process.sequential,  # Optional: Sequential task execution is default
    full_output=True,
    step_callback=log_step,
  )

  # Starting the task execution process with enhanced feedback
  result = crew.kickoff()
  #print(result)
  #print(crew.agents)

if __name__ == "__main__":
  print("Welcome to the API Spec Chatbot! Ask me anything about the API Spec or event to call parts of the API:")
  while True:
      user_input = input("> ")
      process_input(user_input)
