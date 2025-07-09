import os
from flask import Flask, request, jsonify, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from flask_babel import Babel, gettext as _
from sqlalchemy.dialects.mysql import LONGBLOB

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(app.root_path, 'translations')
app.config['LANGUAGES'] = {'en': 'English', 'kn': 'Kannada', 'te': 'Telugu'}

def determine_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en', 'kn', 'te'])

babel = Babel(app, locale_selector=determine_locale)
db = SQLAlchemy(app)
CORS(app)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    locality = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=True)
    area_value = db.Column(db.Float, nullable=True)
    area_unit = db.Column(db.String(20), nullable=True)
    bedrooms = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    features = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    mediator_name = db.Column(db.String(100), nullable=True)
    mediator_contact = db.Column(db.String(20), nullable=True)
    listing_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    photos = db.relationship('PropertyPhoto', backref='property', lazy=True, cascade="all, delete-orphan")

class PropertyPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_data = db.Column(LONGBLOB, nullable=False)
    mimetype = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

def get_image_data_and_mimetype(file):
    try:
        file.seek(0)
        image_data = file.read()
        mimetype = file.mimetype
        return image_data, mimetype
    except Exception as e:
        print(f"Error reading file for DB storage: {e}")
        return None, None

@app.route('/property_photos/<int:photo_id>')
def serve_property_photo(photo_id):
    photo = PropertyPhoto.query.get(photo_id)
    if photo and photo.image_data:
        return Response(photo.image_data, mimetype=photo.mimetype)
    return jsonify({'error': 'Photo not found or data missing'}), 404

@app.route('/')
def home():
    return _("Real Estate Backend is Running!")

@app.route('/properties', methods=['POST'])
def add_property():
    try:
        property_type = request.form.get('property_type')
        address = request.form.get('address')
        city = request.form.get('city')
        locality = request.form.get('locality')

        price_val = request.form.get('price')
        price = float(price_val) if price_val else None

        area_value_val = request.form.get('area_value')
        area_value = float(area_value_val) if area_value_val else None

        area_unit = request.form.get('area_unit')

        bedrooms_val = request.form.get('bedrooms')
        bedrooms = int(bedrooms_val) if bedrooms_val else None

        bathrooms_val = request.form.get('bathrooms')
        bathrooms = int(bathrooms_val) if bathrooms_val else None

        description = request.form.get('description')
        features = request.form.get('features')
        status = request.form.get('status')
        mediator_name = request.form.get('mediator_name')
        mediator_contact = request.form.get('mediator_contact')

        listing_date_str = request.form.get('listing_date')
        listing_date = datetime.strptime(listing_date_str, '%Y-%m-%d').date() if listing_date_str else None

        new_property = Property(
            property_type=property_type,
            address=address,
            city=city,
            locality=locality,
            price=price,
            area_value=area_value,
            area_unit=area_unit,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            description=description,
            features=features,
            status=status,
            mediator_name=mediator_name,
            mediator_contact=mediator_contact,
            listing_date=listing_date,
            created_at=datetime.now()
        )

        db.session.add(new_property)
        db.session.flush()

        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo_file in photos:
                if photo_file and photo_file.filename != '':
                    image_data, mimetype = get_image_data_and_mimetype(photo_file)
                    if image_data and mimetype:
                        new_photo = PropertyPhoto(property_id=new_property.id, image_data=image_data, mimetype=mimetype)
                        db.session.add(new_photo)
        db.session.commit()

        return jsonify({'message': 'Property added successfully!', 'property_id': new_property.id}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error adding property: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/properties', methods=['GET'])
def get_properties():
    try:
        query = Property.query

        property_type = request.args.get('property_type')
        if property_type:
            query = query.filter_by(property_type=property_type)

        min_price = request.args.get('min_price')
        if min_price:
            query = query.filter(Property.price >= float(min_price))

        max_price = request.args.get('max_price')
        if max_price:
            query = query.filter(Property.price <= float(max_price))

        city = request.args.get('city')
        if city:
            query = query.filter(Property.city.ilike(f'%{city}%'))

        locality = request.args.get('locality')
        if locality:
            query = query.filter(Property.locality.ilike(f'%{locality}%'))

        bedrooms = request.args.get('bedrooms')
        if bedrooms:
            query = query.filter(Property.bedrooms >= int(bedrooms))

        bathrooms = request.args.get('bathrooms')
        if bathrooms:
            query = query.filter(Property.bathrooms >= int(bathrooms))

        properties = query.all()

        properties_list = []
        for prop in properties:
            photos_data = [{
                'id': photo.id,
                'image_url': f"{request.url_root.rstrip('/')}/property_photos/{photo.id}"
            } for photo in prop.photos]

            properties_list.append({
                'id': prop.id,
                'property_type': prop.property_type,
                'address': prop.address,
                'city': prop.city,
                'locality': prop.locality,
                'price': prop.price,
                'area_value': prop.area_value,
                'area_unit': prop.area_unit,
                'bedrooms': prop.bedrooms,
                'bathrooms': prop.bathrooms,
                'description': prop.description,
                'features': prop.features,
                'status': prop.status,
                'mediator_name': prop.mediator_name,
                'mediator_contact': prop.mediator_contact,
                'listing_date': prop.listing_date.isoformat() if prop.listing_date else None,
                'created_at': prop.created_at.isoformat(),
                'photos': photos_data
            })
        return jsonify(properties_list), 200
    except Exception as e:
        print(f"Error fetching properties: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/properties/<int:property_id>', methods=['DELETE'])
def delete_property(property_id):
    try:
        property_to_delete = Property.query.get_or_404(property_id)
        db.session.delete(property_to_delete)
        db.session.commit()
        return jsonify({'message': 'Property deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting property: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
