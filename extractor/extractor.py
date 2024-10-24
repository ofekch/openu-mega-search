import asyncio
import json
import os
import hashlib
from datetime import datetime

import pytesseract
from pdf2image import convert_from_path
import unicodedata
import re
custom_config = r'--oem 3 --psm 6'

def format_text_after_extraction(raw_text):
    text = raw_text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[\u200B-\u200F\uFEFF]', '', text)  # Removes zero-width, RLM, LRM, etc.
    text = ''.join([char for char in text if char.isprintable()])
    return text

def extract_text_from_pdf(pdf_path):
    text_heb_eng = ''
    text_heb = ''
    print('converting file', pdf_path)
    pages = convert_from_path(pdf_path, 300)
    print('converted file', pdf_path, len(pages))
    i = 0
    for page in pages:
        i+=1
        print('on page', pdf_path, i)
        text_heb += pytesseract.image_to_string(page, lang='heb', config=custom_config)
        text_heb_eng += pytesseract.image_to_string(page, lang='heb+eng', config=custom_config)
    return format_text_after_extraction(text_heb), format_text_after_extraction(text_heb_eng)

FILE_EXTRACTORS_BY_TYPE = {
    'pdf': extract_text_from_pdf
}

def calculate_file_hash(file_path, algorithm='md5'):
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

async def async_list_dir(path):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, os.listdir, path)

async def async_is_dir(path):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, os.path.isdir, path)

def transform_file_data(course_id, file_path):
    file_type = file_path.split('.')[-1]
    if file_type not in FILE_EXTRACTORS_BY_TYPE:
        print(f"Extractor for {file_type} not found", file_path)
        return
    if os.path.getsize(file_path) > 100000000: #100MB
        print(f"File too large", file_path)
        return
    file_hash = calculate_file_hash(file_path)
    output_path = f'./extractor/course-files/extracted/{course_id}/transformed/{file_hash}.json'
    if os.path.exists(output_path):
        print(f"File already exists, skipping", file_path)
        return
    text_heb, text_heb_eng = FILE_EXTRACTORS_BY_TYPE[file_type](file_path)
    try:
        with open(output_path, 'w', encoding="utf-8") as f:
            json.dump({
                'course_id': course_id,
                'timestamp': datetime.utcnow().isoformat(),
                'hash': file_hash,
                'text_heb': text_heb,
                'text_heb_eng': text_heb_eng,
                'file_path': file_path.split(f'/{course_id}/')[1]
            }, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to write file {output_path}", e)


async def transform_path_data(course_id, path, pool, results):
    coroutines = []
    is_directory = await async_is_dir(path)
    if not is_directory:
        return [*results, pool.apply_async(transform_file_data, (course_id, path))]
    dir_content = await async_list_dir(path)
    for obj in dir_content:
        next_path = f'{path}/{obj}'
        coroutines.append(transform_path_data(course_id, next_path, pool, results))
    transform_results = await asyncio.gather(*coroutines)
    return [*results, *[item for sublist in transform_results for item in sublist]]
