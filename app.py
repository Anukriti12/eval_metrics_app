import streamlit as st
import subprocess
import os
import ast
from openai import AzureOpenAI

def generate_response(input_text):

    client = AzureOpenAI(
        azure_endpoint=azure_openai_endpoint, 
        api_key=azure_openai_api_key,  
        api_version="2024-02-01"
    )

    response = client.chat.completions.create(
        model="gpt-4o",  # Use your deployment name here
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input_text}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

azure_openai_api_key  = st.sidebar.text_input('Azure OpenAI API Key')
azure_openai_endpoint = st.sidebar.text_input('Azure OpenAI Endpoint') 

st.title('Evaluation Metrics for Text Simplification')

with st.form('my_form'):

    original = st.text_area('Original Text:', 'This is actor advocate Andy Arias.')
    reference = st.text_area('Reference Text:', 'This is Andy Arias, I am an actor and advocate.')
    prompt1 = '''
		You are an expert in accessible communication, tasked with transforming complex text into clear, accessible plain language for individuals with Intellectual and Developmental Disabilities (IDD) or those requiring simplified content. Retain all essential information and intent while prioritizing readability, comprehension, and inclusivity.

		Text simplification refers to rewriting or adapting text to make it easier to read and understand while keeping the same level of detail and precision. Make sure you focus on simplification and not summarization. The length of generated output text must be similar to that of input text.

		Stick to the provided input text and only simplify the language. Don't provide the answer or hallucinate or provide any irrelevant information, not mentioned in the input text. 

		Guidelines for Simplification:
		Vocabulary and Terminology:
		Replace uncommon, technical, or abstract words with simple, everyday language.
		Define unavoidable complex terms in plain language within parentheses upon first use (example: “cardiologist (heart doctor)”).
		Avoid idioms, metaphors, sarcasm, or culturally specific references.

		Sentence Structure:
		Use short sentences (10--15 words max). Break long sentences into 1–2 ideas each.
		Prefer active voice (example: “The doctor examined the patient” vs. “The patient was examined by the doctor”).
		Avoid nested clauses, passive voice, and ambiguous pronouns (example: “they,” “it”).

		Clarity and Flow:
		Organize content logically, using headings/subheadings to group related ideas.
		Use bullet points or numbered lists for steps, options, or key points.
		Ensure each paragraph focuses on one main idea.

		Tone and Engagement:
		Write in a neutral, conversational tone (avoid formal or academic language).
		Address the reader directly with “you” or “we” where appropriate.
		Use consistent terms for concepts (avoid synonyms that may confuse).

		Avoid Exclusionary Elements:
		Remove jargon, acronyms (unless defined), and expand abbreviations if needed (example: “ASAP” → “as soon as possible”).
		Eliminate metaphors, idioms, or implied meanings (example: “hit the books” → “study”).
		Avoid double negatives (example: “not uncommon” → “common”).

		Structural Support:
		Add clear headings to label sections (example: “How to Apply for Benefits”).
		Use formatting tools like bold for key terms or warnings.
		Chunk information into short paragraphs with line breaks for visual ease.

		Inclusivity Checks:
		Ensure content is free of bias, stereotypes, or assumptions about the reader.
		Use gender-neutral language (example: “they” instead of “he/she”).


		Output Requirements:
		Return only the simplified text, without markdown, emojis, or images.
		Preserve original context, facts, and intent. Do not omit critical details.
		Prioritize clarity over brevity; focus on simplification and not summarization. The length of generated output text should be same or similar to that of input text.
		Do not simplify already simple text.

		Example Transformation:
		Original: “Individuals experiencing adverse climatic conditions may necessitate relocation to mitigate health risks.”
		Simplified: “If weather conditions become dangerous, people might need to move to stay safe.”

		For the provided input text, apply the above guidelines rigorously. Ensure the output is accessible to readers with varied cognitive abilities, emphasizing clarity, simplicity, and logical structure. Verify that the simplified text aligns with plain language standards like WCAG and PlainLanguage.gov.
'''
    prompt = st.text_area('Existing Prompt:', prompt1)
    # text = st.text_area('Enter input text for simplification:', original)
    final_input = prompt + "\n\n" + original

    if not azure_openai_api_key or not azure_openai_endpoint:
        st.warning('Please enter your Azure OpenAI API key and endpoint!', icon='⚠')

    gpt_response_button = st.form_submit_button('GPT4 generated simplified text')
    response = ''
    if gpt_response_button and azure_openai_api_key and azure_openai_endpoint:
        st.session_state.response = generate_response(final_input)
    
    system = st.text_area('System Text:', st.session_state.get('response', '').replace('\n', ' '))

    # This is Andy Arias. He is an actor and he speaks up for people\'s rights.
    
    uploaded_original = st.file_uploader("Upload Original Text File:", type=['txt'], key="original")
    uploaded_reference = st.file_uploader("Upload Reference Text File:", type=['txt'], key="reference")
    uploaded_system = st.file_uploader("Upload System Text File:", type=['txt'], key="system")
    submitted = st.form_submit_button('Submit')


