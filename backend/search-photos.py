import json
import boto3
import urllib3

# --- CONFIGURATION ---
OS_DOMAIN = 'exampple of os domain ' # Your OS Domain
OS_INDEX = 'photos'
OS_AUTH = ('example', 'example!')

# LEX CONFIGURATION 
LEX_BOT_ID = 'BX1H9FKPB2'      
LEX_BOT_ALIAS_ID = 'TSTALIASID' 

# --- CLIENTS ---
lex_client = boto3.client('lexv2-runtime')
http = urllib3.PoolManager()

def lambda_handler(event, context):
    print("Received Event:", json.dumps(event))
    
    # 1. Extract the Query
    q = 'trees' 
    if event.get('queryStringParameters') and event['queryStringParameters'].get('q'):
        q = event['queryStringParameters']['q']
    
    print(f"Raw Query: {q}")
    
    keywords = []
    
    # 2. DISAMBIGUATE via LEX (Strict Assignment Req 3.c.i)
    # We send the sentence to Lex. Lex decides what the "Keyword" is.
    try:
        lex_response = lex_client.recognize_text(
            botId=LEX_BOT_ID,
            botAliasId=LEX_BOT_ALIAS_ID,
            localeId='en_US',
            sessionId='test-session-123', 
            text=q
        )
        
        print("Lex Response:", json.dumps(lex_response))
        
        # 3. Extract Slots (Assignment Req 3.c.ii)
        # Lex returns a nested JSON. We dig for the 'Keyword' slot.
        slots = lex_response.get('sessionState', {}).get('intent', {}).get('slots', {})
        
        if slots:
            for slot_name, slot_data in slots.items():
                # Check if Lex actually found a value
                if slot_data and slot_data.get('value'):
                    found_word = slot_data['value']['interpretedValue']
                    keywords.append(found_word)
                    print(f"Lex identified keyword: {found_word}")
                    
    except Exception as e:
        print(f"Lex Error: {e}")
        # If Lex fails (e.g. misconfiguration), fallback to raw query
        keywords = [q]

    # If Lex returned nothing (or error), use raw query
    if not keywords:
        keywords = [q]

    print(f"Final Search Keywords: {keywords}")

    # 4. Search OpenSearch 
    should_clause = [{"match": {"labels": k}} for k in keywords]
    query = {
        "size": 20,
        "query": {
            "bool": {
                "should": should_clause
            }
        }
    }
    
    # 5. Execute Search
    url = f'https://{OS_DOMAIN}/{OS_INDEX}/_search'
    headers = urllib3.make_headers(basic_auth=f"{OS_AUTH[0]}:{OS_AUTH[1]}")
    headers['Content-Type'] = 'application/json'
    
    results = []
    try:
        response = http.request('POST', url, body=json.dumps(query), headers=headers)
        response_body = json.loads(response.data.decode('utf-8'))
        
        hits = response_body.get('hits', {}).get('hits', [])
        results = [hit['_source'] for hit in hits]
    except Exception as e:
        print(f"Error searching OS: {e}")

# 6. Return Response
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",  # <--- THIS IS CRITICAL
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(results)
    }