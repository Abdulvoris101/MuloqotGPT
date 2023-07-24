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