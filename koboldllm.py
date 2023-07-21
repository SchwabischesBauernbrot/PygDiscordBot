"""Wrapper around KoboldAI API."""
import logging
from typing import Any, Dict, List, Optional

import requests

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

logger = logging.getLogger(__name__)


def clean_url(url: str) -> str:
    """Remove trailing slash and /api from url if present."""
    if url.endswith("/api"):
        return url[:-4]
    elif url.endswith("/"):
        return url[:-1]
    else:
        return url
""

class KoboldApiLLM2(LLM):
    """
    A class that acts as a wrapper for the Kobold API language model.

    It includes several fields that can be used to control the text generation process.

    To use this class, instantiate it with the required parameters and call it with a
    prompt to generate text. For example:

        kobold = KoboldApiLLM(endpoint="http://localhost:5000")
        result = kobold("Write a story about a dragon.")

    This will send a POST request to the Kobold API with the provided prompt and
    generate text.
    """

    endpoint: str
    """The API endpoint to use for generating text."""

    use_story: Optional[bool] = False
    """ Whether or not to use the story from the KoboldAI GUI when generating text. """

    use_authors_note: Optional[bool] = False
    """Whether to use the author's note from the KoboldAI GUI when generating text.
    
    This has no effect unless use_story is also enabled.
    """

    use_world_info: Optional[bool] = False
    """Whether to use the world info from the KoboldAI GUI when generating text."""

    use_memory: Optional[bool] = False
    """Whether to use the memory from the KoboldAI GUI when generating text."""

    max_context_length: Optional[int] = 2048
    """Maximum number of tokens to send to the model.
    
    minimum: 1
    """

    max_length: Optional[int] = 400
    """Number of tokens to generate.
    
    maximum: 512
    minimum: 1
    """

    rep_pen: Optional[float] = 1.21
    """Base repetition penalty value.
    
    minimum: 1
    """

    rep_pen_range: Optional[int] = 1024
    """Repetition penalty range.
    
    minimum: 0
    """

    rep_pen_slope: Optional[float] = 0.9
    """Repetition penalty slope.
    
    minimum: 0
    """

    temperature: Optional[float] = 0.7
    """Temperature value.
    
    exclusiveMinimum: 0
    """

    tfs: Optional[float] = 0.9
    """Tail free sampling value.
    
    maximum: 1
    minimum: 0
    """

    top_a: Optional[float] = 0.9
    """Top-a sampling value.
    
    minimum: 0
    """

    top_p: Optional[float] = 0.95
    """Top-p sampling value.
    
    maximum: 1
    minimum: 0
    """

    top_k: Optional[int] = 0
    """Top-k sampling value.
    
    minimum: 0
    """

    typical: Optional[float] = 0.5
    """Typical sampling value.
    
    maximum: 1
    minimum: 0
    """

    stop_sequence: Optional[List[str]] = []


    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling koboldApiLLM."""
        return {
            "use_story": self.use_story,
            "use_authors_note": self.use_authors_note,
            "use_world_info": self.use_world_info,
            "use_memory": self.use_memory,
            "max_context_length": self.max_context_length,
            "max_length": self.max_length,
            "rep_pen": self.rep_pen,
            "rep_pen_range": self.rep_pen_range,
            "rep_pen_slope": self.rep_pen_slope,
            "temperature": self.temperature,
            "tfs": self.tfs,
            "top_a": self.top_a,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "typical": self.typical,
            "stop_sequence": self.stop_sequence
        }


    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {**{"endpoint": self.endpoint}, **self._default_params}

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "koboldai"

    def _get_parameters(self, stop: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Prepare parameters in format needed by KoboldAI.

        Args:
            stop (Optional[List[str]]): List of stop sequences for koboldApiLLM.

        Returns:
            Dictionary containing the combined parameters.
        """

        # Raise error if stop sequences are in both input and default params
        # if self.stop and stop is not None:
        if self.stop_sequence and stop is not None:
            raise ValueError("`stop` found in both the input and default params.")

        params = self._default_params


        # then sets it as configured, or default to an empty list:
        params["stop_sequence"] = self.stop_sequence or stop or []

        return params

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Calls the koboldApiLLM web API and returns the output.

        This function sends a request to the koboldApiLLM web API with the provided prompt 
        and stop sequences. It then processes the response, ensuring the stop sequences are 
        removed from the text and any leading or trailing whitespace is stripped off.

        Args:
            prompt: The prompt to use for generation.
            stop: A list of strings to stop generation when encountered.

        Returns:
            The generated text stripped of stop sequences and leading or trailing whitespace.

        Example:
            .. code-block:: python

                from langchain.llms import koboldApiLLM
                llm = koboldApiLLM(endpoint="http://localhost:5000")
                llm("Write a story about llamas.")
        """
        # Construct the URL for the koboldApiLLM web API
        url = f"{clean_url(self.endpoint)}/api/v1/generate"

        # Get the request parameters
        params = self._get_parameters(stop)
            
        # Make a copy of the parameters and add the prompt
        request = params.copy()
        request["prompt"] = prompt

        # Send the request to the koboldApiLLM web API
        response = requests.post(url, json=request)

        if response.status_code == 200:
            # Process the successful response
            text = response.json()["results"][0]["text"]

            # If stop sequences are provided, remove them from the text
            if stop is not None:
                for sequence in stop:
                    if text.endswith(sequence):
                        text = text.rsplit(sequence, 1)[0]
                # Strip off any trailing whitespace or newline characters
                text = text.rstrip()
        else:
            # If the response was not successful, print an error and set the text to an empty string
            print(f"ERROR: response: {response}")
            text = ""

        # Return the text, ensuring there is no leading whitespace
        return text.lstrip()