from smolagents import (
    CodeAgent,
    ManagedAgent,
)

class TaskGeneratorAgent:
    def __init__(self, tools: list, model):
        self.agent = CodeAgent(tools=tools, model=model)
        self.task_archive = ['None']

    def add_to_archive(self, task: str):
        # If task archive is none, overwrite it
        if self.task_archive[0] == 'None':
            self.task_archive[0] = task
        else:
            self.task_archive.append(task)

    def run(self, requirements: str) -> str:
        """
        Prompt is appneded with requirements (make it a little more difficult)
        TODO: fiddle with requirements
        """
        prompt = "Your goal is to generate the requirements (in english) to an active directory network. Your network should be slightly more difficult than the previous examples. If the task archive is none, generate a simple Active directory netowrk with one DC and one workstation where the admin password is 'password'\n"
        prompt += f"--- Task Archive ---\n{self.task_archive}"
        prompt += "\n"
        prompt += requirements
        task = self.agent.run(prompt)
        self.add_to_archive(task)
        return task