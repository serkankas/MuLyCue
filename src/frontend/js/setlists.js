/**
 * Setlists Manager for MuLyCue
 * Manage gig/show setlists
 */

let setlists = [];
let currentSetlist = null;
let currentSongs = [];
let availableSongs = [];

// Load setlists on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadSetlists();
    await loadAvailableSongs();
});

// Load all setlists
async function loadSetlists() {
    try {
        const response = await fetch('/api/setlists');
        const data = await response.json();
        setlists = data.setlists || [];
        renderSetlists();
    } catch (error) {
        console.error('Error loading setlists:', error);
        showToast('Error loading setlists', 'error');
    }
}

// Render setlists grid
function renderSetlists() {
    const grid = document.getElementById('setlists-grid');
    const emptyState = document.getElementById('empty-state');

    if (setlists.length === 0) {
        grid.style.display = 'none';
        emptyState.style.display = 'flex';
        return;
    }

    grid.style.display = 'grid';
    emptyState.style.display = 'none';

    grid.innerHTML = setlists.map(setlist => `
        <div class="setlist-card" data-id="${setlist.id}">
            <div class="setlist-card-header">
                <div>
                    <h3>${setlist.name}</h3>
                    ${setlist.description ? `<p class="setlist-description">${setlist.description}</p>` : ''}
                </div>
                <div class="setlist-card-actions">
                    <button onclick="event.stopPropagation(); editSetlist('${setlist.id}')" title="Edit">✏️</button>
                    <button onclick="event.stopPropagation(); deleteSetlist('${setlist.id}')" title="Delete">🗑️</button>
                </div>
            </div>

            <div class="setlist-meta">
                <span>🎵 ${setlist.song_count} songs</span>
                <span>⏱️ ${setlist.estimated_time}</span>
            </div>

            ${setlist.tags && setlist.tags.length > 0 ? `
                <div class="setlist-tags">
                    ${setlist.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
            ` : ''}

            <div class="setlist-actions">
                <button onclick="loadSetlistToPlayer('${setlist.id}')" class="btn-primary">
                    ▶️ Load & Play
                </button>
                <button onclick="editSetlist('${setlist.id}')" class="btn-secondary">
                    Edit
                </button>
            </div>
        </div>
    `).join('');
}

// Show new setlist modal
function showNewSetlistModal() {
    currentSetlist = null;
    currentSongs = [];
    document.getElementById('modal-title').textContent = 'New Setlist';
    document.getElementById('setlist-form').reset();
    document.getElementById('auto-advance').checked = true;
    document.getElementById('show-countdown').checked = true;
    document.getElementById('gap-seconds').value = 5;
    renderSongsList();
    document.getElementById('setlist-modal').style.display = 'flex';
}

// Edit setlist
async function editSetlist(setlistId) {
    try {
        const response = await fetch(`/api/setlists/${setlistId}`);
        const setlist = await response.json();

        currentSetlist = setlist;
        currentSongs = setlist.songs || [];

        document.getElementById('modal-title').textContent = 'Edit Setlist';
        document.getElementById('setlist-name').value = setlist.name;
        document.getElementById('setlist-description').value = setlist.description || '';
        document.getElementById('setlist-tags').value = setlist.tags ? setlist.tags.join(', ') : '';
        document.getElementById('auto-advance').checked = setlist.settings.auto_advance;
        document.getElementById('loop-setlist').checked = setlist.settings.loop;
        document.getElementById('shuffle-setlist').checked = setlist.settings.shuffle;
        document.getElementById('show-countdown').checked = setlist.settings.countdown;
        document.getElementById('gap-seconds').value = setlist.settings.gap_seconds;

        renderSongsList();
        document.getElementById('setlist-modal').style.display = 'flex';
    } catch (error) {
        console.error('Error loading setlist:', error);
        showToast('Error loading setlist', 'error');
    }
}

// Close setlist modal
function closeSetlistModal() {
    document.getElementById('setlist-modal').style.display = 'none';
    currentSetlist = null;
    currentSongs = [];
}

// Save setlist
document.getElementById('setlist-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('setlist-name').value;
    const description = document.getElementById('setlist-description').value;
    const tagsInput = document.getElementById('setlist-tags').value;
    const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];

    const setlistData = {
        version: '1.0.0',
        name: name,
        description: description || null,
        created_at: currentSetlist ? currentSetlist.created_at : new Date().toISOString(),
        modified_at: new Date().toISOString(),
        settings: {
            auto_advance: document.getElementById('auto-advance').checked,
            gap_seconds: parseInt(document.getElementById('gap-seconds').value),
            loop: document.getElementById('loop-setlist').checked,
            shuffle: document.getElementById('shuffle-setlist').checked,
            countdown: document.getElementById('show-countdown').checked
        },
        songs: currentSongs,
        tags: tags
    };

    try {
        let response;
        if (currentSetlist) {
            // Update existing
            response = await fetch(`/api/setlists/${currentSetlist.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(setlistData)
            });
        } else {
            // Create new
            response = await fetch('/api/setlists', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(setlistData)
            });
        }

        if (response.ok) {
            showToast(currentSetlist ? 'Setlist updated' : 'Setlist created', 'success');
            closeSetlistModal();
            await loadSetlists();
        } else {
            throw new Error('Failed to save setlist');
        }
    } catch (error) {
        console.error('Error saving setlist:', error);
        showToast('Error saving setlist', 'error');
    }
});

// Delete setlist
async function deleteSetlist(setlistId) {
    if (!confirm('Are you sure you want to delete this setlist?')) return;

    try {
        const response = await fetch(`/api/setlists/${setlistId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Setlist deleted', 'success');
            await loadSetlists();
        } else {
            throw new Error('Failed to delete setlist');
        }
    } catch (error) {
        console.error('Error deleting setlist:', error);
        showToast('Error deleting setlist', 'error');
    }
}

// Load setlist to player
async function loadSetlistToPlayer(setlistId) {
    try {
        const response = await fetch(`/api/setlists/${setlistId}/load`, {
            method: 'POST'
        });

        if (response.ok) {
            showToast('Setlist loaded! Opening player...', 'success');
            setTimeout(() => {
                window.location.href = '/static/player-panels.html';
            }, 1000);
        } else {
            throw new Error('Failed to load setlist');
        }
    } catch (error) {
        console.error('Error loading setlist:', error);
        showToast('Error loading setlist', 'error');
    }
}

// Load available songs
async function loadAvailableSongs() {
    try {
        const response = await fetch('/api/songs');
        availableSongs = await response.json();
    } catch (error) {
        console.error('Error loading songs:', error);
    }
}

// Show add song modal
function showAddSongModal() {
    renderAvailableSongs();
    document.getElementById('add-song-modal').style.display = 'flex';
}

// Close add song modal
function closeAddSongModal() {
    document.getElementById('add-song-modal').style.display = 'none';
}

// Render available songs
function renderAvailableSongs(filter = '') {
    const container = document.getElementById('available-songs');

    const filtered = filter
        ? availableSongs.filter(song =>
            song.title.toLowerCase().includes(filter.toLowerCase()) ||
            song.artist.toLowerCase().includes(filter.toLowerCase())
        )
        : availableSongs;

    if (filtered.length === 0) {
        container.innerHTML = '<div class="empty-songs"><p>No songs found</p></div>';
        return;
    }

    container.innerHTML = filtered.map(song => `
        <div class="available-song-item" onclick="addSongToSetlist('${song.id}')">
            <div class="available-song-title">${song.title}</div>
            <div class="available-song-meta">
                ${song.artist} • ${song.key} • ${song.bpm} BPM • ${formatDuration(song.duration)}
            </div>
        </div>
    `).join('');
}

// Search songs
document.getElementById('song-search').addEventListener('input', (e) => {
    renderAvailableSongs(e.target.value);
});

// Add song to setlist
function addSongToSetlist(songId) {
    const song = availableSongs.find(s => s.id === songId);
    if (!song) return;

    currentSongs.push({
        id: song.id,
        title: song.title,
        artist: song.artist,
        duration: song.duration,
        notes: null,
        transpose: 0,
        key: song.key,
        bpm: song.bpm
    });

    renderSongsList();
    closeAddSongModal();
}

// Render songs list
function renderSongsList() {
    const container = document.getElementById('songs-list');

    if (currentSongs.length === 0) {
        container.innerHTML = '<div class="empty-songs"><p>No songs added yet. Click "Add Song" to get started.</p></div>';
        updateSetlistSummary();
        return;
    }

    container.innerHTML = currentSongs.map((song, index) => `
        <div class="song-item" draggable="true" data-index="${index}">
            <div class="song-item-info">
                <div class="song-item-title">${index + 1}. ${song.title}</div>
                <div class="song-item-meta">
                    ${song.artist} • ${song.key || 'C'} • ${song.bpm || 120} BPM • ${formatDuration(song.duration)}
                </div>
            </div>
            <div class="song-item-actions">
                <button onclick="moveSongUp(${index})" ${index === 0 ? 'disabled' : ''}>↑</button>
                <button onclick="moveSongDown(${index})" ${index === currentSongs.length - 1 ? 'disabled' : ''}>↓</button>
                <button onclick="removeSong(${index})">🗑️</button>
            </div>
        </div>
    `).join('');

    updateSetlistSummary();
}

// Move song up
function moveSongUp(index) {
    if (index === 0) return;
    [currentSongs[index - 1], currentSongs[index]] = [currentSongs[index], currentSongs[index - 1]];
    renderSongsList();
}

// Move song down
function moveSongDown(index) {
    if (index === currentSongs.length - 1) return;
    [currentSongs[index], currentSongs[index + 1]] = [currentSongs[index + 1], currentSongs[index]];
    renderSongsList();
}

// Remove song
function removeSong(index) {
    currentSongs.splice(index, 1);
    renderSongsList();
}

// Update setlist summary
function updateSetlistSummary() {
    const totalSongs = currentSongs.length;
    const totalDuration = currentSongs.reduce((sum, song) => sum + song.duration, 0);
    const gapSeconds = parseInt(document.getElementById('gap-seconds').value) || 0;
    const totalWithGaps = totalDuration + (totalSongs - 1) * gapSeconds;

    document.getElementById('total-songs').textContent = totalSongs;
    document.getElementById('total-duration').textContent = formatDuration(totalWithGaps);
}

// Format duration
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

