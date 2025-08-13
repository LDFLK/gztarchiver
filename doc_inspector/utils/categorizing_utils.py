import requests
from doc_inspector.LLM import GAZETTE_CLASSIFICATION_PROMPT
from pathlib import Path
import csv

def classify_gazette(content, doc_id, api_key):
    """
    Classifies a gazette document using DeepSeek LLM API
    
    Args:
        content (str): The gazette content to classify
        doc_id (str): Document ID for reference
        api_key (str): DeepSeek API key
        
    Returns:
        dict: Classification result with type and reasoning
    """
    
    # DeepSeek API endpoint
    url = "https://api.deepseek.com/v1/chat/completions"
    
    # Construct the prompt with classification criteria
    prompt = GAZETTE_CLASSIFICATION_PROMPT.format(doc_id=doc_id, content=content)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        llm_response = result['choices'][0]['message']['content'].strip()
        
        # Extract type and reasoning
        lines = llm_response.split('\n')
        type_line = ""
        reasoning_line = ""
        
        for line in lines:
            if line.startswith("Type:"):
                type_line = line.replace("Type:", "").strip()
            elif line.startswith("Reasoning:"):
                reasoning_line = line.replace("Reasoning:", "").strip()
        
        # Determine final classification
        if "1" in type_line:
            classification_type = "ORGANISATIONAL"
        elif "2" in type_line:
            classification_type = "PEOPLE"
        elif "3" in type_line:
            classification_type = "HYBRID"
        elif "NOT APPLICABLE" in type_line.upper():
            classification_type = "NOT APPLICABLE"
        else:
            classification_type = "NOT FOUND"
        
        return {
            "document_id": doc_id,
            "type": classification_type,
            "reasoning": reasoning_line if reasoning_line else llm_response,
            "raw_response": llm_response,
            "success": True
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "document_id": doc_id,
            "type": "ERROR",
            "reasoning": f"API request failed: {str(e)}",
            "raw_response": None,
            "success": False
        }
    except KeyError as e:
        return {
            "document_id": doc_id,
            "type": "ERROR",
            "reasoning": f"Unexpected API response format: {str(e)}",
            "raw_response": response.text if 'response' in locals() else None,
            "success": False
        }
    except Exception as e:
        return {
            "document_id": doc_id,
            "type": "ERROR",
            "reasoning": f"Unexpected error: {str(e)}",
            "raw_response": None,
            "success": False
        }
        
def save_classified_doc_metadata(metadata_list, archive_location, year):
    
    year_folder = Path(archive_location).expanduser() / str(year)
    year_folder.mkdir(parents=True, exist_ok=True)
    
    # Set the CSV file path
    csv_file_path = year_folder / "classified_metadata.csv"
    
    # Write or append to the CSV file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Document ID", "Document Date", "Gazette Type", "Reasoning"])
        for row in metadata_list:
            writer.writerow(row)

    print(f"[✓] Metadata saved to {csv_file_path}")
        
    return


def prepare_classified_metadata(llm_ready_texts, api_key):
    classified_metadata = []
    classified_metadata_dic = {}
        
    for doc_id in llm_ready_texts:
        doc_text = llm_ready_texts[doc_id]["text"]
        doc_date = llm_ready_texts[doc_id]["doc_date"]
        print(f"Document ID: {doc_id}")
        print(f"Document Date: {doc_date}")
        res = classify_gazette(doc_text, doc_id, api_key)
        if res["success"]:
            doc_type = res['type']
            doc_type_reason = res['reasoning']
            print(f"Gazette type: {res['type']}")
            print(f"Reasoning: {res['reasoning']}")
        else:
            doc_type = "Error"
            doc_type_reason = res['reasoning']
            print(f"Error: {res['reasoning']}")
        # Append metadata for later saving
        classified_metadata.append((doc_id, doc_date, doc_type, doc_type_reason))
        classified_metadata_dic[doc_id] = {
            'doc_date': doc_date,
            'doc_type': doc_type,
            'reasoning': doc_type_reason
        }
        print("\n" + "="*80 + "\n") 
    
    return classified_metadata, classified_metadata_dic