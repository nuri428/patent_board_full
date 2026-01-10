import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import logging
from django.conf import settings
from .patent_db import Patent

logger = logging.getLogger(__name__)


class KoreanPatentLookup:
    KIPRIS_API_BASE_URL = "http://kipris.or.kr/kipris/openapi/rest"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'KIPRIS_API_KEY', None)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Patent-Board-System/1.0',
            'Accept': 'application/xml'
        })
    
    def search_patents(self, 
                      query: Optional[str] = None,
                      title: Optional[str] = None,
                      assignee: Optional[str] = None,
                      inventor: Optional[str] = None,
                      ipc_code: Optional[str] = None,
                      application_date_from: Optional[str] = None,
                      application_date_to: Optional[str] = None,
                      publication_date_from: Optional[str] = None,
                      publication_date_to: Optional[str] = None,
                      page: int = 1,
                      per_page: int = 20) -> List[Dict]:
        endpoints = []
        
        if title:
            endpoints.append(('documentSearch', {
                'searchString': title,
                'searchField': 'INVENTION_TITLE'
            }))
        
        if assignee:
            endpoints.append(('applicantSearch', {
                'searchString': assignee,
                'searchField': 'APPLICANT_NAME'
            }))
        
        if inventor:
            endpoints.append(('inventorSearch', {
                'searchString': inventor,
                'searchField': 'INVENTOR_NAME'
            }))
        
        if ipc_code:
            endpoints.append(('ipcSearch', {
                'searchString': ipc_code,
                'searchField': 'IPC_CODE'
            }))
        
        if query:
            endpoints.append(('advancedSearch', {
                'searchString': query,
                'searchField': 'ALL'
            }))
        
        all_results = []
        
        for endpoint, params in endpoints:
            try:
                url = f"{self.KIPRIS_API_BASE_URL}/{endpoint}.do"
                api_params = {
                    'accessKey': self.api_key,
                    'pageNo': page,
                    'perPage': per_page,
                    'sortSpec': 'AD',
                    'descending': 'true',
                    **params
                }
                
                if application_date_from:
                    api_params['applicationDateStart'] = application_date_from.replace('-', '')
                if application_date_to:
                    api_params['applicationDateEnd'] = application_date_to.replace('-', '')
                if publication_date_from:
                    api_params['publicationDateStart'] = publication_date_from.replace('-', '')
                if publication_date_to:
                    api_params['publicationDateEnd'] = publication_date_to.replace('-', '')
                
                response = self.session.get(url, params=api_params, timeout=30)
                response.raise_for_status()
                
                results = self._parse_kipris_response(response.text)
                all_results.extend(results)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error searching KIPRIS {endpoint}: {str(e)}")
                continue
        
        return all_results
    
    def get_patent_details(self, patent_number: Optional[str] = None, application_number: Optional[str] = None) -> Optional[Dict]:
        if not patent_number and not application_number:
            raise ValueError("Either patent_number or application_number must be provided")
        
        search_id = application_number or patent_number
        
        try:
            url = f"{self.KIPRIS_API_BASE_URL}/patentInfoService.do"
            params = {
                'accessKey': self.api_key,
                'serviceKey': self.api_key
            }
            
            if application_number:
                params['applicationNumber'] = application_number
            else:
                params['patentNumber'] = patent_number
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return self._parse_patent_details(response.text)
            
        except Exception as e:
            logger.error(f"Error getting patent details for {search_id}: {str(e)}")
            return None
    
    def _parse_kipris_response(self, xml_data: str) -> List[Dict]:
        patents = []
        try:
            root = ET.fromstring(xml_data)
            
            for item in root.findall('.//item'):
                patent_data = {
                    'patent_id': self._get_text(item, 'applicationNumber'),
                    'country': 'KR',
                    'title': self._get_text(item, 'inventionTitle'),
                    'abstract': self._get_text(item, 'abstract'),
                    'assignee': self._get_text(item, 'applicantName'),
                    'inventors': self._parse_inventors(item),
                    'filing_date': self._parse_date(self._get_text(item, 'applicationDate')),
                    'publication_date': self._parse_date(self._get_text(item, 'publicationDate')),
                    'grant_date': self._parse_date(self._get_text(item, 'registrationDate')),
                    'ipc_classifications': self._parse_ipc_codes(item),
                    'status': self._determine_status(self._get_text(item, 'registrationDate')),
                    'priority_date': self._parse_date(self._get_text(item, 'priorityDate')),
                    'family_id': self._get_text(item, 'familyId'),
                    'patent_type': self._determine_patent_type(self._get_text(item, 'applicationNumber')),
                }
                patents.append(patent_data)
                
        except Exception as e:
            logger.error(f"Error parsing KIPRIS response: {str(e)}")
        
        return patents
    
    def _parse_patent_details(self, xml_data: str) -> Optional[Dict]:
        try:
            root = ET.fromstring(xml_data)
            item = root.find('.//item')
            
            if item is None:
                return None
            
            patent_data = {
                'patent_id': self._get_text(item, 'applicationNumber'),
                'country': 'KR',
                'title': self._get_text(item, 'inventionTitle'),
                'abstract': self._get_text(item, 'abstract'),
                'claims': self._get_text(item, 'claims'),
                'description': self._get_text(item, 'description'),
                'assignee': self._get_text(item, 'applicantName'),
                'inventors': self._parse_inventors(item),
                'applicants': self._parse_applicants(item),
                'filing_date': self._parse_date(self._get_text(item, 'applicationDate')),
                'publication_date': self._parse_date(self._get_text(item, 'publicationDate')),
                'grant_date': self._parse_date(self._get_text(item, 'registrationDate')),
                'ipc_classifications': self._parse_ipc_codes(item),
                'status': self._determine_status(self._get_text(item, 'registrationDate')),
                'priority_date': self._parse_date(self._get_text(item, 'priorityDate')),
                'family_id': self._get_text(item, 'familyId'),
                'patent_type': self._determine_patent_type(self._get_text(item, 'applicationNumber')),
                'legal_status': self._get_text(item, 'legalStatus'),
            }
            
            return patent_data
            
        except Exception as e:
            logger.error(f"Error parsing patent details: {str(e)}")
            return None
    
    def _get_text(self, element, tag):
        found = element.find(tag)
        return found.text.strip() if found is not None and found.text else None
    
    def _parse_inventors(self, item) -> List[str]:
        inventors = []
        inventor_elements = item.findall('.//inventorName')
        for element in inventor_elements:
            if element.text:
                inventors.append(element.text.strip())
        return inventors
    
    def _parse_applicants(self, item) -> List[str]:
        applicants = []
        applicant_elements = item.findall('.//applicantName')
        for element in applicant_elements:
            if element.text:
                applicants.append(element.text.strip())
        return applicants
    
    def _parse_ipc_codes(self, item) -> List[str]:
        codes = []
        code_elements = item.findall('.//ipcCode')
        for element in code_elements:
            if element.text:
                codes.append(element.text.strip())
        return codes
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        if not date_str or date_str.strip() == '':
            return None
        
        try:
            # KIPRIS date format: YYYYMMDD
            if len(date_str.strip()) == 8:
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                return f"{year}-{month}-{day}"
            return date_str.strip()
        except:
            return date_str.strip()
    
    def _determine_status(self, registration_date: Optional[str]) -> str:
        if not registration_date or registration_date.strip() == '':
            return 'pending'
        return 'granted'
    
    def _determine_patent_type(self, application_number: Optional[str]) -> str:
        if not application_number:
            return 'utility'
        
        # Korean patent number patterns
        if '10-' in application_number or application_number.startswith('10'):
            return 'utility'
        elif '20-' in application_number or application_number.startswith('20'):
            return 'utility'  # Utility model
        elif '30-' in application_number or application_number.startswith('30'):
            return 'design'
        
        return 'utility'
    
    def save_to_database(self, patent_data: Dict) -> Patent:
        patent, created = Patent.objects.update_or_create(
            patent_id=patent_data['patent_id'],
            defaults=patent_data
        )
        
        if created:
            logger.info(f"Created new patent: {patent_data['patent_id']}")
        else:
            logger.info(f"Updated patent: {patent_data['patent_id']}")
        
        return patent
    
    def search_and_save(self, **search_params) -> List[Patent]:
        results = self.search_patents(**search_params)
        saved_patents = []
        
        for patent_data in results:
            try:
                patent = self.save_to_database(patent_data)
                saved_patents.append(patent)
            except Exception as e:
                logger.error(f"Error saving patent {patent_data.get('patent_id', 'unknown')}: {str(e)}")
                continue
        
        return saved_patents


