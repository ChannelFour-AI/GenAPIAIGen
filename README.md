# Getting Started

I recommend having the `devcontainers` extension installed. If so, you can build an image based on the config and be up and running no time.
OSX: `CMD+SHIFT+P` > dev containers: rebuild container.

For all scripts exporting the Google ENV `GOOGLE_API_KEY` (API key from ai.google.dev) is required. 

## Running script 1

Simple python script to perform a Get `/ping` and expect a `pong` response.

`python 1.\ pingpong.py`

## Running script 2

Python script showing using an agent for 2 different "services"

`python 2.\ multi-service.py`

Enter `get` and `hello` or `get` and `ping`

## Running script 3

Python script showing N agents working on behalf of an OpenAPI (Swagger) spec:

`python 3.\ openapi.py`

You can ask it about the API (i.e `what can I do?`) or request actual data (i.e. `get all pets`). This supports getting a single pet with an ID or getting a listing of all pets.

## Running script 4

If VertexAI via Google Cloud, set `gcloud auth application-default login` on your actual machine and all should be good since we pass these settings up from the host. You may need to restart your dev container if you run this after starting it.

This is not working fully. The goal was to generate a fuction / tool for the routes which we don't have a fuction or tool for. In an ideal state, we could pass a OpenAPI specification in, and let all the functions get created dynimically.