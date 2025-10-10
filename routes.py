from flask import render_template, request, redirect, url_for, flash, jsonify
from tests.my_session_data import test_sessions as my_sessions
from tests.join_session_data import test_sessions as join_sessions
from tests.location_data import test_locations
from tests.course_offering_data import test_course_offerings

def register_routes(app):
    
    @app.route("/")
    def home():
        return render_template("main_dashboard.html", my_sessions=my_sessions, join_sessions=join_sessions)
    
    @app.route("/login")
    def login():
        return render_template("auth/login.html", title="Login")
    
    @app.route("/register")
    def register():
        return render_template("auth/register.html", title="Register")
    
    @app.route("/reset-password")
    def reset_password():
        return render_template("auth/reset_pass.html", title="Reset Password")
    
    @app.route("/create_session", methods=['GET', 'POST'])
    def create_session():
        if request.method == 'POST':
            # Get form data
            max_attendees = request.form.get('max_attendees', type=int)
            description = request.form.get('description')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            chill_level = request.form.get('chill_level')
            
            # TODO: Add database logic here to save the session
            
            flash('Study session created successfully!', 'success')
            return redirect(url_for('home'))
            
        return render_template("create_session.html", title="Create Session")
    
    @app.route("/leave_session/<int:session_id>", methods=['POST'])
    def leave_session(session_id):
        # Find and remove the session from my_sessions
        session_to_remove = None
        for session in my_sessions:
            if session['id'] == session_id:
                session_to_remove = session
                break
        
        if session_to_remove:
            my_sessions.remove(session_to_remove)
            return jsonify({'success': True, 'message': 'Successfully left the session'})
        else:
            return jsonify({'success': False, 'message': 'Session not found'}), 404
    
    # API endpoints for locations
    @app.route("/api/locations", methods=['GET'])
    def get_locations():
        query = request.args.get('q', '').lower()
        
        # Filter locations based on query
        filtered_locations = [
            location for location in test_locations
            if query in location['address'].lower() or query in location['room_number'].lower()
        ]
        
        return jsonify(filtered_locations)
    
    @app.route("/api/locations", methods=['POST'])
    def create_location():
        data = request.get_json()
        
        # Validate required fields
        if not data.get('address') or not data.get('room_number'):
            return jsonify({'success': False, 'message': 'Address and room number are required'}), 400
        
        # Validate field lengths
        if len(data['address']) > 100:
            return jsonify({'success': False, 'message': 'Address must be 100 characters or less'}), 400
        if len(data['room_number']) > 20:
            return jsonify({'success': False, 'message': 'Room number must be 20 characters or less'}), 400
        
        # Check if location already exists
        for location in test_locations:
            if location['address'].lower() == data['address'].lower() and \
               location['room_number'].lower() == data['room_number'].lower():
                return jsonify({'success': False, 'message': 'This location already exists'}), 409
        
        # Generate new ID
        new_id = max([loc['id'] for loc in test_locations]) + 1 if test_locations else 1
        
        # Create new location
        new_location = {
            'id': new_id,
            'address': data['address'],
            'room_number': data['room_number']
        }
        
        test_locations.append(new_location)
        
        return jsonify({'success': True, 'location': new_location})
    
    # API endpoints for course offerings
    @app.route("/api/courses", methods=['GET'])
    def get_courses():
        query = request.args.get('q', '').lower()
        
        # Filter courses based on query
        filtered_courses = [
            course for course in test_course_offerings
            if query in course['title'].lower() or 
               query in course['section'].lower() or 
               query in course['professor_name'].lower()
        ]
        
        return jsonify(filtered_courses)
    
    @app.route("/api/courses", methods=['POST'])
    def create_course():
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'section', 'year', 'term', 'professor_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Validate field lengths
        if len(data['title']) > 100:
            return jsonify({'success': False, 'message': 'Title must be 100 characters or less'}), 400
        if len(data['section']) > 20:
            return jsonify({'success': False, 'message': 'Section must be 20 characters or less'}), 400
        if len(data['professor_name']) > 50:
            return jsonify({'success': False, 'message': 'Professor name must be 50 characters or less'}), 400
        
        # Validate year and term
        try:
            year = int(data['year'])
            term = int(data['term'])
            if year < 2020 or year > 2100:
                return jsonify({'success': False, 'message': 'Year must be between 2020 and 2100'}), 400
            if term not in [1, 2, 3]:
                return jsonify({'success': False, 'message': 'Term must be 1 (Fall), 2 (Spring), or 3 (Summer)'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid year or term'}), 400
        
        # Check if course offering already exists
        for course in test_course_offerings:
            if course['title'].lower() == data['title'].lower() and \
               course['section'].lower() == data['section'].lower() and \
               course['year'] == year and \
               course['term'] == term:
                return jsonify({'success': False, 'message': 'This course offering already exists'}), 409
        
        # Generate new ID
        new_id = max([course['id'] for course in test_course_offerings]) + 1 if test_course_offerings else 1
        
        # Create new course offering
        new_course = {
            'id': new_id,
            'title': data['title'],
            'section': data['section'],
            'year': year,
            'term': term,
            'professor_name': data['professor_name']
        }
        
        test_course_offerings.append(new_course)
        
        return jsonify({'success': True, 'course': new_course})
