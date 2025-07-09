import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next'; 

function PropertyList() {
  const { t, i18n } = useTranslation('common'); 

  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteLoading, setDeleteLoading] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [currentMediaIndex, setCurrentMediaIndex] = useState(0);
  const [filters, setFilters] = useState({
    property_type: '',
    city: '',
    locality: '',
    min_price: '',
    max_price: '',
    min_area: '',
    max_area: '',
    bedrooms: '',
    bathrooms: '',
    keyword: '',
  });

  const fetchProperties = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const queryParams = new URLSearchParams(filters).toString();
      const response = await axios.get(`http://localhost:5000/properties?${queryParams}`, {
        headers: {
          'Accept-Language': i18n.language, 
        }
      });
      setProperties(response.data);
    } catch (err) {
      console.error('Error fetching properties:', err.response ? err.response.data : err.message);
      setError(t('failed_to_fetch_properties')); 
    } finally {
      setLoading(false);
    }
  }, [filters, t, i18n.language]); 

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value,
    }));
  };

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    fetchProperties();
  };

  const handleClearFilters = () => {
    setFilters({
      property_type: '',
      city: '',
      locality: '',
      min_price: '',
      max_price: '',
      min_area: '',
      max_area: '',
      bedrooms: '',
      bathrooms: '',
      keyword: '',
    });
  };

  const handleDeleteProperty = async (propertyId) => {
    const confirmDelete = window.confirm(t('confirm_delete_property'));
    if (!confirmDelete) return;

    setDeleteLoading(prev => ({ ...prev, [propertyId]: true }));
    
    try {
      await axios.delete(`http://localhost:5000/properties/${propertyId}`, {
        headers: {
          'Accept-Language': i18n.language,
        }
      });
      
      setProperties(prevProperties => 
        prevProperties.filter(property => property.id !== propertyId)
      );
      
      alert(t('property_deleted_successfully'));
      
    } catch (err) {
      console.error('Error deleting property:', err.response ? err.response.data : err.message);
      alert(t('failed_to_delete_property'));
    } finally {
      setDeleteLoading(prev => ({ ...prev, [propertyId]: false }));
    }
  };

  const openGallery = (property) => {
    setSelectedProperty(property);
    setCurrentMediaIndex(0);
    setModalOpen(true);
  };

  const closeGallery = () => {
    setModalOpen(false);
    setSelectedProperty(null);
    setCurrentMediaIndex(0);
  };

  const nextMedia = () => {
    if (selectedProperty && selectedProperty.photos) {
      setCurrentMediaIndex(prev => 
        prev < selectedProperty.photos.length - 1 ? prev + 1 : 0
      );
    }
  };

  const prevMedia = () => {
    if (selectedProperty && selectedProperty.photos) {
      setCurrentMediaIndex(prev => 
        prev > 0 ? prev - 1 : selectedProperty.photos.length - 1
      );
    }
  };

  const renderMedia = (photo) => {
    if (!photo) return null;
    
    const isVideo = photo.mime_type ? 
      photo.mime_type.startsWith('video/') : 
      photo.image_url.match(/\.(mp4|webm|ogg|avi|mov)$/i);
    
    if (isVideo) {
      return (
        <video 
          controls 
          className="gallery-media"
          style={{ maxWidth: '100%', maxHeight: '80vh' }}
        >
          <source src={photo.image_url} type={photo.mime_type || 'video/mp4'} />
          Your browser does not support the video tag.
        </video>
      );
    } else {
      return (
        <img 
          src={photo.image_url} 
          alt={`Property media ${currentMediaIndex + 1}`}
          className="gallery-media"
          style={{ maxWidth: '100%', maxHeight: '80vh', objectFit: 'contain' }}
        />
      );
    }
  };

  return (
    <div className="property-list-container">
      <h2>{t('view_filter_properties')}</h2>

      <form onSubmit={handleFilterSubmit} className="filters-form">
        <div className="filter-group">
          <label>{t('type')}:</label>
          <select name="property_type" value={filters.property_type} onChange={handleFilterChange}>
            <option value="">{t('all')}</option>
            <option value="Apartment">{t('apartment')}</option>
            <option value="Land">{t('land')}</option>
            <option value="House">{t('house')}</option>
            <option value="Commercial">{t('commercial')}</option>
          </select>
        </div>

        <div className="filter-group">
          <label>{t('city')}:</label>
          <input type="text" name="city" value={filters.city} onChange={handleFilterChange} placeholder={t('city_placeholder')} />
        </div>

        <div className="filter-group">
          <label>{t('locality')}:</label>
          <input type="text" name="locality" value={filters.locality} onChange={handleFilterChange} placeholder={t('locality_placeholder')} />
        </div>

        <div className="filter-group">
          <label>{t('price_label')}:</label>
          <input type="number" name="min_price" value={filters.min_price} onChange={handleFilterChange} placeholder={t('min_price')} />
          <input type="number" name="max_price" value={filters.max_price} onChange={handleFilterChange} placeholder={t('max_price')} />
        </div>

        <div className="filter-group">
          <label>{t('area_label')}:</label>
          <input type="number" name="min_area" value={filters.min_area} onChange={handleFilterChange} placeholder={t('min_area')} />
          <input type="number" name="max_area" value={filters.max_area} onChange={handleFilterChange} placeholder={t('max_area')} />
        </div>

        <div className="filter-group">
          <label>{t('bedrooms')}:</label>
          <input type="number" name="bedrooms" value={filters.bedrooms} onChange={handleFilterChange} placeholder={t('exact_bedrooms')} min="0" />
        </div>

        <div className="filter-group">
          <label>{t('bathrooms')}:</label>
          <input type="number" name="bathrooms" value={filters.bathrooms} onChange={handleFilterChange} placeholder={t('exact_bathrooms')} min="0" />
        </div>

        <div className="filter-group">
          <label>{t('keyword')}:</label>
          <input type="text" name="keyword" value={filters.keyword} onChange={handleFilterChange} placeholder={t('features_placeholder')} />
        </div>

        <div className="filter-actions">
          <button type="submit" className="filter-button">{t('apply_filters')}</button>
          <button type="button" onClick={handleClearFilters} className="clear-button">{t('clear_filters')}</button>
        </div>
      </form>

      {loading ? (
        <p>{t('loading_properties')}</p>
      ) : error ? (
        <p className="error-message">{error}</p>
      ) : properties.length === 0 ? (
        <p>{t('no_properties_found')}</p>
      ) : (
        <div className="property-grid">
          {properties.map((property) => (
            <div key={property.id} className="property-card">
              <img
                src={(property.photos && property.photos.length > 0 ? property.photos[0].image_url : null) || `https://via.placeholder.com/300x200?text=${t('no_image')}`}
                alt={property.address}
                className="property-image"
                onClick={() => property.photos && property.photos.length > 0 && openGallery(property)}
                style={{ cursor: property.photos && property.photos.length > 0 ? 'pointer' : 'default' }}
              />
              <h3>{t(property.property_type.toLowerCase())} - {property.address}, {property.city}</h3>
              <p><strong>{t('price_label')}:</strong> ₹{property.price.toLocaleString('en-IN')}</p>
              <p><strong>{t('area_label')}:</strong> {property.area_value} {t(property.area_unit)}</p>
              {property.bedrooms && <p><strong>{t('bedrooms')}:</strong> {property.bedrooms}</p>}
              {property.bathrooms && <p><strong>{t('bathrooms')}:</strong> {property.bathrooms}</p>}
              <p className="property-description">{property.description}</p>
              {property.features && property.features.trim() !== '' && (
                <p><strong>{t('features')}:</strong> {property.features}</p>
              )}
              <p className="mediator-info">{t('contact')}: {property.mediator_name} ({property.mediator_contact})</p>
              <div className="property-actions">
                <button 
                  className="delete-button"
                  onClick={() => handleDeleteProperty(property.id)}
                  disabled={deleteLoading[property.id]}
                >
                  {deleteLoading[property.id] ? t('deleting') : t('Delete')}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Gallery */}
      {modalOpen && selectedProperty && (
        <div className="gallery-modal" onClick={closeGallery}>
          <div className="gallery-content" onClick={(e) => e.stopPropagation()}>
            <button className="gallery-close" onClick={closeGallery}>&times;</button>
            
            {selectedProperty.photos && selectedProperty.photos.length > 0 && (
              <>
                <div className="gallery-media-container">
                  {renderMedia(selectedProperty.photos[currentMediaIndex])}
                </div>
                
                {selectedProperty.photos.length > 1 && (
                  <>
                    <button className="gallery-nav gallery-prev" onClick={prevMedia}>&#8249;</button>
                    <button className="gallery-nav gallery-next" onClick={nextMedia}>&#8250;</button>
                    
                    <div className="gallery-counter">
                      {currentMediaIndex + 1} / {selectedProperty.photos.length}
                    </div>
                  </>
                )}
              </>
            )}
            
            <div className="gallery-property-info">
              <h3>{selectedProperty.address}, {selectedProperty.city}</h3>
              <p>₹{selectedProperty.price.toLocaleString('en-IN')}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PropertyList;
