let currentTrackId = null;

async function updateNowPlaying() {
  try {
    const res = await fetch("/now-playing/progress");
    const data = await res.json();

    // Update progress bar
    updateProgressBar(data.progress_ms, data.duration_ms);

    // If track changed, reload track info fragment
    if (data.track_id && data.track_id !== currentTrackId) {
      currentTrackId = data.track_id;
      await refreshTrackInfo();
    }
  } catch (err) {
    console.error("Error fetching progress:", err);
  }
}

function updateProgressBar(progress, duration) {
  const secondsPassed = Math.floor(progress / 1000);
  const secondsTotal = Math.floor(duration / 1000);
  const progressText = document.getElementById("progress-text");

  if (progressText) {
    progressText.textContent = `${secondsPassed} seconds of ${secondsTotal}`;
  }
}

async function refreshTrackInfo() {
  try {
    const res = await fetch("/now-playing/track-info");
    const html = await res.text();
    document.getElementById("track-info").innerHTML = html;
  } catch (err) {
    console.error("Error refreshing track info:", err);
  }
}

setInterval(updateNowPlaying, 3000); // Update every 3 seconds