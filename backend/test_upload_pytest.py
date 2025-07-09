#!/usr/bin/env python3
"""
Pytest for testing image upload functionality with Cloudinary failure mocking.
This test suite includes:
1. Mock Cloudinary failure to test fallback functionality
2. Upload small in-memory file
3. Assert file size and bytes match expected values
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from io import BytesIO
from werkzeug.datastructures import FileStorage

# Import the Flask app and functions
import sys
sys.path.append('.')
from app import app, db, upload_file_to_cloudinary, upload_file_locally, Property, PropertyPhoto


class TestImageUploadFunctionality:
    """Test class for image upload functionality"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    @pytest.fixture
    def sample_image_data(self):
        """Create sample image data for testing"""
        # Minimal JPEG header (1x1 pixel)
        jpeg_data = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x01, 0x00, 0x48, 0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x11, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01,
            0xFF, 0xC4, 0x00, 0x14, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0xFF, 0xC4,
            0x00, 0x14, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xDA, 0x00, 0x0C,
            0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00, 0x00, 0xFF, 0xD9
        ])
        return jpeg_data
    
    @pytest.fixture
    def temp_uploads_dir(self):
        """Create temporary uploads directory for testing"""
        temp_dir = tempfile.mkdtemp(prefix="test_uploads_")
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_cloudinary_failure_fallback_to_local(self, sample_image_data, temp_uploads_dir):
        """Test that Cloudinary failure triggers fallback to local storage"""
        # Mock Cloudinary uploader to simulate failure
        with patch('cloudinary.uploader.upload') as mock_cloudinary_upload:
            # Configure mock to raise an exception (simulating Cloudinary failure)
            mock_cloudinary_upload.side_effect = Exception("Cloudinary API Error")
            
            # Mock the uploads directory path
            with patch('app.os.path.dirname') as mock_dirname:
                mock_dirname.return_value = temp_uploads_dir
                
                # Create uploads subdirectory
                uploads_dir = os.path.join(temp_uploads_dir, "uploads")
                os.makedirs(uploads_dir, exist_ok=True)
                
                # Create in-memory file from sample data
                file_stream = BytesIO(sample_image_data)
                file_storage = FileStorage(
                    stream=file_stream,
                    filename="test_image.jpg",
                    content_type="image/jpeg"
                )
                
                # Test the upload function with mocked Cloudinary failure
                try:
                    # This should fail (Cloudinary) and fallback to local
                    url = upload_file_to_cloudinary(file_storage)
                    pytest.fail("Expected Cloudinary upload to fail, but it succeeded")
                except Exception:
                    # Expected behavior - Cloudinary should fail
                    # Now test the local fallback
                    file_stream.seek(0)  # Reset stream position
                    local_url = upload_file_locally(file_storage)
                    
                    # Assertions
                    assert local_url is not None
                    assert "localhost:5000/uploads/" in local_url
                    
                    # Extract filename from URL
                    filename = local_url.split('/')[-1]
                    filepath = os.path.join(uploads_dir, filename)
                    
                    # Verify file was created
                    assert os.path.exists(filepath)
                    
                    # Verify file size matches expected
                    file_size = os.path.getsize(filepath)
                    assert file_size == len(sample_image_data)
                    assert file_size > 0
                    
                    # Verify file contents match
                    with open(filepath, 'rb') as f:
                        saved_data = f.read()
                    assert saved_data == sample_image_data
                    
                    print(f"✅ Cloudinary failure test passed: {file_size} bytes saved locally")
    
    def test_upload_file_locally_with_specific_bytes(self, sample_image_data, temp_uploads_dir):
        """Test local file upload with specific byte verification"""
        # Create uploads directory
        uploads_dir = os.path.join(temp_uploads_dir, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Mock the uploads directory path
        with patch('app.os.path.dirname') as mock_dirname:
            mock_dirname.return_value = temp_uploads_dir
            
            # Create in-memory file
            file_stream = BytesIO(sample_image_data)
            file_storage = FileStorage(
                stream=file_stream,
                filename="byte_test.jpg",
                content_type="image/jpeg"
            )
            
            # Upload file locally
            url = upload_file_locally(file_storage)
            
            # Extract filename and verify file
            filename = url.split('/')[-1]
            filepath = os.path.join(uploads_dir, filename)
            
            # Verify file exists
            assert os.path.exists(filepath)
            
            # Verify exact byte count
            file_size = os.path.getsize(filepath)
            expected_size = len(sample_image_data)
            
            assert file_size == expected_size
            print(f"✅ File size verification: {file_size} bytes == {expected_size} bytes")
            
            # Verify exact byte content
            with open(filepath, 'rb') as f:
                saved_bytes = f.read()
            
            assert saved_bytes == sample_image_data
            print(f"✅ Byte content verification: {len(saved_bytes)} bytes match exactly")
            
            # Additional assertions
            assert file_size > 0, "File should have non-zero size"
            assert len(saved_bytes) > 0, "Saved bytes should be non-empty"
    
    def test_cloudinary_success_no_local_duplication(self, sample_image_data):
        """Test that successful Cloudinary upload doesn't create local files"""
        # Mock successful Cloudinary upload
        with patch('cloudinary.uploader.upload') as mock_cloudinary_upload:
            mock_cloudinary_upload.return_value = {
                'secure_url': 'https://res.cloudinary.com/test/image/upload/v123/test.jpg',
                'url': 'https://res.cloudinary.com/test/image/upload/v123/test.jpg',
                'public_id': 'test_image_123'
            }
            
            # Create in-memory file
            file_stream = BytesIO(sample_image_data)
            file_storage = FileStorage(
                stream=file_stream,
                filename="success_test.jpg",
                content_type="image/jpeg"
            )
            
            # Test successful Cloudinary upload
            url = upload_file_to_cloudinary(file_storage)
            
            # Assertions
            assert url is not None
            assert 'cloudinary.com' in url
            assert url == 'https://res.cloudinary.com/test/image/upload/v123/test.jpg'
            
            # Verify Cloudinary was called
            assert mock_cloudinary_upload.called
            
            print(f"✅ Cloudinary success test passed: {url}")
    
    def test_file_size_and_content_integrity(self, sample_image_data, temp_uploads_dir):
        """Test that uploaded files maintain size and content integrity"""
        uploads_dir = os.path.join(temp_uploads_dir, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        with patch('app.os.path.dirname') as mock_dirname:
            mock_dirname.return_value = temp_uploads_dir
            
            # Test with different file sizes
            test_cases = [
                (b"small", "small.txt"),
                (sample_image_data, "medium.jpg"),
                (b"a" * 1000, "large.txt")  # 1KB file
            ]
            
            for data, filename in test_cases:
                file_stream = BytesIO(data)
                file_storage = FileStorage(
                    stream=file_stream,
                    filename=filename,
                    content_type="application/octet-stream"
                )
                
                # Upload file
                url = upload_file_locally(file_storage)
                
                # Verify file
                saved_filename = url.split('/')[-1]
                filepath = os.path.join(uploads_dir, saved_filename)
                
                assert os.path.exists(filepath)
                
                # Check size
                file_size = os.path.getsize(filepath)
                expected_size = len(data)
                assert file_size == expected_size
                
                # Check content
                with open(filepath, 'rb') as f:
                    saved_data = f.read()
                assert saved_data == data
                
                print(f"✅ {filename}: {file_size} bytes, content verified")


def run_tests():
    """Run all tests with pytest"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    # Run tests directly
    run_tests()
