import React, { useState } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

function AddPropertyForm() {
  const { t,i18n } = useTranslation('common'); 

  const [formData, setFormData] = useState({
    property_type: '',
    address: '',
    city: '',
    locality: '',
    price: '',
    area_value: '',
    area_unit: 'sqft',
    bedrooms: '',
    bathrooms: '',
    description: '',
    features: '',
    status: 'Available',
    mediator_name: '',
    mediator_contact: '',
    listing_date: new Date().toISOString().split('T')[0],
  });
  const [photos, setPhotos] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [photoPreviews, setPhotoPreviews] = useState([]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handlePhotoChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setPhotos(selectedFiles);
    const newPreviews = selectedFiles.map(file => URL.createObjectURL(file));
    setPhotoPreviews(newPreviews);
  };

  const removeFile = (indexToRemove) => {
    const updatedFiles = photos.filter((_, index) => index !== indexToRemove);
    const updatedPreviews = photoPreviews.filter((_, index) => index !== indexToRemove);
    
    // Clean up the removed preview URL to prevent memory leaks
    URL.revokeObjectURL(photoPreviews[indexToRemove]);
    
    setPhotos(updatedFiles);
    setPhotoPreviews(updatedPreviews);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    if (photos.length === 0) {
      setError(t('no_photos_uploaded')); 
      return;
    }

    const data = new FormData();
    for (const key in formData) {
      let value = formData[key];
      if ((key === 'bedrooms' || key === 'bathrooms') && value === '') {
        value = null;
      }
      data.append(key, value);
    }
    photos.forEach((photo) => {
      data.append('photos', photo);
    });

    try {
       await axios.post('http://localhost:5000/properties', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept-Language': i18n.language, 
        },
      });
      setMessage(t('property_added_successfully'));
      setFormData({
        property_type: '',
        address: '',
        city: '',
        locality: '',
        price: '',
        area_value: '',
        area_unit: 'sqft',
        bedrooms: '',
        bathrooms: '',
        description: '',
        features: '',
        status: 'Available',
        mediator_name: '',
        mediator_contact: '',
        listing_date: new Date().toISOString().split('T')[0],
      });
      setPhotos([]);
      setPhotoPreviews([]);
    } catch (err) {
      console.error('Error adding property:', err.response ? err.response.data : err.message);
      setError(err.response ? err.response.data.error : t('failed_to_add_property')); 
    }
  };

  return (
    <div className="form-container">
      <h2>{t('add_new_property')}</h2>
      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>{t('type')}:</label>
          <select name="property_type" value={formData.property_type} onChange={handleChange} required>
            <option value="">{t('select_type')}</option>
            <option value="Apartment">{t('apartment')}</option>
            <option value="Land">{t('land')}</option>
            <option value="House">{t('house')}</option>
            <option value="Commercial">{t('commercial')}</option>
          </select>
        </div>
        <div className="form-group">
          <label>{t('address')}:</label>
          <input type="text" name="address" value={formData.address} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>{t('city')}:</label>
          <input type="text" name="city" value={formData.city} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>{t('locality')}:</label>
          <input type="text" name="locality" value={formData.locality} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>{t('price')}:</label>
          <input type="number" name="price" value={formData.price} onChange={handleChange} required />
        </div>
        <div className="form-group area-input">
          <label>{t('area_size')}:</label>
          <input type="number" name="area_value" value={formData.area_value} onChange={handleChange} required />
          <select name="area_unit" value={formData.area_unit} onChange={handleChange}>
            <option value="sqft">{t('sqft')}</option>
            <option value="sqm">{t('sqm')}</option>
            <option value="acres">{t('acres')}</option>
            <option value="gunta">{t('gunta')}</option>
          </select>
        </div>
        {(formData.property_type === 'Apartment' || formData.property_type === 'House') && (
          <>
            <div className="form-group">
              <label>{t('bedrooms')}:</label>
              <input type="number" name="bedrooms" value={formData.bedrooms} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>{t('bathrooms')}:</label>
              <input type="number" name="bathrooms" value={formData.bathrooms} onChange={handleChange} />
            </div>
          </>
        )}
        <div className="form-group">
          <label>{t('description')}:</label>
          <textarea name="description" value={formData.description} onChange={handleChange}></textarea>
        </div>
        <div className="form-group">
          <label>{t('features')} ({t('features_placeholder')}):</label>
          <input type="text" name="features" value={formData.features} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>{t('status')}:</label>
          <select name="status" value={formData.status} onChange={handleChange}>
            <option value="Available">{t('available')}</option>
            <option value="Under Agreement">{t('under_agreement')}</option>
            <option value="Sold/Rented">{t('sold_rented')}</option>
          </select>
        </div>
        <div className="form-group">
          <label>{t('mediator_name')}:</label>
          <input type="text" name="mediator_name" value={formData.mediator_name} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>{t('mediator_contact')}:</label>
          <input type="text" name="mediator_contact" value={formData.mediator_contact} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>{t('listing_date')}:</label>
          <input type="date" name="listing_date" value={formData.listing_date} onChange={handleChange} />
        </div>
        <div className="form-group">
          <label>{t('property_photos_videos')}:</label>
          <input 
            type="file" 
            multiple 
            accept="image/*,video/*" 
            onChange={handlePhotoChange} 
          />
          <div className="file-previews">
            {photos.map((file, index) => (
              <div key={index} className="file-preview">
                {file.type.startsWith('image/') ? (
                  <img 
                    src={photoPreviews[index]} 
                    alt={`preview ${index}`} 
                    className="photo-thumbnail" 
                  />
                ) : file.type.startsWith('video/') ? (
                  <video 
                    src={photoPreviews[index]} 
                    className="video-thumbnail" 
                    controls
                  />
                ) : (
                  <div className="file-info">
                    <span>{file.name}</span>
                    <span>({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                  </div>
                )}
                <button 
                  type="button" 
                  className="remove-file-btn"
                  onClick={() => removeFile(index)}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
        <button type="submit" className="submit-button">{t('add_property')}</button>
      </form>
    </div>
  );
}

export default AddPropertyForm;