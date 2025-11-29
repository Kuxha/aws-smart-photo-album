# 📸 Smart Photo Album - AWS Serverless Application

## Overview
This is a cloud-native intelligent photo search application built for the NYU Cloud Computing course. It allows users to upload photos with custom tags and search for them using natural language queries (e.g., "show me dogs and trees"). The application leverages AWS Serverless architecture to ensure scalability and cost-efficiency.

## Architecture
**Services Used:**
* **Frontend:** S3 (Static Web Hosting), API Gateway SDK.
* **API Layer:** API Gateway (REST), CORS enabled.
* **Backend:** AWS Lambda (Python 3.12).
* **NLP:** Amazon Lex (Intent recognition & Keyword extraction).
* **AI/ML:** Amazon Rekognition (Object detection).
* **Search Engine:** Amazon OpenSearch (Metadata indexing).
* **Storage:** Amazon S3 (Raw image storage).

## Project Structure
* `/frontend` - Contains the Single Page Application (HTML/JS) and generated SDK.
* `/backend` - Python code for Lambda functions (`index-photos` and `search-photos`).


## Features
1.  **AI-Powered Indexing:** Automatically detects labels in uploaded photos using Rekognition.
2.  **Voice/Text Search:** Uses Lex to disambiguate natural language queries.
3.  **Custom Metadata:** Supports user-defined labels via S3 Metadata headers.
4.  **Direct Uploads:** Utilizes API Gateway S3 Proxy for secure, direct binary uploads.

## Setup
1.  **Frontend:** Upload the contents of the `frontend` folder to a public S3 bucket enabled for Static Website Hosting.
2.  **Backend:** Deploy the Python scripts to AWS Lambda.