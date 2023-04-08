console.log("This is handle button file")

var button = document.getElementById("my_button")

var STRIPE_PUBLISHABLE_KEY = 'pk_test_51MgrsGBQaa9YVByTDOqfwq6KRbSHLpXz7qlbHfrEYZ6GlCTAcCOfS3twyzLtorKVOfF7pJ6sWihyDApoy8Z9iUww00PxffUbrG'
var STRIPE_SECRET_KEY = 'sk_test_51MgrsGBQaa9YVByTibBRyP0pJe900jB034J6VUV05ZsHUnOzz31E4WQV3eRGQNPo0avPD4T5x1AsYtGsrYvlzlpp0058XVXTOl'




  // new
  // Event handler
  document.querySelector("#my_button").addEventListener("click", () => {
    // Get Checkout Session ID
    fetch("/create-checkout-session/")
    .then((result) => { return result.json(); })
    .then((data) => {
    const stripe = Stripe(data.publicKey);
      console.log(data);
      // Redirect to Stripe Checkout
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    });
  });
