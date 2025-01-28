# SnowPilotAnalytics
 
## Mary Kate's Snow Pilot Analytics Independent Study

 The data for this project comes from Snowpilot.org


 ## Setting up Jupyter Notebook

 1. Install Jupyter Notebook
    
    ```
    python3 -m venv .venv
    .venv\Scripts\activate
    pip install jupyter

    ```

2. Install necessary libraries

   ```
   choco install python
   pip install pandas
   pip install numpy
   pip install matplotlib
   pip install seaborn
   pip install scikit-learn
   ```

Resources:

https://snowpilot.org/

https://github.com/SnowpitData/AvscienceServer

https://github.com/abkfenris/snowpit/tree/master/snowpit

https://github.com/ArcticSnow/snowpyt

http://caaml.org/Schemas/V4.2/Doc/#complexType_RescuedByBaseType_Link0BC1FC30


Project Objectives:

1. Create a data model and GitHub repository for working with CAAML files from the SnowPilot database (SnowPylot?)
2. Use Jupyter Notebooks to analyze the data and answer research questions
3. Summarize and present results at the Western Snow Conference in May 2025



To do
*Testing*
1. Add tests to check if updating library (Explore Pytest)
2. Add tests to make sure parsing matches caaml file
3. Test process
   Load file
   parse file
   check if parsing matches expected output
4. Set up smaller tests
   ex. "test get_longitude"

*Structure*
1. Make snowPilotObs class a shell
2. Make separate caaml-parser class
* Input: caaml file, version. return: snowpit object

