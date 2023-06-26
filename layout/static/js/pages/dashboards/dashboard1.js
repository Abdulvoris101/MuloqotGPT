/*
Template Name: Admin Pro Admin
Author: Wrappixel
Email: niravjoshi87@gmail.com
File: js
*/
$(function () {
    "use strict";
    // ============================================================== 
    // Newsletter
    // ============================================================== 

    //ct-visits
    new Chartist.Line('#ct-visits', {
        labels: ['2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015'],
        series: [
            [5, 2, 7, 4, 5, 3, 5, 4]
            , [2, 5, 2, 6, 2, 5, 2, 4]
        ]
    }, {
        top: 0,
        low: 1,
        showPoint: true,
        fullWidth: true,
        plugins: [
            Chartist.plugins.tooltip()
        ],
        axisY: {
            labelInterpolationFnc: function (value) {
                return (value / 1) + 'k';
            }
        },
        showArea: true
    });


    var chart = [chart];

    var sparklineLogin = function () {
        $('#sparklinedash').sparkline([0, 5, 6, 10, 9, 12, 4, 9], {
            type: 'bar',
            height: '30',
            barWidth: '4',
            resize: true,
            barSpacing: '5',
            barColor: '#7ace4c'
        });
        $('#sparklinedash2').sparkline([0, 5, 6, 10, 9, 12, 4, 9], {
            type: 'bar',
            height: '30',
            barWidth: '4',
            resize: true,
            barSpacing: '5',
            barColor: '#7460ee'
        });
        $('#sparklinedash3').sparkline([0, 5, 6, 10, 9, 12, 4, 9], {
            type: 'bar',
            height: '30',
            barWidth: '4',
            resize: true,
            barSpacing: '5',
            barColor: '#11a0f8'
        });
        $('#sparklinedash4').sparkline([0, 5, 6, 10, 9, 12, 4, 9], {
            type: 'bar',
            height: '30',
            barWidth: '4',
            resize: true,
            barSpacing: '5',
            barColor: '#f33155'
        });
    }
    var sparkResize;
    $(window).on("resize", function (e) {
        clearTimeout(sparkResize);
        sparkResize = setTimeout(sparklineLogin, 500);
    });
    sparklineLogin();
});

const searchInput = document.getElementById('searchInput');

searchInput.addEventListener('input', function() {
    const query = searchInput.value.toLowerCase();
    console.log(query);
    filterResults(query);
});

function filterResults(query) {
    const tableBody = document.querySelector('tbody');
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
    const activatedRows = document.querySelectorAll('tbody tr');

    activatedRows.forEach(function(row) {
        const checkboxCell = row.querySelector('td:nth-child(5) span');
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

