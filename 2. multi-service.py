from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI


llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    #model="gemini-1.5-pro",
    convert_system_message_to_human=True,
    verbose=False,
    streaming=False,
    temperature=0.2,
)


requester = Agent(
  role='Requester',
  goal='Request responses',
  verbose=False,
  backstory=(
    "You are an expiremental AI acting as one end of an API."
    "As such, you should be able to request information from the other end of the API as quickly and efficiently as possible."
  ),
  tools=[],
  allow_delegation=True,
  llm=llm
)

ping_service_responder = Agent(
  role='Ping Service',
  goal='Respond to a requests for Ping',
  verbose=False,
  backstory=(
    "You are an expiremental AI acting as one end of an API."
    "As such, you should be able to resopond with information from the other end of the API as quickly and efficiently as possible."
    "Respond with just the body of the response, do not include an headers, status codes, etc."
    "You only support the following API calls:"
    "Route: /ping"
    "Verbs: GET"
    "Response: pong"
    "Any of requests, respond with 'Not Found'"
  ),
  tools=[],
  allow_delegation=True,
  llm=llm
)

hello_world_service = Agent(
  role='Hello World Service',
  goal='Respond to a requests for Hello World',
  verbose=False,
  backstory=(
    "You are an expiremental AI acting as one end of an API."
    "As such, you should be able to resopond with information from the other end of the API as quickly and efficiently as possible."
    "Respond with just the body of the response, do not include an headers, status codes, etc."
    "You only support the following API calls:"
    "Route: /hello"
    "Verbs: GET"
    "Response: Hello World!"
    "Any of requests, respond with 'Not Found'"
  ),
  tools=[],
  allow_delegation=True,
  llm=llm
)


#ask for user input from command line
verb = input("Enter the verb: ")
route = input("Enter the route: ")


Request_task = Task(
  description=(
    "Request: {verb} {route}"
  ),
  expected_output="a response",
  tools=[],
  agent=requester,
)

crew = Crew(
  agents=[requester, ping_service_responder, hello_world_service],
  tasks=[Request_task],
  process=Process.sequential  # Optional: Sequential task execution is default
)

# Starting the task execution process with enhanced feedback
result = crew.kickoff(inputs={'verb': verb, 'route': route})
print(result)