
# !pip install langchain langchain_openai langchain_core langchain_community pydantic
from langchain_openai import ChatOpenAI #, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field, validator, create_model
from typing import List, Optional, Text, Dict
from IPython.display import display, Markdown

# ## Defining the structured output desired from chat gpt
# ## Tip was to use make_model
# # https://stackoverflow.com/questions/63257839/best-way-to-specify-nested-dict-with-pydantic
# class Coordinates(BaseModel):
#     SW: List[float]
#     NE: List[float]
    
# class RegionCoordinates(BaseModel):
#     rural: Optional[Coordinates]
#     urban: Optional[Coordinates]
                            
# class DataParams(BaseModel):
#     """
#     Represents the parameters for data analysis.

#     Attributes:
#         city_region_name (str): The name of the city or region.
#         coordinates (Optional[RegionCoordinates]): The coordinates of the city or region.
#         time (Dict[str, str]): A dictionary containing time-related information.
#     """
#     city_region_name: str
#     coordinates: Optional[RegionCoordinates]
#     time: Dict[str, str]
    
    
# def suggest_data_params(query: str, temperature=0.1, model_type='gpt-4o',
#                        return_llm = False, return_json=True) -> str:
#     """
#     Suggests data parameters for downloading MODIS data for a specific region and time range.
    
#     Args:
#         query (str): The query describing the requirements for the data download.
#         temperature (float, optional): The temperature parameter for the language model. Defaults to 0.1.
#         model_type (str, optional): The type of language model to use. Defaults to 'gpt-4o'.
#         return_llm (bool, optional): Whether to return the language model chain. Defaults to False.
#         return_json (bool, optional): Whether to return the response as JSON. Defaults to True.
    
#     Returns:
#         str: The response from the language model chain or the JSON response, depending on the value of return_json.
#     """
    
#     # The prompt template for suggesting data parameters
#     prompt = """
#     I am performing an urban heat island analysis project with MODIS data. I need to download MODIS data for a specific region and time range.
#     I need to select a region and time range for the data download, keeping the following in mind:
#     {query}
    
#     Provide me the data parameters for the download (city_region_name, coordinates as SW [lat,long] NE [lat,long], time_start named 'start', time_end named 'end') in the following format:
#     Format Instructions:
#     {format_instructions}
#     """
#     # Create a ChatPromptTemplate object
#     final_prompt_template = PromptTemplate.from_template(prompt)

#     # Get api key for OpenAI from the environment or session state (if on Streamlit)
#     try:
#         api_key = st.session_state.OPENAI_API_KEY
#     except:
#         api_key = os.getenv('OPENAI_API_KEY')
        
#     # Instantiate the language model and setting the specific model (chat-gpto is newest and reasonable price)
#     # and  set the temperature (creativity level)
#     llm = ChatOpenAI(temperature=temperature, model=model_type, api_key=api_key)
    
#     if return_json:
#         # # JsonOutputParser will use the data model classes from above
#         parser = JsonOutputParser(pydantic_object=DataParams,)    
#         # Add formatting instructions for pydantic
#         instructions =  parser.get_format_instructions()
            
#     else:
#         ## StrOutputParser will return the response as a string
#         parser = StrOutputParser(output_key="response")
#         # Manually defining the format instructions
#         instructions = "Respond with text for each topic as a nested list with the topic number,  descriptive label,top words, and short insight."
        
#     ## Adding the instructions to the prompt template
#     final_prompt_template = final_prompt_template.partial(format_instructions=instructions)
    
    
#     # Making the final chain
#     llm_chain = final_prompt_template | llm | parser
    
#     # Return the chain if specified
#     if return_llm:
#         return llm_chain
    
#     else:
    
#         # Invoke the chain with the query to get the response
#         response = llm_chain.invoke(input=dict(query=query))
#         return response


# Define Pydantic models for structured output
class Coordinates(BaseModel):
    SW: List[float]
    NE: List[float]

class RegionCoordinates(BaseModel):
    rural: Optional[Coordinates]
    urban: Optional[Coordinates]


class FIPS(BaseModel):
    state_fips: str
    county_fips: List[str]
    census_tract_fips: List[str]
    # urban_census_tract_fips: List[str]
class RegionFIPS(BaseModel):
    state_fips: str
    # rural_census_tract_fips: List[str]
    rural: Optional[FIPS]
    urban: Optional[FIPS]
    # urban_census_tract_fips: List[str]

class DataParamsFips(BaseModel):
    city_region_name: str
    coordinates: Optional[RegionCoordinates]
    time: Dict[str, str]
    fips: Optional[RegionFIPS]



## Updated suggest function with FIPS added to prompt
def suggest_data_params(specs: str, temperature=0.0, model_type='gpt-4o', return_json=True,
                        pydantic_model=DataParamsFips) -> str:
    """
    Suggests data parameters for downloading MODIS data for a specific region and time range.
    
    Args:
        query (str): The query describing the requirements for the data download.
        temperature (float, optional): The temperature parameter for the language model. Defaults to 0.1.
        model_type (str, optional): The type of language model to use. Defaults to 'gpt-4o'.
        return_llm (bool, optional): Whether to return the language model chain. Defaults to False.
        return_json (bool, optional): Whether to return the response as JSON. Defaults to True.
    
    Returns:
        str: The response from the language model chain or the JSON response, depending on the value of return_json.
    """
    
    # The prompt template for suggesting data parameters
    prompt = """
    I am performing an urban heat island analysis project with MODIS data comparing urban areas vs. rural areas. 
    I need to download MODIS data for 2 nearby non-overlapping regions (urban area and rural area outside of city) and time range.
    Help me select the urban and rural regions and time following the instructions below.
    {specs}
    
    Provide me the data parameters for the download (city_region_name - e.g 'Albany, NY', coordinates as SW [lat,long] NE [lat,long], time_start named 'start', time_end named 'end') 
    also include the state FIPS and a list of every census tract fips code included within the selected regions for the Census API, in the following format:
    Format Instructions:
    Use the 2-letter abbreviations for the state.
    {format_instructions}
    """
    # Create a ChatPromptTemplate object
    final_prompt_template = PromptTemplate.from_template(prompt)

    # Get api key for OpenAI from the environment or session state (if on Streamlit)
    api_key = os.getenv('OPENAI_API_KEY')
        
    # Instantiate the language model and setting the specific model (chat-gpto is newest and reasonable price)
    # and  set the temperature (creativity level)
    llm = ChatOpenAI(temperature=temperature, model=model_type, api_key=api_key)
    
    if return_json:
        # # JsonOutputParser will use the data model classes from above
        parser = JsonOutputParser(pydantic_object=pydantic_model,)    
        # Add formatting instructions for pydantic
        instructions =  parser.get_format_instructions()
            
    else:
        ## StrOutputParser will return the response as a string
        parser = StrOutputParser(output_key="response")
        # Manually defining the format instructions
        instructions = "Respond with markdown-flavored text."
        
        
    ## Adding the instructions to the prompt template
    final_prompt_template = final_prompt_template.partial(format_instructions=instructions)
    
    
    # Making the final chain
    llm_chain = final_prompt_template | llm | parser
    
    # Invoke the chain with the query to get the response
    return llm_chain.invoke(input=dict(specs=specs))