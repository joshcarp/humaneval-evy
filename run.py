from human_eval.data import write_jsonl, read_problems
from human_eval.execution import check_correctness
from multiprocessing import freeze_support
import anthropic
from openai import OpenAI
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

client = OpenAI()


problems = read_problems()

convert_prompt = ""
with open("convert.prompt", "r") as file:
    convert_prompt = file.read()

evy_file = open("evy.humaneval.jsonl", "a")
evy_file_lock = Lock()

def convert_to_evy(python_code):
    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
    )
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0,
        system=convert_prompt,
             messages=[
                    {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": python_code
                    }
                ]
            }
             ]
    )
    try:
        msg = message.content.pop().text
    except:
        msg = "{}"
    return msg

import json

def generate_one_completion(prompt):
    evy = convert_to_evy_openai(prompt["prompt"] + prompt["canonical_solution"] + "\n\n" + prompt["test"])
    if evy != "{}":
        evy_dict = json.loads(evy)
        evy = json.dumps({
            "task_id": prompt["task_id"],
            "prompt": evy_dict["function_signature"],
            "canonical_solution": evy_dict["solution"],
            "test": evy_dict["test"],
            "entry_point": evy_dict["entry_point"]
        })
    with evy_file_lock:
        evy_file.write(evy+"\n")
    print(f"completed {prompt["task_id"]} with length of {len(evy)}")
    return evy

def convert_to_evy_openai(python_code):
    response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
    {
    "role": "system",
    "content": convert_prompt,
    },
    {
    "role": "user",
    "content": python_code,
    },
    ],
    temperature=0,
    max_tokens=1002,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    
    content = response.choices[0].message.content
    # strip the leading ```json and trailing ``` with string operations
    content = content.lstrip('```json').rstrip('```')
    return content

if __name__ == '__main__':
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(generate_one_completion, problems[task_id]): task_id for task_id in problems}
        for future in as_completed(futures):
            task_id = futures[future]
            try:
                future.result()
            except Exception as exc:
                print(f'Task {task_id} generated an exception: {exc}')

# if __name__ == '__main__':
#     num_samples_per_task = 200
#     samples = [
#         dict(task_id=task_id, completion=generate_one_completion(problems[task_id]))
#         for task_id in problems
#         for _ in range(num_samples_per_task)
#     ]
#     write_jsonl("samples.jsonl", samples)
#     for sample in samples:
#         task_id = sample["task_id"]
#         completion = sample["completion"]
#         problem = problems[task_id]
#         result = check_correctness(problem, completion, timeout=3.0)
#         print(result)




