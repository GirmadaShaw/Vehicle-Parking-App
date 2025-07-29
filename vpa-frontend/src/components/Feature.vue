<script setup>
import 'primeicons/primeicons.css';
</script>

<template>
    <div>
        <div class="container">
            <div class="phone-feature">
                <img src="/phone-feature.png" alt="phone showing price and features">
            </div>

            <div class="features">
                <div class="feature">
                    <i class="pi pi-lock icon-size" />
                    <h3> Secure </h3>
                    <p> Your data stays fully protected. </p>
                </div>
                <div class="feature">
                    <i class="pi pi-check icon-size" />
                    <h3> Reliable </h3>
                    <p> Always there when you need. </p>
                </div>
                <div class="feature">
                    <i class="pi pi-clock icon-size" />
                    <h3> Fast </h3>
                    <p> Book your parking in seconds. </p>
                </div>
                <div class="feature">
                    <i class="pi pi-face-smile icon-size" />
                    <h3> Easy </h3>
                    <p> Simple steps, smooth parking experience. </p>
                </div>
            </div>
        </div>

        <div class="cta-container">

            <div class="cta">
                <div>
                    <h2>3 Easy steps to secure parking</h2>
                </div>
                <div>
                    <p>You can have an instant booking then and there or you can schedule your parking beforehand</p>
                </div>
            </div>


            <div class="steps">
                <div class="img">
                    <img src="/step1.png" alt="Step 1 is to search your parking lot">
                </div>
                <div class="step">
                    <p> Step 1 </p>
                    <h3> Search </h3>
                    <p>You can easily search a parking space near you</p>
                </div>
            </div>

            <div class="steps">
                <div class="step">
                    <p> Step 2 </p>
                    <h3> Select </h3>
                    <p>You can select any space at any time and any place</p>
                </div>
                <div class="img">
                    <img src="/step2.png" alt="Step 2 is to select the lot">
                </div>
            </div>

            <div class="steps">
                <div class="img">
                    <img src="/step3.png" alt="Step 3 is to pay">
                </div>
                <div class="step">
                    <p> Step 3 </p>
                    <h3> Pay </h3>
                    <p>You can get a space at a very reasonable price</p>
                </div>
            </div>

        </div>
    </div>
</template>


<style scoped>
.container {
    background-color: #C9F7EC;
    height: 90vh;
    width: 98vw;
    display: flex;
    justify-content: space-around;
}

.phone-feature {
    max-width: 40%;
    height: 86vh;
    display: flex;
    align-content: center;
    justify-content: center;
    padding: 1%;
}

.phone-feature img {
    border-radius: 5%;
    height: 90%;
}


.features {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    row-gap: 15px;
    column-gap: 1.5rem;
    padding-top: 50px;
}

.feature {
    background-color: #DBF9F1;
    border-radius: 25px;
    height: 150px;
    width: 300px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.6s ease;
}


.feature:hover {
    transform: translateY(-5px);
}

.feature img {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 10px;
    margin-bottom: 10px;
}

.feature p {
    font-family: 'Montserrat';
    font-weight: 400;
    color: black;
    margin: 0;
}

.feature h3 {
    font-size: 26px;
    font-weight: bolder;
}

.icon-size {
    font-size: 2rem;
}


.cta-container {
    width: 99vw;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.cta {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.cta h2 {
    font-size: 65px;
    font-weight: 900;
}

.cta p {
    font-size: 26px;
    font-weight: 400;
}

.steps {
    width: 100%;
    display: flex;
    padding: 50px;
    gap: 15rem;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
}

.step {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-content: center;
}

.step p {
    font-size: 18px;
    color: gray;
    font-weight: 400;
}

.step h3 {
    font-size: 36px;
    font-weight: 700;
    padding-bottom: 1px;
    padding-top: 1em;
}

.img {
    position: relative;
    width: 300px;
    height: auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

.img::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 120%;
    height: 120%;
    background-color: #C9F7EC;
    border-radius: 45% 55% 50% 60% / 60% 50% 55% 45%;
    z-index: 1;
    filter: blur(40px);
    opacity: 0.8;
}

.img img {
    max-width: 100%;
    height: auto;
    position: relative;
    z-index: 2;
    object-fit: contain;
}
</style>
