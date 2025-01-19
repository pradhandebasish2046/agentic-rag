# chat-bot

![image](https://github.com/user-attachments/assets/bb38ac55-3940-4b74-865c-d094ffc5aafc)


# Scope of Improvement
1. Prompt Engineering 
2. Better context preserve
3. Latency
4. Handling source links properly



# How to run?
### STEPS:

Clone the repository

```bash
https://github.com/pradhandebasish2046/agentic-rag.git
```
### STEP 01- Update the .env file by adding the groq and brave api key
### STEP 02
Run below commands
```bash
docker build -t agent .
docker run -p 8000:8000 agent
```
### STEP 03
Go to http://localhost:8000/chainlit and upload pdf file or files and ask the question
