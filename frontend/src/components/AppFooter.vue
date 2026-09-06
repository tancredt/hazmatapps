<template>
  <footer class="app-footer">
    <div class="footer-content">
      <p class="copyright">&copy; 2026 Fire Rescue Victoria. All rights reserved.</p>
      <p class="disclaimer">Internal use only. Authorized personnel only.</p>
      <p class="support">For support, contact the FRV Hazmat Department.</p>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: #2c3e50;
  color: #999;
  padding: 0.35rem 2rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.footer-content p {
  margin: 0;
  font-size: 0.75rem;
  white-space: nowrap;
}

.copyright {
  font-weight: 500;
  color: #bbb;
}

.disclaimer {
  color: #888;
}

.support {
  color: #777;
  font-size: 0.75rem;
}

@media (max-width: 768px) {
  .app-footer {
    padding: 0.5rem 1rem;
  }

  .footer-content {
    flex-direction: column;
    gap: 0.25rem;
  }

  .footer-content p {
    font-size: 0.7rem;
    white-space: normal;
  }
}
</style>
