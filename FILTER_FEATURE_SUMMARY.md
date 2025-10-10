# Filter Feature Implementation

## Overview
The main dashboard now includes a collapsible filter panel that allows users to filter study sessions by multiple criteria. The UI is clean, consistent with the dashboard design, and doesn't take up space when not in use.

## Features

### Filter Criteria
Users can filter sessions by:
1. **Course Name** - Filter by specific course titles
2. **Location** - Filter by location address (e.g., Main Library, Student Center)
3. **Year** - Filter by course year (e.g., 2025)
4. **Term** - Filter by semester (Fall, Spring, Summer)
5. **Professor** - Filter by professor name

### Additional Features
- **Live Search Bar** - Works in conjunction with filters
- **Real-time Filtering** - Filters apply automatically when selections change
- **Clear All Button** - Quickly reset all filters
- **No Results Message** - Displays when no sessions match the criteria
- **Collapsible Panel** - Slides down smoothly when Filter button is clicked
- **Visual Feedback** - Filter button changes color when panel is active

## User Experience

### How to Use
1. Click the **"⚙ Filter"** button in the "Join a Session" section
2. The filter panel slides down, revealing filter options
3. Select any combination of filters from the dropdowns
4. Sessions automatically filter as you make selections
5. Use the search bar for additional text-based filtering
6. Click **"Clear All"** to reset all filters
7. Click the Filter button again to collapse the panel

### Design Highlights
- **Collapsible Design** - Panel slides down from the filter button (max-height animation)
- **Consistent Styling** - Purple gradient matching the app's color scheme
- **Responsive Grid** - Filter fields adapt to screen size
- **Smooth Animations** - 0.4s ease-out transitions
- **Icon Rotation** - Gear icon rotates when panel is active
- **Button State** - Filter button turns purple when active

## Technical Implementation

### Files Modified

#### 1. **tests/join_session_data.py** & **tests/my_session_data.py**
- Added `course_id` and `location_id` to each session
- Updated session titles and locations to match course/location data

#### 2. **templates/partials/session_card.html**
- Added data attributes for filtering:
  - `data-course-id`
  - `data-location-id`
  - `data-course-name`
  - `data-location-address`
  - `data-course-year`
  - `data-course-term`
  - `data-professor-name`
- Lookup course and location data using Jinja filters

#### 3. **templates/main_dashboard.html**
- Added collapsible filter panel with 5 filter dropdowns
- Added filter header with "Clear All" button
- Added "Apply Filters" button (though filters apply automatically)
- Added "No Results" message display
- Assigned IDs to search bar and sessions list for JavaScript access
- Filter options populated dynamically from course and location data

#### 4. **routes.py**
- Updated home route to pass `courses` and `locations` data to template
- Template now has access to all course offerings and locations for filter dropdowns

#### 5. **static/js/dashboard.js**
- Added filter panel toggle functionality
- Implemented `applyFilters()` function that:
  - Reads all filter values
  - Reads search bar value
  - Checks each session card's data attributes
  - Shows/hides cards based on match criteria
  - Displays "no results" message when needed
- Added `clearFilters()` function
- Auto-applies filters when:
  - Any dropdown changes
  - Search bar changes
  - Apply button is clicked

#### 6. **static/css/style.css**
- Added comprehensive filter panel styles:
  - `.filter-panel` - Collapsible container with max-height animation
  - `.filter-panel.active` - Expanded state
  - `.filter-header` - Header with title and clear button
  - `.filter-grid` - Responsive grid for filter fields
  - `.filter-select` - Styled dropdowns with focus states
  - `.apply-filters-btn` - Purple gradient button
  - `.filter_sessions.active` - Active state for filter button
  - `.no-results` - Message display when no matches
- Added responsive styles for mobile devices

## Filter Logic

The filtering system uses **AND logic** - sessions must match ALL selected filters:

```javascript
if (matchesCourse && matchesLocation && matchesYear && matchesTerm && matchesProfessor && matchesSearch) {
    // Show session card
} else {
    // Hide session card
}
```

Empty filters (not selected) are ignored, so users can filter by any combination.

## Responsive Design

### Desktop
- Filter grid displays 2-3 columns depending on screen width
- Horizontal layout for all controls

### Mobile (< 768px)
- Filter grid switches to single column
- Filter header stacks vertically
- All buttons become full width
- Panel max-height increased to 800px to accommodate vertical layout

## Data Structure

### Session Object
```python
{
    "id": 3,
    "course_id": 3,
    "location_id": 1,
    "title": "😤 Data Structures - Section A",
    "location": "Main Library - Room 101",
    "time": "7:00 AM",
    "attendees": 15
}
```

### Course Object
```python
{
    "id": 1,
    "title": "Principles Of Database Systems",
    "section": "A",
    "year": 2025,
    "term": 1,  # 1=Fall, 2=Spring, 3=Summer
    "professor_name": "Dr. Smith"
}
```

### Location Object
```python
{
    "id": 1,
    "address": "Main Library",
    "room_number": "101"
}
```

## Future Enhancements

Potential improvements for the filter system:
- Add "Save Filter Preset" functionality
- Add filter count badge showing active filters
- Add advanced filters (time of day, attendee count range)
- Add sorting options (by time, popularity, etc.)
- Add filter history/recent filters
- Add multi-select for courses/locations
- Add filter animations for individual cards

