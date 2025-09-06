import subprocess

def chat(messages, model="llama3"):
    """
    Call Ollama locally with a list of messages:
    [{"role":"system","content":"..."}, {"role":"user","content":"..."}]
    """
    # Convert messages into a simple chat prompt
    prompt = ""
    for m in messages:
        role = m["role"]
        content = m["content"]
        prompt += f"{role.upper()}: {content}\n"
    prompt += "ASSISTANT:"

    # Run Ollama
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True
    )

    # Decode the model's reply
    return result.stdout.decode().strip()