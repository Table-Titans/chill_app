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
});

