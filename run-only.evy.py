
import json
import os
import re

# Create evy_files directory if it doesn't exist
if not os.path.exists("evy_files"):
    os.makedirs("evy_files")
if not os.path.exists("original_evy"):
    os.makedirs("original_evy")

functions = open("functions.evy", "r")
functions = functions.read()

# Open the evy2.humaneval.jsonl file
total = 0
failed = 0
passed_names = []

# read all files in manual/ directory and read contents to map:
manual_files_content = {}
for filename in os.listdir("manual/"):
    if filename.endswith(".evy"):
        with open(os.path.join("manual/", filename), "r") as file:
            filename = filename.replace("manual/", "")
            manual_files_content[filename] = file.read()


with open("evy2.humaneval.jsonl", "r") as f:
    for line in f:
        # Parse each JSON line
        data = json.loads(line)
        # Extract relevant fields
        task_id = data["task_id"]
        filename = f"{task_id.replace('/', '_')}.evy"
        prompt = data["prompt"]
        canonical_solution = data["canonical_solution"]
        test = data["test"]
        entry_point = data["entry_point"]
        
        # Stitch together the Evy code
        if filename in manual_files_content:
            evy_code = manual_files_content[filename]
            print(f"Using manual file for {task_id}")   
        else:
            evy_code = f"{prompt}\n    {canonical_solution.replace("\n", "\n    ")}\nend\n{test}\n\n{functions}\ncheck\nfinished\n"
        with open(f"original_evy/{filename}", "w") as original_evy_file:
            original_evy_file.write(evy_code)
        with open( f"evy_files/{filename}", "w") as evy_file:
            evy_file.write(evy_code)
        
        # Run the Evy code and check for success

        total += 1
        exit_code = os.system(f"evy run evy_files/{filename}")
        if exit_code == 0:
            passed_names.append(task_id)
            print(f"Success: {task_id}")
        else:
            failed += 1
            print(f"Failure: {task_id}")
            break   

print(f"Total: {total}, Failed: {failed}, Success: {total - failed}")
print(passed_names)
