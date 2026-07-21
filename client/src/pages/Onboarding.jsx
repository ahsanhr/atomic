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


import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/Navbar";
import {
  completeQuest,
  createPlaidLinkToken,
  createSandboxPublicToken,
  exchangePlaidToken,
  getDashboard,
  syncPlaidTransactions,
  TOKEN_KEY,
} from "../api";


const onboardingSteps = [
 {
   id: "bank",
   type: "bank",
   title: "Let's connect your bank account",
   subtitle: "to see how you've been spending",
   buttonText: "next →",
 },
 {
   id: "incomeExpenses",
   type: "amount",
   intro: "This is how much you spent on:",
   title: "income earning expenses",
   subtitle: "last month",
   description: "(car, internet, phone bills, etc.)",
   amount: 450,
 },
 {
   id: "rent",
   type: "amount",
   intro: "This is how much you spent on:",
   title: "rent / mortgage",
   subtitle: "last month",
   amount: 1400,
 },
 {
   id: "insurance",
   type: "amount",
   intro: "This is how much you spent on:",
   title: "insurance payments",
   subtitle: "last month",
   description: "(health, car, eye, etc.)",
   amount: 325,
 },
 {
   id: "groceries",
   type: "amount",
   intro: "This is how much you spent on:",
   title: "groceries and takeout",
   subtitle: "last month",
   amount: 520,
 },
 {
   id: "debt",
   type: "amount",
   intro: "This is how much you spent on:",
   title: "debt payments",
   subtitle: "last month",
   description: "(credit card, personal, student, etc.)",
   amount: 275,
 },
 {
   id: "essentials",
   type: "amount",
   intro: "This is how much you spent on:",
   title: "monthly essentials",
   subtitle: "last month",
   description: "(toiletries, power, water bills)",
   amount: 190,
 },
 {
   id: "takeHomePay",
   type: "amount",
   intro: "Finally this was your:",
   title: "take home pay",
   subtitle: "last month",
   description: "(income, side payments, etc.)",
   amount: 3200,
 },
 {
   id: "savingsIntro",
   type: "savings-intro",
   title: "one more thing - lets get started with a savings goal!",
   buttonText: "i'm ready →",
 },
 {
   id: "hasSavings",
   type: "yes-no",
   title: "do you currently have any savings or an emergency fund?",
 },
 {
   id: "noSavings",
   type: "message",
   title: "no worries! we'll make one for you.",
   buttonText: "next →",
 },
 {
   id: "goalChoice",
   type: "goal-choice",
   title: "amazing! we'll build on that.",
 },
];


