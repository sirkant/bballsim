document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    attachSortingListeners();

    // Bind the click event on the sidebar
    document.getElementById('sidebar').addEventListener('click', function(event) {
        // Stop the default link behavior
        event.preventDefault();

        // Check if a team link was clicked using event delegation
        let target = event.target;
        while (target != this) {
            if (target.classList.contains('team-link')) {
                console.log('Team link clicked', target);

                // Extract the team ID from the data attribute
                const teamId = target.getAttribute('data-team-id');
                console.log('Fetching details for team with ID:', teamId);

                // Call the function to fetch team details
                fetchTeamDetails(teamId);
                return;
            }
            target = target.parentNode;
        }
    });

    function fetchTeamDetails(teamId) {
        // Use the fetch API to send an AJAX request to the server
        fetch(`/team/${teamId}`)
            .then(response => {
                if (response.ok) {
                    console.log(`Response for team ${teamId} received`);
                    return response.text();
                } else {
                    throw new Error(`Network response was not ok for team ID ${teamId}.`);
                }
            })
            .then(html => {
                // Debug: Log the HTML response
                console.log(`HTML response for team ${teamId}:`, html);
                // Replace the content div with the response from the server
                document.getElementById('content').innerHTML = html;
                // Attach sorting listeners to new content
                attachSortingListeners();
            })
            .catch(error => {
                console.error('Error fetching team details:', error);
            });
    }
});

    function sortTable(n, table) {
        let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
        switching = true;
        // Set the sorting direction to ascending:
        dir = "asc";
        while (switching) {
            switching = false;
            rows = table.rows;
            for (i = 1; i < (rows.length - 1); i++) {
                shouldSwitch = false;
                x = rows[i].getElementsByTagName("TD")[n];
                y = rows[i + 1].getElementsByTagName("TD")[n];
                if (dir == "asc") {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir == "desc") {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
            if (shouldSwitch) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount++;
            } else {
                if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                }
            }
        }
    }

    function attachSortingListeners() {
        let headers = document.querySelectorAll('.sortable');
        headers.forEach(function(header, index) {
            header.addEventListener('click', function() {
                let table = header.closest('table');
                sortTable(index, table);
            });
        });
    }