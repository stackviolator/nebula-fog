from smolagents import (
    CodeAgent,
    tool
)
import os
from python_terraform import Terraform, IsFlagged

def DeployTerraformToAws(terraform_dir: str, variables=None):
    """
    Deploy a Terraform script to AWS using the Terraform SDK.

    Args:
        terraform_dir (str): Path to the Terraform configuration directory.
        variables (dict): A dictionary of Terraform variables to be passed during the apply stage.
    """
    try:
        # Initialize Terraform
        tf = Terraform(working_dir=terraform_dir)
        print(f"Initializing Terraform in directory: {terraform_dir}")
        return_code, stdout, stderr = tf.init()
        if return_code != 0:
            return (f"Terraform initialization failed: {stderr}")

        # Apply the Terraform script
        print("Applying Terraform configuration...")
        apply_params = {"auto-approve": IsFlagged}
        if variables:
            apply_params.update(variables)
        
        return_code, stdout, stderr = tf.apply(input=False, **apply_params)
        if return_code != 0:
            return(f"Terraform apply failed: {stderr}")
        
        # Fetch outputs
        print("Fetching Terraform outputs...")
        return_code, outputs, stderr = tf.output(full_value=True)
        if return_code != 0:
            return (f"Failed to fetch Terraform outputs: {stderr}")
        
        print("Terraform deployment completed successfully.")
        return outputs
    
    except Exception as e:
        print(f"Error during Terraform deployment: {e}")
        raise

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