class USPatentLookup:
    USPTO_API_BASE_URL = "https://patft.uspto.gov"
    PEDS_API_BASE_URL = "https://ped.uspto.gov/api"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'USPTO_API_KEY', None)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Patent-Board-System/1.0',
            'Accept': 'application/json'
        })
    
    def search_patents(self,
                      query: Optional[str] = None,
                      title: Optional[str] = None,
                      assignee: Optional[str] = None,
                      inventor: Optional[str] = None,
                      ipc_code: Optional[str] = None,
                      abstract: Optional[str] = None,
                      filing_date_from: Optional[str] = None,
                      filing_date_to: Optional[str] = None,
                      grant_date_from: Optional[str] = None,
                      grant_date_to: Optional[str] = None,
                      limit: int = 20) -> List[Dict]:
        
        search_params = {
            'q': self._build_query_string(
                query=query, title=title, assignee=assignee, 
                inventor=inventor, ipc_code=ipc_code, abstract=abstract
            ),
            'f': 'json',
            'c': limit
        }
        
        if filing_date_from or filing_date_to:
            date_filter = f"isd:[{filing_date_from} TO {filing_date_to}]"
            search_params['q'] += f" AND {date_filter}"
        
        if grant_date_from or grant_date_to:
            grant_filter = f"pd:[{grant_date_from} TO {grant_date_to}]"
            search_params['q'] += f" AND {grant_filter}"
        
        try:
            url = f"{self.USPTO_API_BASE_URL}/netacgi/nph-Parser"
            response = self.session.get(url, params=search_params, timeout=30)
            response.raise_for_status()
            
            return self._parse_uspto_response(response.text)
            
        except Exception as e:
            logger.error(f"Error searching USPTO: {str(e)}")
            return []
    
    def get_patent_details(self, patent_number: str) -> Optional[Dict]:
        try:
            # Try PEDS API first
            peds_url = f"{self.PEDS_API_BASE_URL}/searches"
            peds_params = {
                'q': f"patentNumber:{patent_number}"
            }
            
            response = self.session.get(peds_url, params=peds_params, timeout=30)
            
            if response.status_code == 200:
                return self._parse_peds_response(response.json())
            else:
                # Fallback to full-text parsing
                return self._get_patent_details_fulltext(patent_number)
                
        except Exception as e:
            logger.error(f"Error getting US patent details for {patent_number}: {str(e)}")
            return None
    
    def _build_query_string(self, query: Optional[str] = None, title: Optional[str] = None, 
                           assignee: Optional[str] = None, inventor: Optional[str] = None, 
                           ipc_code: Optional[str] = None, abstract: Optional[str] = None) -> str:
        query_parts = []
        
        if title:
            query_parts.append(f'ttl:("{title}")')
        if assignee:
            query_parts.append(f'anm:("{assignee}")')
        if inventor:
            query_parts.append(f'inm:("{inventor}")')
        if ipc_code:
            query_parts.append(f'icl:("{ipc_code}")')
        if abstract:
            query_parts.append(f'abst:("{abstract}")')
        if query:
            query_parts.append(f'("{query}")')
        
        return ' AND '.join(query_parts) if query_parts else '*'
    
    def _parse_uspto_response(self, response_text: str) -> List[Dict]:
        patents = []
        try:
            import json
            data = json.loads(response_text) if isinstance(response_text, str) else response_text
            
            if 'query' in data and 'results' in data['query']:
                for result in data['query']['results']:
                    patent_data = {
                        'patent_id': result.get('patentNumber', ''),
                        'country': 'US',
                        'title': result.get('title', ''),
                        'abstract': result.get('abstract', ''),
                        'assignee': result.get('assigneeEntityName', ''),
                        'inventors': self._parse_uspto_inventors(result),
                        'filing_date': self._parse_uspto_date(result.get('applicationDate')),
                        'publication_date': self._parse_uspto_date(result.get('publicationDate')),
                        'grant_date': self._parse_uspto_date(result.get('grantDate')),
                        'status': 'granted' if result.get('grantDate') else 'pending',
                        'ipc_classifications': result.get('mainClassification', '').split(';') if result.get('mainClassification') else [],
                        'patent_type': self._determine_us_patent_type(result.get('patentNumber', '')),
                    }
                    patents.append(patent_data)
                    
        except Exception as e:
            logger.error(f"Error parsing USPTO response: {str(e)}")
        
        return patents
    
    def _parse_peds_response(self, data: Dict) -> Optional[Dict]:
        try:
            if not data.get('query', {}).get('results'):
                return None
            
            result = data['query']['results'][0]
            patent_data = {
                'patent_id': result.get('patentNumber', ''),
                'country': 'US',
                'title': result.get('title', ''),
                'abstract': result.get('abstract', ''),
                'claims': result.get('claims', ''),
                'description': result.get('description', ''),
                'assignee': result.get('assigneeEntityName', ''),
                'inventors': self._parse_peds_inventors(result),
                'applicants': self._parse_peds_applicants(result),
                'filing_date': self._parse_peds_date(result.get('applicationDate')),
                'publication_date': self._parse_peds_date(result.get('publicationDate')),
                'grant_date': self._parse_peds_date(result.get('grantDate')),
                'ipc_classifications': result.get('mainClassification', '').split(';') if result.get('mainClassification') else [],
                'uspc_classifications': result.get('uspc', '').split(';') if result.get('uspc') else [],
                'status': 'granted' if result.get('grantDate') else 'pending',
                'family_id': result.get('familyId', ''),
                'patent_type': self._determine_us_patent_type(result.get('patentNumber', '')),
                'legal_status': result.get('legalStatus', ''),
            }
            
            return patent_data
            
        except Exception as e:
            logger.error(f"Error parsing PEDS response: {str(e)}")
            return None
    
    def _get_patent_details_fulltext(self, patent_number: str) -> Optional[Dict]:
        try:
            url = f"{self.USPTO_API_BASE_URL}/netacgi/nph-Parser"
            params = {
                'patentnumber': patent_number,
                'patentnumber': patent_number,
                'type': 'patent'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return self._parse_fulltext_patent(response.text, patent_number)
            
        except Exception as e:
            logger.error(f"Error getting fulltext patent details: {str(e)}")
            return None
    
    def _parse_fulltext_patent(self, html_content: str, patent_number: str) -> Dict:
        # This would require HTML parsing implementation
        # For now, return basic structure
        return {
            'patent_id': patent_number,
            'country': 'US',
            'title': '',
            'abstract': '',
            'status': 'pending',
            'patent_type': 'utility',
        }
    
    def _parse_uspto_inventors(self, result: Dict) -> List[str]:
        inventors = []
        if 'inventors' in result:
            for inventor in result['inventors']:
                if isinstance(inventor, dict) and 'name' in inventor:
                    inventors.append(inventor['name'])
        return inventors
    
    def _parse_peds_inventors(self, result: Dict) -> List[str]:
        inventors = []
        if 'inventorNameArray' in result:
            for inventor in result['inventorNameArray']:
                if isinstance(inventor, str):
                    inventors.append(inventor.strip())
        return inventors
    
    def _parse_peds_applicants(self, result: Dict) -> List[str]:
        applicants = []
        if 'applicantNameArray' in result:
            for applicant in result['applicantNameArray']:
                if isinstance(applicant, str):
                    applicants.append(applicant.strip())
        return applicants
    
    def _parse_uspto_date(self, date_str: str) -> Optional[str]:
        if not date_str:
            return None
        return date_str
    
    def _parse_peds_date(self, date_str: str) -> Optional[str]:
        if not date_str:
            return None
        
        try:
            # PEDS date format might be YYYY-MM-DD
            return date_str.split('T')[0] if 'T' in date_str else date_str
        except:
            return date_str
    
    def _determine_us_patent_type(self, patent_number: str) -> str:
        if not patent_number:
            return 'utility'
        
        # US patent number patterns
        if patent_number.startswith('D'):
            return 'design'
        elif patent_number.startswith('PP'):
            return 'plant'
        else:
            return 'utility'
    
    def save_to_database(self, patent_data: Dict) -> Patent:
        patent, created = Patent.objects.update_or_create(
            patent_id=patent_data['patent_id'],
            defaults=patent_data
        )
        
        if created:
            logger.info(f"Created new US patent: {patent_data['patent_id']}")
        else:
            logger.info(f"Updated US patent: {patent_data['patent_id']}")
        
        return patent
    
    def search_and_save(self, **search_params) -> List[Patent]:
        results = self.search_patents(**search_params)
        saved_patents = []
        
        for patent_data in results:
            try:
                patent = self.save_to_database(patent_data)
                saved_patents.append(patent)
            except Exception as e:
                logger.error(f"Error saving US patent {patent_data.get('patent_id', 'unknown')}: {str(e)}")
                continue
        
        return saved_patents