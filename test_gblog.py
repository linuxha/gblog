#!/usr/bin/env python3
"""
Unit tests for gblog.py

These tests verify the core functionality without requiring actual Google API credentials.
"""

import unittest
import sys
import os
from unittest.mock import patch, mock_open, MagicMock

# Add the parent directory to the path so we can import gblog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the Google API imports before importing gblog
sys.modules['google.oauth2.credentials'] = MagicMock()
sys.modules['google_auth_oauthlib.flow'] = MagicMock()
sys.modules['google.auth.transport.requests'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['googleapiclient.errors'] = MagicMock()

import gblog


class TestGblogFileOperations(unittest.TestCase):
    """Test file reading functionality"""
    
    def test_read_file_content_success(self):
        """Test reading a valid file"""
        test_content = "This is a test post with <strong>HTML</strong>"
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            content = gblog.read_file_content('test.txt')
            self.assertEqual(content, test_content)
    
    def test_read_file_not_found(self):
        """Test handling of missing file"""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            with self.assertRaises(SystemExit) as cm:
                gblog.read_file_content('nonexistent.txt')
            self.assertEqual(cm.exception.code, 1)
    
    def test_read_file_permission_error(self):
        """Test handling of permission denied"""
        with patch('builtins.open', side_effect=PermissionError()):
            with self.assertRaises(SystemExit) as cm:
                gblog.read_file_content('nopermission.txt')
            self.assertEqual(cm.exception.code, 1)
    
    def test_read_file_unicode_error(self):
        """Test handling of Unicode decode errors"""
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
            with self.assertRaises(SystemExit) as cm:
                gblog.read_file_content('badencoding.txt')
            self.assertEqual(cm.exception.code, 1)


class TestGblogConstants(unittest.TestCase):
    """Test that constants are properly defined"""
    
    def test_scopes_defined(self):
        """Test that OAuth scopes are defined"""
        self.assertIsInstance(gblog.SCOPES, list)
        self.assertIn('https://www.googleapis.com/auth/blogger', gblog.SCOPES)
    
    def test_default_files_defined(self):
        """Test that default file paths are defined"""
        self.assertEqual(gblog.DEFAULT_CREDENTIALS_FILE, 'credentials.json')
        self.assertEqual(gblog.DEFAULT_TOKEN_FILE, 'token.json')


class TestGblogPostConstruction(unittest.TestCase):
    """Test post body construction"""
    
    def test_post_body_basic(self):
        """Test basic post body structure"""
        # This test verifies the structure would be correct
        # without actually calling the API
        
        # Verify the function signature accepts the right parameters
        import inspect
        sig = inspect.signature(gblog.post_to_blog)
        params = list(sig.parameters.keys())
        
        self.assertIn('service', params)
        self.assertIn('blog_id', params)
        self.assertIn('title', params)
        self.assertIn('content', params)
        self.assertIn('labels', params)
        self.assertIn('is_draft', params)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
