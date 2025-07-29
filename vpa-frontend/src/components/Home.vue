<script setup>
import Feature from './Feature.vue'
import Review from './Review.vue'
import Contact from './Contact.vue';
</script>


<template>
     <div>
       <div class="container">
            <div class="text-div">
                <h2 class="appname"> KwikPark </h2>
                <h1 class="title">Parking Was Never Easier</h1>
                <p class="subtitle">
                    Now, you won't have to waste your time looking for a parking spot every time you're out.
                </p>
            </div>

            <div class="phone-div">
                <img src="/phone-hero.png" alt="Map shown in phone">
            </div>
        </div>

        <Feature />
        <Review />
        <Contact />
        
    </div>
</template>


<style scoped>
.container {
    display: flex;
    gap: 1rem;
    height: 90vh;
    width: 100vw;
    overflow: hidden;
    padding: 0 5%;
}

.text-div {
    display: flex;
    flex-direction: column;
    gap: 4rem;
    min-width: 30%;
    padding: 20px;
}

.appname {
    font-size: 36px;
    font-weight: 500;
    color: black;
}


.title {
    font-size: 75px;
    font-weight: 900;
    color: black;
    margin-bottom: 1px;
}

.subtitle {
    font-size: 22px;
    font-weight: 650;
    color: #333333;
    margin-bottom: 30px;
}

.phone-div {
    position: relative;
    min-width: 55%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.phone-div::before {
    content: '';
    position: absolute;
    top: 5%;
    left: 0;
    width: 90%;
    height: 90%;
    background: radial-gradient(circle at 30% 70%, #DBF9F1, #C9F7EC, #7ADEC6, #6BB2A1);
    border-radius: 60% 40% 70% 90% / 50% 60% 40% 60%;
    z-index: 1;
    transform: rotate(10deg);
    filter: blur(40px);
    /* Professional soft edge */
}

.phone-div img {
    max-width: 90%;
    height: auto;
    position: relative;
    z-index: 2;
    object-fit: contain;
}

@media (max-width: 900px) {
    .container {
        flex-direction: column;
        text-align: center;
        padding: 30px;
    }

    .phone-div {
        margin-top: 30px;
    }

    .phone-div::before {
        width: 80%;
        height: 80%;
        top: 10%;
        left: 10%;
    }

    .phone-div img {
        max-width: 80%;
    }
}
</style>