export default function Onboarding() {
 const [current, setCurrent] = useState(0);
 const [selectedGoal, setSelectedGoal] = useState("");
 const [dashboard, setDashboard] = useState(null);
 const [connectionError, setConnectionError] = useState("");
 const [connecting, setConnecting] = useState(false);

 useEffect(() => {
   if (localStorage.getItem(TOKEN_KEY)) {
     getDashboard().then(setDashboard).catch(() => {});
   }
 }, []);


 const step = onboardingSteps[current];
 const isLastStep = current === onboardingSteps.length - 1;


 function nextStep() {
   if (!isLastStep) {
     setCurrent((previous) => previous + 1);
   } else {
     console.log("Onboarding finished", {
       selectedGoal,
     });
   }
 }


 function previousStep() {
   if (current > 0) {
     setCurrent((previous) => previous - 1);
   }
 }


 function handleSavingsAnswer(answer) {
   if (answer === "no") {
     const noSavingsIndex = onboardingSteps.findIndex(
       (item) => item.id === "noSavings"
     );


     setCurrent(noSavingsIndex);
   } else {
     const goalChoiceIndex = onboardingSteps.findIndex(
       (item) => item.id === "goalChoice"
     );


     setCurrent(goalChoiceIndex);
   }
 }


 function goToGoalChoices() {
   const goalChoiceIndex = onboardingSteps.findIndex(
     (item) => item.id === "goalChoice"
   );


   setCurrent(goalChoiceIndex);
 }

 async function finishConnection(publicToken) {
   await exchangePlaidToken(publicToken);
   await syncPlaidTransactions();
   setDashboard(await getDashboard());
   setCurrent(1);
 }

 async function connectSandbox() {
   setConnectionError("");
   setConnecting(true);
   try {
     const result = await createSandboxPublicToken();
     if (result.already_connected) {
       setDashboard(await getDashboard());
       setCurrent(1);
       return;
     }
     await finishConnection(result.public_token);
   } catch (error) {
     setConnectionError(error.message);
   } finally {
     setConnecting(false);
   }
 }

 async function connectWithPlaid() {
   setConnectionError("");
   setConnecting(true);
   try {
     if (!window.Plaid) {
       throw new Error("Plaid Link is still loading. Try again in a moment.");
     }
     const { link_token: linkToken } = await createPlaidLinkToken();
     const handler = window.Plaid.create({
       token: linkToken,
       onSuccess: async (publicToken) => {
         try {
           await finishConnection(publicToken);
         } catch (error) {
           setConnectionError(error.message);
         } finally {
           setConnecting(false);
         }
       },
       onExit: () => setConnecting(false),
     });
     handler.open();
   } catch (error) {
     setConnectionError(error.message);
     setConnecting(false);
   }
 }


 return (
   <div className="onboarding-page">
     <NavBar />


     <main className="onboarding-main">
       {step.type === "bank" && (
         <section className="onboarding-wide-screen">
           <h1>{step.title}</h1>
           <p>{step.subtitle}</p>


           <div className="onboarding-plaid-actions">
             <button
               type="button"
               className="onboarding-pill-button"
               onClick={connectSandbox}
               disabled={connecting}
             >
               {connecting ? "connecting..." : "use plaid sandbox"}
             </button>
             <button
               type="button"
               className="onboarding-link-button"
               onClick={connectWithPlaid}
               disabled={connecting}
             >
               connect with Plaid Link
             </button>
           </div>
           {connectionError && <p className="form-error">{connectionError}</p>}
         </section>
       )}


       {step.type === "amount" && (
         <section className="onboarding-card">
           <div className="onboarding-card-heading">
             <p className="onboarding-intro">{step.intro}</p>
             <h1>{step.title}</h1>
             <p className="onboarding-subtitle">{step.subtitle}</p>


             {step.description && (
               <p className="onboarding-description">
                 {step.description}
               </p>
             )}
           </div>


           <p className="onboarding-amount">
             ${amountForStep(step.id, dashboard).toLocaleString(undefined, {
               minimumFractionDigits: 2,
               maximumFractionDigits: 2,
             })}
           </p>


           <div className="onboarding-card-bottom">


             <div className="onboarding-navigation">
               <button
                 type="button"
                 className="onboarding-small-button"
                 onClick={previousStep}
               >
                 ←
               </button>


               <button
                 type="button"
                 className="onboarding-next-button"
                 onClick={nextStep}
               >
                 next →
               </button>
             </div>
           </div>
         </section>
       )}


       {step.type === "savings-intro" && (
         <section className="onboarding-wide-screen">
           <h1>{step.title}</h1>


           <button
             type="button"
             className="onboarding-pill-button onboarding-wide-button"
             onClick={nextStep}
           >
             {step.buttonText}
           </button>
         </section>
       )}


       {step.type === "yes-no" && (
         <section className="onboarding-wide-screen">
           <h1>{step.title}</h1>


           <div className="onboarding-yes-no">
             <button
               type="button"
               className="onboarding-choice-button"
               onClick={() => handleSavingsAnswer("no")}
             >
               no
             </button>


             <button
               type="button"
               className="onboarding-choice-button"
               onClick={() => handleSavingsAnswer("yes")}
             >
               yes
             </button>
           </div>
         </section>
       )}


       {step.type === "message" && (
         <section className="onboarding-wide-screen">
           <h1>{step.title}</h1>


           <button
             type="button"
             className="onboarding-pill-button onboarding-wide-button"
             onClick={goToGoalChoices}
           >
             {step.buttonText}
           </button>
         </section>
       )}


       {step.type === "goal-choice" && (
         <section className="onboarding-goal-screen">
           <h1>{step.title}</h1>


           <div className="onboarding-goal-options">
             <button
               type="button"
               className={
                 selectedGoal === "three-month"
                   ? "onboarding-goal-button onboarding-goal-selected"
                   : "onboarding-goal-button"
               }
               onClick={() => setSelectedGoal("three-month")}
             >
               i want to make a 3 month emergency fund
             </button>


             <button
               type="button"
               className={
                 selectedGoal === "six-month"
                   ? "onboarding-goal-button onboarding-goal-selected"
                   : "onboarding-goal-button"
               }
               onClick={() => setSelectedGoal("six-month")}
             >
               i want to make a 6 month emergency fund
             </button>


             <button
               type="button"
               className={
                 selectedGoal === "other"
                   ? "onboarding-goal-button onboarding-goal-selected"
                   : "onboarding-goal-button"
               }
               onClick={() => setSelectedGoal("other")}
             >
               i have another savings goal
               <br />
               (vacation, house, car, etc.)
             </button>
           </div>


           {selectedGoal && (
             <button
              type="button"
              className="onboarding-pill-button onboarding-continue-button"
              onClick={() => {
                completeQuest('input_savings_goal').catch(() => {});
                window.location.href = "/room";
              }}>
              continue →
              </button>
           )}
         </section>
       )}
     </main>
   </div>
 );
}

function amountForStep(stepId, dashboard) {
 if (!dashboard) return 0;

 const categories = dashboard.spending_by_category || [];
 const categoryAmount = (words) => categories
   .filter((item) => words.some((word) => String(item.category || "").toLowerCase().includes(word)))
   .reduce((total, item) => total + Number(item.amount || 0), 0);

 const amounts = {
   incomeExpenses: dashboard.expenses,
   rent: categoryAmount(["rent", "housing"]),
   insurance: categoryAmount(["insurance"]),
   groceries: categoryAmount(["food", "drink", "grocery"]),
   debt: categoryAmount(["debt", "loan"]),
   essentials: categoryAmount(["utility", "personal", "general service"]),
   takeHomePay: dashboard.income,
 };

 return Number(amounts[stepId] || 0);
}
