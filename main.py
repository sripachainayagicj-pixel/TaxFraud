#!/usr/bin/env python3
"""
FraudSight - Tax Evasion Network Detection System
Main entry point for the FastAPI backend application
"""

import uvicorn
from backend.main import app

if __name__ == "__main__":
    print("Starting FraudSight Backend...")
    print("Access the application at: http://localhost:8000")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

@app.get("/api/export")
def export_data():
    results = run_analysis()
    suspicious = results.get("suspicious_companies", [])
    
    output = io.StringIO()
    # Handle empty rows
    if not suspicious:
        writer = csv.writer(output)
        writer.writerow(["No suspicious companies found."])
    else:
        writer = csv.DictWriter(output, fieldnames=["company_id", "reason", "import_amount", "tax_paid"])
        writer.writeheader()
        writer.writerows(suspicious)
        
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=fraud_report.csv"}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)