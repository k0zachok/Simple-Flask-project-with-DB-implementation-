document.addEventListener('DOMContentLoaded', (event) => {
    const friendsList = document.getElementById('friends-list');
    const sentRequestsList = document.getElementById('sent-requests-list');
    const receivedRequestsList = document.getElementById('received-requests-list');

    function clearLists() {
        friendsList.innerHTML = '';
        sentRequestsList.innerHTML = '';
        receivedRequestsList.innerHTML = '';
    }

    document.getElementById('show-friends').addEventListener('click', function() {
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

    document.getElementById('show-sent-requests').addEventListener('click', function() {
        clearLists();
        fetch('/get_sent_requests')
            .then(response => response.json())
            .then(data => {
                sentRequestsList.innerHTML = data.sent_requests.join(', ');
            });
    });

    document.getElementById('show-received-requests').addEventListener('click', function() {
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

    document.getElementById('add-friend').addEventListener('click', function() {
        document.getElementById('add-friend-form').style.display = 'block';
    });

    document.getElementById('send-request').addEventListener('click', function() {
        const friendUsername = document.getElementById('friend-username').value;
        fetch(`/send_friend_request/${friendUsername}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                // Update the list of sent requests
                fetch('/get_sent_requests')
                    .then(response => response.json())
                    .then(data => {
                        sentRequestsList.innerHTML = data.sent_requests.join(', ');
                    });
            });
    });
});