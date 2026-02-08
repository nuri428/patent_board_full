"""
MCP Tools for Patent Identifier Extraction and URL Generation
특허 식별자 추출 및 URL 생성을 위한 MCP 도구 모듈
"""

import re
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class PatentIdentifier(BaseModel):
    """특허 식별자 정보"""
    id: str = Field(..., description="특허 번호")
    country: str = Field(..., description="국가 코드 (US, KR, WIPO 등)")
    type: str = Field(..., description="특허 유형 (utility, design, plant 등)")
    raw_text: str = Field(..., description="원본 텍스트")


class PatentUrl(BaseModel):
    """생성된 특허 URL 정보"""
    url: str = Field(..., description="생성된 URL")
    title: str = Field(..., description="URL 제목")
    source: str = Field(..., description="출처 (google, uspto, kipris 등)")
    country: str = Field(..., description="국가 코드")
    patent_id: str = Field(..., description="특허 ID")


class PatentExtractionResult(BaseModel):
    """특허 ID 추출 결과"""
    found: List[PatentIdentifier] = Field(default_factory=list, description="발견된 특허 ID 목록")
    raw_text: str = Field(..., description="원본 텍스트")
    has_patents: bool = Field(default=False, description="특허 ID 포함 여부")


class PatentUrlResult(BaseModel):
    """URL 생성 결과"""
    urls: List[PatentUrl] = Field(default_factory=list, description="생성된 URL 목록")
    errors: List[str] = Field(default_factory=list, description="발생한 오류")


class PatentIdentifierTool:
    """특허 식별자 추출 도구"""
    
    def __init__(self):
        # 정규식 패턴 정의
        self.patterns = {
            # 미국 특허: US1234567, US12,345,678, US2023-1234567, US20231234567
            'US': re.compile(
                r'\bUS(?:[-\s]?)?(?:(?:20|19)\d{2}[-\s]?)?\d{6,}(?:,\d{3})*(?:-\d+)?\b',
                re.IGNORECASE
            ),
            # 한국 특허: KR1020230001234, KR-10-2023-001234, KR10-2023-001234
            'KR': re.compile(
                r'\bKR(?:[-\s]?)?(?:10|20)[-\s]?\d{4}[-\s]?\d{7}\b',
                re.IGNORECASE
            ),
            # WIPO/PCT 특허: WO2023056789A1, PCT/IB2023/123456
            'WIPO': re.compile(
                r'\b(?:WO|PCT/)(?:IB|EP|US|JP|KR)/?\d{4}/?\d{6,}(?:[A-Z]\d+)?\b',
                re.IGNORECASE
            ),
            # 일반적인 특허 패턴 (국가코드 + 숫자)
            'GENERIC': re.compile(
                r'\b([A-Z]{2})[-\s]?\d{6,}(?:,\d{3})*(?:-\d+)?\b',
                re.IGNORECASE
            )
        }
    
    def extract_patent_ids(self, text: str) -> PatentExtractionResult:
        """입력 텍스트에서 특허 식별자 추출"""
        found_patents = []
        processed_text = text
        
        # 각 국가별 패턴으로 매칭
        for country, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                patent_id = self._normalize_patent_id(match.group(), country)
                if patent_id:
                    found_patents.append(PatentIdentifier(
                        id=patent_id,
                        country=country.upper(),
                        type=self._infer_patent_type(patent_id, country),
                        raw_text=match.group()
                    ))
                    # 원본 텍스트에서는 매칭된 부분 제거 (중복 방지)
                    processed_text = processed_text.replace(match.group(), '[PATENT]', 1)
        
        # 중복 제거
        unique_patents = list({p.id: p for p in found_patents}.values())
        
        return PatentExtractionResult(
            found=unique_patents,
            raw_text=text,
            has_patents=len(unique_patents) > 0
        )
    
    def _normalize_patent_id(self, raw_id: str, country: str) -> Optional[str]:
        """특허 ID 표준화"""
        # 특수문자 제거
        cleaned = re.sub(r'[-\s,]', '', raw_id.upper())
        
        # 국가 코드 제거 (중복 방지)
        if cleaned.startswith('US'):
            cleaned = cleaned[2:]
        elif cleaned.startswith('KR'):
            cleaned = cleaned[2:]
        elif cleaned.startswith('WO'):
            cleaned = cleaned[2:]
        
        # 길이 검증
        if country == 'US' and (6 <= len(cleaned) <= 12):
            return f"US{cleaned}"
        elif country == 'KR' and len(cleaned) == 11:
            return f"KR{cleaned}"
        elif country == 'WIPO' and len(cleaned) >= 8:
            return f"WO{cleaned}"
        elif country == 'GENERIC' and len(cleaned) >= 6:
            return f"{raw_id[:2]}{cleaned}"  # 원본 국가코드 유지
        
        return None
    
    def _infer_patent_type(self, patent_id: str, country: str) -> str:
        """특허 유형 추론"""
        if country == 'US':
            if len(patent_id) > 8:
                return 'utility'  # 발명특허 (긴 번호)
            else:
                return 'design'  # 디자인특허 (짧은 번호)
        elif country == 'KR':
            return 'utility'  # 한국은 대부분 발명특허
        elif country == 'WIPO':
            return 'international'
        return 'unknown'


