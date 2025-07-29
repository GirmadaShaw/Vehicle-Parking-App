<script setup>
import SummaryCard from './SummaryCard.vue'
import ReservationCard from './ReservationCard.vue';
import LotCard from './LotStats.vue';
import UserStats from './UserStats.vue';
import FinancialCard from './FinancialCard.vue';

</script>

<template>
  <div>
    <h1 class="title">Your Dashboard, Girmada</h1>
    <SummaryCard />
    <h2 class="title">Reservations</h2>
    <ReservationCard />
    <h2 class="title">Lot Performance Overview</h2>
    <LotCard />
    <h2 class="title">User Stats</h2>
    <UserStats />
    <h2 class="title">Financials</h2>
    <FinancialCard />
</div>
</template>

<style>
.title {
  color: #6bb2a1;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
}
</style>