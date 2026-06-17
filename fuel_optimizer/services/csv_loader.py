import os
import pandas as pd

class FuelStationRepository:
    # Set the default argument to the correct assessment CSV name
    def __init__(self, filename="fuel-prices-for-be-assessment.csv"):
        # Resolves to D:\Spotter-AI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir)) 
        
        self.file_path = os.path.join(project_root, filename)
        print(f"DEBUG: Repository is looking for the file at: {self.file_path}")

    def get_all(self):
        try:
            df = pd.read_csv(self.file_path)
            return df.to_dict(orient="records")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Could not locate the fuel data CSV. Looked at absolute path: {self.file_path}. "
                f"Please verify that the file name matches exactly."
            )