class PatentUrlGenerator:
    """특허 URL 생성 도구"""
    
    def __init__(self):
        # URL 템플릿 정의
        self.url_templates = {
            'US': {
                'google': 'https://patents.google.com/patent/US{patent_id}',
                'uspto': 'https://ppubs.uspto.gov/pubweb/numsearch?search=US{patent_id}',
                'patft': 'https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv&r=0&p=1&f=S&l=50&d=PG01&OS={patent_id}&RS={patent_id}'
            },
            'KR': {
                'google': 'https://patents.google.com/patent/KR{patent_id}',
                'kipris': 'https://plus.kipris.or.kr/patent/DetailPatent?pubnum={patent_id}',
                'kipris_web': 'https://www.kipris.or.kr/kisis/pro/patent/patnScheP.do?reSearch=Y&pubnum={patent_id}'
            },
            'WIPO': {
                'google': 'https://patents.google.com/patent/WO{patent_id}',
                'wipo': 'https://patentscope.wipo.int/search/en/detail.jsf?docId={patent_id}'
            }
        }
        
        # 소스별 제목
        self.source_titles = {
            'google': 'Google Patents',
            'uspto': 'USPTO Patent Full Text',
            'patft': 'USPTO Patent Database',
            'kipris': 'KIPRI Patent Database',
            'kipris_web': 'KIPRI Web Service',
            'wipo': 'WIPO Patentscope'
        }
    
    def generate_urls(self, patent_identifiers: List[PatentIdentifier], 
                     sources: Optional[List[str]] = None) -> PatentUrlResult:
        """특허 식별자로 URL 생성"""
        generated_urls = []
        errors = []
        
        # 기본 소스 설정
        if sources is None:
            sources = ['google']  # 기본은 Google Patents
        
        for patent in patent_identifiers:
            country = patent.country
            patent_id = patent.id
            
            # 국가별 사용 가능한 소스 확인
            available_sources = self.url_templates.get(country, {}).keys()
            valid_sources = [s for s in sources if s in available_sources]
            
            if not valid_sources:
                errors.append(f"No URL sources available for {country} patents")
                continue
            
            # 각 소스별 URL 생성
            for source in valid_sources:
                try:
                    template = self.url_templates[country][source]
                    clean_patent_id = patent_id
                    if clean_patent_id.startswith(country):
                        clean_patent_id = clean_patent_id[len(country):]
                    
                    url = template.format(patent_id=clean_patent_id)
                    
                    generated_urls.append(PatentUrl(
                        url=url,
                        title=self.source_titles.get(source, source),
                        source=source,
                        country=country,
                        patent_id=patent_id
                    ))
                except Exception as e:
                    errors.append(f"Failed to generate URL for {patent_id} from {source}: {str(e)}")
        
        return PatentUrlResult(
            urls=generated_urls,
            errors=errors
        )
    
    def generate_complete_response(self, text: str, 
                                 include_sources: Optional[List[str]] = None) -> Dict:
        """완전한 응답 생성 (특허 ID 추출 + URL 생성)"""
        # 특허 ID 추출
        identifier_tool = PatentIdentifierTool()
        extraction_result = identifier_tool.extract_patent_ids(text)
        
        if not extraction_result.found:
            return {
                "has_patents": False,
                "message": "No patent identifiers found in the text.",
                "extraction": extraction_result.model_dump()
            }
        
        # URL 생성
        url_result = self.generate_urls(extraction_result.found, include_sources)
        
        # 응답 포맷팅
        response = {
            "has_patents": True,
            "patent_count": len(extraction_result.found),
            "extracted_patents": extraction_result.found,
            "generated_urls": url_result.urls,
            "errors": url_result.errors,
            "message": self._format_response_message(extraction_result.found, url_result.urls)
        }
        
        return response
    
    def _format_response_message(self, patents: List[PatentIdentifier], 
                                urls: List[PatentUrl]) -> str:
        """응답 메시지 포맷팅"""
        if not patents:
            return "No patent identifiers found."
        
        message = f"Found {len(patents)} patent identifier(s):\n"
        
        for i, patent in enumerate(patents, 1):
            patent_sources = [url for url in urls if url.patent_id == patent.id]
            sources_text = ", ".join([f"{url.title}" for url in patent_sources])
            message += f"\n{i}. {patent.id} ({patent.country}): {sources_text}"
        
        return message


# 전역 인스턴스 생성
patent_identifier_tool = PatentIdentifierTool()
patent_url_generator = PatentUrlGenerator()


# MCP 도구로 노출될 함수
def extract_patent_ids(text: str) -> Dict:
    """특허 식별자 추출 도구"""
    result = patent_identifier_tool.extract_patent_ids(text)
    return result.dict()


def generate_patent_urls(patent_ids: List[str], country: str, 
                        sources: Optional[List[str]] = None) -> Dict:
    """특허 URL 생성 도구"""
    # patent_ids를 PatentIdentifier로 변환
    patents = []
    for pid in patent_ids:
        patents.append(PatentIdentifier(
            id=pid,
            country=country,
            type='unknown',
            raw_text=pid
        ))
    
    result = patent_url_generator.generate_urls(patents, sources)
    return result.dict()


def analyze_patent_text(text: str) -> Dict:
    """텍스트 내 특허 정보 분석 (통합 도구)"""
    return patent_url_generator.generate_complete_response(text)


# 테스트 함수
def test_patent_extraction():
    """특허 ID 추출 테스트"""
    test_cases = [
        "US1234567에 대해 알려주세요",
        "KR1020230001234와 KR10-2023-001234를 비교해 주세요",
        "WO2023056789A1 특허의 상세 정보가 필요합니다",
        "US2023-1234567, US11,223,344 여러 미국 특허가 있습니다",
        "관련없는 텍스트입니다"
    ]
    
    tool = PatentIdentifierTool()
    
    for test_text in test_cases:
        print(f"\n테스트 텍스트: {test_text}")
        result = tool.extract_patent_ids(test_text)
        print(f"결과: {len(result.found)}개 특허 발견")
        for patent in result.found:
            print(f"  - {patent.id} ({patent.country})")


if __name__ == "__main__":
    test_patent_extraction()