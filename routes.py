from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from werkzeug.utils import secure_filename
from tests.my_session_data import test_sessions as my_sessions
from tests.join_session_data import test_sessions as join_sessions
from tests.location_data import test_locations
from tests.course_offering_data import test_course_offerings
from tests.room_type_data import test_room_types
from tests.tag_data import test_tags, test_session_tags
from tests.resource_data import test_resources
from tests.reminder_data import test_reminders

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

    def find_room_type(room_type_id):
        if not room_type_id:
            return None
        return next((room for room in test_room_types if room['id'] == room_type_id), None)

    def get_session_tag_ids(session_id):
        if not session_id:
            return []
        return [link['tag_id'] for link in test_session_tags if link['session_id'] == session_id]

    def find_tags(tag_ids):
        if not tag_ids:
            return []
        return [tag for tag in test_tags if tag['id'] in tag_ids]

    def get_resources_for_session(session_id):
        return [resource for resource in test_resources if resource['session_id'] == session_id]

    def get_reminders_for_session(session_id):
        reminders = [reminder for reminder in test_reminders if reminder['session_id'] == session_id]
        formatted = []
        for reminder in reminders:
            reminder_copy = dict(reminder)
            reminder_copy['display_time'] = format_datetime_string(reminder_copy.get('reminder_time'))
            formatted.append(reminder_copy)
        return formatted

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
        room_type = find_room_type(session_copy.get('room_type_id'))
        session_copy['room_type'] = room_type

        tag_ids = session_copy.get('tag_ids') or get_session_tag_ids(session_copy['id'])
        session_copy['tag_ids'] = tag_ids
        session_copy['tags'] = find_tags(tag_ids)
        session_copy['resources'] = get_resources_for_session(session_copy['id'])
        session_copy['reminders'] = get_reminders_for_session(session_copy['id'])

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
                             locations=test_locations,
                             room_types=test_room_types,
                             tags=test_tags)
    
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
            room_type_id = request.form.get('room_type_id', type=int)
            reminder_time = request.form.get('reminder_time')
            tag_ids = []
            for raw_tag in request.form.getlist('tags'):
                try:
                    tag_ids.append(int(raw_tag))
                except (TypeError, ValueError):
                    continue
            resource_ids = []
            reminder_ids = []
            organizer = "You"

            selected_course = find_course(course_id)
            selected_location = find_location(location_id)
            room_type = find_room_type(room_type_id)

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

            # Handle resource upload (placeholder upload to CDN)
            resource_file = request.files.get('resource_file')
            if resource_file and resource_file.filename:
                filename = secure_filename(resource_file.filename)
                if '.' not in filename:
                    flash('Resources must have a .txt or .pdf extension.', 'error')
                    return redirect(request.url)
                extension = filename.rsplit('.', 1)[-1].lower()
                if extension not in ('txt', 'pdf'):
                    flash('Resources must be a text or PDF file.', 'error')
                    return redirect(request.url)

                existing_resource_ids = [resource['id'] for resource in test_resources]
                new_resource_id = max(existing_resource_ids) + 1 if existing_resource_ids else 1
                fake_url = f"https://cdn.example.com/uploads/{filename}"

                new_resource = {
                    "id": new_resource_id,
                    "session_id": new_session_id,
                    "resource_name": filename,
                    "resource_url": fake_url,
                    "updated_by": 0
                }
                test_resources.append(new_resource)
                resource_ids.append(new_resource_id)

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
                "room_type_id": room_type['id'] if room_type else None,
                "tag_ids": tag_ids,
                "resource_ids": resource_ids,
                "reminder_ids": reminder_ids
            }

            if reminder_time:
                existing_reminder_ids = [reminder['id'] for reminder in test_reminders]
                new_reminder_id = max(existing_reminder_ids) + 1 if existing_reminder_ids else 1
                new_reminder = {
                    "id": new_reminder_id,
                    "session_id": new_session_id,
                    "user_id": 0,
                    "reminder_time": reminder_time,
                    "reminder_sent": False
                }
                test_reminders.append(new_reminder)
                reminder_ids.append(new_reminder_id)

            for tag_id in tag_ids:
                test_session_tags.append({
                    "session_id": new_session_id,
                    "tag_id": tag_id
                })

            my_sessions.append(new_session)
            
            # TODO: Add database logic here to save the session
            
            flash('Study session created successfully!', 'success')
            return redirect(url_for('view_session', session_id=new_session_id))
            
        return render_template("create_session.html", title="Create Session", room_types=test_room_types, tags=test_tags)

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
            attendees=context['attendees'],
            tags=test_tags,
            room_types=test_room_types
        )

    @app.route("/sessions/<int:session_id>/resources", methods=['POST'])
    def upload_session_resource(session_id):
        session_record = find_session(session_id)
        if not session_record:
            abort(404)

        organizer_name = session_record.get('organizer', '')
        if "You" not in organizer_name:
            flash('Only the session organizer can upload resources for now.', 'error')
            return redirect(url_for('view_session', session_id=session_id))

        resource_file = request.files.get('resource_file')
        if not resource_file or not resource_file.filename:
            flash('Please choose a text or PDF file to upload.', 'error')
            return redirect(url_for('view_session', session_id=session_id))

        filename = secure_filename(resource_file.filename)
        if '.' not in filename:
            flash('Resources must have a .txt or .pdf extension.', 'error')
            return redirect(url_for('view_session', session_id=session_id))

        extension = filename.rsplit('.', 1)[-1].lower()
        if extension not in ('txt', 'pdf'):
            flash('Resources must be a text or PDF file.', 'error')
            return redirect(url_for('view_session', session_id=session_id))

        existing_resource_ids = [resource['id'] for resource in test_resources]
        new_resource_id = max(existing_resource_ids) + 1 if existing_resource_ids else 1
        fake_url = f"https://cdn.example.com/uploads/{filename}"

        new_resource = {
            "id": new_resource_id,
            "session_id": session_id,
            "resource_name": filename,
            "resource_url": fake_url,
            "updated_by": 0
        }
        test_resources.append(new_resource)

        resource_ids = session_record.setdefault('resource_ids', [])
        resource_ids.append(new_resource_id)

        flash('Resource uploaded. The CDN link is a placeholder until storage is in place.', 'success')
        return redirect(url_for('view_session', session_id=session_id))
    
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
