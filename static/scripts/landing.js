const startGameButton = document.querySelector('.start-game');
const howToPlayButton = document.querySelector('.how-to-play');
const saveFilesButton = document.querySelector('.save-files');

startGameButton.addEventListener('click', () => {
  // Add logic to start the game
  console.log('Starting the game...');
});

howToPlayButton.addEventListener('click', () => {
  // Redirect to the "How to Play" page
  window.location.href = 'how-to-play.html';
});

saveFilesButton.addEventListener('click', () => {
  // Add logic to handle save files
  console.log('Accessing save files...');
});