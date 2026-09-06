<template>
  <div class="welcome-page">
    <div class="welcome-container">
      <h1>Hazmat Equipment Inventory</h1>
      <p>Please log in to continue.</p>
      <LoginForm />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import LoginForm from './LoginForm.vue';
import { onMounted } from 'vue';

const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  await authStore.checkAuth();
  if (authStore.isAuthenticated) {
    router.push('/detectors');
  }
});
</script>

<style scoped>
.welcome-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #f5f5f5;
}

.welcome-container {
  max-width: 400px;
  width: 100%;
  padding: 2rem;
  text-align: center;
}

.welcome-container h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
}

.welcome-container p {
  color: #666;
  margin-bottom: 1.5rem;
}
</style>