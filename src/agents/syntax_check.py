from smolagents import CodeAgent
import subprocess

class TerraformValidatorAgent:
    def __init__(self, tools: list, model):
        self.agent = CodeAgent(tools=tools, model=model)

    def validate(self, tf_file: str) -> str:
        """
        Validates a Terraform file for syntax errors using `terraform validate`.
        
        Parameters:
        - tf_file (str): Path to the Terraform file.

        Returns:
        - str: Validation result as a string.
        """
        # Create the prompt for the agent
        prompt = f"""
        Your goal is to validate the provided Terraform file for syntax errors. 
        Use `terraform validate` to check the file. 
        Respond with 'Valid Terraform configuration' if there are no syntax errors 
        or 'Invalid Terraform configuration: <error_message>' if errors are found.

        --- Terraform file ---
        Path: {tf_file}
        """
        
        # Use Terraform CLI to validate
        try:
            # Initialize the Terraform directory
            subprocess.run(["terraform", "init"], cwd=tf_file.rsplit("/", 1)[0], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Run the `terraform validate` command
            result = subprocess.run(["terraform", "validate"], cwd=tf_file.rsplit("/", 1)[0], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # If no errors, return valid message
            return "Valid Terraform configuration"
        
        except subprocess.CalledProcessError as e:
            # Catch validation errors and return them
            error_message = e.stderr.decode("utf-8")
            return f"Invalid Terraform configuration: {error_message}"

        # Fallback to using the agent if needed (optional)
        self.agent.run(prompt)
