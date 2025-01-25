from smolagents import (
    CodeAgent
)

class MoIAgent:
    def __init__(self, tools: list, model):
        self.agent = CodeAgent(tools=tools, model=model)

    def run(self):
        prompt += "Your goal is to determine if the provided computer network is interesting to an agent attempting to learn penetration testing. Respond with either 'This network is interesting' or 'This network is not interesting'"
        prompt += "--- Network description ---"
        self.agent.run(prompt)