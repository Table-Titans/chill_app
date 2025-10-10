// Handle Leave Session button clicks
document.addEventListener('DOMContentLoaded', function() {
    // Get all leave session buttons
    const leaveButtons = document.querySelectorAll('.leave-session');
    
    leaveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sessionId = this.getAttribute('data-session-id');
            const sessionCard = this.closest('.session_card');
            
            // Confirm the action
            if (confirm('Are you sure you want to leave this session?')) {
                // Make POST request to leave session
                fetch(`/leave_session/${sessionId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove the session card from the DOM with animation
                        sessionCard.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                        sessionCard.style.opacity = '0';
                        sessionCard.style.transform = 'translateX(-20px)';
                        
                        // Remove element after animation completes
                        setTimeout(() => {
                            sessionCard.remove();
                            
                            // Check if there are no sessions left in "My Sessions"
                            const mySessionsList = document.querySelector('.sessions-section .sessions-list');
                            if (mySessionsList && mySessionsList.children.length === 0) {
                                const noSessionsMessage = document.createElement('p');
                                noSessionsMessage.textContent = 'You are not currently in any sessions.';
                                noSessionsMessage.style.textAlign = 'center';
                                noSessionsMessage.style.padding = '20px';
                                noSessionsMessage.style.color = '#666';
                                mySessionsList.appendChild(noSessionsMessage);
                            }
                        }, 300);
                    } else {
                        alert('Failed to leave session: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while leaving the session.');
                });
            }
        });
    });
    
    // Filter Panel Toggle
    const filterToggle = document.getElementById('filterToggle');
    const filterPanel = document.getElementById('filterPanel');
    
    if (filterToggle && filterPanel) {
        filterToggle.addEventListener('click', function() {
            filterPanel.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    
    // Filter Functionality
    const applyFiltersBtn = document.getElementById('applyFilters');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const searchBar = document.getElementById('searchBar');
    
    function applyFilters() {
        const courseFilter = document.getElementById('filterCourse').value.toLowerCase();
        const locationFilter = document.getElementById('filterLocation').value.toLowerCase();
        const yearFilter = document.getElementById('filterYear').value;
        const termFilter = document.getElementById('filterTerm').value;
        const professorFilter = document.getElementById('filterProfessor').value.toLowerCase();
        const searchQuery = searchBar ? searchBar.value.toLowerCase() : '';
        
        const sessionCards = document.querySelectorAll('#joinSessionsList .session_card');
        const noResultsMessage = document.getElementById('noResultsMessage');
        let visibleCount = 0;
        
        sessionCards.forEach(card => {
            const courseName = card.getAttribute('data-course-name').toLowerCase();
            const locationAddress = card.getAttribute('data-location-address').toLowerCase();
            const courseYear = card.getAttribute('data-course-year');
            const courseTerm = card.getAttribute('data-course-term');
            const professorName = card.getAttribute('data-professor-name').toLowerCase();
            const cardText = card.textContent.toLowerCase();
            
            // Check if card matches all filters
            const matchesCourse = !courseFilter || courseName.includes(courseFilter);
            const matchesLocation = !locationFilter || locationAddress.includes(locationFilter);
            const matchesYear = !yearFilter || courseYear === yearFilter;
            const matchesTerm = !termFilter || courseTerm === termFilter;
            const matchesProfessor = !professorFilter || professorName.includes(professorFilter);
            const matchesSearch = !searchQuery || cardText.includes(searchQuery);
            
            if (matchesCourse && matchesLocation && matchesYear && matchesTerm && matchesProfessor && matchesSearch) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show/hide no results message
        if (noResultsMessage) {
            noResultsMessage.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }
    
    function clearFilters() {
        document.getElementById('filterCourse').value = '';
        document.getElementById('filterLocation').value = '';
        document.getElementById('filterYear').value = '';
        document.getElementById('filterTerm').value = '';
        document.getElementById('filterProfessor').value = '';
        if (searchBar) searchBar.value = '';
        
        applyFilters();
    }
    
    // Event listeners for filter controls
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearFilters);
    }
    
    // Apply filters when search bar changes
    if (searchBar) {
        searchBar.addEventListener('input', applyFilters);
    }
    
    // Apply filters when any filter changes
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', applyFilters);
    });
});

