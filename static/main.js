document.addEventListener('DOMContentLoaded', (event) => {
    const friendsList = document.getElementById('friends-list');
    const sentRequestsList = document.getElementById('sent-requests-list');
    const receivedRequestsList = document.getElementById('received-requests-list');
    const leaderboardTableBody = document.querySelector('#leaderboard-table tbody');

    function clearLists() {
        if (friendsList) friendsList.innerHTML = '';
        if (sentRequestsList) sentRequestsList.innerHTML = '';
        if (receivedRequestsList) receivedRequestsList.innerHTML = '';
    }

    // Function to fetch and display the default (all users) leaderboard
    function showDefaultLeaderboard() {
        fetch('/leaderboard_data')
            .then(response => response.json())
            .then(data => {
                leaderboardTableBody.innerHTML = '';
                data.forEach(user => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${user.username}</td>
                        <td>${user.points}</td>
                        <td>${user.rank}</td>
                    `;
                    leaderboardTableBody.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching leaderboard data:', error));
    }

    // Function to fetch and display the friends-only leaderboard
    function showFriendsLeaderboard() {
        fetch('/friends_leaderboard_data')
            .then(response => response.json())
            .then(data => {
                leaderboardTableBody.innerHTML = '';
                data.forEach(user => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${user.username}</td>
                        <td>${user.points}</td>
                        <td>${user.rank}</td>
                    `;
                    leaderboardTableBody.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching friends leaderboard data:', error));
    }

    // Initial load: show the default leaderboard
    showDefaultLeaderboard();

    // Event listener for showing default leaderboard
    const showAllLeaderboardButton = document.getElementById('default-leaderboard-button');
    if (showAllLeaderboardButton) {
        showAllLeaderboardButton.addEventListener('click', showDefaultLeaderboard);
    }

    // Event listener for showing friends leaderboard
    const showFriendsLeaderboardButton = document.getElementById('friends-leaderboard-button');
    if (showFriendsLeaderboardButton) {
        showFriendsLeaderboardButton.addEventListener('click', showFriendsLeaderboard);
    }

    const showFriendsButton = document.getElementById('show-friends');
    if (showFriendsButton) {
        showFriendsButton.addEventListener('click', function() {
            clearLists();
            fetch('/get_friends')
                .then(response => response.json())
                .then(data => {
                    data.friends.forEach(friend => {
                        const listItem = document.createElement('li');
                        listItem.textContent = friend;
                        const removeButton = document.createElement('button');
                        removeButton.textContent = 'Remove';
                        removeButton.addEventListener('click', function() {
                            fetch(`/remove_friend/${friend}`, { method: 'POST' })
                                .then(response => response.json())
                                .then(data => {
                                    alert(data.message);
                                    listItem.remove();
                                });
                        });
                        listItem.appendChild(removeButton);
                        friendsList.appendChild(listItem);
                    });
                });
        });
    }

    const showSentRequestsButton = document.getElementById('show-sent-requests');
    if (showSentRequestsButton) {
        showSentRequestsButton.addEventListener('click', function() {
            clearLists();
            fetch('/get_sent_requests')
                .then(response => response.json())
                .then(data => {
                    sentRequestsList.innerHTML = data.sent_requests.join(', ');
                });
        });
    }

    const showReceivedRequestsButton = document.getElementById('show-received-requests');
    if (showReceivedRequestsButton) {
        showReceivedRequestsButton.addEventListener('click', function() {
            clearLists();
            fetch('/get_received_requests')
                .then(response => response.json())
                .then(data => {
                    data.received_requests.forEach(request => {
                        const listItem = document.createElement('li');
                        listItem.textContent = request;
                        const acceptButton = document.createElement('button');
                        acceptButton.textContent = 'Accept';
                        acceptButton.addEventListener('click', function() {
                            fetch(`/accept_friend_request/${request}`, { method: 'POST' })
                                .then(response => response.json())
                                .then(data => {
                                    alert(data.message);
                                    listItem.remove();
                                });
                        });
                        const rejectButton = document.createElement('button');
                        rejectButton.textContent = 'Reject';
                        rejectButton.addEventListener('click', function() {
                            fetch(`/reject_friend_request/${request}`, { method: 'POST' })
                                .then(response => response.json())
                                .then(data => {
                                    alert(data.message);
                                    listItem.remove();
                                });
                        });
                        listItem.appendChild(acceptButton);
                        listItem.appendChild(rejectButton);
                        receivedRequestsList.appendChild(listItem);
                    });
                });
        });
    }

    const addFriendButton = document.getElementById('add-friend');
    if (addFriendButton) {
        addFriendButton.addEventListener('click', function() {
            document.getElementById('add-friend-form').style.display = 'block';
        });
    }

    const sendRequestButton = document.getElementById('send-request');
    if (sendRequestButton) {
        sendRequestButton.addEventListener('click', function() {
            const friendUsername = document.getElementById('friend-username').value;
            fetch(`/send_friend_request/${friendUsername}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    document.getElementById('add-friend-form').style.display = 'none';
                    // Update the list of sent requests
                    fetch('/get_sent_requests')
                        .then(response => response.json())
                        .then(data => {
                            sentRequestsList.innerHTML = data.sent_requests.join(', ');
                        });
                });
        });
    }
});
