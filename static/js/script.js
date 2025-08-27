document.addEventListener('DOMContentLoaded', function() {
    // Login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.text();
                }
            })
            .then(text => {
                // Handle error messages if needed
                console.log(text);
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Symptom assessment functionality
    const symptomCards = document.querySelectorAll('.symptom-card');
    symptomCards.forEach(card => {
        card.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    });

    // Health details form submission
    const healthForm = document.getElementById('healthForm');
    if (healthForm) {
        healthForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // You can add form validation here
            
            // Submit the form
            this.submit();
        });
    }
});

// Function to load diet plans based on user health data
function loadDietPlans() {
    fetch('/api/diet-plans')
        .then(response => response.json())
        .then(data => {
            const dietContainer = document.getElementById('dietPlans');
            if (dietContainer) {
                dietContainer.innerHTML = data.plans.map(plan => `
                    <div class="col-md-4 mb-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">${plan.name}</h5>
                                <p class="card-text">${plan.description}</p>
                                <ul>
                                    ${plan.meals.map(meal => `<li>${meal}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        })
        .catch(error => console.error('Error loading diet plans:', error));
}