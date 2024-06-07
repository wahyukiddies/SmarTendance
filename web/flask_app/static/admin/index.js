const sideLinks = document.querySelectorAll('.sidebar .side-menu li a:not(.logout)');

sideLinks.forEach(item => {
    const li = item.parentElement;
    item.addEventListener('click', () => {
        sideLinks.forEach(i => {
            i.parentElement.classList.remove('active');
        });
        li.classList.add('active');

        // kode untuk memperbarui localStorage 
        const isSidebarOpen = !sideBar.classList.contains('close');
        localStorage.setItem('sidebarOpen', isSidebarOpen);
    });
});


const menuBar = document.querySelector('.content nav .bx.bx-menu');
const sideBar = document.querySelector('.sidebar');
const anchor = document.querySelector('a')

// Untuk memori side-menu
const isSidebarOpen = localStorage.getItem('sidebarOpen') === 'true';

// Mengatur status sidebar sesuai dengan yang diambil dari localStorage
if (isSidebarOpen) {
  sideBar.classList.remove('close');
} else {
  sideBar.classList.add('close');
}

menuBar.addEventListener('click', () => {
  sideBar.classList.toggle('close');
  const isSidebarOpen = !sideBar.classList.contains('close');
  
  // Menyimpan status sidebar ke localStorage
  localStorage.setItem('sidebarOpen', isSidebarOpen);
});

document.addEventListener('click', (event) => {
  const target = event.target;
  if (!sideBar.contains(target) && target !== menuBar && target === anchor) {
    sideBar.classList.add('open');
    
    // Menyimpan status sidebar ke localStorage
    localStorage.setItem('sidebarOpen', true);
  }
});

const searchBtn = document.querySelector('.content nav form .form-input button');
const searchBtnIcon = document.querySelector('.content nav form .form-input button .bx');
const searchForm = document.querySelector('.content nav form');

searchBtn.addEventListener('click', function (e) {
  if (window.innerWidth < 576) {
      e.preventDefault();
      searchForm.classList.toggle('show');
      if (searchForm.classList.contains('show')) {
          searchBtnIcon.classList.replace('bx-search', 'bx-x');
      } else {
          searchBtnIcon.classList.replace('bx-x', 'bx-search');
      }
  }
});

window.addEventListener('resize', () => {
  if (window.innerWidth < 768) {
      sideBar.classList.add('close');
  } else {
      sideBar.classList.remove('close');
  }
  if (window.innerWidth > 576) {
      searchBtnIcon.classList.replace('bx-x', 'bx-search');
      searchForm.classList.remove('show');
  }
});

const toggler = document.getElementById('theme-toggle');

toggler.addEventListener('change', function () {
  if (this.checked) {
      document.body.classList.add('dark');
      localStorage.setItem('theme', 'dark'); // Simpan dark mode
  } else {
      document.body.classList.remove('dark');
      localStorage.setItem('theme', 'light'); // Simpan lightmode
  }
});

document.addEventListener('DOMContentLoaded', function () {
  const sideLinks = document.querySelectorAll('.sidebar .side-menu li a');

  // Fungsi untuk mengatur tema
  const setTheme = (isDark) => {
      if (isDark) {
          document.body.classList.add('dark');
      } else {
          document.body.classList.entriesremove('dark');
      }
  };

  // Fungsi untuk menyimpan tema di localStorage
  const saveTheme = (isDark) => {
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
  };

  // Fungsi untuk memeriksa tema yang disimpan di localStorage
  const checkSavedTheme = () => {
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme === 'dark') {
        setTheme(true);
      } else {
        setTheme(false);
      }
  };

  // Memanggil fungsi untuk memeriksa tema yang disimpan di localStorage
  checkSavedTheme();
  
});

const logoutButton = document.getElementById('logout-button');
const confirmationModal = document.getElementById('confirmation-modal');
const confirmLogoutButton = document.getElementById('confirm-logout');
const cancelLogoutButton = document.getElementById('cancel-logout');

logoutButton.addEventListener('click', (e) => {
  e.preventDefault();
  const logoutUrl = logoutButton.getAttribute('data-logout-url');
  confirmationModal.classList.add('active');
});

cancelLogoutButton.addEventListener('click', () => {
  confirmationModal.classList.remove('active');
});

confirmLogoutButton.addEventListener('click', () => {
  const logoutUrl = logoutButton.getAttribute('data-logout-url');
  window.location.href = logoutUrl;
  confirmationModal.classList.remove('active');
});
