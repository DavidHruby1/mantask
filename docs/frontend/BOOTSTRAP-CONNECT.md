- handleBootstrapSubmit is the gateway
- it needs to check for:
    - if all the fields are filled correctly
    - essential is .env bootstrap seed, that must match (handled on backend)

Flow:
1. user fills the form
2. user clicks submit button which triggers form submit
3. form submit emit goes to the Bootstrap component
4. handleBootstrapSubmit is called <-- **here**
  |
  |
  v
5. goes through Pinia store
  |
  |
  v
6. sends the data to backend
7. backend validates all, checks if seed is correct
8. sends the result back to Bootstrap component
  |
  |
  v
9. Pinia store gets updated
10. Bootstrap component either shows error or redirects to /dashboard
    - but it also has to automatically authenticate the user
