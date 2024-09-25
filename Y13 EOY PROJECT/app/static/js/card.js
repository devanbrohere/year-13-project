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
