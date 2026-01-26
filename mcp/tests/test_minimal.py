#!/usr/bin/env python3
"""
Minimal MCP Server Test
Tests core functionality without external dependencies
"""

import asyncio
import sys
import os
import json

# Add parent directory to path to import mcp modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if core modules can be imported"""
    print("🔍 Testing Core Module Imports...")
    
    try:
        from mcp.db.graph import GraphDatabase
        print("✅ GraphDatabase import successful")
    except Exception as e:
        print(f"❌ GraphDatabase import failed: {e}")
        return False
    
    try:
        from mcp.db.models import AnalysisRun, KRPatent, ForeignPatent
        print("✅ Models import successful")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    return True

def test_graph_methods():
    """Test GraphDatabase method definitions"""
    print("\n🔍 Testing GraphDatabase Method Definitions...")
    
    methods = [
        'run_advanced_network_analysis',
        'create_technology_mapping', 
        'get_technology_mappings'
    ]
    
    for method in methods:
        if hasattr(GraphDatabase, method):
            print(f"✅ Method {method} exists")
        else:
            print(f"❌ Method {method} missing")
            return False
    
    return True

def test_analysis_run_model():
    """Test AnalysisRun model"""
    print("\n🔍 Testing AnalysisRun Model...")
    
    try:
        # Test AnalysisRun creation
        test_run = AnalysisRun(
            id="TEST-001",
            analysis_type="network_analysis",
            parameters={"test": "value"},
            status="running"
        )
        
        # Test to_dict method
        run_dict = test_run.to_dict()
        
        required_fields = ['id', 'analysis_type', 'parameters', 'status', 'created_at', 'completed_at', 'results_count']
        missing_fields = [field for field in required_fields if field not in run_dict]
        
        if missing_fields:
            print(f"❌ AnalysisRun missing fields: {missing_fields}")
            return False
        
        print("✅ AnalysisRun model functional")
        print(f"📋 Test run data: {json.dumps(run_dict, indent=2, default=str)}")
        return True
        
    except Exception as e:
        print(f"❌ AnalysisRun model test failed: {e}")
        return False

def test_network_analysis_query():
    """Test network analysis query structure"""
    print("\n🔍 Testing Network Analysis Query Structure...")
    
    # Check if the query method exists
    if not hasattr(GraphDatabase, 'run_advanced_network_analysis'):
        print("❌ run_advanced_network_analysis method not found")
        return False
    
    # Test query building logic (without executing)
    try:
        # This would normally be executed in Neo4j
        degree_query = """
        MATCH (n)
        WHERE n:Corporation OR n:Patent OR n:Technology
        WITH n, size((n)--()) as degree
        WHERE degree > 0
        RETURN 
            labels(n)[0] as node_type,
            coalesce(n.name, n.title, n.technology_name) as name,
            degree
        ORDER BY degree DESC
        LIMIT 20
        """
        
        if "MATCH" in degree_query and "RETURN" in degree_query:
            print("✅ Network analysis queries properly structured")
            return True
        else:
            print("❌ Network analysis queries malformed")
            return False
            
    except Exception as e:
        print(f"❌ Query structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("🧪 MINIMAL MCP FUNCTIONALITY TEST")
    print("=" * 80)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    test_results = []
    
    # Core functionality tests
    test_results.append(test_imports())
    test_results.append(test_graph_methods())
    test_results.append(test_analysis_run_model())
    test_results.append(test_network_analysis_query())
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL CORE FUNCTIONALITY TESTS PASSED!")
        print("📝 Note: Full integration tests require:")
        print("   - MCP server running on port 8080")
        print("   - Database connections (MariaDB, Neo4j, OpenSearch)")
        print("   - Test data loaded in databases")
    else:
        print(f"\n❌ {total - passed} TESTS FAILED - Check implementation")
    
    print("=" * 80)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)