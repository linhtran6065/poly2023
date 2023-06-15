import openai

openai.api_key = "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"

messages = []
system_msg = "You are a psychologist. Your task is to chat with users. Maximum 5 answers. If the conversation get too long, tell them you can help they reach to master users or professionals"
messages.append({"role": "system", "content": system_msg})

print("Your new assistant is ready!")
while input != "quit()":
    message = input()
    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages)
    reply = response["choices"][0]["message"]["content"]  # reply of chatgpt
    messages.append({"role": "assistant", "content": reply})
    print("\n" + reply + "\n")
