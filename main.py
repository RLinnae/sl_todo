#Import libraries the project is dependent on
import asyncio
import streamlit as st 
from langchain.prompts import PromptTemplate
from langchain import LLMChain
from langchain.llms import OpenAIChat
import ruamel.yaml
from ruamel.yaml import YAML
import pandas as pd
import os
import pickle



# Set the Streamlit page configuration, including the layout and page title/icon
st.set_page_config(layout="wide", page_icon="💡", page_title="Breakit")

# Display the header for the application using HTML markdown
st.markdown(
    "<h1 style='text-align: center;'>Breakit 💡</h1>",
    unsafe_allow_html=True)

# Allow the user to enter their OpenAI API key
user_api_key = st.sidebar.text_input(
    label="#### Your OpenAI API key 👇",
    placeholder="Paste your openAI API key, sk-",
    type="password")

async def main():
    #create placeholder empty tables
    tab1_progress = st.empty()
    tab1_main = st.empty()
    
   
    # Check if the user has entered an OpenAI API key
    if user_api_key == "":
        
        # Display a message asking the user to enter their API key
        st.markdown(
            "<div style='text-align: center;'><h4>👈 Enter your OpenAI API key to start </h4></div>",
            unsafe_allow_html=True)
        st.write("This is a demo of a method sending and retrieving structured data from a LLM to be used in downstream functions, API calls, additional LLM refinement, or database storage procedures.")
        
    else:
        # Set the OpenAI API key as an environment variable
        os.environ["OPENAI_API_KEY"] = user_api_key
        
        # Allow the user to enter their name char to do item
        advisee_name = st.sidebar.text_input(
            label="Your Name",
            placeholder="Bobby boy",
            type="default")
        
        character = st.sidebar.text_input(
            label="The mentor you'd like to help with your task",
            placeholder="Barak Obama, or A lazy robot",
            type="default")
        
        main_task = st.sidebar.text_input(
            label="A task from your to-do list",
            placeholder="Clean the kitchen",
            type="default")
        
        subtask_count = st.sidebar.slider('Numer of Subtasks:', 1, 5, 10)
      
        # If the user has entered their details, display it (debug)
        if advisee_name != "" and character != "" and main_task != "":
            st.sidebar.info("Ready to create subtasks!")
            
        # If the user has not entered details, display a message asking them to do so
        else :
            st.sidebar.info(
            "👆 enter your details to get started"
            )
    
    
        #if advisee_name is not None and character is not None and main_task is not None :
        if st.sidebar.button('Create Subtasks') and advisee_name != "" and character != "" and main_task != "":
            try :
                #async def llm_chain_result(query):   
                    #set up the prompt template
                    template = """You are {character}, advising {advisee_name} on how to complete a task. For <how> use vivid and descriptive language and maintain the vocabulary and voice of {character}. 
                    ' ' ' 
                    main_task: {main_task}
                    number_of_subtasks: {subtask_count}
                    ' ' '
                    respond in the following YAML structure:
                    ' ' '   
                    - main_task:
                      subtasks:
                      - name: ""
                          how: "(one concise sentence)"
                          motivational_wisdom: "({character}s personal story about a similar experience)"
                      summary_encouragement: "(Give some final advice as {character} assuming {advisee_name} has not yet started the subtasks)"
                    ' ' '"""            
                    prompt = PromptTemplate(
                        input_variables=["character", "advisee_name", "main_task", "subtask_count"],
                        template=template,
                        )
                    #define the LLM and chain then run the chain
                    llm=OpenAIChat(model='gpt-3.5-turbo',temperature=1)
                    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
                    
                    with tab1_progress.container():
                        progress_text = "Consulting your mentor: Can take up to 30s"
                        my_bar = st.progress(5, text=progress_text)
                    
                    #run the chain
                    with st.spinner('Consulting'):
                        subtasks = chain.run({'character': character, 'advisee_name': advisee_name,'main_task': main_task,'subtask_count': subtask_count})
                    
                    print(subtasks)
                    #write subtasks to a file (debugging)
                    with open("subtasks.pkl", "wb") as f: 
                        pickle.dump(subtasks, f)    
                    # #read the subtasks from file (debugging)
                    # with open("subtasks.pkl", "rb") as f: 
                    #     subtasks = pickle.load(f) 
                    # # #print(subtasks) 
                    
                    # #Show Preview
                    with tab1_main.container():
                        st.write("## Preview")
                        st.write(subtasks)  
                    
                    
                    # #Parse JSON output
                    # template2 = """parse the following and return only the VALID YAML Structure, remove any misplaced ", -, or : which may cause an error, remove all quote citations ("quote"-citation), if you can improve upon the tasks, keep the same number and re-write as necessary  ' ' ' {subtasks} ' ' '"""
                    # prompt2 = PromptTemplate(
                    #     input_variables=["subtasks"],
                    #     template=template2,
                    #     )
                    
                    # with tab1_progress.container():
                    #     progress_text = "Refining output syntax"
                    #     my_bar = st.progress(50, text=progress_text)
                    
                    # with st.spinner('Cleaning output'):
                    #     chain2 = LLMChain(llm=llm, prompt=prompt2, verbose=True)
                    
                    # subtasks_parsed = chain2.run({'subtasks': subtasks})
                    # st.write(subtasks_parsed)
                    # #print(subtasks_parsed)
                    
                    # #write subtasks to a file (for debugging)
                    # with open("subtasks_parsed.pkl", "wb") as f: 
                    #     pickle.dump(subtasks_parsed, f) 

                  
   
                                    
                    with tab1_progress.container():
                        progress_text = "Creating the data structures"
                        my_bar = st.progress(75, text=progress_text)
                    #Clean up the otuput to remove quotes (could use another YAML parser to work around this)
                    #subtasks_parse_quote = subtasks.replace('"', '')
                    #st.write(subtasks_parse_quote)
                    
                     
                    yaml=YAML(typ='safe')   # default, if not specfied, is 'rt' (round-trip)
                    subtasks_list = ruamel.yaml.safe_load(subtasks)
                    
                    st.write("### Original Response as List")
                    st.write(subtasks_list)
                    
                    # Dataframes
                    subtasks_df = pd.DataFrame(subtasks_list)
                    # Extract Subtasks column
                    subtasks_extracted_list = subtasks_df['subtasks']
                    # Convert to another dataframe
                    subtasks_extracted_df = pd.DataFrame(subtasks_extracted_list[0])
                    
                    st.write("### Original response as Dataframe")
                    st.dataframe(subtasks_df)
                    
                    with tab1_main.container():
                        st.write("### Extracted Subtasks as dataframe")
                        st.dataframe(subtasks_extracted_df)
                        summary_encouragement = subtasks_df['summary_encouragement']
                        st.write(summary_encouragement.item())
                    
                    with tab1_progress.container():
                        progress_text = "Dataframe built"
                        my_bar = st.progress(100, text=progress_text)
                    

            except Exception as e:
                st.error(f"Error: {str(e)}")

#     # Create an expander for the "About" section
#     about = st.sidebar.expander("About 🤖")
    
#     # Write information about the chatbot in the "About" section
#     about.write("#### ChatBot-CSV is an AI chatbot featuring conversational memory, designed to enable users to discuss their CSV data in a more intuitive manner. 📄")
#     about.write("#### He employs large language models to provide users with seamless, context-aware natural language interactions for a better understanding of their CSV data. 🌐")
#     about.write("#### Powered by [Langchain](https://github.com/hwchase17/langchain), [OpenAI](https://platform.openai.com/docs/models/gpt-3-5) and [Streamlit](https://github.com/streamlit/streamlit) ⚡")
#     about.write("#### Source code : [yvann-hub/ChatBot-CSV](https://github.com/yvann-hub/ChatBot-CSV)")

# #Run the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())
