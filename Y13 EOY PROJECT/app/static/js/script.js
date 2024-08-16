document.getElementById('reg-log').addEventListener('change', function() {
    var form = document.getElementById('auth-form');
    if (this.checked) {
        form.action = signupUrl;
        form.querySelector('input[type="submit"]').value = "REGISTER";
    } else {
        form.action = loginUrl;
        form.querySelector('input[type="submit"]').value = "LOGIN";
    }
});


function updateCardList(cards) {
    var cardList = document.getElementById("cardslist");
    cardList.innerHTML = ""; // Clear previous list

    if (cards.length === 0) {
        var noCardMessage = document.createElement("p");
        noCardMessage.textContent = "No cards match the specified filters.";
        noCardMessage.className = "no-card-message"; // Add a class for styling if needed
        cardList.appendChild(noCardMessage);
        return;
    }

    cards.forEach(card => {
        var link = document.createElement("a");
        link.href = `/card/${card.id}`;
        link.className = "item-link";

        var div = document.createElement("div");
        div.className = "item";

        var img = document.createElement("img");
        img.src = card.image ? `/static/${card.image}` : '/static/default_image.jpg';
        img.className = "image";

        var p = document.createElement("p");
        p.textContent = card.name;
        p.className = "name";

        div.appendChild(img);
        div.appendChild(p);
        link.appendChild(div);
        cardList.appendChild(link);
    });
}

// Event listener for the filter button
document.querySelector('button[onclick="filterGames()"]').addEventListener('click', filterCards);

// Filter function
function filterCards() {
    var targetId = document.getElementById("targetDropdown").value;
    var rarityId = document.getElementById("rarityDropdown").value;

    fetch(`/api/cards?Target=${targetId}&Rarity=${rarityId}`)
        .then(response => response.json())
        .then(data => updateCardList(data.cards))
        .catch(error => console.error('Error fetching cards:', error));
}
