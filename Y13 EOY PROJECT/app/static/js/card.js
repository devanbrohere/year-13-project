document.addEventListener('DOMContentLoaded', function() {
    // Get references to the DOM elements
    var selectedFormType = localStorage.getItem('selectedFormType') || 'card_and_stats';
    var cardAndStatsForm = document.getElementById('card-and-stats-form');
    var evolutionForm = document.getElementById('evolution-form');
    var specialForm = document.getElementById('special-form');
    var addSelection = document.getElementById('add-selection');

    // Fetch URLs from data attributes
    var urls = {
        card_and_stats: addSelection.getAttribute('data-card-url'),
        evolution: addSelection.getAttribute('data-evolution-url'),
        special: addSelection.getAttribute('data-special-url')
    };

    // Function to update the URL based on the selected form
    function updateURL(formType) {
        var newUrl = urls[formType];
        if (newUrl) {
            history.pushState(null, '', newUrl); // Update the URL without reloading the page
        }
    }

    // Function to show/hide forms based on the selected option
    function toggleForms() {
        if (selectedFormType === 'card_and_stats') {
            cardAndStatsForm.style.display = 'block';
            evolutionForm.style.display = 'none';
            specialForm.style.display = 'none';

        } else if (selectedFormType === 'evolution') {
            cardAndStatsForm.style.display = 'none';
            evolutionForm.style.display = 'block';
            specialForm.style.display = 'none';

        } else if (selectedFormType === 'special') {
            cardAndStatsForm.style.display = 'none';
            evolutionForm.style.display = 'none';
            specialForm.style.display = 'block';
        }
    }

    addSelection.addEventListener('change', function() {
        selectedFormType = this.value;
        localStorage.setItem('selectedFormType', selectedFormType);

        // Update the URL and toggle forms based on the selection
        updateURL(selectedFormType);
        toggleForms();
    });

    // Initial toggle based on stored value
    toggleForms();
});
