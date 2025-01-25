from smolagents import (
    CodeAgent,
    tool
)
import os

@tool
def WriteFileTool(file_name: str, content: str) -> bool:
    """
    Writes content to a file in the ./templates directory.
    Only allows files within this directory for security.

    Args:
        file_name: Name of the file to write to (relative to ./templates).
        content: The content to write to the file.
    """
    templates_dir = os.path.abspath("./templates")
    try:
        # Ensure the directory exists
        os.makedirs(templates_dir, exist_ok=True)

        # Resolve the full path and check it's within the templates directory
        full_path = os.path.abspath(os.path.join(templates_dir, file_name))
        if not full_path.startswith(templates_dir):
            raise ValueError("Attempt to write outside the ./templates directory is not allowed.")

        # Write the content to the file
        with open(full_path, "w") as file:
            file.write(content)
        return "Could not write to file"

    except (OSError, ValueError, Exception) as e:
        return f"Error writing to file: {e}"

class EnvironmentGeneratorAgent:
    def __init__(self, tools: list, model):
        tools.append(WriteFileTool)
        self.agent = CodeAgent(tools=tools, model=model)

    def run(self, requirements: str):
        prompt = "Your goal is to take a description of a network and generate the terraform to deploy the network. You have access to an AWS instance. Always remove any uneeded resources."
        prompt += f"\n--- Requirements ---\n{requirements}"
        return self.agent.run(prompt)