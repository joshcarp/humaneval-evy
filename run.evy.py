
import json
import os

# Create evy_files directory if it doesn't exist
if not os.path.exists("evy_files"):
    os.makedirs("evy_files")

# Open the evy2.humaneval.jsonl file
with open("evy2.humaneval.jsonl", "r") as f:
    for line in f:
        # Parse each JSON line
        data = json.loads(line)
        
        # Extract relevant fields
        task_id = data["task_id"]
        prompt = data["prompt"]
        canonical_solution = data["canonical_solution"]
        test = data["test"]
        
        # Stitch together the Evy code
        evy_code = f"{prompt}\n{canonical_solution}\n{test}"
        
        # Write Evy code to file
        filename = f"evy_files/{task_id}.evy"
        with open(filename, "w") as evy_file:
            evy_file.write(evy_code)
        
        # Run the Evy code and check for success
        exit_code = os.system(f"evy run {filename}")
        if exit_code == 0:
            print(f"Success: {task_id}")
        else:
            print(f"Failure: {task_id}")