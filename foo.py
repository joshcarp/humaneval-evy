from human_eval.execution import check_correctness
from human_eval.data import read_problems
from human_eval.data import write_jsonl, read_problems

problems = read_problems()

def generate_one_completion(prompt):
    return prompt
num_samples_per_task = 200
samples = [
    dict(task_id=task_id, completion=generate_one_completion(problems[task_id]["prompt"]))
    for task_id in problems
    for _ in range(num_samples_per_task)
]
write_jsonl("samples.jsonl", samples)

