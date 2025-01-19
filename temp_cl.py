import chainlit as cl
from io import BytesIO
import fitz
import time

def process_file1(pdf_file):
    # Simulate processing delay
    doc = fitz.open(pdf_file.path)
    total = ""
    for page in doc:
        text = page.get_text("text", sort=True)
        total += text
    return len(total)

def process_file2(total):
    return total // 100

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

    # # Process each file as soon as it's uploaded
    # for pdf_file in files:
    #     # Notify the user that processing has started for the file
    #     start_msg = cl.Message(content=f"Processing {pdf_file.name}...")
    #     await start_msg.send()

    #     # Process the file (this part is where the actual file processing happens)
    #     n = process_file1(pdf_file)

    #     # Notify the user that processing has ended for the file
    #     end_msg = cl.Message(content=f"Processing complete for 1`{pdf_file.name}`. It contains {n} characters on the first page.")
    #     await end_msg.send()
    #     n2 = process_file2(n)
    #     end_msg = cl.Message(content=f"Processing complete for 2`{pdf_file.name}`. It contains {n2} characters on the first page.")
    #     await end_msg.send()

        # Store the result for the final summary message
        # lengths.append(n)
        # final_summary.append(f"Source link of {pdf_file.name}: {{source with page no 2}}")

    # After processing all files, send the final summary
    # response_content = "Summary of uploaded files:\n" + "\n".join(final_summary)
    # await cl.Message(content=response_content).send()
    req_pdf_file = files[1]
    print(req_pdf_file)
    print(req_pdf_file.name)
    print(req_pdf_file.path)
    elements = [cl.Pdf(name=req_pdf_file.name, display="side", path=req_pdf_file.path, page=2)]
    await cl.Message(content=f"Source link of {req_pdf_file.name}: with page no 2", elements=elements).send()

    # # Send individual source links with page number 2
    # for i, pdf_file in enumerate(files):
    #     elements = [cl.Pdf(name=pdf_file.name, display="side", path=pdf_file.path, page=2)]
