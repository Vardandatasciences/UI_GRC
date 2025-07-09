import sys
sys.setrecursionlimit(3000)  # default is 1000, this raises it safely

import os
import re
import pandas as pd
import PyPDF2
import glob
import pdfplumber
from pypdf import PdfReader
import json
from datetime import datetime
from django.core.cache import cache

def update_progress(task_id, progress, message, status='processing', operation=None):
    """Update the progress of document processing with detailed information."""
    cache_key = f'task_progress_{task_id}'
    progress_data = {
        'progress': progress,
        'message': message,
        'status': status,
        'time': datetime.now().isoformat(),
        'operation': operation or {}
    }
    cache.set(cache_key, json.dumps(progress_data), timeout=3600)

def extract_document_sections(pdf_path, output_dir='extracted_sections', task_id=None):
    """Extract document sections with detailed progress tracking."""
    try:
        if task_id:
            update_progress(task_id, 5, "Initializing document processing", operation={
                'action': 'Document Processing',
                'stage': 'Initialization',
                'file': os.path.basename(pdf_path),
                'progress': 5
            })

        # Find table of contents page
        if task_id:
            update_progress(task_id, 10, "Locating table of contents", operation={
                'action': 'Document Processing',
                'stage': 'TOC Detection',
                'progress': 10
            })
            
        toc_page = find_toc_page(pdf_path)
        
        if task_id:
            update_progress(task_id, 20, "Table of contents found", operation={
                'action': 'Document Processing',
                'stage': 'TOC Processing',
                'progress': 20
            })

        # Extract TOC text
        text_file_path = os.path.join(output_dir, 'table_of_contents.txt')
        extract_toc_to_text(pdf_path, toc_page, text_file_path)
        
        if task_id:
            update_progress(task_id, 30, "Processing table of contents structure", operation={
                'action': 'Document Processing',
                'stage': 'TOC Structure',
                'progress': 30
            })

        # Process TOC and save to Excel
        excel_file_path = os.path.join(output_dir, 'structured_toc.xlsx')
        process_toc_and_save_to_excel(text_file_path, excel_file_path)
        
        if task_id:
            update_progress(task_id, 40, "Analyzing document layout", operation={
                'action': 'Document Processing',
                'stage': 'Layout Analysis',
                'progress': 40
            })

        # Find page offset
        offset = find_offset(pdf_path)
        
        if task_id:
            update_progress(task_id, 50, "Extracting document content", operation={
                'action': 'Document Processing',
                'stage': 'Content Extraction',
                'progress': 50
            })

        # Extract text with styles from all pages
        text_data = extract_text_with_styles_from_pages(pdf_path, 1, get_num_pages(pdf_path))
        
        if task_id:
            update_progress(task_id, 60, "Processing document sections", operation={
                'action': 'Document Processing',
                'stage': 'Section Processing',
                'progress': 60
            })

        # Group text by position
        lines = group_text_by_position(text_data)
        
        if task_id:
            update_progress(task_id, 70, "Detecting section headers", operation={
                'action': 'Document Processing',
                'stage': 'Header Detection',
                'progress': 70
            })

        # Detect first subheading
        first_subheading = detect_first_subheading(lines)
        
        if task_id:
            update_progress(task_id, 80, "Extracting section content", operation={
                'action': 'Document Processing',
                'stage': 'Content Extraction',
                'progress': 80
            })

        # Extract sections
        sections = extract_sections(lines, first_subheading)
        
        if task_id:
            update_progress(task_id, 90, "Saving extracted sections", operation={
                'action': 'Document Processing',
                'stage': 'Content Saving',
                'progress': 90
            })

        # Save sections to files
        save_sections(sections, output_dir)
        
        if task_id:
            update_progress(task_id, 100, "Document processing completed", status='completed', operation={
                'action': 'Document Processing',
                'stage': 'Complete',
                'progress': 100
            })

        return sections

    except Exception as e:
        if task_id:
            update_progress(task_id, 0, f"Error processing document: {str(e)}", status='error', operation={
                'action': 'Document Processing',
                'stage': 'Error',
                'progress': 0
            })
        raise

