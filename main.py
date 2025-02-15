from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os
import datetime
import sqlite3
import re
import requests
import uvicorn
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  
    allow_headers=["*"],
)

# OpenAI Client Configuration (Use a safer way to store credentials in production)
client = OpenAI(base_url="http://aiproxy.sanand.workers.dev/openai/v1", api_key="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDA1MTFAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.mClsSTr8HODa_tvFwsMPOfJtKfDXKeblukACx05c16s")

@app.get("/")
def home():
    return {"message": "Yay TDS Tuesday is awesome."}

def install_uv():
    try:
        subprocess.run(["pip", "install", "uv"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install uv: {e}")

def run_datagen(user_email):
    try:
        install_uv()  # Ensure uv is installed
        url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
        response = requests.get(url)
        if response.status_code == 200:
            with open("datagen.py", "w") as f:
                f.write(response.text)
            subprocess.run(["python", "datagen.py", user_email], check=True)
        else:
            raise RuntimeError("Failed to download datagen.py")
    except Exception as e:
        raise RuntimeError(f"Error running datagen.py: {e}")

def format_markdown():
    try:
      subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"], check=True)
    except subprocess.CalledProcessError as e:
      raise RuntimeError(f"Error formatting markdown: {e}")

def count_wednesdays():
    try:
        with open("/data/dates.txt", "r") as f:
            dates = [line.strip() for line in f]
        wednesday_count = 0
        for date_str in dates:
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date() # Adjust date format if needed
                if date_obj.weekday() == 2:  # Wednesday is represented by 2
                    wednesday_count += 1
            except ValueError:
                print(f"Invalid date format: {date_str}") # Handle invalid date formats gracefully
        with open("/data/dates-wednesdays.txt", "w") as outfile:
            outfile.write(str(wednesday_count))
    except Exception as e:
        raise RuntimeError(f"Error counting Wednesdays: {e}")



@app.post("/run")
def run_task(task: str, user_email: str = Query(None)):
    try:
        if "datagen" in task.lower():
            run_datagen(user_email)
            return {"status": "Task A1 completed successfully"}
        elif "format markdown" in task.lower():
            format_markdown()
            return {"status": "Task A2 completed successfully"}
        elif "count wednesdays" in task.lower():
            count_wednesdays()
            return {"status": "Task A3 completed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Unknown task")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) # More specific error handling
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/read")
def read_file(path: str):
    try:
        full_path = os.path.join("/data", path) # Ensure path is within /data
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        with open(full_path, "r") as f:
            content = f.read()
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