if submitted:
    # and 'response' in st.session_state:
    # response = st.session_state['response']
    # print(response)
    files_to_delete = ['original.txt', 'references.txt', 'simplified.txt']

    for file_name in files_to_delete:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Deleted {file_name}")
        else:
            print(f"{file_name} does not exist and could not be deleted.")

    for text_input, uploaded_file, filename in [
        (original, uploaded_original, 'original.txt'),
        (reference, uploaded_reference, 'references.txt'),
        (system, uploaded_system, 'simplified.txt')
    ]:
            if uploaded_file is not None:
                with open(filename, 'wb') as f:
                    f.write(uploaded_file.getvalue())
            else:
                with open(filename, 'w') as f:
                    single_line = ' '.join(text_input.strip().splitlines()).strip()
                    f.write(single_line + '\n')  # Ensures each is a single line

    # for text_input, uploaded_file, filename in [
    #     (original, uploaded_original, 'original.txt'),
    #     (reference, uploaded_reference, 'references.txt'),
    #     (system, uploaded_system, 'simplified.txt')
    # ]:
    #     print(uploaded_file)
    #     if uploaded_file is not None:
    #         print('yes....')

    #         with open(filename, 'wb') as f:
    #             f.write(uploaded_file.getvalue())
    #     else:
    #         with open(filename, 'w') as f:
    #             f.write(text_input)
    
    def count_lines(filename):
        with open(filename, 'r') as file:
            line_count = sum(1 for line in file)
        return line_count

    file1, file2, file3 = 'original.txt', 'references.txt', 'simplified.txt'

    n1,n2,n3 = str(count_lines(file1)), str(count_lines(file2)), str(count_lines(file3))
    # st.text_area("Length", value=n1, height=150)
    # st.text_area("Length2", value=n2, height=150)
    # st.text_area("Length3", value=n3, height=150)
    print(n1,n2,n3)
    if not (n1==n2 and n2 ==n3):
        st.error("Lengths of original, reference and simplified text should be equal !")



    if (n1==n2 and n2 ==n3):
        cmd = [
            'easse', 'evaluate', '-t', 'custom', '-m', 'bleu,sari,fkgl,sent_bleu,f1_token,sari_legacy,sari_by_operation', '-q',
            '--orig_sents_path', os.path.abspath('original.txt'),
            '--refs_sents_paths', os.path.abspath('references.txt'),
            '-i', os.path.abspath('simplified.txt')
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
    # easse evaluate -t custom -m 'bleu,sari,fkgl,sent_bleu,f1_token,sari_legacy,sari_by_operation' -q --orig_sents_path original.txt --refs_sents_paths references.txt -i simplified.txt
        
        if result.stdout:
            metrics = ast.literal_eval(result.stdout)
            formatted_metrics = "\n".join(f"{key.replace('_', ' ').title()}: {value}" for key, value in metrics.items())
            st.text_area("Evaluation Metrics:", value=formatted_metrics, height=200)
        if result.stderr:
            st.error("Error in Metrics Calculation:")
            st.text_area("Error Details:", value=result.stderr, height=150)

        # Generate and handle the report if original texts are uploaded
        if uploaded_original is not None or uploaded_reference is not None or uploaded_system is not None:
            cmd_report = [
                'easse', 'report', '-t', 'custom', '-m', 'bleu,sari,fkgl,sent_bleu,f1_token,sari_legacy,sari_by_operation,bertscore', 
                '--orig_sents_path', os.path.abspath('original.txt'),
                '--refs_sents_paths', os.path.abspath('references.txt'),
                '-i', os.path.abspath('simplified.txt'), 
                '-p', 'report.html'
            ]
            result_report = subprocess.run(cmd_report, capture_output=True, text=True)
            
            if result_report.stderr:
                st.error("Error in Generating Report:")
                st.text_area("Report Error Details:", value=result_report.stderr, height=150)
            
            if os.path.exists('report.html'):
                with open('report.html', 'rb') as file:
                    file_content = file.read()
                    btn = st.download_button(
                        label="Download Report",
                        data=file_content,
                        file_name="report.html",
                        mime="text/html"
                    )
    elif n1 > n3:
        print('hryyyyy')
        if os.path.exists('simplified.txt'):
            os.remove(file_name)
            print(f"Deleted {file_name}")
        else:
            print(f"{file_name} does not exist and could not be deleted.")

        with open('original.txt', 'r') as original:
            i = 0
            for line in original:
                print(i)
                print(prompt, line)
                input = prompt + "\n\n" + line
                gpt_response = (generate_response(input)).replace('\n', ' ')
                print(gpt_response)
                with open('simplified.txt', 'a') as simplified:
                    simplified.write(f"{gpt_response}\n")
                i=i+1

        with open('simplified.txt', 'rb') as file:
            file_content = file.read()
            btn = st.download_button(
                label="Download Simplified File",
                data=file_content,
                file_name="simplified.txt",
                mime="text/plain"
            )
    # elif os.path.exists('original.txt'):
    #     if os.path.exists('simplified.txt'):
    #         with open('simplified.txt', 'rb') as file:
    #             file_content = file.read()
    #             btn = st.download_button(
    #                 label="Download Simplified File",
    #                 data=file_content,
    #                 file_name="simplified.txt",
    #                 mime="text/txt"
    #             )
    # delete all if exists!
    # files_to_delete = ['original.txt', 'references.txt', 'simplified.txt']

    # for file_name in files_to_delete:
    #     if os.path.exists(file_name):
    #         os.remove(file_name)
    #         print(f"Deleted {file_name}")
    #     else:
    #         print(f"{file_name} does not exist and could not be deleted.")

# easse report -t custom -m 'bleu,sari,fkgl,sent_bleu,f1_token,sari_legacy,sari_by_operation,bertscore' --orig_sents_path original.txt --refs_sents_paths references.txt -i simplified.txt -p report.html
   
