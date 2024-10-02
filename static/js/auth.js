/* Helpers for authentication interaction */

$(document).ready(function() {

console.log("authentication application loaded");

$(".toggle-password").click(function(e) {
  e.preventDefault();

  let input = $("#password");
  let eye = $("#eye-icon");

  if (input.attr("type") === "password") {
    input.attr("type", "text");
  } else {
    input.attr("type", "password");
  }

  eye.toggleClass("fe-eye")
  eye.toggleClass("fe-eye-off")

  return false;
});

});