const functions = require("firebase-functions");
const admin = require("firebase-admin");
const stripe = require("stripe")(functions.config().stripe.secret);
const cors = require("cors")({ origin: true });

admin.initializeApp();

exports.createPaymentIntent = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    try {
      const { amount } = req.body;
      const paymentIntent = await stripe.paymentIntents.create({
        amount,
        currency: "usd",
      });
      res.status(200).send(paymentIntent.client_secret);
    } catch (error) {
      console.error("Error creating payment intent:", error);
      res.status(500).send({ error: error.message });
    }
  });
});
