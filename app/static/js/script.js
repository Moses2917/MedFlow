document.addEventListener('DOMContentLoaded', function() {
  // Sample appointment dates (replace with actual data)
  var appointments = [
    '2024-04-10',
    '2024-04-15',
    '2024-04-26',
    // Add more appointment dates here
  ];

  // Initialize Flatpickr
  flatpickr('#calendar', {
    dateFormat: 'Y-m-d', // Set the date format
    defaultDate: 'today', // Set the initial date
    minDate: 'today', // Set the minimum selectable date
    inline: true, // Render the calendar inline
    enableTime: false, // Disable time selection
    disableMobile: false, // Enable mobile-friendly mode
    // Custom function to determine if a date has appointments
    // Custom function to determine if a date has appointments
    onDayCreate: function(dObj, dStr, fp, dayElem) {
      if (appointments.includes(dStr)) {
        dayElem.classList.add('has-appointment'); // Add a class to dates with appointments
      }
    }
  });
});
