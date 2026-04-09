import pandas as pd
import random

# Generate business data (companies)
# Let's create clusters:
# Cluster 1 (Fraud Ring A): Shared address and director "Ravi"
# Cluster 2 (Fraud Ring B): Shared tax IDs and massive transactions
# Normal companies: sparse or isolated links
businesses = []
taxes = []
customs = []
transactions = []

# Normal Companies (Isolated or small clusters)
for i in range(1, 31):
    c_id = f"C{i}"
    businesses.append({"company_id": c_id, "owner": f"Owner_{i}", "director": f"Dir_{i}", "address": f"Addr_{i}", "tax_id": f"T{i}"})
    taxes.append({"company_id": c_id, "tax_paid": random.randint(10000, 50000)})
    customs.append({"company_id": c_id, "import_amount": random.randint(0, 50000)})
    if i > 1 and random.random() > 0.7:
        transactions.append({"source": c_id, "target": f"C{i-1}", "amount": random.randint(1000, 5000)})

# Fraud Ring A (Shared Director, Address)
for i in range(31, 41):
    c_id = f"C{i}"
    businesses.append({"company_id": c_id, "owner": "Ravi", "director": "Director_X", "address": "123 Fraud Ave", "tax_id": f"TA{i}"})
    taxes.append({"company_id": c_id, "tax_paid": 0})
    customs.append({"company_id": c_id, "import_amount": random.randint(500000, 2000000)})
    # Heavy intra-cluster transactions
    transactions.append({"source": f"C{random.randint(31, 40)}", "target": c_id, "amount": random.randint(100000, 500000)})

# Fraud Ring B (Shared Tax ID / Shell Companies)
for i in range(41, 55):
    c_id = f"C{i}"
    tax_id = "TB_SHARED" if i < 50 else f"TB{i}"
    businesses.append({"company_id": c_id, "owner": f"Proxy_{i}", "director": "Director_Y", "address": f"Addr_{i}", "tax_id": tax_id})
    taxes.append({"company_id": c_id, "tax_paid": random.randint(0, 500)})
    customs.append({"company_id": c_id, "import_amount": random.randint(1000000, 5000000)})
    transactions.append({"source": f"C{random.randint(41, 54)}", "target": c_id, "amount": random.randint(500000, 1000000)})

# Cross-Fraud Ring transactions
transactions.append({"source": "C35", "target": "C45", "amount": 2500000})
transactions.append({"source": "C38", "target": "C50", "amount": 3000000})

pd.DataFrame(businesses).to_csv("business.csv", index=False)
pd.DataFrame(taxes).to_csv("tax.csv", index=False)
pd.DataFrame(customs).to_csv("customs.csv", index=False)
pd.DataFrame(transactions).to_csv("transactions.csv", index=False)

print("Generated complex datasets successfully.")
