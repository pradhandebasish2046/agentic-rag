import chainlit as cl
from src.services.final_pipeline import generate_response
from io import BytesIO
import fitz
import time
from src.services.chunking.custom_chunking import final_chunking_pipeline

def process_file1(pdf_file):
    # time.sleep(3)  # Simulate processing delay
    doc = fitz.open(pdf_file.path)
    total = ""
    for page in doc:
        text = page.get_text("text", sort=True)
        total+=text
    return len(total)

def process_file2(total):
    time.sleep(1)
    return total//100

@cl.on_chat_start
async def start():
    # Wait for the user to upload files
    files = await cl.AskFileMessage(
        content="Please upload one or more PDF files to begin!",
        accept=["application/pdf"],
        max_size_mb=20,
        max_files=10
    ).send()

    # Initialize a list to hold lengths of text from the first page of each PDF
    lengths = []
    final_summary = []

    # Process each file as soon as it's uploaded
    for pdf_file in files:
        # Notify the user that processing has started for the file
        start_msg = cl.Message(content=f"Processing `{pdf_file.name}`...")
        await start_msg.send()

        # Process the file (this part is where the actual file processing happens)
        documents, metadata, corpus_json  = final_chunking_pipeline(pdf_file.path)

        # Notify the user that processing has ended for the file
        end_msg = cl.Message(content=f"Processing complete for 1`{pdf_file.name}`. It contains {len(documents),len(metadata)} chunks")
        await end_msg.send()
        # n2 = process_file2(n)
        # end_msg = cl.Message(content=f"Processing complete for 2`{pdf_file.name}`. It contains {n2} characters on the first page.")
        # await end_msg.send()

        # Store the result for the final summary message
        # lengths.append(n)
        # final_summary.append(f"{pdf_file.name}: {n} characters on the first page.")

    # response_content = "Summary of uploaded files:\n" + "\n".join(final_summary) 
    req_file = files[0]
    req_el = [cl.Pdf(name=req_file.name, display="side", path=req_file.path, page=2)]
    final_output = f"the answer is found and it present in {req_file.name}"
    await cl.Message(content=final_output, elements=req_el).send()

    # for i, pdf_file in enumerate(files): 
         
        # await cl.Message(content=f"Source link of {pdf_file.name}: {{source {i+1} with page no 2}}", elements=elements).send()
