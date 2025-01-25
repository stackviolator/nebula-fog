from smolagents import (
    CodeAgent,
    ManagedAgent,
)

class TaskGeneratorAgent:
    def __init__(self, tools: list, model):
        self.agent = CodeAgent(tools=tools, model=model)
        self.task_archive = ['None']
    
    def run(self, requirements: str) -> str:
        """
        Prompt is appneded with requirements (make it a little more difficult)
        TODO: fiddle with requirements
        TODO: add to archive
        """
        prompt = "Your goal is to generate the requirements (in english) to an active directory network. Your network should be slightly more difficult than the previous examples. If the task archive is none, generate a simple Active directory netowrk with one DC and one workstation where the admin password is 'password'\n"
        prompt += f"--- Task Archive ---\n{self.task_archive}"
        prompt += "\n"
        prompt += requirements
        temp = self.agent.run(prompt)
        print("\n\n\n\n")
        print(temp)