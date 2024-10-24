import asyncio
import multiprocessing
import zipfile
import os
import argparse
from extractor import transform_path_data
from db_upsert import upsert_to_elasticsearch

BASE_PATH = './extractor/course-files'
SUBFOLDERS_TO_PROCESS = ['Exams', 'Mamans']

def extract_zip(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

async def extract_and_process_course(course_id, file_name):
    extracted_path = f'{BASE_PATH}/extracted/{course_id}'
    extract_zip(f'{BASE_PATH}/{file_name}', extracted_path)
    [extracted_dir_name] = [dir_name for dir_name in os.listdir(extracted_path) if course_id in dir_name]
    extracted_path = f'{extracted_path}/{extracted_dir_name}'
    mkdir_path = f'{BASE_PATH}/extracted/{course_id}/transformed'
    if not os.path.exists(mkdir_path):
        os.makedirs(mkdir_path)
    coroutines = []
    with multiprocessing.Pool(4) as pool:
        for subfolder in SUBFOLDERS_TO_PROCESS:
            subfolder_path = f'{extracted_path}/{subfolder}'
            if not os.path.exists(subfolder_path):
                print(f"Subfolder {subfolder} not found in {course_id}")
                continue
            results = []
            coroutines.append(transform_path_data(course_id, subfolder_path, pool, results))
        results = await asyncio.gather(*coroutines)
        [item.wait() for proc in results for item in proc]
    print(f"Finished extracting {course_id}")

def format_index_name(course_name):
    return course_name.replace(".zip", "").replace(" ", "_").lower()

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--course', type=str, required=True, help="Course id to extract and process")
    args = parser.parse_args()
    course_id = args.course
    available_files = os.listdir(BASE_PATH)
    coroutines = []
    [course_file] = [file for file in available_files if course_id in file]
    if not course_file:
        print(f"Course {course_id} file not found")
        exit(1)
    course_name = course_file
    await extract_and_process_course(course_id, course_file)
    await asyncio.gather(*coroutines)
    await upsert_to_elasticsearch(index_name=format_index_name(course_name), path=f"{BASE_PATH}/extracted/{course_id}/transformed")
    print('Finished processing course')
    exit(0)


if __name__ == '__main__':
    asyncio.run(main())
