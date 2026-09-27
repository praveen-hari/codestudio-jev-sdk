import { JevClient } from "@syncfusion/codestudio-jev";

const client = JevClient.fromEnv();
const result = await client.decide({
  state: {
    service: "checkout",
    impact: "Payment processing is unavailable for every customer.",
  },
  questions: {
    is_incident: {
      type: "noul",
      instructions: "Does this state describe a production incident?",
    },
    owner: {
      type: "choice",
      instructions: "Which team should own the response?",
      criteria: {
        payments: "Checkout, billing, or payment processing.",
        frontend: "Rendering, layout, or browser behavior.",
      },
    },
    urgency: {
      type: "score",
      instructions: "How urgent is this incident?",
      criteria: ["Low", "Medium", "Critical"],
    },
  },
});

console.log(JSON.stringify(result, null, 2));