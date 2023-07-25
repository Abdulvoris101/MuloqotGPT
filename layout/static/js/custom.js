// window.onload = function() {
//   // Set the number of visible pages
//   var visiblePages = 10; // You can adjust this value according to your preference

//   // Hide all pages initially
//   $('#pagination li.page-item').hide();

//   // Show the first batch of pages
//   $('#pagination li.page-item').slice(0, visiblePages).show();

//   // Get the total_pages value from the hidden input field
//   var total_pages = parseInt($('#total_pages').val());

//   // Add a click event handler to the pagination links
//   $('#pagination a.page-link').click(function(e) {
//     e.preventDefault();

//     // Get the current page from the clicked link's href

//     var currentPage = parseInt($(this).data("page"));

//     // Calculate the range of pages to be shown
//     var startIndex = currentPage - Math.floor(visiblePages / 2);
//     var endIndex = currentPage + Math.ceil(visiblePages / 2);

//     // Make sure the range doesn't go beyond the total number of pages
//     if (startIndex < 1) {
//       startIndex = 1;
//       endIndex = Math.min(visiblePages, total_pages);
//     }
//     if (endIndex > total_pages) {
//       endIndex = total_pages;
//       startIndex = Math.max(1, total_pages - visiblePages + 1);
//     }

//     // Hide all pages and show the calculated range
//     $('#pagination li.page-item').hide();
//     $('#pagination li.page-item').slice(startIndex - 1, endIndex).show();

//     // // Update the URL with the new page query parameter
//     var newUrl = window.location.pathname + '?page=' + currentPage;

//     // Redirect to the new page
//     window.location.href = newUrl;
//   });
// };

$(document).ready(function() {
  $("#allchats").hide();
  // Set the number of visible pages
  var visiblePages = 10; // You can adjust this value according to your preference

  // Function to show the correct pages based on the current page
  function showPages(currentPage) {
    var startIndex = currentPage - Math.floor(visiblePages / 2);
    var endIndex = currentPage + Math.ceil(visiblePages / 2);

    // Make sure the range doesn't go beyond the total number of pages
    if (startIndex < 1) {
      startIndex = 1;
      endIndex = Math.min(visiblePages, total_pages);
    }
    if (endIndex > total_pages) {
      endIndex = total_pages;
      startIndex = Math.max(1, total_pages - visiblePages + 1);
    }

    // Hide all pages and show the calculated range
    $('#pagination li.page-item').hide();
    $('#pagination li.page-item').slice(startIndex - 1, endIndex).show();
  }

  // Get the total_pages value from the hidden input field
  var total_pages = parseInt($('#total_pages').val());

  // Get the current page from the URL query parameter (?page=num)
  var currentPage = parseInt(new URLSearchParams(window.location.search).get('page')) || 1;

  // Show the correct pages based on the current page
  showPages(currentPage);
  // Add a click event handler to the pagination links
  $('#pagination a.page-link').click(function(e) {
    e.preventDefault();

    // Get the current page from the clicked link's href
    var currentPage = parseInt($(this).data("page"));

    // Update the URL with the new page query parameter
    var newUrl = window.location.pathname + '?page=' + currentPage;

    // Redirect to the new page
    window.location.href = newUrl;

  });
});



const searchInput = document.getElementById('searchInput');

searchInput.addEventListener('input', function() {
    const query = searchInput.value.toLowerCase();
    filterResults(query);
});


function filterResults(query) {
    

    $("#paginated-chats").hide();
    $("#allchats").show();

    if (query.length == 0 ) {
        $("#paginated-chats").show();
        $("#allchats").hide();
    }

    const tableBody = document.querySelector('#allchats');

    const rows = tableBody.querySelectorAll('tr');

    rows.forEach(function(row) {
        const cells = row.querySelectorAll('td');
        let match = false;

        cells.forEach(function(cell) {
            const text = cell.textContent.toLowerCase();
            if (text.includes(query)) {
                match = true;
            }
        });

        if (match) {
            row.style.display = ''; // Show the row
        } else {
            row.style.display = 'none'; // Hide the row
        }
    });
}

const activatedCheckbox = document.getElementById('activatedCheckbox');

activatedCheckbox.addEventListener('change', filterTableRows);

function filterTableRows() {
    

    const activatedRows = document.querySelectorAll('#allchats tr');
    
    activatedRows.forEach(function(row) {
        const checkboxCell = row.querySelector('#activated_row');
        
        const isChecked = activatedCheckbox.checked;

        const rowShouldDisplay = (isChecked && checkboxCell.innerHTML === 'True') || (!isChecked);
        
        if (rowShouldDisplay) {
            row.style.display = ''; // Show the row
        } else {
            row.style.display = 'none'; // Hide the row
        }
    });
}

const sortDateCheckbox = document.getElementById('sortDate');

sortDateCheckbox.addEventListener('change', sortTableByDate);

function sortTableByDate() {
  const tableBody = document.querySelector('tbody');
  const rows = Array.from(tableBody.querySelectorAll('tr'));


  rows.sort(function (a, b) {
    const dateAElement = a.querySelector('td:nth-child(6) span');
    const dateBElement = b.querySelector('td:nth-child(6) span');

    if (!dateAElement || !dateBElement) {
      return 0; // Return 0 to maintain the current order if the date elements are not found
    }

    const dateA = new Date(dateAElement.textContent);
    const dateB = new Date(dateBElement.textContent);

    if (sortDateCheckbox.checked) {
      return dateB - dateA; // Sort in descending order (newest first)
    } else {
      return dateA - dateB; // Sort in ascending order (oldest first)
    }
  });

  // Append the sorted rows back to the table body
  tableBody.innerHTML = '';
  rows.forEach(function (row) {
    tableBody.appendChild(row);
  });
}
