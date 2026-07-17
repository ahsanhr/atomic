// api.js — centralized frontend API client
//
// all requests from the React application to the Flask backend
// should be defined in this file
//
// planned API operations:
//   - sign up
//   - log in
//   - submit onboarding information
//   - fetch dashboard and room state
//   - fetch quests
//   - complete a quest
//   - create and exchange Plaid tokens
//   - sync transactions
//   - roll for a friend
//
// responsibilities:
//   - use the backend base URL from environment variables
//   - attach the user's JWT to protected requests
//   - parse responses consistently
//   - surface request errors to pages
