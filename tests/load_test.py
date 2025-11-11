"""
Load Testing for AutoMentor CRM
Tests performance with large datasets (100+ records)
Measures response times, dashboard rendering, and database operations
"""
import time
import requests
import statistics
from datetime import datetime
import json

BASE_URL = "http://127.0.0.1:5000"
TEST_ITERATIONS = 3

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}")
    print(f"{text}")
    print(f"{'=' * 70}{Colors.ENDC}")

def print_test(text):
    print(f"{Colors.OKBLUE}▸ {text}{Colors.ENDC}")

def print_pass(text, duration=None):
    duration_str = f" ({duration:.2f}ms)" if duration else ""
    print(f"{Colors.OKGREEN}✓ {text}{duration_str}{Colors.ENDC}")

def print_fail(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_metric(label, value, unit="ms", threshold=None):
    """Print a metric with color coding based on threshold"""
    if threshold and value > threshold:
        color = Colors.WARNING
    else:
        color = Colors.OKGREEN
    print(f"  {color}{label:.<40} {value:.2f} {unit}{Colors.ENDC}")


class LoadTester:
    """Load testing suite for AutoMentor CRM"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.results = {
            'api_response_times': [],
            'dashboard_load_times': [],
            'create_times': [],
            'update_times': [],
            'delete_times': [],
            'errors': []
        }
    
    def check_server(self):
        """Verify server is running"""
        print_test("Checking server availability...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print_pass("Server is running")
                return True
            else:
                print_fail(f"Server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print_fail("Server is not running. Start with: python app.py")
            return False
        except Exception as e:
            print_fail(f"Error connecting to server: {e}")
            return False
    
    def test_api_response_time(self, iterations=TEST_ITERATIONS):
        """Test API GET response time"""
        print_test(f"Testing API response times ({iterations} iterations)...")
        times = []
        
        for _ in range(iterations):
            start = time.time()
            try:
                response = requests.get(f"{self.base_url}/api/recruits")
                duration = (time.time() - start) * 1000  # Convert to ms
                
                if response.status_code == 200:
                    times.append(duration)
                else:
                    self.results['errors'].append(f"GET /api/recruits returned {response.status_code}")
            except Exception as e:
                self.results['errors'].append(f"GET /api/recruits failed: {e}")
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            self.results['api_response_times'] = times
            print_pass(f"API response times measured")
            print_metric("Average", avg_time, threshold=100)
            print_metric("Min", min_time)
            print_metric("Max", max_time)
            
            return avg_time < 200  # Pass if under 200ms
        else:
            print_fail("No successful API responses")
            return False
    
    def test_dashboard_load_time(self, iterations=TEST_ITERATIONS):
        """Test dashboard page load time"""
        print_test(f"Testing dashboard load times ({iterations} iterations)...")
        times = []
        
        for _ in range(iterations):
            start = time.time()
            try:
                response = requests.get(f"{self.base_url}/")
                duration = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    times.append(duration)
                    # Check if response is HTML
                    if 'text/html' not in response.headers.get('content-type', ''):
                        print_warning("Dashboard response is not HTML")
                else:
                    self.results['errors'].append(f"GET / returned {response.status_code}")
            except Exception as e:
                self.results['errors'].append(f"GET / failed: {e}")
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            self.results['dashboard_load_times'] = times
            print_pass(f"Dashboard load times measured")
            print_metric("Average", avg_time, threshold=500)
            print_metric("Min", min_time)
            print_metric("Max", max_time)
            
            return avg_time < 1000  # Pass if under 1 second
        else:
            print_fail("No successful dashboard loads")
            return False
    
    def test_create_operations(self, count=20):
        """Test creating multiple recruits"""
        print_test(f"Testing bulk create operations ({count} recruits)...")
        times = []
        created_ids = []
        
        for i in range(count):
            recruit_data = {
                'name': f'Load Test Recruit {i+1}',
                'email': f'loadtest{i+1}@example.com',
                'phone': f'(555) {100+i:03d}-{1000+i:04d}',
                'stage': ['New', 'Contacted', 'In Training', 'Licensed'][i % 4],
                'notes': f'Load test recruit #{i+1}'
            }
            
            start = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/api/recruits",
                    json=recruit_data,
                    headers={'Content-Type': 'application/json'}
                )
                duration = (time.time() - start) * 1000
                
                if response.status_code == 201:
                    times.append(duration)
                    data = response.json()
                    created_ids.append(data['id'])
                else:
                    self.results['errors'].append(f"POST recruit {i+1} returned {response.status_code}")
            except Exception as e:
                self.results['errors'].append(f"POST recruit {i+1} failed: {e}")
        
        if times:
            avg_time = statistics.mean(times)
            total_time = sum(times)
            
            self.results['create_times'] = times
            print_pass(f"Created {len(created_ids)}/{count} recruits")
            print_metric("Average per create", avg_time, threshold=100)
            print_metric("Total time", total_time)
            print_metric("Throughput", len(created_ids) / (total_time / 1000), "ops/sec")
            
            return created_ids
        else:
            print_fail("No successful creates")
            return []
    
    def test_update_operations(self, recruit_ids, count=20):
        """Test updating multiple recruits"""
        print_test(f"Testing bulk update operations ({min(count, len(recruit_ids))} updates)...")
        times = []
        
        for i, recruit_id in enumerate(recruit_ids[:count]):
            update_data = {
                'name': f'Updated Load Test {i+1}',
                'stage': 'Licensed',
                'notes': f'Updated via load test at {datetime.now().isoformat()}'
            }
            
            start = time.time()
            try:
                response = requests.put(
                    f"{self.base_url}/api/recruits/{recruit_id}",
                    json=update_data,
                    headers={'Content-Type': 'application/json'}
                )
                duration = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    times.append(duration)
                else:
                    self.results['errors'].append(f"PUT recruit {recruit_id} returned {response.status_code}")
            except Exception as e:
                self.results['errors'].append(f"PUT recruit {recruit_id} failed: {e}")
        
        if times:
            avg_time = statistics.mean(times)
            total_time = sum(times)
            
            self.results['update_times'] = times
            print_pass(f"Updated {len(times)} recruits")
            print_metric("Average per update", avg_time, threshold=100)
            print_metric("Total time", total_time)
            
            return True
        else:
            print_fail("No successful updates")
            return False
    
    def test_delete_operations(self, recruit_ids, count=20):
        """Test deleting multiple recruits"""
        print_test(f"Testing bulk delete operations ({min(count, len(recruit_ids))} deletes)...")
        times = []
        
        for recruit_id in recruit_ids[:count]:
            start = time.time()
            try:
                response = requests.delete(f"{self.base_url}/api/recruits/{recruit_id}")
                duration = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    times.append(duration)
                else:
                    self.results['errors'].append(f"DELETE recruit {recruit_id} returned {response.status_code}")
            except Exception as e:
                self.results['errors'].append(f"DELETE recruit {recruit_id} failed: {e}")
        
        if times:
            avg_time = statistics.mean(times)
            total_time = sum(times)
            
            self.results['delete_times'] = times
            print_pass(f"Deleted {len(times)} recruits")
            print_metric("Average per delete", avg_time, threshold=100)
            print_metric("Total time", total_time)
            
            return True
        else:
            print_fail("No successful deletes")
            return False
    
    def test_large_dataset_performance(self):
        """Test with 100+ records"""
        print_test("Testing with 100+ records in database...")
        
        # Get current count
        try:
            response = requests.get(f"{self.base_url}/api/recruits")
            if response.status_code == 200:
                current_count = len(response.json())
                print(f"  Current database size: {current_count} recruits")
                
                if current_count < 100:
                    print_warning(f"Database has only {current_count} records. Run add_demo_data.py to add more.")
                
                # Test dashboard load with current dataset
                start = time.time()
                dash_response = requests.get(f"{self.base_url}/")
                duration = (time.time() - start) * 1000
                
                if dash_response.status_code == 200:
                    print_metric(f"Dashboard load ({current_count} records)", duration, threshold=1000)
                    
                    if duration < 1000:
                        print_pass("Dashboard loads quickly with large dataset")
                        return True
                    else:
                        print_warning("Dashboard load time exceeds 1 second")
                        return False
                else:
                    print_fail(f"Dashboard returned status {dash_response.status_code}")
                    return False
            else:
                print_fail(f"Could not get recruit count: {response.status_code}")
                return False
        except Exception as e:
            print_fail(f"Error testing large dataset: {e}")
            return False
    
    def test_concurrent_reads(self, concurrent=5, iterations=10):
        """Test concurrent read operations"""
        print_test(f"Testing {concurrent} concurrent reads ({iterations} iterations)...")
        
        import concurrent.futures
        
        def fetch_recruits():
            start = time.time()
            response = requests.get(f"{self.base_url}/api/recruits")
            duration = (time.time() - start) * 1000
            return duration if response.status_code == 200 else None
        
        times = []
        for _ in range(iterations):
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent) as executor:
                futures = [executor.submit(fetch_recruits) for _ in range(concurrent)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
                times.extend([r for r in results if r is not None])
        
        if times:
            avg_time = statistics.mean(times)
            max_time = max(times)
            
            print_pass(f"Completed {len(times)} concurrent reads")
            print_metric("Average response time", avg_time, threshold=200)
            print_metric("Max response time", max_time, threshold=500)
            
            return avg_time < 500
        else:
            print_fail("No successful concurrent reads")
            return False
    
    def generate_summary(self):
        """Generate test summary report"""
        print_header("LOAD TEST SUMMARY")
        
        if self.results['api_response_times']:
            avg_api = statistics.mean(self.results['api_response_times'])
            print(f"\n{Colors.BOLD}API Performance:{Colors.ENDC}")
            print_metric("Average GET /api/recruits", avg_api, threshold=200)
        
        if self.results['dashboard_load_times']:
            avg_dash = statistics.mean(self.results['dashboard_load_times'])
            print(f"\n{Colors.BOLD}Dashboard Performance:{Colors.ENDC}")
            print_metric("Average dashboard load", avg_dash, threshold=500)
        
        if self.results['create_times']:
            avg_create = statistics.mean(self.results['create_times'])
            print(f"\n{Colors.BOLD}CRUD Performance:{Colors.ENDC}")
            print_metric("Average CREATE", avg_create, threshold=100)
        
        if self.results['update_times']:
            avg_update = statistics.mean(self.results['update_times'])
            print_metric("Average UPDATE", avg_update, threshold=100)
        
        if self.results['delete_times']:
            avg_delete = statistics.mean(self.results['delete_times'])
            print_metric("Average DELETE", avg_delete, threshold=100)
        
        if self.results['errors']:
            print(f"\n{Colors.FAIL}{Colors.BOLD}Errors ({len(self.results['errors'])}):{Colors.ENDC}")
            for error in self.results['errors'][:10]:  # Show first 10 errors
                print(f"  {Colors.FAIL}• {error}{Colors.ENDC}")
            if len(self.results['errors']) > 10:
                print(f"  {Colors.FAIL}... and {len(self.results['errors']) - 10} more{Colors.ENDC}")
        else:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ No errors encountered{Colors.ENDC}")
        
        print()


def main():
    """Run all load tests"""
    print_header("AUTOMENTOR CRM - LOAD TESTING SUITE")
    print(f"{Colors.OKCYAN}Testing server at: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    
    tester = LoadTester(BASE_URL)
    
    # Check server
    if not tester.check_server():
        print_fail("\nLoad tests aborted - server not available")
        return
    
    # Run tests
    print_header("PERFORMANCE TESTS")
    
    # Test 1: API response times
    tester.test_api_response_time()
    
    # Test 2: Dashboard load times
    tester.test_dashboard_load_time()
    
    # Test 3: Create operations
    print()
    created_ids = tester.test_create_operations(count=20)
    
    # Test 4: Update operations
    if created_ids:
        print()
        tester.test_update_operations(created_ids, count=20)
    
    # Test 5: Delete operations
    if created_ids:
        print()
        tester.test_delete_operations(created_ids, count=20)
    
    # Test 6: Large dataset
    print()
    tester.test_large_dataset_performance()
    
    # Test 7: Concurrent reads
    print()
    tester.test_concurrent_reads(concurrent=5, iterations=10)
    
    # Generate summary
    tester.generate_summary()
    
    print_header("LOAD TESTING COMPLETE")
    print()


if __name__ == "__main__":
    main()
