// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
  populateForm();
  setupEventListeners();
});

function setupEventListeners() {
  const cancelBtn = document.getElementById('cancelProfileBtn');
  const profileForm = document.getElementById('profileForm');
  const logoutBtn = document.getElementById('logoutBtn');

  if (cancelBtn) {
    cancelBtn.addEventListener('click', function(e) {
      e.preventDefault();
      window.location.href = '/calorie-counter/dashboard';
    });
  }
  
  if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
      e.preventDefault();
      saveProfile();
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }
}

function populateForm() {
  // Load profile data from localStorage
  const defaultProfile = {
    height: '5\'10"',
    weight: '180 lbs',
    age: '28 years',
    gender: 'Male',
    weightGoal: '165 lbs',
    activityLevel: '5 days',
    caloriesNeeded: '2200 kcal'
  };
  
  const profileData = JSON.parse(localStorage.getItem('profileData') || JSON.stringify(defaultProfile));
  
  const heightInput = document.getElementById('editHeight');
  const weightInput = document.getElementById('editWeight');
  const ageInput = document.getElementById('editAge');
  const genderInput = document.getElementById('editGender');
  const goalInput = document.getElementById('editWeightGoal');
  const activityInput = document.getElementById('editActivityLevel');
  const caloriesInput = document.getElementById('editCaloriesNeeded');
  
  if (heightInput) heightInput.value = profileData.height || '';
  if (weightInput) weightInput.value = profileData.weight || '';
  if (ageInput) ageInput.value = profileData.age || '';
  if (genderInput) genderInput.value = profileData.gender || '';
  if (goalInput) goalInput.value = profileData.weightGoal || '';
  if (activityInput) activityInput.value = profileData.activityLevel || '';
  if (caloriesInput) caloriesInput.value = profileData.caloriesNeeded || '';
}

function saveProfile() {
  // Get values from form
  const heightInput = document.getElementById('editHeight');
  const weightInput = document.getElementById('editWeight');
  const ageInput = document.getElementById('editAge');
  const genderInput = document.getElementById('editGender');
  const goalInput = document.getElementById('editWeightGoal');
  const activityInput = document.getElementById('editActivityLevel');
  const caloriesInput = document.getElementById('editCaloriesNeeded');
  
  // Create updated profile object
  const updatedProfile = {
    height: heightInput ? heightInput.value : '',
    weight: weightInput ? weightInput.value : '',
    age: ageInput ? ageInput.value : '',
    gender: genderInput ? genderInput.value : '',
    weightGoal: goalInput ? goalInput.value : '',
    activityLevel: activityInput ? activityInput.value : '',
    caloriesNeeded: caloriesInput ? caloriesInput.value : ''
  };
  
  // Save to localStorage
  localStorage.setItem('profileData', JSON.stringify(updatedProfile));
  
  // TODO: Send to backend
  console.log('Profile saved:', updatedProfile);
  
  // Return to dashboard
  window.location.href = '/calorie-counter/dashboard';
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
