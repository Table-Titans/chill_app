from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from tests.my_session_data import test_sessions as my_sessions
from tests.join_session_data import test_sessions as join_sessions
from tests.location_data import test_locations
from tests.course_offering_data import test_course_offerings

def register_routes(app):

    def find_course(course_id):
        if not course_id:
            return None
        return next((course for course in test_course_offerings if course['id'] == course_id), None)

    def find_location(location_id):
        if not location_id:
            return None
        return next((location for location in test_locations if location['id'] == location_id), None)

    def find_session(session_id):
        for collection in (my_sessions, join_sessions):
            for session in collection:
                if session['id'] == session_id:
                    return session
        return None

    def format_datetime_string(value):
        if not value:
            return None
        try:
            dt = datetime.fromisoformat(value)
            # Remove leading zero from day component in a cross-platform safe way
            formatted = dt.strftime("%B %d, %Y %I:%M %p")
            return formatted.replace(" 0", " ").lstrip("0")
        except ValueError:
            return value

    def build_session_context(session_record):
        if not session_record:
            return None

        session_copy = dict(session_record)
        course = find_course(session_copy.get('course_id'))
        location = find_location(session_copy.get('location_id'))

        # Prefer explicit start/end times; fall back to generic time if needed
        start_display = session_copy.get('start_time')
        end_display = session_copy.get('end_time')
        if start_display and "T" in start_display:
            start_display = format_datetime_string(start_display)
        if end_display and "T" in end_display:
            end_display = format_datetime_string(end_display)

        if not start_display:
            start_display = session_copy.get('time') or "TBD"
        if not end_display:
            end_display = session_copy.get('end_time_display') or "TBD"

        session_copy['start_time'] = start_display
        session_copy['end_time'] = end_display

        attendees_data = session_copy.get('attendee_list', session_copy.get('attendees'))

        return {
            'session': session_copy,
            'course': course,
            'location': location,
            'attendees': attendees_data
        }
    
    @app.route("/")
    def home():
        return render_template("main_dashboard.html", 
                             my_sessions=my_sessions, 
                             join_sessions=join_sessions,
                             courses=test_course_offerings,
                             locations=test_locations)
    
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
            course_id = request.form.get('course_id', type=int)
            location_id = request.form.get('location_id', type=int)
            course_input = request.form.get('course', '').strip()
            location_input = request.form.get('location', '').strip()
            max_attendees = request.form.get('max_attendees', type=int)
            description = request.form.get('description')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            chill_level = request.form.get('chill_level')
            organizer = "You"

            selected_course = find_course(course_id)
            selected_location = find_location(location_id)

            course_title = selected_course['title'] if selected_course else course_input or "Study Session"
            course_section = selected_course['section'] if selected_course and selected_course.get('section') else ""
            professor_name = selected_course['professor_name'] if selected_course else None
            course_year = selected_course['year'] if selected_course else None
            course_term = selected_course['term'] if selected_course else None

            location_display = None
            if selected_location:
                location_display = f"{selected_location['address']} - Room {selected_location['room_number']}"
            elif location_input:
                location_display = location_input
            else:
                location_display = "TBD"

            def decorate_title(base_title, section):
                if section:
                    return f"{base_title} - Section {section}"
                return base_title

            emoji_prefix = chill_level if chill_level in ("😎", "🤓", "😤") else ""
            base_title = decorate_title(course_title, course_section)
            session_title = f"{emoji_prefix} {base_title}".strip()

            start_display = format_datetime_string(start_time) if start_time else None
            end_display = format_datetime_string(end_time) if end_time else None

            existing_ids = [session['id'] for session in my_sessions] + [session['id'] for session in join_sessions]
            new_session_id = max(existing_ids) + 1 if existing_ids else 1

            new_session = {
                "id": new_session_id,
                "course_id": selected_course['id'] if selected_course else None,
                "location_id": selected_location['id'] if selected_location else None,
                "title": session_title,
                "location": location_display,
                "time": start_display or start_time or "TBD",
                "attendees": 1,
                "max_attendees": max_attendees,
                "description": description,
                "attendee_list": ["You (Organizer)"],
                "start_time": start_time,
                "end_time": end_time,
                "organizer": organizer,
                "chill_level": emoji_prefix,
                "professor_name": professor_name,
                "year": course_year,
                "term": course_term,
                "section": course_section,
            }

            my_sessions.append(new_session)
            
            # TODO: Add database logic here to save the session
            
            flash('Study session created successfully!', 'success')
            return redirect(url_for('view_session', session_id=new_session_id))
            
        return render_template("create_session.html", title="Create Session")

    @app.route("/sessions/<int:session_id>")
    def view_session(session_id):
        session_record = find_session(session_id)
        if not session_record:
            abort(404)

        context = build_session_context(session_record)

        return render_template(
            "session.html",
            session=context['session'],
            course=context['course'],
            location=context['location'],
            attendees=context['attendees']
        )
    
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

    @app.route("/404")
    def show_not_found():
        return render_template("errors/404.html"), 404

    @app.errorhandler(404)
    def handle_not_found(error):
        return render_template("errors/404.html"), 404
