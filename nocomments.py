
import asyncio
import streamlit as st 
from langchain.prompts import PromptTemplate
from langchain import LLMChain
from langchain.llms import OpenAIChat
import yaml
import pandas as pd
import os
import pickle




st.set_page_config(layout="wide", page_icon="💡", page_title="Breakit")


st.markdown(
    "<h1 style='text-align: center;'>Subtask Generator 💡</h1>",
    unsafe_allow_html=True)


user_api_key = st.sidebar.text_input(
    label="
    placeholder="Paste your openAI API key, sk-",
    type="password")

async def main():
    
    tab1_main = st.empty()
    tab1_progress = st.empty()
   
    
    if user_api_key == "":
        
        
        st.markdown(
            "<div style='text-align: center;'><h4>👈 Enter your OpenAI API key to start </h4></div>",
            unsafe_allow_html=True)
        
    else:
        
        os.environ["OPENAI_API_KEY"] = user_api_key
        
        
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
      
        
        if advisee_name != "" and character != "" and main_task != "":
            st.sidebar.info("Ready to create subtasks!")
            
        
        else :
            st.sidebar.info(
            "👆 enter your details to get started"
            )
    
    
        
        if st.sidebar.button('Create Subtasks') and advisee_name != "" and character != "" and main_task != "":
            try :
                
                    
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
    motivational_quote: ""
  summary_encouragement: (Give some final advice as {character} assuming they have not yet started the subtasks)
' ' '"""            
                    prompt = PromptTemplate(
                        input_variables=["character", "advisee_name", "main_task"],
                        template=template,
                        )
                    
                    llm=OpenAIChat(model='gpt-3.5-turbo',temperature=1)
                    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
                    
                    with tab1_progress.container()
                        progress_text = "Consulting your mentor"
                        my_bar = st.progress(5, text=progress_text)

                    
                        my_bar.progress(percent_complete + 1, text=progress_text)
                    
                    
                    with st.spinner('Consulting'):
                        subtasks = chain.run({'character': character, 'advisee_name': advisee_name,'main_task': main_task})
                    
                    print(subtasks)
                    
                    with open("subtasks.pkl", "wb") as f: 
                        pickle.dump(subtasks, f) 
                    
                    with tab1_main.container():
                        st.write("
                        st.write(subtasks)     
                    
                    template2 = """parse the following and return only the VALID YAML Structure, remove any unicode which may cause an error ' ' ' {subtasks} ' ' '"""
                    prompt2 = PromptTemplate(
                        input_variables=["subtasks"],
                        template=template2,
                        )
                    
                    with tab1_progress.container()
                        progress_text = "Refining output syntax"
                        my_bar = st.progress(50, text=progress_text)
                    
                    with st.spinner('Cleaning output'):
                        chain2 = LLMChain(llm=llm, prompt=prompt2, verbose=True)
                    st.success('output cleaned')
                    subtasks_parsed = chain2.run({'subtasks': subtasks})
                    
                    
                    
                    
                    

                    
                    
                    
                    
   
                                    
                    with tab1_progress.container()
                        progress_text = "Creating the data structures"
                        my_bar = st.progress(75, text=progress_text)
                    
                    
                    
                    
                        yaml_str = subtasks_parsed
                        
                        yaml_obj = yaml.safe_load(yaml_str)
                        
                        
                        df = pd.DataFrame(yaml_obj)
                        
                        
                        
                        
                        
                        
                        
                        tasks = []
    
                        
                        for i, task in enumerate(df.loc["Subtasks", df.columns[0]]):
                            
                            name = task.get('name')
                            how = task.get('how')
                            quote = task.get('motivational_quote')

                            
                            tasks.append((i+1, name, how, quote))
                    
                    
                    new_df = pd.DataFrame(tasks, columns=["Task number", "name", "how", "motivational_quote"])
                    
                    with tab1_main.container():
                        st.dataframe(new_df, use_container_width=True)
                        st.write(df.loc["summary_encouragement",df.columns[0]])
                    
                    


                    
                    for index, row in new_df.iterrows():
                        
                        task_number = row["Task number"]
                        name = row["name"]
                        how = row["how"]
                        quote = row["motivational_quote"]

                        
                        print(f'Task {task_number}: {name}\nHow: {how}\nQuote: "{quote}"\n');

                    
                    st.write(subtasks) 
                    

            except Exception as e:
                st.error(f"Error: {str(e)}")



    







if __name__ == "__main__":
    asyncio.run(main())
