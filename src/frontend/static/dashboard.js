// Current date state
let currentDate = new Date();
let dailyEntries = [];

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
  setupEventListeners();
  updateDateDisplay();
  updateProfileDisplay();
});

function setupEventListeners() {
  const logoutBtn = document.getElementById('logoutBtn');
  const profileBtn = document.getElementById('profileBtn');
  const prevDay = document.getElementById('prevDay');
  const nextDay = document.getElementById('nextDay');
  const searchBtn = document.getElementById('searchBtn');
  const searchInput = document.getElementById('searchInput');
  const manualEntryBtn = document.getElementById('manualEntryBtn');

  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }
  if (profileBtn) {
    profileBtn.addEventListener('click', function() {
      window.location.href = '/calorie-counter/edit-profile';
    });
  }
  if (prevDay) {
    prevDay.addEventListener('click', function() {
      changeDate(-1);
    });
  }
  if (nextDay) {
    nextDay.addEventListener('click', function() {
      changeDate(1);
    });
  }
  if (searchBtn) {
    searchBtn.addEventListener('click', handleSearch);
  }
  if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        handleSearch();
      }
    });
  }
  if (manualEntryBtn) {
    manualEntryBtn.addEventListener('click', handleManualEntry);
  }
}

function updateDateDisplay() {
  const month = String(currentDate.getMonth() + 1).padStart(2, '0');
  const day = String(currentDate.getDate()).padStart(2, '0');
  const year = currentDate.getFullYear();
  const dateEl = document.getElementById('currentDate');
  if (dateEl) {
    dateEl.textContent = month + '/' + day + '/' + year;
  }
  // TODO: Load entries for this date from backend
  loadEntriesForDate();
}

function changeDate(days) {
  currentDate.setDate(currentDate.getDate() + days);
  updateDateDisplay();
}

function getLocalDateString() {
  const month = String(currentDate.getMonth() + 1).padStart(2, '0');
  const day = String(currentDate.getDate()).padStart(2, '0');
  const year = currentDate.getFullYear();
  return `${year}-${month}-${day}`;
}

function loadEntriesForDate() {
  const formattedDate = getLocalDateString();

  fetch(`/get_calories?date=${formattedDate}&user_id=${USER_ID}`)
    .then(res => res.json())
    .then(data => {
      dailyEntries = data.map(entry => ({
        id: entry.id,
        name: entry.food_name,
        calories: entry.calories
      }));

      renderEntries();
      updateTotalCalories();
    })
    .catch(err => {
      console.error('Error loading entries:', err);
    });
}

function renderEntries() {
  const entriesList = document.getElementById('entriesList');
  if (!entriesList) return;

  if (dailyEntries.length === 0) {
    entriesList.innerHTML = '<div class="no-entries">No entries for this day yet. Search or add manually to log food.</div>';
    return;
  }

  let html = '';
  dailyEntries.forEach(function(entry) {
    html += '<div class="entry-item">' +
      '<div class="entry-info">' +
        '<div class="entry-name">' + entry.name + '</div>' +
        '<div class="entry-calories">' + entry.calories + ' cal</div>' +
      '</div>' +
      '<button class="delete-entry-btn" data-id="' + entry.id + '">' +
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
          '<path d="M3 6h18"></path>' +
          '<path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>' +
          '<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>' +
        '</svg>' +
      '</button>' +
    '</div>';
  });
  entriesList.innerHTML = html;

  // Add delete listeners
  document.querySelectorAll('.delete-entry-btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      const id = parseInt(e.currentTarget.getAttribute('data-id'));
      deleteEntry(id);
    });
  });
}

function deleteEntry(id) {
  fetch(`http://localhost:7003/delete_calorie/${id}`, {
    method: 'DELETE'
  })
  .then(res => res.json())
  .then(() => {
    dailyEntries = dailyEntries.filter(function(entry) {
      return entry.id !== id;
    });

    renderEntries();
    updateTotalCalories();
  })
  .catch(err => {
    console.error('Error deleting entry:', err);
  });
}

function updateTotalCalories() {
  const total = dailyEntries.reduce(function(sum, entry) {
    return sum + entry.calories;
  }, 0);
  const totalEl = document.getElementById('totalCalories');
  if (totalEl) {
    totalEl.textContent = total;
  }
}

