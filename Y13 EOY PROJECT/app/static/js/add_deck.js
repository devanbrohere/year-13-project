let deck = [];
let selectedCardId = null;
let replacedCard = null;

// Select a card from the grid
function selectCard(cardId, imagePath) {
    if (deck.length < 8) {
        addCardToDeck(cardId, imagePath);
        hideCardFromGrid(cardId);
    } else {
        selectedCardId = cardId; // Card selected for replacement
        hideNonDeckCards(); // Hide all non-deck cards
        shakeDeckContinuously();
    }
}

// Add card to the first empty deck slot
function addCardToDeck(cardId, imagePath) {
    for (let i = 1; i <= 8; i++) {
        let slot = document.getElementById('slot' + i);
        if (!slot.classList.contains('filled')) {
            slot.classList.add('filled');
            slot.style.backgroundImage = 'url(' + imagePath + ')';
            slot.dataset.cardId = cardId;

            // Update the corresponding hidden input field
            document.getElementById('card' + i + '_id').value = cardId;

            deck.push({ id: cardId, imagePath: imagePath });
            hideCardFromGrid(cardId);
            break;
        }
    }
}

// Hide a card in the grid when it's added to the deck
function hideCardFromGrid(cardId) {
    let cardElement = document.getElementById('card-' + cardId);
    if (cardElement) {
        cardElement.style.display = 'none';
    }
}

// Show a card in the grid when it's removed from the deck
function showCardInGrid(cardId) {
    let cardElement = document.getElementById('card-' + cardId);
    if (cardElement) {
        cardElement.style.display = 'block';
    }
}

// Hide all non-deck cards except the selected one
function hideNonDeckCards() {
    let cardElements = document.querySelectorAll('.card-item');
    cardElements.forEach(card => {
        let cardId = card.getAttribute('id').split('-')[1];
        if (!deck.some(d => d.id === cardId) && cardId !== selectedCardId) {
            card.style.display = 'none';
        }
    });
}

// Shake the deck slots to indicate replacement
function shakeDeckContinuously() {
    document.querySelector('#cancelShake').style.display = 'block';
    document.querySelector('.shake-overlay').style.display = 'block';
    for (let i = 1; i <= 8; i++) {
        let slot = document.getElementById('slot' + i);
        if (slot.classList.contains('filled')) {
            slot.classList.add('continuous-shake');
        }
    }
}

// Replace the card in a slot with the selected one
function replaceCardInSlot(slotIndex) {
    let slot = document.getElementById('slot' + slotIndex);
    if (slot.classList.contains('filled') && selectedCardId) {
        let selectedCard = { id: selectedCardId, imagePath: document.querySelector('#card-' + selectedCardId + ' img').src };

        // Remove the replaced card
        if (replacedCard) {
            showCardInGrid(replacedCard.id);
        }

        replacedCard = deck.find(d => d.id === slot.dataset.cardId); // Card being replaced
        deck = deck.filter(d => d.id !== slot.dataset.cardId); // Remove old card from deck
        deck.push(selectedCard); // Add new card to the deck

        slot.dataset.cardId = selectedCard.id;
        slot.style.backgroundImage = 'url(' + selectedCard.imagePath + ')';

        // Update the corresponding hidden input field
        document.getElementById('card' + slotIndex + '_id').value = selectedCard.id;

        stopShakingDeck();
        showAllCards();
        selectedCardId = null;
    }
}

// Stop shaking animation and show all cards
function stopShakingDeck() {
    document.querySelector('#cancelShake').style.display = 'none';
    document.querySelector('.shake-overlay').style.display = 'none';
    for (let i = 1; i <= 8; i++) {
        let slot = document.getElementById('slot' + i);
        slot.classList.remove('continuous-shake');
    }
}

// Cancel replacement and reset card selections
function cancelShake() {
    stopShakingDeck();
    selectedCardId = null;
    replacedCard = null;
    showAllCards();
}

// Show only the cards that are not in the deck
function showAllCards() {
    let cardElements = document.querySelectorAll('.card-item');
    cardElements.forEach(card => {
        let cardId = card.getAttribute('id').split('-')[1];
        if (!deck.some(d => d.id === cardId)) {
            card.style.display = 'block'; // Only show cards not in the deck
        } else {
            card.style.display = 'none'; // Hide cards already in the deck
        }
    });
}

// Function to create form data from the deck
function createFormData(deck) {
    const formData = new FormData();
    deck.forEach((card, index) => {
        if (card && card.id) {
            formData.append(`card${index + 1}_id`, card.id);
        }
    });
    return formData;
}

