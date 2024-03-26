
import json
import os
import re

# Create evy_files directory if it doesn't exist
if not os.path.exists("python_files"):
    os.makedirs("python_files")

# functions = open("functions.evy", "r")
# functions = functions.read()

# Open the evy2.humaneval.jsonl file
total = 0
failed = 0
passed_names = []
with open("data/Humaneval.jsonl", "r") as f:
    for line in f:
        # Parse each JSON line
        data = json.loads(line)
        
        # Extract relevant fields
        task_id = data["task_id"]
        prompt = data["prompt"]
        canonical_solution = data["canonical_solution"]
        test = data["test"]
        entry_point = data["entry_point"]
        
        # Stitch together the Evy code
        evy_code = f"{prompt}\n{canonical_solution}\n{test}\ncheck({entry_point})"
        evy_codelines = evy_code.split("\n")

        # for i, line in enumerate(evy_codelines):
        #     if "func check candidate:any" in line:
        #         evy_codelines[i] = "func check"
        #     elif "candidate" in line:
        #         evy_codelines[i] = evy_codelines[i].replace("candidate", entry_point)
        #     elif "abs" in line and "func abs" not in line:
        #         evy_codelines[i] = evy_codelines[i].replace("abs", "abs (")
        #         evy_codelines[i] += (")")
        #     elif re.search(r"range \w+", line):
        #             evy_codelines[i] = re.sub(r"range (\w+)", r"range (len \1)", evy_codelines[i])
        #     elif "assert" in line and "==" in line:
        #         evy_codelines[i] = evy_codelines[i].replace("==", "")
        #     evy_codelines[i] = evy_codelines[i].replace("'", '"')
            

        
        evy_code = "\n".join(evy_codelines)
        # evy_code
        
        # Write Evy code to file
        filename = f"python_files/{task_id.replace('/', '_')}.py"
        with open(filename, "w") as evy_file:
            evy_file.write(evy_code)
        
        # Run the Evy code and check for success

        total += 1
        exit_code = os.system(f"python {filename}")
        if exit_code == 0:
            passed_names.append(task_id)
            print(f"Success: {task_id}")
        else:
            failed += 1
            print(f"Failure: {task_id}")
            break

print(f"Total: {total}, Failed: {failed}, Success: {total - failed}")
print(passed_names)
