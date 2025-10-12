from datetime import datetime

from flask import abort, flash, jsonify, redirect, render_template, request, url_for

from tests.course_offering_data import test_course_offerings
from tests.join_session_data import test_sessions as join_sessions
from tests.location_data import test_locations
from tests.my_session_data import test_sessions as my_sessions


def register_routes(app):
    def get_course(course_id):
        if not course_id:
            return None
        for course in test_course_offerings:
            if course["id"] == course_id:
                return course
        return None

    def get_location(location_id):
        if not location_id:
            return None
        for location in test_locations:
            if location["id"] == location_id:
                return location
        return None

    def get_session(session_id):
        for collection in (my_sessions, join_sessions):
            for session in collection:
                if session["id"] == session_id:
                    return session
        return None

    def format_display_time(raw_value):
        if not raw_value:
            return None
        try:
            return datetime.fromisoformat(raw_value).strftime("%b %d, %Y %I:%M %p")
        except ValueError:
            return raw_value

    def build_session_context(session_record):
        if not session_record:
            return None

        session_info = dict(session_record)
        course = get_course(session_info.get("course_id"))
        location = get_location(session_info.get("location_id"))

        start_display = format_display_time(session_info.get("start_time"))
        end_display = format_display_time(session_info.get("end_time"))
        time_display = session_info.get("time") or start_display or "TBD"

        session_info["start_display"] = start_display
        session_info["end_display"] = end_display
        session_info["time_display"] = time_display
        session_info["description"] = session_info.get("description") or "No description provided."
        session_info["organizer"] = session_info.get("organizer") or "Organizer not listed"

        location_label = session_info.get("location")
        if not location_label and location:
            location_label = location["address"]
            room = location.get("room_number")
            if room:
                location_label = f"{location_label} - Room {room}"
        map_query = location_label or ""

        attendee_store = session_record.get("attendee_list")
        attendee_count = session_record.get("attendees")

        if isinstance(attendee_store, dict):
            attendee_lines = [f"{key}: {value}" for key, value in attendee_store.items()]
        elif isinstance(attendee_store, list):
            attendee_lines = attendee_store
        elif isinstance(attendee_store, str):
            attendee_lines = [attendee_store]
        else:
            attendee_lines = []

        term_lookup = {1: "Fall", 2: "Spring", 3: "Summer"}
        course_details = None
        if course:
            course_details = {
                "title": course.get("title"),
                "section": course.get("section"),
                "year": course.get("year"),
                "term": term_lookup.get(course.get("term"), course.get("term")),
                "professor": course.get("professor_name"),
            }

        location_details = None
        if location_label:
            location_details = {
                "label": location_label,
                "map_query": map_query,
            }

        return {
            "session": session_info,
            "course_details": course_details,
            "location_details": location_details,
            "attendee_list": attendee_lines,
            "attendee_count": attendee_count,
        }

    @app.route("/")
    def home():
        course_lookup = {course["id"]: course for course in test_course_offerings}
        location_lookup = {loc["id"]: loc for loc in test_locations}

        course_titles = sorted({course["title"] for course in test_course_offerings})
        location_addresses = sorted({loc["address"] for loc in test_locations})
        course_years = sorted(
            {course["year"] for course in test_course_offerings if course.get("year")},
            reverse=True,
        )
        professor_names = sorted(
            {course["professor_name"] for course in test_course_offerings if course.get("professor_name")}
        )
        term_options = [(1, "Fall"), (2, "Spring"), (3, "Summer")]

        return render_template(
            "main_dashboard.html",
            my_sessions=my_sessions,
            join_sessions=join_sessions,
            courses=test_course_offerings,
            locations=test_locations,
            course_lookup=course_lookup,
            location_lookup=location_lookup,
            course_titles=course_titles,
            location_addresses=location_addresses,
            course_years=course_years,
            professor_names=professor_names,
            term_options=term_options,
        )

    @app.route("/login")
    def login():
        return render_template("auth/login.html", title="Login")

    @app.route("/register")
    def register():
        return render_template("auth/register.html", title="Register")

    @app.route("/reset-password")
    def reset_password():
        return render_template("auth/reset_pass.html", title="Reset Password")

    @app.route("/create_session", methods=["GET", "POST"])
    def create_session():
        if request.method == "POST":
            course_id = request.form.get("course_id", type=int)
            location_id = request.form.get("location_id", type=int)
            course_input = request.form.get("course", "").strip()
            location_input = request.form.get("location", "").strip()
            max_attendees = request.form.get("max_attendees", type=int) or 1
            description = (request.form.get("description") or "").strip()
            start_time = request.form.get("start_time")
            end_time = request.form.get("end_time")
            chill_level = request.form.get("chill_level") or ""

            selected_course = get_course(course_id)
            selected_location = get_location(location_id)

            base_title = selected_course["title"] if selected_course else (course_input or "Study Session")
            section_suffix = selected_course.get("section") if selected_course and selected_course.get("section") else ""
            if section_suffix:
                base_title = f"{base_title} - Section {section_suffix}"

            emoji_prefix = chill_level if chill_level in ("😎", "🤓", "😤") else ""
            session_title = f"{emoji_prefix} {base_title}".strip()

            if selected_location:
                location_display = selected_location["address"]
                room_number = selected_location.get("room_number")
                if room_number:
                    location_display = f"{location_display} - Room {room_number}"
            else:
                location_display = location_input or "TBD"

            existing_ids = [session["id"] for session in my_sessions] + [session["id"] for session in join_sessions]
            new_session_id = max(existing_ids) + 1 if existing_ids else 1

            start_display = format_display_time(start_time)

            new_session = {
                "id": new_session_id,
                "course_id": selected_course["id"] if selected_course else None,
                "location_id": selected_location["id"] if selected_location else None,
                "title": session_title,
                "location": location_display,
                "time": start_display or "TBD",
                "attendees": 1,
                "max_attendees": max_attendees,
                "description": description or "No description provided.",
                "attendee_list": ["You (Organizer)"],
                "start_time": start_time,
                "end_time": end_time,
                "organizer": "You",
                "chill_level": emoji_prefix,
            }

            if selected_course:
                new_session.update(
                    {
                        "professor_name": selected_course.get("professor_name"),
                        "year": selected_course.get("year"),
                        "term": selected_course.get("term"),
                        "section": selected_course.get("section"),
                    }
                )
            elif course_input:
                new_session["course_name"] = course_input

            my_sessions.append(new_session)
            flash("Study session created successfully!", "success")
            return redirect(url_for("view_session", session_id=new_session_id))

        return render_template("create_session.html", title="Create Session")

    @app.route("/sessions/<int:session_id>")
    def view_session(session_id):
        session_record = get_session(session_id)
        if not session_record:
            abort(404)

        context = build_session_context(session_record)
        if not context:
            abort(404)

        return render_template("session.html", **context)

    @app.route("/leave_session/<int:session_id>", methods=["POST"])
    def leave_session(session_id):
        for index, session in enumerate(my_sessions):
            if session["id"] == session_id:
                my_sessions.pop(index)
                return jsonify({"success": True, "message": "Successfully left the session"})
        return jsonify({"success": False, "message": "Session not found"}), 404

    @app.route("/api/locations", methods=["GET"])
    def get_locations():
        query = (request.args.get("q") or "").strip().lower()
        if not query:
            return jsonify(test_locations)

        filtered = []
        for location in test_locations:
            haystack = f"{location['address']} {location['room_number']}".lower()
            if query in haystack:
                filtered.append(location)
        return jsonify(filtered)

    @app.route("/api/locations", methods=["POST"])
    def create_location():
        data = request.get_json() or {}
        address = (data.get("address") or "").strip()
        room_number = (data.get("room_number") or "").strip()

        if not address or not room_number:
            return jsonify({"success": False, "message": "Address and room number are required"}), 400

        for location in test_locations:
            if location["address"].lower() == address.lower() and location["room_number"].lower() == room_number.lower():
                return jsonify({"success": False, "message": "This location already exists"}), 409

        new_id = max((loc["id"] for loc in test_locations), default=0) + 1
        new_location = {"id": new_id, "address": address, "room_number": room_number}
        test_locations.append(new_location)
        return jsonify({"success": True, "location": new_location})

    @app.route("/api/courses", methods=["GET"])
    def get_courses():
        query = (request.args.get("q") or "").strip().lower()
        if not query:
            return jsonify(test_course_offerings)

        filtered = []
        for course in test_course_offerings:
            values = [
                course.get("title", ""),
                course.get("section", ""),
                course.get("professor_name", ""),
            ]
            haystack = " ".join(values).lower()
            if query in haystack:
                filtered.append(course)
        return jsonify(filtered)

    @app.route("/api/courses", methods=["POST"])
    def create_course():
        data = request.get_json() or {}
        title = (data.get("title") or "").strip()
        section = (data.get("section") or "").strip()
        professor_name = (data.get("professor_name") or "").strip()
        year = data.get("year")
        term = data.get("term")

        if not all([title, section, professor_name, year, term]):
            return jsonify({"success": False, "message": "All fields are required"}), 400

        try:
            year = int(year)
            term = int(term)
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "Year and term must be numbers"}), 400

        for course in test_course_offerings:
            if (
                course["title"].lower() == title.lower()
                and course["section"].lower() == section.lower()
                and course.get("year") == year
                and course.get("term") == term
            ):
                return jsonify({"success": False, "message": "This course offering already exists"}), 409

        new_id = max((course["id"] for course in test_course_offerings), default=0) + 1
        new_course = {
            "id": new_id,
            "title": title,
            "section": section,
            "year": year,
            "term": term,
            "professor_name": professor_name,
        }
        test_course_offerings.append(new_course)
        return jsonify({"success": True, "course": new_course})

    @app.route("/404")
    def show_not_found():
        return render_template("errors/404.html"), 404

    @app.errorhandler(404)
    def handle_not_found(_error):
        return render_template("errors/404.html"), 404
