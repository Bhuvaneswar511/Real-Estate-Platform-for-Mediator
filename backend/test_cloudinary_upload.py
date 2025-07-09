#!/usr/bin/env python3
"""
Test script to verify Cloudinary upload functionality.
This script will POST to /properties with images to test:
1. Cloudinary upload success with valid credentials
2. Verification that images upload to Cloudinary (URLs contain cloudinary.com)
3. Verification that images are NOT duplicated locally
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
    test_image_path = "test_cloudinary_image.jpg"
    
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

def test_cloudinary_property_upload():
    """Test property upload with image to Cloudinary"""
    print("🔧 Creating test image...")
    test_image_path = create_test_image()
    
    # Get current uploads directory state before upload
    before_upload_files = set()
    if os.path.exists(UPLOADS_DIR):
        before_upload_files = set(os.listdir(UPLOADS_DIR))
    
    try:
        # Prepare form data
        form_data = {
            'property_type': 'Apartment',
            'address': 'Cloudinary Test Address 456',
            'city': 'Cloudinary City',
            'locality': 'Cloudinary Locality',
            'price': '750000',
            'area_value': '1500',
            'area_unit': 'sqft',
            'bedrooms': '4',
            'bathrooms': '3',
            'description': 'Test property for Cloudinary upload functionality',
            'mediator_name': 'Cloudinary Agent',
            'mediator_contact': '+1987654321',
            'status': 'Available'
        }
        
        print("☁️ Uploading property with image (expecting Cloudinary to succeed)...")
        
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
                
                # Check if photos are Cloudinary URLs
                cloudinary_photos = [url for url in photo_urls if 'cloudinary.com' in url or 'res.cloudinary.com' in url]
                local_photos = [url for url in photo_urls if 'localhost:5000/uploads/' in url]
                
                print(f"☁️ Cloudinary photos: {len(cloudinary_photos)}")
                print(f"📁 Local photos: {len(local_photos)}")
                
                if cloudinary_photos:
                    print("✅ Images uploaded to Cloudinary successfully!")
                    
                    # Check if images are NOT duplicated locally
                    after_upload_files = set()
                    if os.path.exists(UPLOADS_DIR):
                        after_upload_files = set(os.listdir(UPLOADS_DIR))
                    
                    new_local_files = after_upload_files - before_upload_files
                    
                    if not new_local_files:
                        print("✅ No new local files created - images were NOT duplicated locally!")
                        return verify_cloudinary_access(cloudinary_photos)
                    else:
                        print(f"❌ New local files found: {new_local_files}")
                        print("Images may have been duplicated locally")
                        return False
                else:
                    print("❌ No Cloudinary photos found - upload may have failed")
                    if local_photos:
                        print("⚠️ Found local photos - this indicates fallback was used instead")
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

def verify_cloudinary_access(cloudinary_urls):
    """Verify that Cloudinary URLs are accessible"""
    print("\n☁️ Verifying Cloudinary URLs...")
    
    all_accessible = True
    for url in cloudinary_urls:
        try:
            print(f"🔗 Testing URL: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                print(f"   ✅ Accessible (Status: {response.status_code})")
                print(f"   📝 Content-Type: {content_type}")
                print(f"   📏 Content-Length: {content_length} bytes")
                
                if content_length > 0 and 'image' in content_type.lower():
                    print(f"   ✅ Valid image content")
                else:
                    print(f"   ⚠️ May not be a valid image")
            else:
                print(f"   ❌ Not accessible (Status: {response.status_code})")
                all_accessible = False
                
        except Exception as e:
            print(f"   ❌ Error accessing URL: {e}")
            all_accessible = False
    
    return all_accessible

def main():
    print("☁️ Testing Cloudinary Upload Functionality")
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
    
    # Show current uploads directory state
    print(f"\n📁 Current uploads directory:")
    if os.path.exists(UPLOADS_DIR):
        files = os.listdir(UPLOADS_DIR)
        for f in files:
            size = os.path.getsize(os.path.join(UPLOADS_DIR, f))
            print(f"   - {f} ({size} bytes)")
    else:
        print("   (directory does not exist)")
    
    # Run upload test
    print("\n" + "=" * 50)
    success = test_cloudinary_property_upload()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Cloudinary upload is working correctly.")
        print("✅ Images upload to Cloudinary")
        print("✅ Images are NOT duplicated locally")
    else:
        print("💥 Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    main()
