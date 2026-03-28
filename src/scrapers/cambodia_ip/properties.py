import json

from urllib.parse import urlencode

properties = {
    "page_url": "https://digitalip.cambodiaip.gov.kh/en/trademark-search",
    "page_details_url": "https://digitalip.cambodiaip.gov.kh/en/trademark-search/trademark-detail",
    "api_url": "https://digitalip.cambodiaip.gov.kh/api/v1/web/trademark-search",
    "image_url": "https://digitalip.cambodiaip.gov.kh/trademark-detail-logo/{code}?type=ts_logo_detail_screen",
    "api_headers": {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es-VE;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://digitalip.cambodiaip.gov.kh',
    }
}

def get_payload_filter_api(filing_number: str) -> dict:
    
    filter = {
        "data": {
            "page": 1,
            "perPage": 20,
            "search": {
            "key": "all",
            "value": ""
            },
            "filter": {
            "province": [],
            "country": [],
            "status": [],
            "applicationType": [],
            "markFeature": [],
            "classification": [],
            "date": [],
            "fillDate": [],
            "regisDate": [],
            "receptionDate": []
            },
            "sortBy": "",
            "advanceSearch": [
            {
                "type": "filing_number",
                "strategy": "contains_word",
                "selectedValues": [
                filing_number
                ],
                "inputValue": "",
                "connectingOperator": "OR"
            }
            ],
            "isAdvanceSearch": False,
            "dateOption": "",
            "typeSubmit": "filter"
        }
    }
    
    return filter

def build_page_url(code_id: str, filing_number: str):
    url = properties["page_details_url"] + "?" + "afnb=" + code_id
    filter_payload_data = get_payload_filter_api(filing_number=filing_number).get("data")
    formatted_payload = {
        "tab": "0",
        "page": str(filter_payload_data['page']),
        "per_page": str(filter_payload_data['perPage']),
        "search": json.dumps(filter_payload_data['search']),
        "filter": json.dumps(filter_payload_data['filter']),
        "sort_by": filter_payload_data['sortBy'],
        "advance_search": json.dumps(filter_payload_data['advanceSearch']),
        "is_advanced_search": str(filter_payload_data['isAdvanceSearch']).lower(),
        "date_option": filter_payload_data['dateOption']
    }
    filter_payload_string = json.dumps((formatted_payload))
    params = {
        "mdftyp": "biblio",
        "callback_url": "/trademark-search/new",
        "callback_query": filter_payload_string
    }
    
    encoded_params = urlencode(params)
    
    return url + "&" + encoded_params