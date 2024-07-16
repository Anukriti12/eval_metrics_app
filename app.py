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
        model="gpt-4",  # Use your deployment name here
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

    prompt = st.text_area('Existing Prompt:', 'Simplify the text following the general guidelines at plainlanguage.gov. Some of these guidelines are: Break up wordy sentences into multiple sentences. Present information at the 8th-grade level or below. Add structure such as useful headings, or lists to highlight steps or requirements, unless it will make the text much longer. Start each paragraph with a topic sentence. Consider who the reader is and speak directly to them. Avoid double negatives. Keep paragraphs short. Use examples to illustrate the text. Be concise.')
    # text = st.text_area('Enter input text for simplification:', original)
    final_input = prompt + original

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

if submitted and 'response' in st.session_state:
    response = st.session_state['response']
    # Handle file uploads or text area inputs
    print(response)
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
                f.write(text_input)
    
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



    if os.path.exists('references.txt') and os.path.exists('original.txt') and os.path.exists('simplified.txt'):
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
    elif not os.path.exists('simplified.txt'):
        with open('original.txt', 'r') as original, open('simplified.txt', 'w') as simplified:
            for line in original:
                gpt_response = generate_response(line)
                simplified.write(f"{gpt_response}")
    elif os.path.exists('original.txt'):
        if os.path.exists('simplified.txt'):
            with open('simplified.txt', 'rb') as file:
                file_content = file.read()
                btn = st.download_button(
                    label="Download Simplified File",
                    data=file_content,
                    file_name="simplified.txt",
                    mime="text/txt"
                )
    # delete all if exists!
    files_to_delete = ['original.txt', 'references.txt', 'simplified.txt']

    for file_name in files_to_delete:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Deleted {file_name}")
        else:
            print(f"{file_name} does not exist and could not be deleted.")
# easse report -t custom -m 'bleu,sari,fkgl,sent_bleu,f1_token,sari_legacy,sari_by_operation,bertscore' --orig_sents_path original.txt --refs_sents_paths references.txt -i simplified.txt -p report.html
   
