// script.js
$(document).ready(function() {
    // Function to generate calendar
    function generateCalendar(year, month) {
      var firstDay = new Date(year, month, 1);
      var lastDay = new Date(year, month + 1, 0);
      var table = '<table class="table table-bordered"><thead><tr><th colspan="7">' + firstDay.toLocaleString('default', { month: 'long' }) + ' ' + year + '</th></tr><tr>';
      var days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      for (var i = 0; i < days.length; i++) {
        table += '<th>' + days[i] + '</th>';
      }
      table += '</tr></thead><tbody><tr>';
  
      var startDay = firstDay.getDay(); // Starting day of the week
      var endDate = lastDay.getDate(); // Last date of the month
  
      // Fill in the days before the first day of the month
      for (var i = 0; i < startDay; i++) {
        table += '<td></td>';
      }
  
      // Fill in the days of the month
      for (var i = 1; i <= endDate; i++) {
        if (startDay === 7) {
          startDay = 0;
          table += '</tr><tr>';
        }
        table += '<td>' + i + '</td>';
        startDay++;
      }
  
      // Fill in the remaining empty cells
      for (var i = startDay; i < 7; i++) {
        table += '<td></td>';
      }
  
      table += '</tr></tbody></table>';
  
      $('.calendar').html(table);
    }
  
    // Initial calendar generation
    var currentDate = new Date();
    generateCalendar(currentDate.getFullYear(), currentDate.getMonth());
  
    // Previous month button click handler
    $('#prevMonth').on('click', function() {
      currentDate.setMonth(currentDate.getMonth() - 1);
      generateCalendar(currentDate.getFullYear(), currentDate.getMonth());
    });
  
    // Next month button click handler
    $('#nextMonth').on('click', function() {
      currentDate.setMonth(currentDate.getMonth() + 1);
      generateCalendar(currentDate.getFullYear(), currentDate.getMonth());
    });
  });
  