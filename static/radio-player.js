// Floating Radio Player with Real Online Stations
class FloatingRadioPlayer {
    constructor() {
        this.isPlaying = false;
        this.isMinimized = false;
        this.currentStation = null;
        this.volume = 0.7;
        this.audio = new Audio();
        this.setupAudio();
        this.createPlayer();
        this.loadStations();
        this.initializeEvents();
    }

    setupAudio() {
        this.audio.volume = this.volume;
        this.audio.addEventListener('loadstart', () => this.showLoading());
        this.audio.addEventListener('canplay', () => this.hideLoading());
        this.audio.addEventListener('play', () => this.updatePlayState(true));
        this.audio.addEventListener('pause', () => this.updatePlayState(false));
        this.audio.addEventListener('error', () => this.handleError());
    }

    loadStations() {
        this.stations = {
            'Pop & Hits': [
                { name: 'SiriusXM Hits 1', url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/SIRIUSXM_HITS1.mp3', icon: '🎵' },
                { name: 'Kiss FM', url: 'https://stream.kissfm.ro:8000/kissfm.aacp', icon: '💋' },
                { name: 'Capital FM', url: 'https://media-ice.musicradio.com/CapitalMP3', icon: '🏙️' },
                { name: 'Virgin Radio', url: 'https://radio.virginradio.co.uk/stream', icon: '🎸' },
                { name: 'Heart FM', url: 'https://media-ice.musicradio.com/HeartLondonMP3', icon: '❤️' }
            ],
            'Rock & Metal': [
                { name: 'Planet Rock', url: 'https://planetradio.co.uk/planetrock/live/', icon: '🤘' },
                { name: 'Kerrang! Radio', url: 'https://stream.kerrangradio.co.uk/kerrang.mp3', icon: '⚡' },
                { name: 'Metal Radio', url: 'https://cast2.asurahosting.com:8045/radio.mp3', icon: '🔥' },
                { name: 'Classic Rock', url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/CLASSICROCK.mp3', icon: '🎸' },
                { name: 'Hard Rock Radio', url: 'https://cast.rockradio.si/rock128', icon: '💀' }
            ],
            'Electronic & Dance': [
                { name: 'Radio FG', url: 'https://radiofg.impek.com/fg', icon: '🎧' },
                { name: 'DI.FM Trance', url: 'https://prem2.di.fm:443/trance?hash=1234567890', icon: '🌀' },
                { name: 'Above & Beyond Radio', url: 'https://abgt.above-beyond.live/radio', icon: '✨' },
                { name: 'Ibiza Global Radio', url: 'https://ibizaglobalradio.streaming-pro.com:8024/ibizaglobal.mp3', icon: '🏝️' },
                { name: 'Energy FM', url: 'https://radio.energy.ch/energyzurich', icon: '⚡' }
            ],
            'Hip-Hop & R&B': [
                { name: 'Hot 97', url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/WQHTFM.mp3', icon: '🔥' },
                { name: 'Power 106', url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/KPWRFM.mp3', icon: '💪' },
                { name: 'The Beat', url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/KBBTFM.mp3', icon: '🎤' },
                { name: 'Hip Hop Nation', url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/SIRIUSXM_HIPHOP.mp3', icon: '🎪' },
                { name: 'Old School 94.7', url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/WQHTOLDSCHOOL.mp3', icon: '📻' }
            ],
            'Jazz & Blues': [
                { name: 'Smooth Jazz', url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/SMOOTHJAZZ.mp3', icon: '🎷' },
                { name: 'Jazz FM', url: 'https://edge-bauerseoprod-01-gos2.sharp-stream.com/jazzfm.mp3', icon: '🎺' },
                { name: 'Blues Radio', url: 'https://playerservices.streamtheworld.com/api/livestream-redirect/BLUESRADIO.mp3', icon: '🎸' },
                { name: 'WBGO Jazz', url: 'https://wbgo.streamguys1.com/wbgo128', icon: '🎵' },
                { name: 'TSF Jazz', url: 'https://tsfjazz.ice.infomaniak.ch/tsfjazz-high.mp3', icon: '🎹' }
            ],
            'Classic & Opera': [
                { name: 'Classic FM', url: 'https://media-ice.musicradio.com/ClassicFMMP3', icon: '🎼' },
                { name: 'WQXR Classical', url: 'https://stream.wqxr.org/wqxr', icon: '🎻' },
                { name: 'BBC Radio 3', url: 'https://stream.live.vc.bbcmedia.co.uk/bbc_radio_three', icon: '🏛️' },
                { name: 'Venice Classic Radio', url: 'https://174.36.206.197:8000/veniceradio', icon: '🎭' },
                { name: 'Scala Radio', url: 'https://stream-al.planetradio.co.uk/scala.mp3', icon: '🎪' }
            ]
        };
    }

    createPlayer() {
        const playerHTML = `
            <div id="floating-radio-player" class="radio-player">
                <div class="radio-header">
                    <div class="radio-title">
                        <span class="radio-icon">📻</span>
                        <span class="radio-text">AffiliateBot Radio</span>
                    </div>
                    <div class="radio-controls-header">
                        <button id="minimize-radio" class="control-btn">−</button>
                        <button id="close-radio" class="control-btn">×</button>
                    </div>
                </div>
                
                <div id="radio-content" class="radio-content">
                    <div class="now-playing">
                        <div class="station-info">
                            <div class="station-name">Select a station</div>
                            <div class="station-genre">Choose your music</div>
                        </div>
                        <div class="visualizer">
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                        </div>
                    </div>
                    
                    <div class="player-controls">
                        <button id="play-pause-btn" class="control-btn main-control">▶️</button>
                        <button id="stop-btn" class="control-btn">⏹️</button>
                        <button id="mute-btn" class="control-btn">🔊</button>
                        <input type="range" id="volume-slider" min="0" max="100" value="70" class="volume-slider">
                    </div>
                    
                    <div class="station-categories">
                        <div class="category-tabs">
                            ${Object.keys(this.stations).map(category => 
                                `<button class="category-tab" data-category="${category}">${category}</button>`
                            ).join('')}
                        </div>
                        
                        <div class="stations-container">
                            ${Object.entries(this.stations).map(([category, stations]) => `
                                <div class="station-list" data-category="${category}" style="display: none;">
                                    ${stations.map(station => `
                                        <div class="station-item" data-url="${station.url}" data-name="${station.name}">
                                            <span class="station-icon">${station.icon}</span>
                                            <span class="station-title">${station.name}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div id="radio-loading" class="loading-indicator" style="display: none;">
                    <div class="loading-spinner"></div>
                    <span>Loading station...</span>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', playerHTML);
        this.playerElement = document.getElementById('floating-radio-player');
        
        // Show first category by default
        const firstCategory = Object.keys(this.stations)[0];
        document.querySelector(`[data-category="${firstCategory}"]`).style.display = 'block';
        document.querySelector(`.category-tab[data-category="${firstCategory}"]`).classList.add('active');
    }

    initializeEvents() {
        // Category tabs
        document.querySelectorAll('.category-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                this.showCategory(category);
            });
        });

        // Station selection
        document.querySelectorAll('.station-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const url = e.currentTarget.dataset.url;
                const name = e.currentTarget.dataset.name;
                this.playStation(url, name);
            });
        });

        // Player controls
        document.getElementById('play-pause-btn').addEventListener('click', () => this.togglePlayPause());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopPlayback());
        document.getElementById('mute-btn').addEventListener('click', () => this.toggleMute());
        document.getElementById('minimize-radio').addEventListener('click', () => this.toggleMinimize());
        document.getElementById('close-radio').addEventListener('click', () => this.closePlayer());
        
        // Volume control
        document.getElementById('volume-slider').addEventListener('input', (e) => {
            this.setVolume(e.target.value / 100);
        });

        // Make player draggable
        this.makeDraggable();
    }

    showCategory(category) {
        // Hide all station lists
        document.querySelectorAll('.station-list').forEach(list => {
            list.style.display = 'none';
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.category-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected category
        document.querySelector(`[data-category="${category}"]`).style.display = 'block';
        document.querySelector(`.category-tab[data-category="${category}"]`).classList.add('active');
    }

    playStation(url, name) {
        this.currentStation = { url, name };
        this.audio.src = url;
        this.audio.load();
        this.audio.play();
        
        document.querySelector('.station-name').textContent = name;
        document.querySelector('.station-genre').textContent = 'Now Playing';
        
        // Highlight selected station
        document.querySelectorAll('.station-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-name="${name}"]`).classList.add('active');
    }

    togglePlayPause() {
        if (this.isPlaying) {
            this.audio.pause();
        } else {
            if (this.currentStation) {
                this.audio.play();
            }
        }
    }

    stopPlayback() {
        this.audio.pause();
        this.audio.currentTime = 0;
        this.updatePlayState(false);
        document.querySelector('.station-name').textContent = 'Select a station';
        document.querySelector('.station-genre').textContent = 'Choose your music';
    }

    toggleMute() {
        this.audio.muted = !this.audio.muted;
        document.getElementById('mute-btn').textContent = this.audio.muted ? '🔇' : '🔊';
    }

    setVolume(volume) {
        this.volume = volume;
        this.audio.volume = volume;
    }

    toggleMinimize() {
        this.isMinimized = !this.isMinimized;
        const content = document.getElementById('radio-content');
        const minimizeBtn = document.getElementById('minimize-radio');
        
        if (this.isMinimized) {
            content.style.display = 'none';
            minimizeBtn.textContent = '+';
            this.playerElement.classList.add('minimized');
        } else {
            content.style.display = 'block';
            minimizeBtn.textContent = '−';
            this.playerElement.classList.remove('minimized');
        }
    }

    closePlayer() {
        this.stopPlayback();
        this.playerElement.style.display = 'none';
    }

    showPlayer() {
        this.playerElement.style.display = 'block';
    }

    updatePlayState(playing) {
        this.isPlaying = playing;
        document.getElementById('play-pause-btn').textContent = playing ? '⏸️' : '▶️';
        
        const visualizer = document.querySelector('.visualizer');
        if (playing) {
            visualizer.classList.add('active');
        } else {
            visualizer.classList.remove('active');
        }
    }

    showLoading() {
        document.getElementById('radio-loading').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('radio-loading').style.display = 'none';
    }

    handleError() {
        this.hideLoading();
        alert('Unable to load this radio station. Please try another one.');
        this.updatePlayState(false);
    }

    makeDraggable() {
        let isDragging = false;
        let dragOffset = { x: 0, y: 0 };
        
        const header = document.querySelector('.radio-header');
        
        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            dragOffset.x = e.clientX - this.playerElement.offsetLeft;
            dragOffset.y = e.clientY - this.playerElement.offsetTop;
            document.addEventListener('mousemove', handleDrag);
            document.addEventListener('mouseup', stopDrag);
        });
        
        const handleDrag = (e) => {
            if (isDragging) {
                this.playerElement.style.left = (e.clientX - dragOffset.x) + 'px';
                this.playerElement.style.top = (e.clientY - dragOffset.y) + 'px';
            }
        };
        
        const stopDrag = () => {
            isDragging = false;
            document.removeEventListener('mousemove', handleDrag);
            document.removeEventListener('mouseup', stopDrag);
        };
    }
}

// Global radio player instance
let radioPlayer;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    radioPlayer = new FloatingRadioPlayer();
});

// Add radio toggle button to existing pages
function addRadioToggleButton() {
    if (!document.getElementById('radio-toggle-btn')) {
        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'radio-toggle-btn';
        toggleBtn.className = 'radio-toggle-button';
        toggleBtn.innerHTML = '📻';
        toggleBtn.title = 'Open Radio Player';
        
        toggleBtn.addEventListener('click', () => {
            if (radioPlayer) {
                radioPlayer.showPlayer();
            }
        });
        
        document.body.appendChild(toggleBtn);
    }
}

// Auto-add toggle button when page loads
document.addEventListener('DOMContentLoaded', addRadioToggleButton);