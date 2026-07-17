// Onboarding.jsx — financial onboarding and generated-goals reveal
//
// collects the minimum information needed to create a starting plan
//
// user inputs:
//   - monthly income
//   - necessary monthly expenses
//   - current savings
//
// flow:
//   1. user submits their financial information
//   2. backend generates weekly spending and monthly savings goals
//   3. generated goals are revealed to the user
//   4. user continues into the first-day tutorial or room
//
// responsibilities:
//   - manage the onboarding form
//   - display loading and error states
//   - show the generated goals
//   - initialize the user's first room state through the API
