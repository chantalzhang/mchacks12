const startGameButton = document.querySelector('.start-game');
const howToPlayButton = document.querySelector('.how-to-play');

startGameButton.addEventListener('click', () => {
  // Add logic to start the game
  console.log('Starting the game...');
});

howToPlayButton.addEventListener('click', () => {
  // Redirect to the how-to-play route
  window.location.href = '/howToPlay';
});