function sendMail(contactForm) {
    let element = document.getElementById("email_activity");
    element.classList.add("pulse");
    element.classList.remove("teal");
    element.classList.add("amber");
    emailjs.send("gmail", "westernonion", {
        "to_email": contactForm.report_email.value,
        "email_body": contactForm.email_body.value
    }).then(
        function(response) {
            console.log("Email SUCCESS", response);
            contactForm.submit();
        },
        function(error) {
            console.log("Email FAILED", error);
            element.classList.remove("pulse");
            element.classList.remove("amber");
            element.classList.add("red");
            M.toast({html: 'Could NOT send the email. Try again'})
            return false;
        }
    );
    return false;
}