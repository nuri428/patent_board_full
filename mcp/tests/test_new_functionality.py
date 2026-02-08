import asyncio
import httpx
import os
import sys
import json
from datetime import datetime

sys.path.append(os.getcwd())

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
API_KEY = "test-key-123456"

class TestNewMCPFunctionality:
    def __init__(self):
        self.test_results = {}
        self.failed_tests = []
        
    async def log_test(self, test_name, status, details=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {test_name}: {'✅ PASS' if status else '❌ FAIL'} {details}")
        if not status:
            self.failed_tests.append(test_name)
        self.test_results[test_name] = {"status": status, "details": details}
    
    async def test_health_check(self):
        """Test server health and connectivity"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{BASE_URL}/health")
                success = resp.status_code == 200
                await self.log_test(
                    "Server Health Check", 
                    success,
                    f"Status: {resp.status_code}"
                )
                return success
        except Exception as e:
            await self.log_test("Server Health Check", False, f"Exception: {str(e)}")
            return False

    async def test_tools_list(self):
        """Test that all new tools appear in tools list"""
        expected_new_tools = [
            "run_network_analysis",
            "create_technology_mapping", 
            "get_technology_mappings",
            "get_analysis_run_results"
        ]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(f"{BASE_URL}/tools/list", headers={"X-API-Key": API_KEY})
                success = resp.status_code == 200
                if success:
                    tools = resp.json()
                    tool_names = [t['name'] for t in tools]
                    missing_tools = [t for t in expected_new_tools if t not in tool_names]
                    found_new_tools = [t for t in expected_new_tools if t in tool_names]
                    
                    await self.log_test(
                        "Tools List Verification",
                        len(missing_tools) == 0,
                        f"New tools found: {found_new_tools}, Missing: {missing_tools}"
                    )
                else:
                    await self.log_test("Tools List Verification", False, f"Status: {resp.status_code}")
                return success
        except Exception as e:
            await self.log_test("Tools List Verification", False, f"Exception: {str(e)}")
            return False

    async def test_network_analysis(self):
        """Test Neo4j GDS network analysis functionality"""
        test_payload = {
            "node_types": ["Corporation", "Technology", "Patent"],
            "include_centrality": True,
            "include_communities": True,
            "include_link_prediction": True
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{BASE_URL}/tools/run_network_analysis",
                    json=test_payload,
                    headers={"X-API-Key": API_KEY}
                )
                
                if resp.status_code != 200:
                    await self.log_test(
                        "Network Analysis", 
                        False, 
                        f"HTTP {resp.status_code}: {resp.text[:200]}"
                    )
                    return False
                
                data = resp.json()
                success = (
                    'data' in data and
                    isinstance(data['data'], dict) and
                    'degree_centrality' in data['data'] and
                    'betweenness_centrality' in data['data'] and
                    'link_prediction' in data['data']
                )
                
                if success:
                    centrality_count = len(data['data']['degree_centrality'])
                    link_count = len(data['data']['link_prediction'])
                    await self.log_test(
                        "Network Analysis",
                        True,
                        f"Found {centrality_count} centrality items, {link_count} link predictions"
                    )
                else:
                    await self.log_test("Network Analysis", False, "Invalid response structure")
                    
                return success
                
        except Exception as e:
            await self.log_test("Network Analysis", False, f"Exception: {str(e)}")
            return False

    async def test_technology_mapping(self):
        """Test Technology V2 Mapper functionality"""
        # Test creating a mapping
        test_mapping = {
            "patent_id": "TEST-PATENT-001",
            "technology_id": "TECH-001", 
            "confidence": 0.85,
            "method": "IPC_MAPPING",
            "analysis_run_id": "TEST-RUN-001",
            "is_partial": False,
            "applied_config_version": "2.1.0",
            "synergy_bonus_applied": True,
            "negative_keywords_matched": ["obsolete", "deprecated"],
            "confidence_before_cap": 0.95
        }
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                # Create mapping
                create_resp = await client.post(
                    f"{BASE_URL}/tools/create_technology_mapping",
                    json=test_mapping,
                    headers={"X-API-Key": API_KEY}
                )
                
                create_success = create_resp.status_code == 200
                if not create_success:
                    await self.log_test(
                        "Create Technology Mapping",
                        False,
                        f"Create failed: {create_resp.status_code} - {create_resp.text[:200]}"
                    )
                    return False
                
                # Test retrieving mappings
                filter_payload = {
                    "analysis_run_id": "TEST-RUN-001",
                    "confidence_threshold": 0.5
                }
                
                retrieve_resp = await client.post(
                    f"{BASE_URL}/tools/get_technology_mappings",
                    json=filter_payload,
                    headers={"X-API-Key": API_KEY}
                )
                
                retrieve_success = retrieve_resp.status_code == 200
                if retrieve_success:
                    data = retrieve_resp.json()
                    if 'data' in data and isinstance(data['data'], list):
                        mappings = data['data']
                        test_mapping_found = any(
                            m.get('patent_id') == "TEST-PATENT-001" and 
                            m.get('confidence') == 0.85 
                            for m in mappings
                        )
                        
                        await self.log_test(
                            "Technology Mapping",
                            test_mapping_found,
                            f"Created: {create_success}, Retrieved: {len(mappings)} mappings, Test mapping found: {test_mapping_found}"
                        )
                    else:
                        await self.log_test("Technology Mapping", False, "Invalid retrieval response")
                else:
                    await self.log_test("Technology Mapping", False, f"Retrieve failed: {retrieve_resp.status_code}")
                    
                return create_success and retrieve_success
                
        except Exception as e:
            await self.log_test("Technology Mapping", False, f"Exception: {str(e)}")
            return False

    async def test_analysis_run_results(self):
        """Test comprehensive analysis run results functionality"""
        test_run_id = "TEST-RUN-001"
        payload = {
            "analysis_run_id": test_run_id,
            "include_opensearch": True,
            "include_neo4j": True,
            "include_tech_mappings": True,
            "limit": 50
        }
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    f"{BASE_URL}/tools/get_analysis_run_results",
                    json=payload,
                    headers={"X-API-Key": API_KEY}
                )
                
                if resp.status_code == 404:
                    # Expected if analysis run doesn't exist
                    await self.log_test(
                        "Analysis Run Results - Missing Run",
                        True,
                        "Correctly returned 404 for non-existent run"
                    )
                    return True
                elif resp.status_code != 200:
                    await self.log_test(
                        "Analysis Run Results",
                        False,
                        f"HTTP {resp.status_code}: {resp.text[:200]}"
                    )
                    return False
                
                data = resp.json()
                success = (
                    'data' in data and
                    isinstance(data['data'], dict) and
                    'analysis_run_id' in data['data'] and
                    'metadata' in data['data']
                )
                
                if success:
                    run_data = data['data']
                    has_opensearch = 'opensearch_sections' in run_data
                    has_neo4j = 'network_analysis' in run_data
                    has_mappings = 'technology_mappings' in run_data
                    
                    await self.log_test(
                        "Analysis Run Results",
                        True,
                        f"OpenSearch: {has_opensearch}, Neo4j: {has_neo4j}, Mappings: {has_mappings}"
                    )
                else:
                    await self.log_test("Analysis Run Results", False, "Invalid response structure")
                    
                return success
                
        except Exception as e:
            await self.log_test("Analysis Run Results", False, f"Exception: {str(e)}")
            return False

    async def test_opensearch_integration(self):
        """Test OpenSearch indexing and search functionality"""
        # Test patent section indexing
        test_section = {
            "analysis_run_id": "TEST-RUN-OS-001",
            "patent_id": "TEST-PATENT-OS-001", 
            "section_type": "ABSTRACT",
            "section_content": "This is a test abstract about artificial intelligence and machine learning systems for data processing.",
            "ipc_codes": ["G06N", "G06F"],
            "cpc_codes": ["G06N3/00", "G06F16/00"]
        }
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                # Index section
                index_resp = await client.post(
                    f"{BASE_URL}/tools/index_patent_sections",
                    json=test_section,
                    headers={"X-API-Key": API_KEY}
                )
                
                index_success = index_resp.status_code == 200
                if not index_success:
                    await self.log_test(
                        "OpenSearch Indexing",
                        False,
                        f"Index failed: {index_resp.status_code} - {index_resp.text[:200]}"
                    )
                    return False
                
                # Test search
                search_payload = {
                    "query": "artificial intelligence",
                    "section_types": ["ABSTRACT"],
                    "limit": 10,
                    "analysis_run_id": "TEST-RUN-OS-001"
                }
                
                search_resp = await client.post(
                    f"{BASE_URL}/tools/search_patent_sections",
                    json=search_payload,
                    headers={"X-API-Key": API_KEY}
                )
                
                search_success = search_resp.status_code == 200
                if search_success:
                    data = search_resp.json()
                    if 'data' in data and isinstance(data['data'], list):
                        results = data['data']
                        test_doc_found = any(
                            'TEST-PATENT-OS-001_ABSTRACT' in result.get('id', '')
                            for result in results
                        )
                        
                        await self.log_test(
                            "OpenSearch Integration",
                            test_doc_found,
                            f"Indexed: {index_success}, Search results: {len(results)}, Test doc found: {test_doc_found}"
                        )
                    else:
                        await self.log_test("OpenSearch Integration", False, "Invalid search response")
                else:
                    await self.log_test("OpenSearch Integration", False, f"Search failed: {search_resp.status_code}")
                    
                return index_success and search_success
                
        except Exception as e:
            await self.log_test("OpenSearch Integration", False, f"Exception: {str(e)}")
            return False

    async def test_semantic_search(self):
        """Test semantic search functionality"""
        payload = {
            "query": "machine learning algorithms",
            "limit": 5,
            "similarity_threshold": 0.7,
            "analysis_run_id": "TEST-RUN-OS-001"
        }
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    f"{BASE_URL}/tools/semantic_search",
                    json=payload,
                    headers={"X-API-Key": API_KEY}
                )
                
                success = resp.status_code == 200
                if success:
                    data = resp.json()
                    has_data = 'data' in data and isinstance(data['data'], list)
                    result_count = len(data.get('data', []))
                    
                    await self.log_test(
                        "Semantic Search",
                        has_data,
                        f"Results found: {result_count}"
                    )
                else:
                    await self.log_test("Semantic Search", False, f"HTTP {resp.status_code}")
                    
                return success
                
        except Exception as e:
            await self.log_test("Semantic Search", False, f"Exception: {str(e)}")
            return False

    async def test_error_handling(self):
        """Test error handling for various scenarios"""
        error_tests = [
            {
                "name": "Invalid API Key",
                "url": f"{BASE_URL}/tools/list",
                "headers": {"X-API-Key": "invalid-key"},
                "expected_status": [401, 403]
            },
            {
                "name": "Missing Required Fields", 
                "url": f"{BASE_URL}/tools/create_technology_mapping",
                "json": {"patent_id": "TEST"}, # Missing required fields
                "headers": {"X-API-Key": API_KEY},
                "expected_status": [400, 422]
            },
            {
                "name": "Invalid Confidence Range",
                "url": f"{BASE_URL}/tools/create_technology_mapping", 
                "json": {
                    "patent_id": "TEST",
                    "technology_id": "TECH",
                    "confidence": 1.5,  # Invalid: > 1.0
                    "method": "TEST",
                    "analysis_run_id": "TEST"
                },
                "headers": {"X-API-Key": API_KEY},
                "expected_status": [400, 422]
            }
        ]
        
        all_passed = True
        for test in error_tests:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        test["url"],
                        json=test.get("json"),
                        headers=test["headers"]
                    )
                    
                    status_valid = resp.status_code in test["expected_status"]
                    if not status_valid:
                        all_passed = False
                        
                    await self.log_test(
                        f"Error Handling - {test['name']}",
                        status_valid,
                        f"Expected: {test['expected_status']}, Got: {resp.status_code}"
                    )
            except Exception as e:
                all_passed = False
                await self.log_test(f"Error Handling - {test['name']}", False, f"Exception: {str(e)}")
        
        return all_passed

    async def run_all_tests(self):
        """Execute all tests and generate summary"""
        print("=" * 80)
        print("🧪 COMPREHENSIVE MCP NEW FUNCTIONALITY TEST SUITE")
        print("=" * 80)
        print(f"Testing against: {BASE_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test sequence
        tests = [
            ("Basic Connectivity", self.test_health_check),
            ("Tools Discovery", self.test_tools_list),
            ("Network Analysis", self.test_network_analysis),
            ("Technology Mapping", self.test_technology_mapping),
            ("Analysis Run Results", self.test_analysis_run_results),
            ("OpenSearch Integration", self.test_opensearch_integration),
            ("Semantic Search", self.test_semantic_search),
            ("Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            await test_func()
            print()
        
        # Final summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results.values() if t['status']])
        failed_tests_count = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests_count}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        print("=" * 80)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return failed_tests_count == 0


async def main():
    tester = TestNewMCPFunctionality()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())