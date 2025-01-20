# chat-bot


![image]

https://github.com/user-attachments/assets/9e6a6ba8-6ccd-4738-af87-4de863c43818

(https://github.com/user-attachments/assets/f35c31b8-39a3-4c28-a71d-d77de5850aaf)



# Scope of Improvement
1. Prompt Engineering 
2. Better context preserve
3. Latency
4. Handling source links properly
5. Better chunking appproach



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
