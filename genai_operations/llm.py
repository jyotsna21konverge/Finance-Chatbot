import logging
import os
import logging
from langchain_openai import ChatOpenAI
from exceptions import LLMInitializationError, IncorrectAPIKey

# Initialize logger
logger = logging.getLogger("Backend-Service")


class LLM:
    """
    Represents a Language Model (LLM) object with functionalities to load models, tokenizers,
    and create pipelines for various tasks.
    """

    def __init__(self) -> None:
        """
        Initializes a Language Model (LLM) object. No parameters are initialized during object creation.
        """
        pass

    def openai(self, openai_key, model, temperature=0):
        """
        Initializes an LLM object using an ChatOpenAI model.

        :param model(str): The name of the OpenAI model to use.
        :param openai_key(str): The API key for accessing the OpenAI API.
        :param temperature(int): The temperature for the model to generate responses (default is 0).
        :param max_tokens(int): The max_tokens for the model to generate responses (default is 512).

        :return: An LLM object or None if initialization fails.
        """
        os.environ["OPENAI_API_KEY"] = openai_key
        llm = None
        try:
            llm = ChatOpenAI(model_name=model, temperature=temperature)
            logger.info(f"Successfully called '{model}' from OpenAI")
        except Exception as e:
            logger.error(f"Error during OpenAI initialization: {str(e)}")
            raise LLMInitializationError(f"Error during OpenAI initialization: {str(e)}")
        return llm
        