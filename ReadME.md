### FIXED TOKEN ABSTRACT ATTENTION TEST (FTAAT)
Automated python code that implements automatic prompting and grading to deepseek & openai API. 
I would suggest not using the streamlit aspect as its not complete.


Notebooks for reference:
- FTAAT.ipynb: Full notebook for the first version of this experiment. The first code block in this notebook will contain the code to manually call the experiment runner which includes grading. The implementation within the notebook only supports openai API, and the shared helper methods were moved out to scripts/helpers.
 - token_generation.ipynb: Similar to the FTAAT notebook, this includes all code for the first implementation of the token set generation and separator testing.
 - Visual.ipynb: This is used to make graphics based on the results. Its mostly hard coded and needs updates. However, at the top of this file you will find 2 code blocks used for cleaning and re evaluating the results. API errors: The experiment running pipeline does not catch all api errors. Due to this there is a hard coded python script (first block) to check for a set of errors and remove those tests. Format Flaw: the qualificaitons for a format flaw changed and may change so there is a re evaluation script (second block). This will reassign format flaw and accuracies. 



`prompt_template.j2`
This contains the formatting and instruciton text that the prompt is built from. Some variables can be added such as N and K.


### BUGS:
Deepseek take so long???

