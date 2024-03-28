import csv
import os

# Directory containing the code files
code_directory = 'manual'

# Output CSV file
output_file = 'code_files.csv'

# Get a list of code files in the directory
code_files = [file for file in os.listdir(code_directory) if file.endswith('.evy')]

# Open the output CSV file in write mode
with open(output_file, 'w', newline='') as csvfile:
    # Create a CSV writer object with the appropriate dialect
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Write the header row
    csv_writer.writerow(['Code'])

    # Iterate over each code file
    for code_file in code_files:
        file_path = os.path.join(code_directory, code_file)

        # Read the code file
        with open(file_path, 'r') as file:
            code_content = file.read()

        # Write the code file details to the CSV file
        csv_writer.writerow([code_content])