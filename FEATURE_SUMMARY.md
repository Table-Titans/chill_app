# Create Location & Course Offering Feature

## Overview
Users can now create new locations and course offerings on-the-fly when creating a session. This is implemented using modal dialogs that appear when users click the "+ Create New" option in the autocomplete suggestions.

## How It Works

### User Flow

1. **Navigate to Create Session Page** (`/create_session`)
2. **Search for Location or Course**
   - Start typing in the "Location" or "Course" field
   - Autocomplete suggestions will appear showing existing options
   - A "+ Create New" option appears at the top of suggestions

3. **Create New Location**
   - Click "+ Create New" in the location suggestions
   - Modal opens with fields:
     - **Address** (max 100 characters)
     - **Room Number** (max 20 characters)
   - Click "Create Location" to save
   - The new location is automatically selected in the form

4. **Create New Course Offering**
   - Click "+ Create New" in the course suggestions
   - Modal opens with fields:
     - **Course Title** (max 100 characters)
     - **Section** (max 20 characters)
     - **Year** (2020-2100, defaults to current year)
     - **Term** (Fall/Spring/Summer)
     - **Professor Name** (max 50 characters)
   - Click "Create Course" to save
   - The new course is automatically selected in the form

## Technical Implementation

### Files Created/Modified

1. **tests/location_data.py** (NEW)
   - Contains test location data with id, address, room_number

2. **tests/course_offering_data.py** (NEW)
   - Contains test course offering data with id, title, section, year, term, professor_name

3. **templates/create_session.html** (MODIFIED)
   - Added hidden fields for location_id and course_id
   - Added two modal forms (location and course)
   - Updated JavaScript to handle autocomplete with "Create New" option
   - Added modal interaction handlers
   - Added form submission handlers for creating new entities

4. **routes.py** (MODIFIED)
   - Added API endpoint: `GET /api/locations` - Search locations
   - Added API endpoint: `POST /api/locations` - Create new location
   - Added API endpoint: `GET /api/courses` - Search courses
   - Added API endpoint: `POST /api/courses` - Create new course offering
   - All endpoints include validation and duplicate checking

5. **static/css/style.css** (MODIFIED)
   - Added comprehensive modal styling
   - Added autocomplete enhancement for "Create New" option
   - Added responsive design for modals on mobile devices

### API Endpoints

#### GET /api/locations?q=query
Returns filtered locations based on search query
```json
[
  {
    "id": 1,
    "address": "Main Library",
    "room_number": "101"
  }
]
```

#### POST /api/locations
Creates a new location
**Request Body:**
```json
{
  "address": "Student Center",
  "room_number": "205"
}
```
**Response:**
```json
{
  "success": true,
  "location": {
    "id": 7,
    "address": "Student Center",
    "room_number": "205"
  }
}
```

#### GET /api/courses?q=query
Returns filtered course offerings based on search query
```json
[
  {
    "id": 1,
    "title": "Database Systems",
    "section": "A",
    "year": 2025,
    "term": 1,
    "professor_name": "Dr. Smith"
  }
]
```

#### POST /api/courses
Creates a new course offering
**Request Body:**
```json
{
  "title": "Advanced Programming",
  "section": "B",
  "year": 2025,
  "term": 2,
  "professor_name": "Prof. Johnson"
}
```
**Response:**
```json
{
  "success": true,
  "course": {
    "id": 7,
    "title": "Advanced Programming",
    "section": "B",
    "year": 2025,
    "term": 2,
    "professor_name": "Prof. Johnson"
  }
}
```

### Validation Rules

**Location:**
- Address: Required, max 100 characters
- Room Number: Required, max 20 characters
- Duplicate check: Prevents same address + room number combination

**Course Offering:**
- Title: Required, max 100 characters
- Section: Required, max 20 characters
- Year: Required, integer between 2020-2100
- Term: Required, 1 (Fall), 2 (Spring), or 3 (Summer)
- Professor Name: Required, max 50 characters
- Duplicate check: Prevents same title + section + year + term combination

## Testing

To test the feature:

1. Start the Flask app: `python app.py`
2. Navigate to `/create_session`
3. Try typing in the Location field - you'll see existing locations
4. Click "+ Create New" to open the modal
5. Fill in the form and submit
6. Verify the new location is selected automatically
7. Repeat for Course field

## Future Enhancements

- Add database persistence (currently uses in-memory test data)
- Add building/campus information to locations
- Add course prerequisites
- Add edit/delete functionality for existing locations and courses
- Add admin panel for bulk management