function addEntry(name, calories) {
  const formattedDate = getLocalDateString();

  fetch('http://localhost:7003/add_calorie', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: USER_ID,
      food_name: name,
      calories: calories,
      date: formattedDate
    })
  })
  .then(res => res.json())
  .then(data => {
    // Use ID from backend instead of Date.now()
    const newEntry = {
      id: data.id,
      name: name,
      calories: calories
    };

    dailyEntries.push(newEntry);
    renderEntries();
    updateTotalCalories();
  })
  .catch(err => {
    console.error('Error adding entry:', err);
  });
}

function handleLogout() {
  fetch('/logout', {
    method: 'GET',
    credentials: 'include'
  })
  .then(function(response) {
    if (response.ok) {
      window.location.href = '/';
    } else {
      console.error('Logout failed');
      alert('Logout failed. Please try again.');
    }
  })
  .catch(function(error) {
    console.error('Error during logout:', error);
    alert('An error occurred during logout.');
  });
}

function handleSearch() {
  const searchInput = document.getElementById('searchInput');
  const query = searchInput ? searchInput.value.trim() : '';
  
  if (!query) {
    alert('Please enter a food name to search');
    return;
  }
  
  const searchBtn = document.getElementById('searchBtn');
  if (searchBtn) {
    searchBtn.textContent = 'Searching...';
    searchBtn.disabled = true;
  }
  
  fetch('/openAICalc', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({input:query})
  })
  .then(function(response) {
    return response.json();
  })
  .then(function(data) {
    if (searchBtn) {
      searchBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
        '<circle cx="11" cy="11" r="8"></circle>' +
        '<path d="m21 21-4.35-4.35"></path>' +
      '</svg>';
      searchBtn.disabled = false;
    }
    
    if (data && query && data.total_calories) {
      // Successfully got nutrition info, add it
      addEntry(query, data.total_calories);
      if (searchInput) searchInput.value = '';
    } else {
      alert('No nutrition info found. Please try manual entry.');
    }
  })
  .catch(function(error) {
    console.error('Search error:', error);
    if (searchBtn) {
      searchBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
        '<circle cx="11" cy="11" r="8"></circle>' +
        '<path d="m21 21-4.35-4.35"></path>' +
      '</svg>';
      searchBtn.disabled = false;
    }
    alert('Error searching. Please try manual entry.');
  });
}

function handleManualEntry() {
  const nameInput = document.getElementById('manualName');
  const caloriesInput = document.getElementById('manualCalories');
  
  const name = nameInput ? nameInput.value.trim() : '';
  const calories = caloriesInput ? parseInt(caloriesInput.value) : 0;
  
  if (!name) {
    alert('Please enter a food name');
    return;
  }
  
  if (!calories || calories <= 0) {
    alert('Please enter valid calories');
    return;
  }
  
  addEntry(name, calories);
  
  // Clear inputs
  if (nameInput) nameInput.value = '';
  if (caloriesInput) caloriesInput.value = '';
}

function updateProfileDisplay() {
  // Load profile data from localStorage
  const defaultProfile = {
    weight: '180 lbs',
    age: '28 years',
    gender: 'Male',
    weightGoal: '165 lbs',
    activityLevel: '5 days',
    caloriesNeeded: '2200 kcal'
  };
  
  const profileData = JSON.parse(localStorage.getItem('profileData') || JSON.stringify(defaultProfile));
  
  const weightEl = document.getElementById('displayWeight');
  const ageEl = document.getElementById('displayAge');
  const genderEl = document.getElementById('displayGender');
  const goalEl = document.getElementById('displayWeightGoal');
  const activityEl = document.getElementById('displayActivityLevel');
  const caloriesEl = document.getElementById('displayCaloriesNeeded');
  
  if (weightEl) weightEl.textContent = profileData.weight;
  if (ageEl) ageEl.textContent = profileData.age;
  if (genderEl) genderEl.textContent = profileData.gender;
  if (goalEl) goalEl.textContent = profileData.weightGoal;
  if (activityEl) activityEl.textContent = profileData.activityLevel;
  if (caloriesEl) caloriesEl.textContent = profileData.caloriesNeeded;
}
