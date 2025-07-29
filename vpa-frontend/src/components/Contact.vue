<template>
  <div class="contact-container">
    <div class="booklot">
        <h1>Start using <span class="highlight">KwikPark</span> App now!</h1>
        <p>and start saving your time</p>
        <router-link to="/booklot">
            <button class="cta-button">Book Your Spot Now</button>
        </router-link>
        
    </div>

    <div class="social-links">
      <div class="links">
        <p>Follow Us</p>
        <div class="link">
            <i class="pi pi-facebook"></i>
            <i class="pi pi-instagram"></i>

            <a href="https://www.linkedin.com/in/paramveer13/" target="_blank">
                <i class="pi pi-linkedin"></i>
            </a>
            
            <a href="mailto:girmadashaw@gmail.com?subject=We need your feedback" target="_blank">
                <i class="pi pi-inbox"></i>
            </a>

            <a href="https://x.com/GirmadaShaw" target="_blank">
                <i class="pi pi-twitter"></i>
            </a>
            
        </div>
      </div>

      <div class="policy">
        <h5>Security</h5>
        <p>Privacy Policy</p>
        <p>Terms and Conditions</p>
      </div>
    </div>

    <div class="kwikpark-text">
      KwikPark
    </div>
  </div>
</template>

<style scoped>

.contact-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100vh;
  padding: 5px;
}

.booklot{
  background: linear-gradient(to bottom, #7ADEC6, #6BB2A1);
  padding: 6rem 2rem;
  text-align: center;
  color: white;
}

.booklot h1{
    font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.booklot .highlight {
  font-weight: 700;
}

.booklot p {
  font-size: 1.1rem;
  color: whitesmoke;
  margin-bottom: 2rem;
}

.cta-button {
  background-color: white;
  color: #6BB2A1;
  border: none;
  border-radius: 25px;
  padding: 0.8rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.cta-button:hover {
  background-color: #6BB2A1;
  color: white;
}

.social-links {
  display: flex;
  justify-content: space-around;
  gap: 40rem;
  margin-top: 2rem;
  margin-left: 1rem;
}

.social-links a {
  text-decoration: none;
  color: #333;
  font-size: 20px;
  font-weight: 500;
  transition: color 0.3s;
}

.links i:hover {
  font-size: 2.2rem;
}


.links{
    min-width: 20%;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1rem;
}
.links p{
    font-size: 22px;
    font-weight: 600;
}
.link{
    display: flex;
    gap: 3rem;
}
.link i{
    font-size: 2rem;
    color: #6BB2A1;
}

.policy{
    width: 20%;
}

.policy h5 {
    font-size: 22px;
    font-weight: 600;
}
.policy p{
    font-size: 18px;
    font-weight: 300;
    color: gray;
}

.kwikpark-text {
  text-align: center;
  font-size: 19vw;
  font-weight: 800;
  background: linear-gradient(to bottom, white, #7ADEC6);
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
