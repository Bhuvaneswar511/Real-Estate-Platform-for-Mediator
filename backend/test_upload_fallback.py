#!/usr/bin/env python3
"""
Test script to verify image upload fallback functionality.
This script will POST to /properties with images to test:
1. Cloudinary upload failure and fallback to local storage
2. Verification that files are saved locally with non-zero size
"""

import requests
import os
import time
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:5000"
UPLOADS_DIR = "uploads"

def create_test_image():
    """Create a small test image file for testing"""
    test_image_path = "test_image.jpg"
    
    # Create a minimal JPEG image (1x1 pixel)
    jpeg_header = bytes([
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
    
    with open(test_image_path, 'wb') as f:
        f.write(jpeg_header)
    
    return test_image_path

def test_property_upload():
    """Test property upload with image"""
    print("🔧 Creating test image...")
    test_image_path = create_test_image()
    
    try:
        # Prepare form data
        form_data = {
            'property_type': 'House',
            'address': 'Test Address 123',
            'city': 'Test City',
            'locality': 'Test Locality',
            'price': '500000',
            'area_value': '1200',
            'area_unit': 'sqft',
            'bedrooms': '3',
            'bathrooms': '2',
            'description': 'Test property for fallback functionality',
            'mediator_name': 'Test Agent',
            'mediator_contact': '+1234567890',
            'status': 'Available'
        }
        
        print("📤 Uploading property with image (expecting Cloudinary to fail)...")
        
        # Upload property with image
        with open(test_image_path, 'rb') as f:
            files = {'photos': (test_image_path, f, 'image/jpeg')}
            
            response = requests.post(
                f"{BASE_URL}/properties",
                data=form_data,
                files=files
            )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Property upload successful!")
            
            # Parse response to get property details
            response_data = response.json()
            if 'property' in response_data and 'photos' in response_data['property']:
                photo_urls = response_data['property']['photos']
                print(f"📸 Photo URLs: {photo_urls}")
                
                # Check if photos are local URLs (fallback worked)
                local_photos = [url for url in photo_urls if 'localhost:5000/uploads/' in url]
                if local_photos:
                    print("✅ Fallback to local storage worked!")
                    return check_local_files(local_photos)
                else:
                    print("❌ No local photos found - fallback may not have worked")
                    return False
            else:
                print("❌ No photos in response")
                return False
        else:
            print(f"❌ Property upload failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload test: {e}")
        return False
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def check_local_files(photo_urls):
    """Check that local files exist and have non-zero size"""
    print("\n🔍 Checking local files...")
    
    all_valid = True
    for url in photo_urls:
        if 'localhost:5000/uploads/' in url:
            filename = url.split('/')[-1]
            filepath = os.path.join(UPLOADS_DIR, filename)
            
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"📁 File: {filename}")
                print(f"   📏 Size: {file_size} bytes")
                
                if file_size > 0:
                    print(f"   ✅ File has non-zero size and is viewable")
                    
                    # Try to access the file via URL
                    try:
                        file_response = requests.get(url)
                        if file_response.status_code == 200:
                            print(f"   ✅ File is accessible via URL")
                        else:
                            print(f"   ❌ File not accessible via URL: {file_response.status_code}")
                            all_valid = False
                    except Exception as e:
                        print(f"   ❌ Error accessing file via URL: {e}")
                        all_valid = False
                else:
                    print(f"   ❌ File has zero size!")
                    all_valid = False
            else:
                print(f"❌ File not found: {filepath}")
                all_valid = False
    
    return all_valid

def main():
    print("🧪 Testing Image Upload Fallback Functionality")
    print("=" * 50)
    
    # Test server connectivity
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print(f"❌ Backend server responded with status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("💡 Make sure the Flask server is running on localhost:5000")
        return
    
    # Run upload test
    print("\n" + "=" * 50)
    success = test_property_upload()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Fallback functionality is working correctly.")
    else:
        print("💥 Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    main()
