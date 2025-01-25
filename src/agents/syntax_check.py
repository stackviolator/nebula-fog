import os
import subprocess

from smolagents import CodeAgent

class TerraformValidatorAgent:
    """
    Iteratively validates and attempts to fix a Terraform configuration
    until syntax errors are resolved (or a max number of attempts is reached).
    """
    def __init__(self, tools: list, model, max_attempts: int = 5):
        self.agent = CodeAgent(tools=tools, model=model)
        self.max_attempts = max_attempts

    def validate_and_fix(self, tf_path: str) -> str:
        """
        Continuously validate Terraform file or directory using 'terraform validate'.
        If there's a syntax error, ask the CodeAgent for fixes and rewrite the file,
        repeating until success or until `max_attempts` is exhausted.

        Parameters:
        - tf_path (str): Path to the Terraform file or directory.

        Returns:
        - str: Final validation outcome as a string:
          'Valid Terraform configuration' if fixed successfully, otherwise
          'Could not fix Terraform configuration after N attempts: <last_error_message>'
        """
        # Determine the directory from tf_path
        if os.path.isdir(tf_path):
            dir_path = tf_path
            tf_file_content = None  # Not strictly required if multiple TF files
        else:
            dir_path = os.path.dirname(tf_path)
            # Read the content of the TF file for potential rewriting
            with open(tf_path, 'r', encoding='utf-8') as f:
                tf_file_content = f.read()
        
        attempt = 0
        last_error_message = ""

        while attempt < self.max_attempts:
            attempt += 1

            print(f"--- Attempt {attempt} ---")
            
            # Initialize and validate
            init_result, init_error = self._run_terraform_init(dir_path)
            if init_error:
                # If `terraform init` fails, no reason to continue
                last_error_message = init_error
                break

            validation_result, validation_error = self._run_terraform_validate(dir_path)
            if not validation_error:
                # If no error, we’re done
                return "Valid Terraform configuration"
            
            # If there's an error, store it, then try to fix the Terraform code
            last_error_message = validation_error
            print(f"Validation error encountered:\n{validation_error}")

            # If we have a single TF file, attempt to fix its content
            if tf_file_content is not None:
                tf_file_content = self._attempt_fix_with_agent(tf_file_content, validation_error)
                # Overwrite the file with updated content
                with open(tf_path, 'w', encoding='utf-8') as f:
                    f.write(tf_file_content)
            else:
                # If multiple TF files, or a directory, the fix approach may differ
                # For example, read all .tf files and feed them to the agent
                # (Implementation is left to you)
                break

        return (f"Could not fix Terraform configuration after "
                f"{self.max_attempts} attempts: {last_error_message}")

    def _run_terraform_init(self, dir_path: str) -> tuple:
        """
        Runs `terraform init` in the specified directory and returns (stdout, stderr).
        """
        try:
            completed_proc = subprocess.run(
                ["terraform", "init", "-input=false"],
                cwd=dir_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return (completed_proc.stdout.decode("utf-8").strip(), None)
        except subprocess.CalledProcessError as e:
            return (None, e.stderr.decode("utf-8").strip())

    def _run_terraform_validate(self, dir_path: str) -> tuple:
        """
        Runs `terraform validate` in the specified directory and returns (stdout, stderr).
        If stderr is empty, validation succeeded.
        """
        try:
            completed_proc = subprocess.run(
                ["terraform", "validate"],
                cwd=dir_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return (completed_proc.stdout.decode("utf-8").strip(), None)
        except subprocess.CalledProcessError as e:
            return (None, e.stderr.decode("utf-8").strip())

    def _attempt_fix_with_agent(self, tf_content: str, error_message: str) -> str:
        """
        Calls a language model (through CodeAgent) to fix the Terraform code,
        given the current content and the validation error message.

        Returns the updated Terraform code as a string.
        """
        prompt = f"""
        I have the following Terraform code:

        ```
        {tf_content}
        ```

        The validation error is:
        {error_message}

        Please fix the syntax errors or any misconfigurations in the Terraform code above.
        Return the corrected Terraform code only, no extra commentary.
        """
        improved_code = self.agent.run(prompt)
        return improved_code or tf_content
