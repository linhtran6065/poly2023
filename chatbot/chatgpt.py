import openai

openai.api_key = "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"

messages = []
system_msg = "You are a psychologist. Your task is to chat with users. Maximum 5 answers. If the conversation get too long, tell them you can help they reach to master users or professionals"
messages.append({"role": "system", "content": system_msg})

print("Your new assistant is ready!")
while input != "quit()":
    message = input()
    messages.append({"role": "user", "content": message})  # input cua user
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages)
    reply = response["choices"][0]["message"]["content"]  # reply of chatgpt
    messages.append({"role": "assistant", "content": reply})
    print("\n" + reply + "\n")


data = [
    {
        "number": 1,
        "question": "I have a kind word for everyone",
        "options": ["1", "2", "3", "4", "5"]
    },
    {
        "number": 2,
        "question": "I am always prepared",
        "options": ["1", "2", "3", "4", "5"]
    },
    {
        "number": 3,
        "question": "I feel comfortable around people",
        "options": ["1", "2", "3", "4", "5"]
    },
    {
        "number": 4,
        "question": "I often feel blue",
        "options": ["1", "2", "3", "4", "5"]
    },
    {
        "number": 5,
        "question": "I am very good at identifying the emotions I am feeling",
        "options": ["1", "2", "3", "4", "5"]
    },
    {
        "number": 6,
        "question": "I believe in the importance of art",
        "options": ["1", "2", "3", "4", "5"]
    },
    {
        "number": 7,
        "question": "I am the life of the party",
        "options": ["1", "2", "3", "4", "5"]
    },
    {
        "number": 8,
        "question": "I am very good at reading body language",
        "options": ["1", "2", "3", "4", "5"]
    },
    {
        "number": 9,
        "question": "There are many things that I do not like about myself",
        "options": ["1", "2", "3", "4", "5"]
    },
    {
        "number": 10,
        "question": "My moods change easily",
        "options": ["1", "2", "3", "4", "5"]
    }
]
