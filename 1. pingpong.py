import os
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
  allow_delegation=False,
  llm=llm
)

responder = Agent(
  role='Responder',
  goal='Respond to a requests',
  verbose=False,
  backstory=(
    "You are an expiremental AI acting as one end of an API."
    "As such, you should be able to resopond with information from the other end of the API as quickly and efficiently as possible."
    "Respond with just the body of the response, do not include an headers, status codes, etc."
  ),
  tools=[],
  allow_delegation=True,
  llm=llm
)

# Research task
Request_task = Task(
  description=(
    "Request: {verb} {route}"
  ),
  expected_output="a response",
  tools=[],
  agent=requester,
)

# Writing task with language model configuration
response_task = Task(
  description=(
    "You only support the following API calls:"
    "Route: /ping"
    "Verbs: GET"
    "Response: pong"
    "Any of requests, respond with 'Not Found'"
  ),
  expected_output="pong",
  tools=[],
  agent=responder,
  async_execution=False,
)

# Forming the tech-focused crew with enhanced configurations
crew = Crew(
  agents=[requester, responder],
  tasks=[Request_task, response_task],
  process=Process.sequential  # Optional: Sequential task execution is default
)

# Starting the task execution process with enhanced feedback
result = crew.kickoff(inputs={'verb': "GET", 'route': '/ping'})
print(result)