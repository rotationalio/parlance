/*
 * main.js
 * Main entry point for the parlance application
 */

$(document).ready(function() {
  // Bind the logout action
  $(".logout").click(function(e) {
    e.preventDefault();
    $("#logoutForm").submit();
    return false;
  });
});