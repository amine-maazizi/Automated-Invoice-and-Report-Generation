import subprocess

def create_scheduled_task(script_path, task_name="SendEmailsTask", time="09:00"):
    """
    Create a scheduled task to run the Python script using Windows Task Scheduler.

    Parameters:
    - script_path (str): The full path to the Python script.
    - task_name (str): The name of the scheduled task.
    - time (str): The time in HH:MM format when the task should run daily.
    """
    try:
        # Define the command to create a scheduled task
        command = [
            "schtasks", "/create", "/tn", task_name, "/tr", f'python "{script_path}"', "/sc", "daily", "/st", time, "/rl", "HIGHEST"
        ]

        # Run the command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(f"Scheduled task '{task_name}' created successfully to run daily at {time}.")
        else:
            print(f"Failed to create scheduled task: {result.stderr}")

    except Exception as e:
        print(f"An error occurred: {e}")


def delete_scheduled_task(task_name="SendEmailsTask"):
    """
    Delete the scheduled task from Windows Task Scheduler.

    Parameters:
    - task_name (str): The name of the scheduled task to delete.
    """
    try:
        # Define the command to delete the scheduled task
        command = ["schtasks", "/delete", "/tn", task_name, "/f"]

        # Run the command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(f"Scheduled task '{task_name}' deleted successfully.")
        else:
            print(f"Failed to delete scheduled task: {result.stderr}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Example usage
    script_path = "D:\\Portfolio\\Automated Invoice and Report Generation System\\main.py"  # Replace with your script path
    create_scheduled_task(script_path, time="22:30")
