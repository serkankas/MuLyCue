/**
 * Editor mode JavaScript for MuLyCue
 * Handles song creation and editing
 */

// Global state
let currentSong = null;
let sections = [];
let audioPlayer = null;
let selectedEntry = null;
let isDirty = false;

// Initialize editor
document.addEventListener('DOMContentLoaded', () => {
    audioPlayer = document.getElementById('audioPlayer');
    
    // Set up audio player events
    audioPlayer.addEventListener('timeupdate', updateTimeDisplay);
    audioPlayer.addEventListener('loadedmetadata', updateDuration);
    
    // Set up file input
    document.getElementById('audioFile').addEventListener('change', handleAudioFileUpload);
    
    // Load song from URL parameter if present
    const urlParams = new URLSearchParams(window.location.search);
    const songId = urlParams.get('song');
    if (songId) {
        loadSong(songId);
    } else {
        // Initialize empty song
        initializeEmptySong();
    }
    
    // Mark as dirty when form changes
    document.getElementById('metadataForm').addEventListener('input', () => {
        isDirty = true;
    });
    
    // Warn before leaving if unsaved changes
    window.addEventListener('beforeunload', (e) => {
        if (isDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
});

function initializeEmptySong() {
    currentSong = {
        version: "1.0.0",
        meta: {
            title: "",
            artist: "",
            album: "",
            year: null,
            genre: "",
            bpm: 120,
            key: "C",
            time_signature: "4/4",
            transpose: 0,
            capo: 0,
            duration: 0,
            audio_file: null,
            prefer_notation: "sharp"
        },
        sections: []
    };
    sections = [];
    renderSections();
}

async function loadSong(songId) {
    try {
        const response = await fetch(`${API_URL}/songs/${songId}`);
        currentSong = await response.json();
        
        // Populate form
        document.getElementById('title').value = currentSong.meta.title;
        document.getElementById('artist').value = currentSong.meta.artist;
        document.getElementById('album').value = currentSong.meta.album || '';
        document.getElementById('year').value = currentSong.meta.year || '';
        document.getElementById('genre').value = currentSong.meta.genre || '';
        document.getElementById('key').value = currentSong.meta.key;
        document.getElementById('bpm').value = currentSong.meta.bpm;
        document.getElementById('timeSignature').value = currentSong.meta.time_signature;
        document.getElementById('capo').value = currentSong.meta.capo;
        
        // Load sections
        sections = currentSong.sections || [];
        renderSections();
        
        // Load audio if available
        if (currentSong.meta.audio_file) {
            audioPlayer.src = `/data/songs/${currentSong.meta.audio_file}`;
        }
        
        isDirty = false;
        showToast('Song loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading song:', error);
        showToast('Error loading song', 'error');
    }
}

function newSong() {
    if (isDirty && !confirm('You have unsaved changes. Create new song anyway?')) {
        return;
    }
    
    initializeEmptySong();
    document.getElementById('metadataForm').reset();
    audioPlayer.src = '';
    isDirty = false;
}

async function saveSong() {
    // Validate form
    if (!document.getElementById('metadataForm').checkValidity()) {
        showToast('Please fill in all required fields', 'warning');
        return;
    }
    
    // Collect metadata
    currentSong.meta.title = document.getElementById('title').value;
    currentSong.meta.artist = document.getElementById('artist').value;
    currentSong.meta.album = document.getElementById('album').value;
    currentSong.meta.year = parseInt(document.getElementById('year').value) || null;
    currentSong.meta.genre = document.getElementById('genre').value;
    currentSong.meta.key = document.getElementById('key').value;
    currentSong.meta.bpm = parseInt(document.getElementById('bpm').value);
    currentSong.meta.time_signature = document.getElementById('timeSignature').value;
    currentSong.meta.capo = parseInt(document.getElementById('capo').value);
    currentSong.sections = sections;
    
    try {
        // Create FormData for file upload
        const formData = new FormData();
        
        // Create .mlc file
        const mlcBlob = new Blob([JSON.stringify(currentSong, null, 2)], { type: 'application/json' });
        const mlcFilename = `${currentSong.meta.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.mlc`;
        formData.append('mlc_file', mlcBlob, mlcFilename);
        
        // Add audio file if uploaded
        const audioFile = document.getElementById('audioFile').files[0];
        if (audioFile) {
            formData.append('audio_file', audioFile);
        }
        
        // Upload
        const response = await fetch(`${API_URL}/songs`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        isDirty = false;
        showToast('Song saved successfully', 'success');
    } catch (error) {
        console.error('Error saving song:', error);
        showToast('Error saving song', 'error');
    }
}

// Section Management
function addSection() {
    const section = {
        name: `Section ${sections.length + 1}`,
        order: sections.length + 1,
        start_time: audioPlayer.currentTime || 0,
        end_time: audioPlayer.currentTime + 10 || 10,
        entries: []
    };
    
    sections.push(section);
    renderSections();
    isDirty = true;
}

function deleteSection(index) {
    if (confirm('Delete this section?')) {
        sections.splice(index, 1);
        // Reorder remaining sections
        sections.forEach((s, i) => s.order = i + 1);
        renderSections();
        isDirty = true;
    }
}

function renderSections() {
    const container = document.getElementById('sectionsContainer');
    
    if (sections.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No sections yet. Click "Add Section" to start!</p></div>';
        return;
    }
    
    container.innerHTML = sections.map((section, index) => `
        <div class="section-card" data-index="${index}">
            <div class="section-header">
                <input type="text" value="${section.name}" 
                       onchange="updateSectionName(${index}, this.value)"
                       class="section-name-input">
                <div class="section-times">
                    <input type="number" step="0.1" value="${section.start_time.toFixed(1)}"
                           onchange="updateSectionTime(${index}, 'start', this.value)"
                           class="time-input">
                    <span>→</span>
                    <input type="number" step="0.1" value="${section.end_time.toFixed(1)}"
                           onchange="updateSectionTime(${index}, 'end', this.value)"
                           class="time-input">
                </div>
                <button onclick="deleteSection(${index})" class="btn-delete">🗑️</button>
            </div>
            <div class="section-body">
                <div class="entries-list" id="entries-${index}">
                    ${renderEntries(section.entries, index)}
                </div>
                <button onclick="addEntry(${index})" class="btn-add-entry">+ Add Entry</button>
            </div>
        </div>
    `).join('');
}

function renderEntries(entries, sectionIndex) {
    if (entries.length === 0) {
        return '<p class="empty">No entries yet</p>';
    }
    
    return entries.map((entry, index) => `
        <div class="entry-item">
            <input type="text" placeholder="Word/lyric" value="${entry.word || ''}"
                   onchange="updateEntry(${sectionIndex}, ${index}, 'word', this.value)">
            <input type="text" placeholder="Chord" value="${entry.chords || ''}"
                   onchange="updateEntry(${sectionIndex}, ${index}, 'chords', this.value)">
            <input type="number" step="0.1" placeholder="Start" value="${entry.start_time.toFixed(1)}"
                   onchange="updateEntry(${sectionIndex}, ${index}, 'start_time', this.value)"
                   class="time-input-small">
            <input type="number" step="0.1" placeholder="End" value="${entry.end_time.toFixed(1)}"
                   onchange="updateEntry(${sectionIndex}, ${index}, 'end_time', this.value)"
                   class="time-input-small">
            <button onclick="deleteEntry(${sectionIndex}, ${index})" class="btn-delete-small">×</button>
        </div>
    `).join('');
}

function updateSectionName(index, value) {
    sections[index].name = value;
    isDirty = true;
}

function updateSectionTime(index, type, value) {
    const time = parseFloat(value);
    if (type === 'start') {
        sections[index].start_time = time;
    } else {
        sections[index].end_time = time;
    }
    isDirty = true;
}

function addEntry(sectionIndex) {
    const section = sections[sectionIndex];
    const currentTime = audioPlayer.currentTime;
    
    const entry = {
        word: "",
        start_time: currentTime,
        end_time: currentTime + 1,
        chords: null
    };
    
    section.entries.push(entry);
    renderSections();
    isDirty = true;
}

function updateEntry(sectionIndex, entryIndex, field, value) {
    const entry = sections[sectionIndex].entries[entryIndex];
    
    if (field === 'start_time' || field === 'end_time') {
        entry[field] = parseFloat(value);
    } else {
        entry[field] = value || null;
    }
    
    isDirty = true;
}

function deleteEntry(sectionIndex, entryIndex) {
    sections[sectionIndex].entries.splice(entryIndex, 1);
    renderSections();
    isDirty = true;
}

// Audio Controls
function handleAudioFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const url = URL.createObjectURL(file);
        audioPlayer.src = url;
        currentSong.meta.audio_file = file.name;
        isDirty = true;
    }
}

function updateTimeDisplay() {
    const currentTime = audioPlayer.currentTime;
    document.getElementById('currentTime').textContent = formatTime(currentTime);
}

function updateDuration() {
    const duration = audioPlayer.duration;
    document.getElementById('duration').textContent = formatTime(duration);
    currentSong.meta.duration = duration;
}

function markStartTime() {
    if (selectedEntry) {
        selectedEntry.start_time = audioPlayer.currentTime;
        renderSections();
        isDirty = true;
    } else {
        showToast('Select an entry first', 'warning');
    }
}

function markEndTime() {
    if (selectedEntry) {
        selectedEntry.end_time = audioPlayer.currentTime;
        renderSections();
        isDirty = true;
    } else {
        showToast('Select an entry first', 'warning');
    }
}

function playSelection() {
    if (selectedEntry) {
        audioPlayer.currentTime = selectedEntry.start_time;
        audioPlayer.play();
    }
}

// Import/Export
function importLyrics() {
    const lyrics = prompt('Paste lyrics (one line per section):');
    if (lyrics) {
        const lines = lyrics.split('\n').filter(l => l.trim());
        
        lines.forEach((line, index) => {
            const section = {
                name: `Verse ${index + 1}`,
                order: sections.length + 1,
                start_time: index * 10,
                end_time: (index + 1) * 10,
                entries: [{
                    word: line.trim(),
                    start_time: index * 10,
                    end_time: (index + 1) * 10,
                    chords: null
                }]
            };
            sections.push(section);
        });
        
        renderSections();
        isDirty = true;
        showToast('Lyrics imported', 'success');
    }
}

function autoSync() {
    showToast('Auto-sync feature coming soon!', 'info');
    // TODO: Implement auto-sync using beat detection
}

