#Import libraries the project is dependent on
import asyncio
import streamlit as st 
from langchain.prompts import PromptTemplate
from langchain import LLMChain
from langchain.llms import OpenAIChat
import yaml
import pandas as pd
import os
import pickle



# Set the Streamlit page configuration, including the layout and page title/icon
st.set_page_config(layout="wide", page_icon="💡", page_title="To-Do Mentor")

# Display the header for the application using HTML markdown
st.markdown(
    "<h1 style='text-align: center;'>Subtask Generator 💡</h1>",
    unsafe_allow_html=True)

# Allow the user to enter their OpenAI API key
user_api_key = st.sidebar.text_input(
    label="#### Your OpenAI API key 👇",
    placeholder="Paste your openAI API key, sk-",
    type="password")

async def main():
    
    tab1_main = st.empty()
    
    # Check if the user has entered an OpenAI API key
    if user_api_key == "":
        
        # Display a message asking the user to enter their API key
        st.markdown(
            "<div style='text-align: center;'><h4>Enter your OpenAI API key to start 😉</h4></div>",
            unsafe_allow_html=True)
        
    else:
        # Set the OpenAI API key as an environment variable
        os.environ["OPENAI_API_KEY"] = user_api_key
        
        # Allow the user to enter thir name char to do item
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
                    template = """You are {character}, advising {advisee_name} on how to complete a task. Use {character}'s <motivational_quote>s that apply to the specific subtask. For <how> use vivid and descriptive language and maintain the vocabulary and voice of {character}. 

' ' ' 
main_task_n: {main_task}
' ' '
' ' '
respond in the following YAML structure:
main_task_n:
  name: 
  Subtasks:
  - name: 
    how: 
    motivational_quote: 
  - name: 
    how: 
    motivational_quote: 
  - name: 
    how: 
    motivational_quote: 
  - name: 
    how: 
    motivational_quote: 
  - name: 
    how: 
    motivational_quote: 
  summary_encouragement: (Give some final advice as {character} assuming they have not yet started the subtasks)
' ' '"""            
                    prompt = PromptTemplate(
                        input_variables=["character", "advisee_name", "main_task"],
                        template=template,
                        )
                    #define the LLM and chain then run the chain
                    llm=OpenAIChat(model='gpt-3.5-turbo',temperature=1)
                    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
                    #run the chain
                    with st.spinner('Consulting'):
                        subtasks = chain.run({'character': character, 'advisee_name': advisee_name,'main_task': main_task})
                    st.success('Response')
                    print(subtasks)
                    #write subtasks to a file (debugging)
                    with open("subtasks.pkl", "wb") as f: 
                        pickle.dump(subtasks, f) 
                        
                    #Parse JSON output
                    template2 = """parse the following and return only the VALID YAML Structure, remove any unicode which may cause an error ' ' ' {subtasks} ' ' '"""
                    prompt2 = PromptTemplate(
                        input_variables=["subtasks"],
                        template=template2,
                        )
                    with st.spinner('Cleaning output'):
                        chain2 = LLMChain(llm=llm, prompt=prompt2, verbose=True)
                    st.success('output cleaned')
                    subtasks_parsed = chain2.run({'subtasks': subtasks})
                    print(subtasks_parsed)
                    
                    #write subtasks to a file (debugging)
                    with open("subtasks_parsed.pkl", "wb") as f: 
                        pickle.dump(subtasks_parsed, f) 

                    # #read the subtasks from file (debugging)
                    # with open("subtasks.pkl", "rb") as f: 
                    #     subtasks = pickle.load(f) 
                    # #print(subtasks)    
                    st.write(subtasks_parsed)                   
                    
                    #Clean up the otuput to remove quotes (could use another YAML parser to work around this)
                    #subtasks_parse_quote = subtasks.replace('"', '')
                    #st.write(subtasks_parse_quote)
                    with st.spinner('Processing final output'):
                        yaml_str = subtasks_parsed
                        # Parse the YAML string
                        yaml_obj = yaml.safe_load(yaml_str)
                        # Convert to pandas dataframe
                        #df = pd.pandas.json_normalize(yaml_obj)
                        df = pd.DataFrame(yaml_obj)
                        
                        # Assume my_var is a variable containing valid JSON
                        #json_str = json.dumps(subtasks) # Convert variable into JSON string
                        #df = pd.read_json(json_str) # Read JSON string into dataframe
                        #st.dataframe(df)
                        
                        # Create an empty list
                        tasks = []

                        # Loop over the dictionary column
                        for i, task in enumerate(df.loc["Subtasks", df.columns[0]]):
                            # Get the values for each key
                            name = task.get('name')
                            how = task.get('how')
                            quote = task.get('motivational_quote')

                            # Append a tuple of the values to the list
                            tasks.append((i+1, name, how, quote))
                    st.success('Done!')
                    # Create a new dataframe from the list
                    new_df = pd.DataFrame(tasks, columns=["Task number", "name", "how", "motivational_quote"])
                    
                    with tab1_main.container():
                        st.dataframe(new_df, use_container_width=True)
                        st.write(df.loc["summary_encouragement",df.columns[0]])
                    # Print the new dataframe
                    #print(new_df)


                    # Loop over the rows of the new dataframe
                    for index, row in new_df.iterrows():
                        # Get the values for each column
                        task_number = row["Task number"]
                        name = row["name"]
                        how = row["how"]
                        quote = row["motivational_quote"]

                        # Print them in a formatted way
                        print(f'Task {task_number}: {name}\nHow: {how}\nQuote: "{quote}"\n');

                    #print("\nSummary: " , df.loc["summary_encouragement",df.columns[0]])
                    

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
