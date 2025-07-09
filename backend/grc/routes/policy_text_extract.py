import re
import json
import os
import pandas as pd
import shutil
import time
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from django.conf import settings
from datetime import datetime
import cache
import glob

# Global progress tracking
progress_tracker = {}

def update_progress(task_id, progress, message, status='processing', operation=None):
    """Update the progress of policy text extraction with detailed information."""
    cache_key = f'task_progress_{task_id}'
    progress_data = {
        'progress': progress,
        'message': message,
        'status': status,
        'time': datetime.now().isoformat(),
        'operation': operation or {}
    }
    cache.set(cache_key, json.dumps(progress_data), timeout=3600)

def get_progress(task_id):
    """Get progress for a specific task"""
    return progress_tracker.get(task_id, {'progress': 0, 'message': 'Starting...'})

def extract_policy_sections(input_text, task_id=None):
    """Extract policy sections with detailed progress tracking."""
    try:
        if task_id:
            update_progress(task_id, 10, "Initializing policy extraction", operation={
                'action': 'Policy Extraction',
                'stage': 'Initialization',
                'progress': 10
            })

        # Parse the text into sections
        sections = []
        current_section = None
        
        if task_id:
            update_progress(task_id, 20, "Parsing document sections", operation={
                'action': 'Policy Extraction',
                'stage': 'Section Parsing',
                'progress': 20
            })

        # Split text into lines and process
        lines = input_text.split('\n')
        for line in lines:
            if task_id and len(sections) > 0 and len(sections) % 10 == 0:
                progress = min(80, 20 + (len(sections) // 10 * 5))
                update_progress(task_id, progress, f"Processing section {len(sections)}", operation={
                    'action': 'Policy Extraction',
                    'stage': 'Section Processing',
                    'progress': progress
                })

            # Process line and update sections
            if line.strip():
                if is_section_header(line):
                    if current_section:
                        sections.append(current_section)
                    current_section = {
                        'title': line.strip(),
                        'content': []
                    }
                elif current_section:
                    current_section['content'].append(line.strip())

        # Add the last section if exists
        if current_section:
            sections.append(current_section)

        if task_id:
            update_progress(task_id, 90, "Finalizing policy extraction", operation={
                'action': 'Policy Extraction',
                'stage': 'Finalization',
                'progress': 90
            })

        # Process sections to extract policy information
        processed_sections = []
        for section in sections:
            processed_section = process_section(section)
            if processed_section:
                processed_sections.append(processed_section)

        if task_id:
            update_progress(task_id, 100, "Policy extraction completed", status='completed', operation={
                'action': 'Policy Extraction',
                'stage': 'Complete',
                'progress': 100
            })

        return processed_sections

    except Exception as e:
        if task_id:
            update_progress(task_id, 0, f"Error extracting policies: {str(e)}", status='error', operation={
                'action': 'Policy Extraction',
                'stage': 'Error',
                'progress': 0
            })
        raise

def process_checked_sections(task_id):
    """Process checked sections with detailed progress tracking."""
    try:
        update_progress(task_id, 10, "Initializing checked sections processing", operation={
            'action': 'Section Processing',
            'stage': 'Initialization',
            'progress': 10
        })

        # Get the checked sections directory
        checked_sections_dir = cache.get(f'checked_sections_dir_{task_id}')
        if not checked_sections_dir:
            raise Exception("Checked sections directory not found")

        update_progress(task_id, 20, "Reading checked sections", operation={
            'action': 'Section Processing',
            'stage': 'Reading',
            'progress': 20
        })

        # Process each checked section
        policies = []
        section_files = glob.glob(os.path.join(checked_sections_dir, '**/*.txt'), recursive=True)
        
        total_files = len(section_files)
        for idx, file_path in enumerate(section_files, 1):
            progress = min(80, 20 + (idx / total_files * 60))
            update_progress(task_id, progress, f"Processing file {idx} of {total_files}", operation={
                'action': 'Section Processing',
                'stage': 'File Processing',
                'file': os.path.basename(file_path),
                'progress': progress
            })

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                section_policies = extract_policy_sections(content)
                policies.extend(section_policies)

        update_progress(task_id, 90, "Generating Excel report", operation={
            'action': 'Section Processing',
            'stage': 'Report Generation',
            'progress': 90
        })

        # Generate Excel report
        excel_path = generate_excel_report(policies, task_id)

        update_progress(task_id, 100, "Processing completed successfully", status='completed', operation={
            'action': 'Section Processing',
            'stage': 'Complete',
            'progress': 100
        })

        return excel_path

    except Exception as e:
        update_progress(task_id, 0, f"Error processing sections: {str(e)}", status='error', operation={
            'action': 'Section Processing',
            'stage': 'Error',
            'progress': 0
        })
        raise

# # Example usage
# if __name__ == "__main__":
#     input_file_path = "ac1.txt"
#     
#     with open(input_file_path, "r", encoding="utf-8") as file:
#         document_text = file.read()
#     
#     result_json = extract_policy_sections(document_text)
#     print(json.dumps(result_json, indent=2))