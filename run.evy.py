
import json
import os
import re

# Create evy_files directory if it doesn't exist
if not os.path.exists("evy_files"):
    os.makedirs("evy_files")

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
            
        evy_codelines = evy_code.split("\n")

        for i, line in enumerate(evy_codelines):
            # if "func check candidate:any" in line:
            #     evy_codelines[i] = "func check"
            # elif "candidate" in line:
            #     evy_codelines[i] = evy_codelines[i].replace("candidate", entry_point)
            # elif "abs " in line and "func" not in line:
                # evy_codelines[i] = evy_codelines[i].replace("abs ", "abs ( ")
                # evy_codelines[i] += (")")
            # elif re.search(r"range \w+", line):
            #         evy_codelines[i] = re.sub(r"range (\w+)", r"range (len \1)", evy_codelines[i])
            # elif "assert" in line and "==" in line:
            #     evy_codelines[i] = evy_codelines[i].replace("==", "")
            evy_codelines[i] = evy_codelines[i].replace("'", '"')
            


        evy_code = "\n".join(evy_codelines)

        replacements = [
            (r"1e-6", r"0.000001"),
            (r"assert truncateNumber (\d+\.\d+)  (\d+\.\d+)", r"assert \2 (truncateNumber \1)"),
            (r"assert abs \( \(truncateNumber (\d+\.\d+) - (\d+\.\d+)\) < 1e-6\)", r"assert true (((abs (truncateNumber (\1 - \2)))<0.000001))"),
            (r"assert abs \( \(truncateNumber (\d+\.\d+) - (\d+\.\d+)\) < 1e-6\)", r"assert true (((abs (truncateNumber (\1 - \2)))<0.000001))"),
            ("assert abs (mean_absolute_deviation [1.0 2.0 3.0] - 2.0 / 3.0) < 0.000001", "assert true (abs (mean_absolute_deviation [1.0 2.0 3.0] - 2.0 / 3.0) < 0.000001)"),
            ("assert abs (mean_absolute_deviation [1.0 2.0 3.0 4.0] - 1.0) < 0.000001", "assert true (abs (mean_absolute_deviation [1.0 2.0 3.0 4.0] - 1.0) < 0.000001)"), 
            ("assert abs (mean_absolute_deviation [1.0 2.0 3.0 4.0 5.0] - 6.0 / 5.0) < 0.000001", "assert true (abs (mean_absolute_deviation [1.0 2.0 3.0 4.0 5.0] - 6.0 / 5.0) < 0.000001)"),
            ("func check candidate:any", "func check"),
            ("candidate", entry_point),
            (r"range (\w+)", r"range (len \1)"),
            (r"assert (.*) ==", r"assert \1"),
            (r"abs (.*)", r"abs ( \1 )"),
            (r"assert truncateNumber 3.5 0.5", r"assert 0.5 (truncateNumber 3.5)"),
            ("assert abs ( (truncateNumber 1.33 - 0.33) < 0.000001 )", "assert true (abs ( (truncateNumber 1.33 - 0.33) < 0.000001 ))"),
            ("assert abs ( (truncateNumber 123.456 - 0.456) < 0.000001 )", "assert true (abs ( (truncateNumber 123.456 - 0.456) < 0.000001 ))"),

        ]
        # evy_code
        
        for pattern, replacement in replacements:
            evy_code = re.sub(pattern, replacement, evy_code)
        
        # Write Evy code to file
        
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
