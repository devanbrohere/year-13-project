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
        special: addSelection.getAttribute('data-special-url'),
        add_card_stats: '/add_card_stats' // Add the URL for the add card stats form
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
        // Show or hide forms based on the selected form type
        cardAndStatsForm.style.display = (selectedFormType === 'card_and_stats') ? 'block' : 'none';
        evolutionForm.style.display = (selectedFormType === 'evolution') ? 'block' : 'none';
        specialForm.style.display = (selectedFormType === 'special') ? 'block' : 'none';
        
        // Set the selected option in the dropdown
        addSelection.value = selectedFormType; // Sync the dropdown selection with stored value
    }

    // Event listener for form type selection
    addSelection.addEventListener('change', function() {
        selectedFormType = this.value;
        localStorage.setItem('selectedFormType', selectedFormType);

        // Update the URL and toggle forms based on the selection
        updateURL(selectedFormType);
        toggleForms();

        // Reload the page to reflect the changes
        location.reload(); // This will refresh the page
    });

    // Initial toggle based on stored value
    toggleForms();
});

// File size validation
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

// Function to check file size
function checkFileSize(inputId) {
    const pictureInput = document.getElementById(inputId);
    pictureInput.addEventListener('change', () => {
        const pictureFile = pictureInput.files[0];

        if (pictureFile && pictureFile.size > MAX_FILE_SIZE) {
            alert('File size exceeds 5 MB limit.');
            pictureInput.value = ''; // Clear the input to allow re-selection
        }
    });
}

// Check file sizes for each input
checkFileSize('image');

// Target checkboxes limit
document.addEventListener("DOMContentLoaded", function() {
    const checkboxes = document.querySelectorAll("#target-checkboxes input[type='checkbox']");
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", function() {
            const checkedCount = Array.from(checkboxes).filter(i => i.checked).length;
            
            if (checkedCount > 2) {
                alert("You can only select up to 2 targets.");
                this.checked = false;  // Uncheck the current checkbox
            }
        });
    });
});