def find_toc_page(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page_num, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text()
                if "Table of Contents" in text or "Contents" in text:
                    return page_num
            except Exception as e:
                print(f"Error reading page {page_num}: {e}")
    return None

def extract_toc_to_text(pdf_path, toc_page_num, text_file_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        toc_page = reader.pages[toc_page_num - 1]
        toc_text = toc_page.extract_text()

    with open(text_file_path, 'w', encoding='utf-8') as text_file:
        text_file.write(toc_text)
    print(f"Table of Contents saved to {text_file_path}")

def process_toc_and_save_to_excel(txt_file_path, excel_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    toc_data = []
    toc_pattern = re.compile(r"^(?P<section>[0-9]+(\.[0-9]+)*)?\s*(?P<section_name>.+?)\s+(?P<page>\d+)$")
    
    for line in lines:
        line = line.strip()
        match = toc_pattern.match(line)
        if match:
            section = match.group('section') if match.group('section') else ''
            section_name = match.group('section_name').rstrip('. ').strip()
            page = int(match.group('page'))
            toc_data.append({'Section': section, 'Section Name': section_name, 'Page Number': page})

    df = pd.DataFrame(toc_data)
    df.to_excel(excel_file_path, index=False)
    print(f"Structured TOC saved to {excel_file_path}")

def find_offset(pdf_path):
    heading_pattern = re.compile(r'^\s*chapter one\s*$', re.IGNORECASE)
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for pdf_page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            lines = text.splitlines()
            for line in lines:
                if heading_pattern.match(line.strip()):
                    return pdf_page_num
    return None

def extract_text_with_styles_from_pages(pdf_path, start_page, end_page):
    """Extract text with styles from specific page range (0-indexed)"""
    with pdfplumber.open(pdf_path) as pdf:
        text_data = []
        for page_num in range(start_page, min(end_page, len(pdf.pages))):
            page = pdf.pages[page_num]
            for char in page.chars:
                text_data.append({
                    "text": char["text"],
                    "page": page_num - start_page + 1,  # Relative page numbering within section
                    "fontname": char.get("fontname", ""),
                    "fontsize": char.get("size", 0),
                    "x": char.get("x0", 0),
                    "y": char.get("top", 0),
                })
        return text_data

def group_text_by_position(text_data, line_tolerance=2):
    grouped_lines = []
    current_line = []

    for char_data in sorted(text_data, key=lambda x: (x["page"], x["y"], x["x"])):
        if not current_line:
            current_line.append(char_data)
        else:
            last_char = current_line[-1]
            same_line = (
                abs(char_data["y"] - last_char["y"]) <= line_tolerance and
                char_data["page"] == last_char["page"]
            )
            if same_line:
                current_line.append(char_data)
            else:
                grouped_lines.append(current_line)
                current_line = [char_data]

    if current_line:
        grouped_lines.append(current_line)

    return grouped_lines

def is_all_caps(text):
    filtered = ''.join(c for c in text if c.isalpha())
    return filtered.isupper() if filtered else False

def is_bold(fontname):
    return "Bold" in fontname or "bold" in fontname

def extract_all_subheadings_with_style(lines, fontname, fontsize, all_caps, bold):
    matched_subheadings = []
    for line in lines:
        text = "".join(char["text"] for char in line).strip()
        if not text:
            continue
        total_chars = len(line)
        if total_chars == 0:
            continue
        total_bold_chars = sum(1 for char in line if is_bold(char.get("fontname", "")))
        overall_line_bold = total_bold_chars / total_chars >= 0.7
        font_counts = {}
        for char in line:
            fnt = char.get("fontname", "")
            font_counts[fnt] = font_counts.get(fnt, 0) + 1
        majority_fontname = max(font_counts, key=font_counts.get) if font_counts else ""

        char_style_matches = []
        for char in line:
            c_fontname = char.get("fontname", "")
            c_fontsize = char.get("fontsize", char.get("size", 0))
            c_text = char["text"]
            c_all_caps = c_text.isalpha() and c_text.isupper()
            c_bold = is_bold(c_fontname)
            fontname_match = (c_fontname == fontname)
            fontsize_match = abs(c_fontsize - fontsize) < 1
            all_caps_match = (c_all_caps == all_caps)
            bold_match = (overall_line_bold == bold)
            is_char_matching = fontname_match and fontsize_match and all_caps_match and bold_match
            char_style_matches.append(is_char_matching)

        start_noise = 0
        for match in char_style_matches:
            if not match:
                start_noise += 1
            else:
                break

        end_noise = 0
        for match in reversed(char_style_matches):
            if not match:
                end_noise += 1
            else:
                break

        if (start_noise + end_noise) / total_chars > 0.3:
            continue

        start_idx = start_noise
        end_idx = total_chars - 1 - end_noise

        while start_idx <= end_idx and line[start_idx]["text"].isspace():
            start_idx += 1
        while end_idx >= start_idx and line[end_idx]["text"].isspace():
            end_idx -= 1

        if start_idx > end_idx:
            continue

        cleaned_text = "".join(char["text"] for char in line[start_idx:end_idx+1]).strip()

        if all_caps and not is_all_caps(cleaned_text):
            continue

        matched_subheadings.append({
            "text": cleaned_text,
            "page": line[0]["page"],
            "fontname": majority_fontname,
            "fontsize": fontsize,
            "all_caps": all_caps,
            "bold": bold,
            "y": line[0]["y"],
        })
    return matched_subheadings

def merge_successive_subheadings(subheadings, y_tolerance=25):
    if not subheadings:
        return []
    merged = []
    prev = subheadings[0]
    for curr in subheadings[1:]:
        same_page = (curr["page"] == prev["page"])
        y_close = abs(curr["y"] - prev["y"]) < y_tolerance
        if same_page and y_close:
            prev["text"] += " " + curr["text"]
            prev["y"] = min(prev["y"], curr["y"])
        else:
            merged.append(prev)
            prev = curr
    merged.append(prev)
    return merged

def detect_first_subheading(lines):
    main_heading = None
    found_main_heading = False
    main_heading_page = None
    main_heading_y = None
    candidates = []
    for line in lines:
        text = "".join(char["text"] for char in line).strip()
        if not text:
            continue
        font_counts = {}
        for char in line:
            fnt = char.get("fontname", "")
            font_counts[fnt] = font_counts.get(fnt, 0) + 1
        majority_fontname = max(font_counts, key=font_counts.get) if font_counts else ""
        fontname = majority_fontname
        fontsize = line[0].get("fontsize", line[0].get("size", 0))
        page = line[0]["page"]
        y = line[0]["y"]

        if not found_main_heading:
            if len(text.split()) <= 10 and fontsize > 10:
                main_heading = {
                    "text": text,
                    "page": page,
                    "fontname": fontname,
                    "fontsize": fontsize,
                    "y": y,
                }
                main_heading_page = page
                main_heading_y = y
                found_main_heading = True
        else:
            if page == main_heading_page and y > main_heading_y + 0.5:
                total_chars = len(line)
                if total_chars == 0:
                    continue
                total_bold_chars = sum(1 for char in line if is_bold(char.get("fontname", "")))
                line_bold = (total_bold_chars / total_chars) >= 0.7
                candidates.append({
                    "text": text,
                    "page": page,
                    "fontname": fontname,
                    "fontsize": fontsize,
                    "y": y,
                    "all_caps": is_all_caps(text),
                    "bold": line_bold,
                })

    if not candidates:
        return []

    filtered_candidates = [c for c in candidates if main_heading and c["y"] > main_heading["y"] + 0.5]
    if not filtered_candidates:
        return []

    filtered_candidates.sort(key=lambda x: (
        -x["fontsize"],
        -int(x["all_caps"]),
        -int(x["bold"]),
    ))

    first_subheading = filtered_candidates[0]

    matched_subheadings = extract_all_subheadings_with_style(
        lines,
        first_subheading["fontname"],
        first_subheading["fontsize"],
        first_subheading["all_caps"],
        first_subheading["bold"],
    )

    return merge_successive_subheadings(matched_subheadings)

def extract_policy_id_from_text(text):
    """Extract policy ID from subheading text (e.g., 'MP-1 POLICY AND PROCEDURES' -> 'MP-1')"""
    import re
    # Pattern to match policy IDs like AC-1, AT-1, MP-1, etc.
    pattern = r'^([A-Z]{2,3}-\d+(?:\(\d+\))?)'
    match = re.match(pattern, text.strip())
    if match:
        return match.group(1)
    return None

def extract_last_subheading_to_section_end(last_subheading, line_number_map, output_path, json_dir):
    start_regex = re.escape(last_subheading['text'][:10].strip().lower())
    start_found = False
    extracted_lines = []
    for entry in line_number_map:
        line_text = "".join(char["text"] for char in entry["line"]).strip()
        line_text_lower = line_text.lower()
        if len(line_text) < 4:
            continue
        if not start_found:
            if re.search(start_regex, line_text_lower):
                start_found = True
                extracted_lines.append(line_text)
            continue
        else:
            extracted_lines.append(line_text)
    if extracted_lines:
        full_text = "\n".join(extracted_lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        # Extract policy ID for JSON filename
        policy_id = extract_policy_id_from_text(last_subheading['text'])
        if policy_id:
            json_filename = f"{policy_id}.json"
        else:
            json_filename = os.path.basename(output_path).replace(".txt", ".json")
        
        json_path = os.path.join(json_dir, json_filename)
        json_data = {
            "subheading": last_subheading['text'],
            "start_text": full_text[:50],
            "content": full_text
        }
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(json_data, jf, indent=2)
        print(f"✅ Saved last subheading extract to {output_path} and JSON")

# Main execution flow
def get_num_pages(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        return len(reader.pages)

def extract_sections(lines, first_subheading):
    sections = []
    current_section = {
        'start_page': 1,
        'end_page': 1,
        'subheadings': [],
        'content': []
    }

    for line in lines:
        text = "".join(char["text"] for char in line).strip()
        if not text:
            continue

        # Check if the line is a subheading
        if first_subheading and text.lower() == first_subheading['text'].lower():
            # If it's a subheading, finalize the current section and start a new one
            if current_section['subheadings']:
                sections.append(current_section)
            current_section = {
                'start_page': line[0]['page'],
                'end_page': line[0]['page'], # Subheading is on the same page as its start
                'subheadings': [first_subheading],
                'content': []
            }
            continue

        # If it's not a subheading, add it to the current section's content
        current_section['content'].append({
            'text': text,
            'page': line[0]['page'],
            'y': line[0]['y']
        })

    # Append the last section if it exists
    if current_section['subheadings']:
        sections.append(current_section)

    return sections

def save_sections(sections, output_dir):
    for i, section in enumerate(sections):
        section_id = str(section['subheadings'][0]['text']).strip() # Use subheading text as section ID
        section_name = str(section['subheadings'][0]['text']).strip() # Use subheading text as section name
        section_folder = os.path.join(output_dir, f"{section_id} {section_name}")
        os.makedirs(section_folder, exist_ok=True)

        txt_dir = os.path.join(section_folder, "txt_chunks")
        json_dir = os.path.join(section_folder, "json_chunks")
        os.makedirs(txt_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)

        print(f"\n[🔍] Subheading extraction for: {section_id} {section_name} (pages {section['start_page']+1}-{section['end_page']})")

        try:
            # Extract text with styles from the specific page range
            text_data = extract_text_with_styles_from_pages(pdf_path, section['start_page'], section['end_page'])
            if not text_data:
                print(f"[⚠️] No text data extracted from {section_id} {section_name}")
                continue

            grouped_lines = group_text_by_position(text_data)
            if not grouped_lines:
                print(f"[⚠️] No grouped lines found in {section_id} {section_name}")
                continue

            page_line_counter = {}
            line_number_map = []
            for line in grouped_lines:
                if not line:
                    continue
                page = line[0]["page"]
                page_line_counter[page] = page_line_counter.get(page, 0) + 1
                line_number_map.append({
                    "line": line,
                    "page": page,
                    "line_on_page": page_line_counter[page]
                })

            subheadings = detect_first_subheading(grouped_lines)
            if not subheadings:
                print(f"[⚠️] No subheadings found in {section_id} {section_name}")
                continue

            print(f"[✅] Found {len(subheadings)} subheadings in {section_id} {section_name}")

            # Create Excel file for subheadings
            excel_path = os.path.join(section_folder, f"{section_id}_subheadings.xlsx")
            df_sub = pd.DataFrame([{"Subheading": s["text"], "Page No": s["page"]} for s in subheadings])
            df_sub.to_excel(excel_path, index=False)

            # Extract text between subheadings
            for i in range(len(subheadings) - 1):
                start_regex = re.escape(subheadings[i]['text'][:10].strip().lower())
                end_regex = re.escape(subheadings[i+1]['text'][:10].strip().lower())
                extracted_lines = []
                start_found = False
                for entry in line_number_map:
                    line_text = "".join(char["text"] for char in entry["line"]).strip()
                    line_text_lower = line_text.lower()
                    if len(line_text) < 4:
                        continue
                    if not start_found:
                        if re.search(start_regex, line_text_lower):
                            start_found = True
                            extracted_lines.append(line_text)
                        continue
                    else:
                        if re.search(end_regex, line_text_lower):
                            break
                        extracted_lines.append(line_text)
                if extracted_lines:
                    # Extract policy ID from current subheading
                    policy_id = extract_policy_id_from_text(subheadings[i]['text'])
                    
                    if policy_id:
                        filename_base = policy_id
                    else:
                        # Fallback to original naming if no policy ID found
                        filename_base = f"extracted_{i+1}_{subheadings[i]['text'][:10].replace(' ','_')}"
                    
                    txt_path = os.path.join(txt_dir, f"{filename_base}.txt")
                    json_path = os.path.join(json_dir, f"{filename_base}.json")
                    full_text = "\n".join(extracted_lines)

                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(full_text)

                    json_data = {
                        "subheading": subheadings[i]['text'],
                        "start_text": full_text[:50],
                        "content": full_text
                    }
                    with open(json_path, "w", encoding="utf-8") as jf:
                        json.dump(json_data, jf, indent=2)

                    print(f"[✅] Saved chunk {i+1}: {filename_base}")

            # Handle last subheading to section end
            if subheadings:
                last_sh = subheadings[-1]
                last_policy_id = extract_policy_id_from_text(last_sh['text'])
                
                if last_policy_id:
                    last_filename = last_policy_id
                else:
                    last_filename = f"extracted_last_{last_sh['text'][:10].replace(' ','_')}_to_end"
                
                last_out_txt = os.path.join(txt_dir, f"{last_filename}.txt")
                extract_last_subheading_to_section_end(last_sh, line_number_map, last_out_txt, json_dir)

            # Clean up Excel file
            try:
                os.remove(excel_path)
            except Exception as e:
                print(f"[❌] Failed to delete Excel {excel_path}: {e}")

        except Exception as e:
            print(f"[❌] Error processing section {section_id} {section_name}: {e}")
            continue

# Example usage:
# extracted_path = extract_document_sections("NIST.SP.800-53r5.pdf")    