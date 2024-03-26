import json
from operator import itemgetter


with open('evy.humaneval.jsonl', 'r') as file:
    data = [json.loads(line) for line in file]

sorted_data = sorted(data, key=lambda x: int(x['task_id'].strip('HumanEval/')))


seen = set()
for elem in sorted_data:
    seen.add(int(elem['task_id'].strip('HumanEval/')))

for i in range(0, len(sorted_data)+1):
    if i not in seen:
        print(f"unseen:", i)
with open('evy2.humaneval.jsonl', 'w') as file:
    for item in sorted_data:
        file.write(json.dumps(item) + '\n')

