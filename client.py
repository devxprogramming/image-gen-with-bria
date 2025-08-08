import os
import json
from typing import Optional, List, Dict, Any
import requests
from dotenv import load_dotenv
import random


load_dotenv()

class BriaClient:
    def __init__(self):
        self.api_token = os.getenv('BRIA_API_TOKEN')
        self.base_url = os.getenv("BASE_URL").rstrip('/')

        self.supported_model_versions: Dict[str, List[str]] = {
            'DEFAULT': ["0.0"],
            'HD': ["2.2"],
            "BASE": ["3.1", "3.2", "3.3"],
            "FAST": ["3.1"]
        }
    

    def select_model_version(self, generation_type: str, model_version: Optional[str] = None, rms: bool = False) -> str:
        """
        Select the model version based on the generation type.

        Args:
            generation_type (str): The type of generation (e.g., 'HD', 'BASE', 'FAST').
            model_version (str, optional): A specific version requested.
            rms (bool): If True, randomly select a version from the supported list for the generation_type.
                        Note: If model_version is also provided and valid, it's currently validated first
                        before potentially being ignored for random selection (check logic comments).

        Returns:
            str: The selected model version string.

        Raises:
            ValueError: If the generation_type is not supported.
        """
        gen_type_upper = generation_type.upper()
        fallback_version_str = self.supported_model_versions['DEFAULT'][0]
        available_versions = self.supported_model_versions[gen_type_upper]

        # 1. If generation type is supported
        if gen_type_upper not in self.supported_model_versions:

            print(f"Warning: Unsupported generation type '{generation_type}'. Falling back to DEFAULT version '{fallback_version_str}'.")
            
            return fallback_version_str


        # 2. --- Random Model Selection (RMS) Logic ---
        if rms:
            if model_version and model_version in available_versions:
                print(f"RMS=True, but requested version '{model_version}' is valid for '{gen_type_upper}'. Using it.")
                return model_version
            elif model_version:
                
                print(f"RMS=True, but requested version '{model_version}' is NOT valid for '{gen_type_upper}'. Falling back to DEFAULT.")
                return fallback_version_str

            # If rms=True and model_version is None, or if model_version was invalid
            if available_versions:
                selected_version = random.choice(available_versions)
                print(f"RMS=True: Randomly selected version '{selected_version}' for '{gen_type_upper}'.")
                return selected_version
            else:
                print(f"RMS=True, but no versions available for '{gen_type_upper}'. Falling back to DEFAULT '{fallback_version_str}'.")
                return fallback_version_str

        # 3. --- Non-RMS Logic ---
        # If a specific model_version is requested (and RMS is False)
        if model_version:
            if model_version in available_versions:
                print(f"RMS=False. Using requested version '{model_version}' for '{gen_type_upper}'.")
                return model_version
            else:
                # Specific version requested but not valid.
                error_msg = (f"Requested version '{model_version}' is not supported for "
                             f"generation type '{gen_type_upper}'. Supported versions: {available_versions}")
                print(f"Error: {error_msg}")
                raise ValueError(error_msg) # Raise error for invalid specific request

        # 4. Default Selection (RMS=False, no specific version)
        # Use the first available version for the type as the default
        if available_versions:
            default_version = available_versions[0] # Or define a specific default per type
            print(f"RMS=False, no specific version requested. Using default version '{default_version}' for '{gen_type_upper}'.")
            return default_version

        # 5. Ultimate Fallback (should rarely happen with good config)
        ultimate_fallback = self.supported_model_versions['DEFAULT'][0]
        print(f"Warning: No specific logic matched for '{gen_type_upper}'. Using ultimate fallback '{ultimate_fallback}'. Check configuration.")
        return ultimate_fallback
            



    def _requestHandler(self, endpoint: str, payload: Dict) -> Dict:
        headers = {"api_token": self.api_token}
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # save json response.
        with open("response.json", "w") as outfile:
            json.dump(response.json(), outfile, indent=4)
            print(f"Saved JSON response at: {outfile.name}")
            outfile.close()
        return response.json()

    def _hd_generation(self, payload: Dict) -> Dict:
        try:
            model_version = self.select_model_version('hd', rms=False)
            endpoint = str(os.getenv("HD_GENERATION").replace("{model_version}",model_version))
            imageRequest = self._requestHandler(endpoint, payload)
        except Exception as e:
            raise ValueError(f"[Error]: {e}")
        return None

    def _base_generation(self, payload: Dict) -> Dict:
        try:
            model_verison = self.select_model_version('base', rms=False)
            endpoint = os.getenv("BASE_GENERATION").replace("{model_version}",model_verison)
            self._requestHandler(endpoint, payload)
        except Exception as e:
            raise ValueError(f"[Error]: {e}")
        return None


instance = BriaClient()
payload = {
  "prompt": "a beautiful sunset over a lake in the mountains with clouds",
  "num_results": 2,
  "sync": True,
  "prompt_enhancement": True
}
instance._base_generation(payload)
