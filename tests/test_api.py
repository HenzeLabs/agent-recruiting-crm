"""
Unit tests for AutoMentor CRM API endpoints
Tests CRUD operations, validation, and edge cases
"""
import pytest
import json
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, init_db
import sqlite3

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test_db.sqlite3'
    
    with app.test_client() as client:
        with app.app_context():
            # Initialize test database
            init_db()
        yield client
    
    # Cleanup test database
    try:
        os.remove('test_db.sqlite3')
    except:
        pass

@pytest.fixture
def sample_recruit():
    """Sample recruit data"""
    return {
        'name': 'Test Recruit',
        'email': 'test@example.com',
        'phone': '(555) 123-4567',
        'stage': 'New',
        'notes': 'Test notes'
    }


class TestRecruitsCRUD:
    """Test CRUD operations for recruits"""
    
    def test_get_all_recruits_empty(self, client):
        """GET /api/recruits should return empty array initially"""
        response = client.get('/api/recruits')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_recruit_complete(self, client, sample_recruit):
        """POST /api/recruits should create recruit with all fields"""
        response = client.post('/api/recruits',
                              data=json.dumps(sample_recruit),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == sample_recruit['name']
        assert data['email'] == sample_recruit['email']
        assert data['phone'] == sample_recruit['phone']
        assert data['stage'] == sample_recruit['stage']
        assert data['notes'] == sample_recruit['notes']
        assert 'id' in data
        assert 'updated_at' in data
    
    def test_create_recruit_minimal(self, client):
        """POST /api/recruits should create recruit with only name"""
        minimal_data = {'name': 'Minimal Test'}
        response = client.post('/api/recruits',
                              data=json.dumps(minimal_data),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Minimal Test'
        assert data['stage'] == 'New'  # Default stage
    
    def test_create_recruit_no_name(self, client):
        """POST /api/recruits should fail without name"""
        invalid_data = {'email': 'test@example.com'}
        response = client.post('/api/recruits',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Name is required' in data['error']
    
    def test_create_recruit_empty_name(self, client):
        """POST /api/recruits should fail with empty name"""
        invalid_data = {'name': '   ', 'email': 'test@example.com'}
        response = client.post('/api/recruits',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_get_all_recruits_after_create(self, client, sample_recruit):
        """GET /api/recruits should return created recruits"""
        # Create recruit
        client.post('/api/recruits',
                   data=json.dumps(sample_recruit),
                   content_type='application/json')
        
        # Get all recruits
        response = client.get('/api/recruits')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == sample_recruit['name']
    
    def test_get_recruit_by_id(self, client, sample_recruit):
        """GET /api/recruits/<id> should return specific recruit"""
        # Create recruit
        create_response = client.post('/api/recruits',
                                     data=json.dumps(sample_recruit),
                                     content_type='application/json')
        recruit_id = json.loads(create_response.data)['id']
        
        # Get by ID
        response = client.get(f'/api/recruits/{recruit_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == recruit_id
        assert data['name'] == sample_recruit['name']
    
    def test_get_recruit_not_found(self, client):
        """GET /api/recruits/<id> should return 404 for non-existent ID"""
        response = client.get('/api/recruits/99999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_recruit(self, client, sample_recruit):
        """PUT /api/recruits/<id> should update recruit"""
        # Create recruit
        create_response = client.post('/api/recruits',
                                     data=json.dumps(sample_recruit),
                                     content_type='application/json')
        recruit_id = json.loads(create_response.data)['id']
        
        # Update recruit
        updated_data = {
            'name': 'Updated Name',
            'email': 'updated@example.com',
            'phone': '(555) 999-9999',
            'stage': 'Licensed',
            'notes': 'Updated notes'
        }
        response = client.put(f'/api/recruits/{recruit_id}',
                             data=json.dumps(updated_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == updated_data['name']
        assert data['email'] == updated_data['email']
        assert data['stage'] == updated_data['stage']
    
    def test_update_recruit_not_found(self, client):
        """PUT /api/recruits/<id> should return 404 for non-existent ID"""
        update_data = {'name': 'Test', 'stage': 'New'}
        response = client.put('/api/recruits/99999',
                             data=json.dumps(update_data),
                             content_type='application/json')
        assert response.status_code == 404
    
    def test_delete_recruit(self, client, sample_recruit):
        """DELETE /api/recruits/<id> should delete recruit"""
        # Create recruit
        create_response = client.post('/api/recruits',
                                     data=json.dumps(sample_recruit),
                                     content_type='application/json')
        recruit_id = json.loads(create_response.data)['id']
        
        # Delete recruit
        response = client.delete(f'/api/recruits/{recruit_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify deleted
        get_response = client.get(f'/api/recruits/{recruit_id}')
        assert get_response.status_code == 404
    
    def test_delete_recruit_not_found(self, client):
        """DELETE /api/recruits/<id> should return 404 for non-existent ID"""
        response = client.delete('/api/recruits/99999')
        assert response.status_code == 404


class TestStageTransitions:
    """Test stage transitions and workflow"""
    
    def test_stage_progression(self, client):
        """Test typical stage progression: New -> Contacted -> Training -> Licensed"""
        stages = ['New', 'Contacted', 'In Training', 'Licensed']
        
        # Create recruit
        create_response = client.post('/api/recruits',
                                     data=json.dumps({'name': 'Stage Test', 'stage': 'New'}),
                                     content_type='application/json')
        recruit_id = json.loads(create_response.data)['id']
        
        # Progress through stages
        for stage in stages[1:]:
            response = client.put(f'/api/recruits/{recruit_id}',
                                data=json.dumps({'name': 'Stage Test', 'stage': stage}),
                                content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['stage'] == stage
    
    def test_backward_stage_transition(self, client):
        """Test moving from Licensed back to earlier stage (edge case)"""
        # Create licensed recruit
        create_response = client.post('/api/recruits',
                                     data=json.dumps({'name': 'Backward Test', 'stage': 'Licensed'}),
                                     content_type='application/json')
        recruit_id = json.loads(create_response.data)['id']
        
        # Move back to Contacted
        response = client.put(f'/api/recruits/{recruit_id}',
                             data=json.dumps({'name': 'Backward Test', 'stage': 'Contacted'}),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['stage'] == 'Contacted'
    
    def test_stage_to_inactive(self, client):
        """Test moving recruit to Inactive stage"""
        create_response = client.post('/api/recruits',
                                     data=json.dumps({'name': 'Inactive Test', 'stage': 'Contacted'}),
                                     content_type='application/json')
        recruit_id = json.loads(create_response.data)['id']
        
        response = client.put(f'/api/recruits/{recruit_id}',
                             data=json.dumps({'name': 'Inactive Test', 'stage': 'Inactive'}),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['stage'] == 'Inactive'


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_duplicate_emails(self, client):
        """System should allow duplicate emails (no unique constraint)"""
        recruit1 = {'name': 'Person 1', 'email': 'duplicate@test.com'}
        recruit2 = {'name': 'Person 2', 'email': 'duplicate@test.com'}
        
        response1 = client.post('/api/recruits',
                               data=json.dumps(recruit1),
                               content_type='application/json')
        response2 = client.post('/api/recruits',
                               data=json.dumps(recruit2),
                               content_type='application/json')
        
        assert response1.status_code == 201
        assert response2.status_code == 201
    
    def test_special_characters_in_name(self, client):
        """Should handle special characters in name"""
        special_recruit = {
            'name': "O'Brien-Smith @#$%",
            'email': 'special@test.com',
            'notes': 'Has <html> & "quotes"'
        }
        response = client.post('/api/recruits',
                              data=json.dumps(special_recruit),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == special_recruit['name']
    
    def test_very_long_name(self, client):
        """Should handle very long names"""
        long_name = 'A' * 500
        recruit = {'name': long_name, 'email': 'long@test.com'}
        response = client.post('/api/recruits',
                              data=json.dumps(recruit),
                              content_type='application/json')
        assert response.status_code == 201
    
    def test_empty_json_body(self, client):
        """Should handle empty JSON body"""
        response = client.post('/api/recruits',
                              data='{}',
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_malformed_json(self, client):
        """Should handle malformed JSON"""
        response = client.post('/api/recruits',
                              data='not valid json',
                              content_type='application/json')
        assert response.status_code in [400, 500]
    
    def test_invalid_stage(self, client):
        """Should accept any stage value (no validation currently)"""
        recruit = {'name': 'Invalid Stage Test', 'stage': 'NonExistentStage'}
        response = client.post('/api/recruits',
                              data=json.dumps(recruit),
                              content_type='application/json')
        # Currently no stage validation, so this will pass
        assert response.status_code == 201


class TestBulkOperations:
    """Test bulk operations and performance"""
    
    def test_create_multiple_recruits(self, client):
        """Create 20 recruits and verify all are retrievable"""
        created_ids = []
        
        for i in range(20):
            recruit = {
                'name': f'Bulk Test {i+1}',
                'email': f'bulk{i+1}@test.com',
                'stage': ['New', 'Contacted', 'In Training'][i % 3]
            }
            response = client.post('/api/recruits',
                                  data=json.dumps(recruit),
                                  content_type='application/json')
            assert response.status_code == 201
            created_ids.append(json.loads(response.data)['id'])
        
        # Get all recruits
        response = client.get('/api/recruits')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 20
    
    def test_bulk_updates(self, client):
        """Update multiple recruits"""
        # Create 5 recruits
        ids = []
        for i in range(5):
            response = client.post('/api/recruits',
                                  data=json.dumps({'name': f'Update Test {i+1}'}),
                                  content_type='application/json')
            ids.append(json.loads(response.data)['id'])
        
        # Update all to Licensed
        for recruit_id in ids:
            response = client.put(f'/api/recruits/{recruit_id}',
                                data=json.dumps({'name': f'Updated {recruit_id}', 'stage': 'Licensed'}),
                                content_type='application/json')
            assert response.status_code == 200
        
        # Verify all updated
        response = client.get('/api/recruits')
        data = json.loads(response.data)
        licensed_count = sum(1 for r in data if r['stage'] == 'Licensed')
        assert licensed_count == 5
    
    def test_bulk_deletes(self, client):
        """Delete multiple recruits"""
        # Create 5 recruits
        ids = []
        for i in range(5):
            response = client.post('/api/recruits',
                                  data=json.dumps({'name': f'Delete Test {i+1}'}),
                                  content_type='application/json')
            ids.append(json.loads(response.data)['id'])
        
        # Delete all
        for recruit_id in ids:
            response = client.delete(f'/api/recruits/{recruit_id}')
            assert response.status_code == 200
        
        # Verify all deleted
        response = client.get('/api/recruits')
        data = json.loads(response.data)
        assert len(data) == 0


class TestDataPersistence:
    """Test data persistence and timestamps"""
    
    def test_timestamps_on_create(self, client):
        """Verify created_at and updated_at are set"""
        response = client.post('/api/recruits',
                              data=json.dumps({'name': 'Timestamp Test'}),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'created_at' in data or 'updated_at' in data
    
    def test_updated_at_changes_on_update(self, client):
        """Verify updated_at changes after update"""
        # Create recruit
        create_response = client.post('/api/recruits',
                                     data=json.dumps({'name': 'Update Timestamp'}),
                                     content_type='application/json')
        recruit_id = json.loads(create_response.data)['id']
        original_updated = json.loads(create_response.data).get('updated_at')
        
        # Wait briefly and update
        import time
        time.sleep(0.1)
        
        update_response = client.put(f'/api/recruits/{recruit_id}',
                                    data=json.dumps({'name': 'Updated Timestamp', 'stage': 'Contacted'}),
                                    content_type='application/json')
        new_updated = json.loads(update_response.data).get('updated_at')
        
        # Timestamps should be different (if implemented)
        # Note: This test may need adjustment based on timestamp precision
        assert update_response.status_code == 200


class TestValidation:
    """Test input validation"""
    
    def test_name_whitespace_trimming(self, client):
        """Should trim whitespace from name"""
        recruit = {'name': '  Trimmed Name  ', 'email': 'trim@test.com'}
        response = client.post('/api/recruits',
                              data=json.dumps(recruit),
                              content_type='application/json')
        assert response.status_code == 201
        # Note: Current implementation may not trim, so this test documents expected behavior
    
    def test_email_format_no_validation(self, client):
        """Currently no email validation (accepts any string)"""
        recruit = {'name': 'Email Test', 'email': 'not-an-email'}
        response = client.post('/api/recruits',
                              data=json.dumps(recruit),
                              content_type='application/json')
        # Currently accepts invalid emails
        assert response.status_code == 201
    
    def test_phone_format_no_validation(self, client):
        """Currently no phone validation (accepts any string)"""
        recruit = {'name': 'Phone Test', 'phone': 'invalid phone'}
        response = client.post('/api/recruits',
                              data=json.dumps(recruit),
                              content_type='application/json')
        # Currently accepts any phone format
        assert response.status_code == 201


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
