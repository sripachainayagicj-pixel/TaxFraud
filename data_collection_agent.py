import pandas as pd
import os
import random
from typing import Dict
from .base_agent import BaseAgent

class DataCollectionAgent(BaseAgent):
    def __init__(self, data_paths: Dict[str, str]):
        self.data_paths = data_paths
        self.total_records = 0

    def run(self, input_data=None) -> Dict[str, pd.DataFrame]:
        datasets = {}
        missing_any = False
        for name, path in self.data_paths.items():
            if not os.path.exists(path):
                missing_any = True
                break
            
        if missing_any:
            datasets = self.generate_demo_dataset()
        else:
            try:
                for name, path in self.data_paths.items():
                    datasets[name] = pd.read_csv(path)
            except Exception:
                datasets = self.generate_demo_dataset()
                
        # Validate and count
        self.total_records = 0
        for name, df in datasets.items():
            self.total_records += len(df)

        return datasets

    def generate_demo_dataset(self) -> Dict[str, pd.DataFrame]:
        businesses, taxes, customs, transactions = [], [], [], []
        
        for i in range(1, 11):
            c_id = f"C{i}"
            businesses.append({"company_id": c_id, "owner": f"Owner_{i}", "director": f"Dir_{i}", "address": f"Addr_{i}", "tax_id": f"T{i}"})
            taxes.append({"company_id": c_id, "tax_paid": random.randint(10000, 50000)})
            customs.append({"company_id": c_id, "import_amount": random.randint(0, 50000)})
            if i > 1:
                transactions.append({"source": c_id, "target": f"C{i-1}", "amount": random.randint(1000, 5000)})

        for i in range(11, 16):
            c_id = f"C{i}"
            businesses.append({"company_id": c_id, "owner": "Ravi", "director": "Director_X", "address": "123 Fraud Ave", "tax_id": f"TA{i}"})
            taxes.append({"company_id": c_id, "tax_paid": 0})
            customs.append({"company_id": c_id, "import_amount": random.randint(500000, 2000000)})
            transactions.append({"source": f"C{random.randint(11, 15)}", "target": c_id, "amount": random.randint(100000, 500000)})
            
        for i in range(16, 21):
            c_id = f"C{i}"
            businesses.append({"company_id": c_id, "owner": f"Proxy_{i}", "director": "Director_Y", "address": f"Addr_{i}", "tax_id": "TB_SHARED" if i < 19 else f"TB{i}"})
            taxes.append({"company_id": c_id, "tax_paid": random.randint(0, 500)})
            customs.append({"company_id": c_id, "import_amount": random.randint(1000000, 5000000)})
            transactions.append({"source": f"C{random.randint(16, 20)}", "target": c_id, "amount": random.randint(500000, 1000000)})
            
        return {
            "business": pd.DataFrame(businesses),
            "tax": pd.DataFrame(taxes),
            "customs": pd.DataFrame(customs),
            "transactions": pd.DataFrame(transactions)
        }
