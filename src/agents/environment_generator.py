from smolagents import (
    CodeAgent
)

class EnvironmentGeneratorAgent:
    def __init__(self, tools: list, model):
        self.agent = CodeAgent(tools=tools, model=model)

    def run(self, requirements: str):
        prompt = "Your goal is to take a description of a network and deploy the network using terraform. You have access to an AWS instance. Always remove any uneeded resources."
        prompt += f"\n--- Requirements ---\n{requirements}"
        self.agent.run(prompt)