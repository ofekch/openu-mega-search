# Openu Mega Search
enables search for course materials from the Openu Mega website. Specifically, it extracts and indexes course files from the Mega website and provides a search interface to search for course materials.
## Overview
This repository contains two main components:
1. **Extractor**: Responsible for extracting and processing course files.
2. **Search App**: Provides search functionality for the processed data.

## Extractor

### Prerequisites
- Python 3.x
- Elasticsearch 7.10.1
- Tesseract OCR with Hebrew language support

### Setup

1. **Install Python Requirements**:
    ```sh
    pip install -r extractor/requirements.txt
    ```

2. **Install Tesseract OCR**:
    - **macOS**:
        ```sh
        brew install tesseract-lang
        ```
    - **Ubuntu**:
        ```sh
        sudo apt-get install tesseract-ocr tesseract-ocr-heb
        ```

3. **Setup Elasticsearch**:
    - Download and install Elasticsearch 7.10.1 from the [official website](https://www.elastic.co/downloads/past-releases/elasticsearch-7-10-1).
    - Start Elasticsearch:
        ```sh
        ./bin/elasticsearch
        ```

4. **Set Environment Variables**:
    - Ensure the following environment variables are set:
        ```sh
        export ELASTICSEARCH_HOST=<your_elasticsearch_host>
        export ELASTICSEARCH_PORT=<your_elasticsearch_port>
        export ELASTICSEARCH_USERNAME=<your_elasticsearch_username>
        export ELASTICSEARCH_PASSWORD=<your_elasticsearch_username>
        ```

### Running the Extractor

1. **Download Course Zip from Mega**:
    - Download the course zip file from Mega and place it in the `./extractor/course-files` directory.

2. **Run the Extractor**:
    - Use the following command to run the extractor:
        ```sh
        python3 ./extractor/main.py --course="<course_id>"
        ```

    Replace `<course_id>` with the ID of the course you want to process.

## Search App

### Prerequisites
- Node.js
- npm
- Elasticsearch 7.10.1

### Setup

1. **Install Dependencies**:
    ```sh
    cd search-app
    npm install
    ```

3. **Setup Elasticsearch**:
    - Download and install Elasticsearch 7.10.1 from the [official website](https://www.elastic.co/downloads/past-releases/elasticsearch-7-10-1).
    - Start Elasticsearch:
        ```sh
        ./bin/elasticsearch
        ```

4. **Set Environment Variables**:
    - Ensure the following environment variables are set:
        ```sh
        export ELASTICSEARCH_HOST=<your_elasticsearch_host>
        export ELASTICSEARCH_PORT=<your_elasticsearch_port>
        export ELASTICSEARCH_USERNAME=<your_elasticsearch_username>
        export ELASTICSEARCH_PASSWORD=<your_elasticsearch_username>
        ```

### Running the Search App
To start the search app, use the following command:
```sh
npm run dev