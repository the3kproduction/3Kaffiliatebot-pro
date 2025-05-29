// Simple Radio Player that works
let radioPlayerVisible = false;

function createSimpleRadio() {
    const radioHTML = `
        <div id="simple-radio-player" style="position: fixed; top: 100px; right: 20px; width: 350px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); z-index: 9999; font-family: Arial, sans-serif; color: white; display: none;">
            <div style="background: rgba(0, 0, 0, 0.2); padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; cursor: move;">
                <div style="display: flex; align-items: center;">
                    <span style="margin-right: 8px; font-size: 16px;">📻</span>
                    <span style="font-size: 14px; font-weight: bold;">AffiliateBot Radio</span>
                </div>
                <div>
                    <button onclick="minimizeRadio()" style="background: rgba(255, 255, 255, 0.2); border: none; color: white; padding: 5px 10px; border-radius: 5px; cursor: pointer; margin-right: 5px;">−</button>
                    <button onclick="closeRadio()" style="background: rgba(255, 255, 255, 0.2); border: none; color: white; padding: 5px 10px; border-radius: 5px; cursor: pointer;">×</button>
                </div>
            </div>
            
            <div id="radio-content" style="padding: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 15px; background: rgba(0, 0, 0, 0.2); border-radius: 10px;">
                    <div>
                        <div id="current-station" style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">Select a station</div>
                        <div id="current-genre" style="font-size: 12px; opacity: 0.8;">Choose your music</div>
                    </div>
                    <div id="visualizer" style="display: flex; align-items: end; gap: 2px; height: 30px;">
                        <div style="width: 3px; height: 10px; background: #4ecdc4; border-radius: 2px;"></div>
                        <div style="width: 3px; height: 20px; background: #4ecdc4; border-radius: 2px;"></div>
                        <div style="width: 3px; height: 15px; background: #4ecdc4; border-radius: 2px;"></div>
                        <div style="width: 3px; height: 25px; background: #4ecdc4; border-radius: 2px;"></div>
                        <div style="width: 3px; height: 12px; background: #4ecdc4; border-radius: 2px;"></div>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px; padding: 10px; background: rgba(0, 0, 0, 0.1); border-radius: 10px;">
                    <button id="play-btn" onclick="togglePlay()" style="background: linear-gradient(135deg, #ff6b6b, #4ecdc4); border: none; color: white; padding: 8px 12px; border-radius: 5px; cursor: pointer; font-size: 18px;">▶️</button>
                    <button onclick="stopRadio()" style="background: rgba(255, 255, 255, 0.2); border: none; color: white; padding: 5px 10px; border-radius: 5px; cursor: pointer;">⏹️</button>
                    <button id="mute-btn" onclick="toggleMute()" style="background: rgba(255, 255, 255, 0.2); border: none; color: white; padding: 5px 10px; border-radius: 5px; cursor: pointer;">🔊</button>
                    <input type="range" id="volume" min="0" max="100" value="70" onchange="setVolume(this.value)" style="flex: 1; height: 5px; background: rgba(255, 255, 255, 0.3); border-radius: 5px; outline: none;">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 15px;">
                        <button onclick="showGenre('pop')" class="genre-btn" style="background: linear-gradient(135deg, #ff6b6b, #4ecdc4); border: none; color: white; padding: 8px 12px; border-radius: 20px; cursor: pointer; font-size: 11px;">Pop & Hits</button>
                        <button onclick="showGenre('rock')" class="genre-btn" style="background: rgba(255, 255, 255, 0.1); border: none; color: white; padding: 8px 12px; border-radius: 20px; cursor: pointer; font-size: 11px;">Rock & Metal</button>
                        <button onclick="showGenre('electronic')" class="genre-btn" style="background: rgba(255, 255, 255, 0.1); border: none; color: white; padding: 8px 12px; border-radius: 20px; cursor: pointer; font-size: 11px;">Electronic</button>
                        <button onclick="showGenre('hiphop')" class="genre-btn" style="background: rgba(255, 255, 255, 0.1); border: none; color: white; padding: 8px 12px; border-radius: 20px; cursor: pointer; font-size: 11px;">Hip-Hop</button>
                        <button onclick="showGenre('jazz')" class="genre-btn" style="background: rgba(255, 255, 255, 0.1); border: none; color: white; padding: 8px 12px; border-radius: 20px; cursor: pointer; font-size: 11px;">Jazz & Blues</button>
                        <button onclick="showGenre('classical')" class="genre-btn" style="background: rgba(255, 255, 255, 0.1); border: none; color: white; padding: 8px 12px; border-radius: 20px; cursor: pointer; font-size: 11px;">Classical</button>
                    </div>
                    
                    <div id="stations-list" style="max-height: 200px; overflow-y: auto;">
                        <div id="pop-stations" class="station-group">
                            <div onclick="playStation('https://playerservices.streamtheworld.com/api/livestream-redirect/SIRIUSXM_HITS1.mp3', 'SiriusXM Hits 1')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px; transition: all 0.3s ease;"><span style="margin-right: 10px;">🎵</span><span>SiriusXM Hits 1</span></div>
                            <div onclick="playStation('https://stream.kissfm.ro:8000/kissfm.aacp', 'Kiss FM')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px; transition: all 0.3s ease;"><span style="margin-right: 10px;">💋</span><span>Kiss FM</span></div>
                            <div onclick="playStation('https://media-ice.musicradio.com/CapitalMP3', 'Capital FM')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px; transition: all 0.3s ease;"><span style="margin-right: 10px;">🏙️</span><span>Capital FM</span></div>
                        </div>
                        
                        <div id="rock-stations" class="station-group" style="display: none;">
                            <div onclick="playStation('https://planetradio.co.uk/planetrock/live/', 'Planet Rock')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">🤘</span><span>Planet Rock</span></div>
                            <div onclick="playStation('https://stream.kerrangradio.co.uk/kerrang.mp3', 'Kerrang! Radio')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">⚡</span><span>Kerrang! Radio</span></div>
                            <div onclick="playStation('https://cast2.asurahosting.com:8045/radio.mp3', 'Metal Radio')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">🔥</span><span>Metal Radio</span></div>
                        </div>
                        
                        <div id="electronic-stations" class="station-group" style="display: none;">
                            <div onclick="playStation('https://radiofg.impek.com/fg', 'Radio FG')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">🎧</span><span>Radio FG</span></div>
                            <div onclick="playStation('https://ibizaglobalradio.streaming-pro.com:8024/ibizaglobal.mp3', 'Ibiza Global Radio')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">🏝️</span><span>Ibiza Global Radio</span></div>
                        </div>
                        
                        <div id="hiphop-stations" class="station-group" style="display: none;">
                            <div onclick="playStation('https://playerservices.streamtheworld.com/api/livestream-redirect/WQHTFM.mp3', 'Hot 97')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">🔥</span><span>Hot 97</span></div>
                            <div onclick="playStation('https://playerservices.streamtheworld.com/api/livestream-redirect/KPWRFM.mp3', 'Power 106')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">💪</span><span>Power 106</span></div>
                        </div>
                        
                        <div id="jazz-stations" class="station-group" style="display: none;">
                            <div onclick="playStation('https://playerservices.streamtheworld.com/api/livestream-redirect/SMOOTHJAZZ.mp3', 'Smooth Jazz')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">🎷</span><span>Smooth Jazz</span></div>
                            <div onclick="playStation('https://edge-bauerseoprod-01-gos2.sharp-stream.com/jazzfm.mp3', 'Jazz FM')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">🎺</span><span>Jazz FM</span></div>
                        </div>
                        
                        <div id="classical-stations" class="station-group" style="display: none;">
                            <div onclick="playStation('https://media-ice.musicradio.com/ClassicFMMP3', 'Classic FM')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">🎼</span><span>Classic FM</span></div>
                            <div onclick="playStation('https://stream.wqxr.org/wqxr', 'WQXR Classical')" style="display: flex; align-items: center; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; cursor: pointer; margin-bottom: 5px;"><span style="margin-right: 10px;">🎻</span><span>WQXR Classical</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', radioHTML);
}

// Radio functionality
let currentAudio = null;
let isPlaying = false;
let isMuted = false;

function showRadio() {
    const player = document.getElementById('simple-radio-player');
    if (player) {
        player.style.display = 'block';
        radioPlayerVisible = true;
    } else {
        createSimpleRadio();
        setTimeout(() => {
            document.getElementById('simple-radio-player').style.display = 'block';
            radioPlayerVisible = true;
        }, 100);
    }
}

function closeRadio() {
    const player = document.getElementById('simple-radio-player');
    if (player) {
        player.style.display = 'none';
        radioPlayerVisible = false;
    }
    if (currentAudio) {
        currentAudio.pause();
        isPlaying = false;
    }
}

function minimizeRadio() {
    const content = document.getElementById('radio-content');
    if (content.style.display === 'none') {
        content.style.display = 'block';
    } else {
        content.style.display = 'none';
    }
}

function showGenre(genre) {
    // Hide all station groups
    const groups = document.querySelectorAll('.station-group');
    groups.forEach(group => group.style.display = 'none');
    
    // Show selected genre
    const selectedGroup = document.getElementById(genre + '-stations');
    if (selectedGroup) selectedGroup.style.display = 'block';
    
    // Update button styles
    const buttons = document.querySelectorAll('.genre-btn');
    buttons.forEach(btn => {
        btn.style.background = 'rgba(255, 255, 255, 0.1)';
    });
    event.target.style.background = 'linear-gradient(135deg, #ff6b6b, #4ecdc4)';
}

function playStation(url, name) {
    if (currentAudio) {
        currentAudio.pause();
    }
    
    currentAudio = new Audio(url);
    currentAudio.volume = 0.7;
    
    currentAudio.addEventListener('loadstart', () => {
        document.getElementById('current-station').textContent = 'Loading...';
    });
    
    currentAudio.addEventListener('canplay', () => {
        document.getElementById('current-station').textContent = name;
        document.getElementById('current-genre').textContent = 'Now Playing';
    });
    
    currentAudio.addEventListener('error', () => {
        document.getElementById('current-station').textContent = 'Error loading station';
        document.getElementById('current-genre').textContent = 'Try another station';
    });
    
    currentAudio.play();
    isPlaying = true;
    document.getElementById('play-btn').textContent = '⏸️';
    
    // Start visualizer animation
    const visualizer = document.getElementById('visualizer');
    if (visualizer) {
        visualizer.style.animation = 'pulse 1s infinite';
    }
}

function togglePlay() {
    if (!currentAudio) return;
    
    if (isPlaying) {
        currentAudio.pause();
        document.getElementById('play-btn').textContent = '▶️';
        isPlaying = false;
    } else {
        currentAudio.play();
        document.getElementById('play-btn').textContent = '⏸️';
        isPlaying = true;
    }
}

function stopRadio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }
    isPlaying = false;
    document.getElementById('play-btn').textContent = '▶️';
    document.getElementById('current-station').textContent = 'Select a station';
    document.getElementById('current-genre').textContent = 'Choose your music';
}

function toggleMute() {
    if (!currentAudio) return;
    
    isMuted = !isMuted;
    currentAudio.muted = isMuted;
    document.getElementById('mute-btn').textContent = isMuted ? '🔇' : '🔊';
}

function setVolume(value) {
    if (currentAudio) {
        currentAudio.volume = value / 100;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Add toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.innerHTML = '📻';
    toggleBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 50%;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    toggleBtn.addEventListener('click', showRadio);
    toggleBtn.addEventListener('mouseenter', () => {
        toggleBtn.style.transform = 'scale(1.1)';
    });
    toggleBtn.addEventListener('mouseleave', () => {
        toggleBtn.style.transform = 'scale(1)';
    });
    
    document.body.appendChild(toggleBtn);
});

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
`;
document.head.appendChild(style);