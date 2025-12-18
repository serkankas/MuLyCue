/**
 * Panel System for MuLyCue
 * Professional drag-and-drop panel system inspired by OBS Studio and DAWs
 */

// Base Panel Class
class Panel {
    constructor(type, config = {}) {
        this.id = `panel-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        this.type = type;
        this.config = {
            x: config.x || 0,
            y: config.y || 0,
            width: config.width || 300,
            height: config.height || 200,
            minWidth: config.minWidth || 200,
            minHeight: config.minHeight || 150,
            visible: config.visible !== false,
            detached: config.detached || false,
            windowId: config.windowId || 'main',
            zIndex: config.zIndex || 1
        };
        
        this.element = this.createElement();
        this.makeDraggable();
        this.makeResizable();
        this.attachEventListeners();
    }
    
    createElement() {
        const panel = document.createElement('div');
        panel.className = `panel panel-${this.type}`;
        panel.id = this.id;
        panel.innerHTML = `
            <div class="panel-header">
                <span class="panel-title">${this.getTitle()}</span>
                <div class="panel-controls">
                    <button class="btn-panel-control btn-detach" title="Pop out to new window">⧉</button>
                    <button class="btn-panel-control btn-minimize" title="Minimize">−</button>
                    <button class="btn-panel-control btn-close" title="Close">×</button>
                </div>
            </div>
            <div class="panel-content"></div>
            <div class="resize-handle resize-se"></div>
            <div class="resize-handle resize-s"></div>
            <div class="resize-handle resize-e"></div>
        `;
        
        this.updatePosition();
        this.updateSize();
        
        return panel;
    }
    
    getTitle() {
        const titles = {
            'lyrics': '📝 Lyrics',
            'chords': '🎸 Chords',
            'bpm': '🥁 BPM',
            'beat': '⏱️ Beat Counter',
            'section': '🎬 Section',
            'timeline': '▶️ Timeline',
            'transpose': '🎹 Transpose'
        };
        return titles[this.type] || this.type;
    }
    
    makeDraggable() {
        const header = this.element.querySelector('.panel-header');
        let isDragging = false;
        let startX, startY;
        
        header.addEventListener('mousedown', (e) => {
            if (e.target.closest('.panel-controls')) return;
            
            isDragging = true;
            startX = e.clientX - this.config.x;
            startY = e.clientY - this.config.y;
            this.element.style.zIndex = Panel.getMaxZIndex() + 1;
            this.config.zIndex = parseInt(this.element.style.zIndex);
            
            this.element.classList.add('dragging');
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            this.config.x = e.clientX - startX;
            this.config.y = e.clientY - startY;
            
            // Snap to edges (optional)
            if (window.panelManager?.snapToEdges) {
                this.snapToEdges();
            }
            
            this.updatePosition();
        });
        
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                this.element.classList.remove('dragging');
                this.saveState();
            }
        });
    }
    
    makeResizable() {
        const handles = this.element.querySelectorAll('.resize-handle');
        
        handles.forEach(handle => {
            let isResizing = false;
            let startX, startY, startWidth, startHeight, startLeft, startTop;
            
            handle.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                isResizing = true;
                startX = e.clientX;
                startY = e.clientY;
                startWidth = this.config.width;
                startHeight = this.config.height;
                startLeft = this.config.x;
                startTop = this.config.y;
                
                this.element.classList.add('resizing');
            });
            
            document.addEventListener('mousemove', (e) => {
                if (!isResizing) return;
                
                const deltaX = e.clientX - startX;
                const deltaY = e.clientY - startY;
                
                if (handle.classList.contains('resize-se')) {
                    // Southeast corner
                    this.config.width = Math.max(this.config.minWidth, startWidth + deltaX);
                    this.config.height = Math.max(this.config.minHeight, startHeight + deltaY);
                } else if (handle.classList.contains('resize-s')) {
                    // South edge
                    this.config.height = Math.max(this.config.minHeight, startHeight + deltaY);
                } else if (handle.classList.contains('resize-e')) {
                    // East edge
                    this.config.width = Math.max(this.config.minWidth, startWidth + deltaX);
                }
                
                this.updateSize();
            });
            
            document.addEventListener('mouseup', () => {
                if (isResizing) {
                    isResizing = false;
                    this.element.classList.remove('resizing');
                    this.saveState();
                }
            });
        });
    }
    
    attachEventListeners() {
        const detachBtn = this.element.querySelector('.btn-detach');
        const minimizeBtn = this.element.querySelector('.btn-minimize');
        const closeBtn = this.element.querySelector('.btn-close');
        
        detachBtn.addEventListener('click', () => this.detach());
        minimizeBtn.addEventListener('click', () => this.minimize());
        closeBtn.addEventListener('click', () => this.close());
    }
    
    snapToEdges() {
        const snapDistance = 20;
        const containerWidth = window.innerWidth;
        const containerHeight = window.innerHeight;
        
        // Snap to left
        if (this.config.x < snapDistance) {
            this.config.x = 0;
        }
        
        // Snap to top
        if (this.config.y < snapDistance) {
            this.config.y = 0;
        }
        
        // Snap to right
        if (this.config.x + this.config.width > containerWidth - snapDistance) {
            this.config.x = containerWidth - this.config.width;
        }
        
        // Snap to bottom
        if (this.config.y + this.config.height > containerHeight - snapDistance) {
            this.config.y = containerHeight - this.config.height;
        }
    }
    
    updatePosition() {
        this.element.style.transform = `translate(${this.config.x}px, ${this.config.y}px)`;
    }
    
    updateSize() {
        this.element.style.width = `${this.config.width}px`;
        this.element.style.height = `${this.config.height}px`;
    }
    
    updateContent(data) {
        // Override in subclasses
    }
    
    detach() {
        const url = `player-panel.html?type=${this.type}&id=${this.id}`;
        const windowFeatures = `width=${this.config.width},height=${this.config.height},resizable=yes`;
        const newWindow = window.open(url, this.id, windowFeatures);
        
        if (newWindow) {
            this.config.detached = true;
            this.config.windowId = this.id;
            
            // Send panel config to new window
            newWindow.addEventListener('load', () => {
                newWindow.postMessage({
                    type: 'panel-config',
                    panelType: this.type,
                    config: this.config
                }, '*');
            });
            
            this.element.style.display = 'none';
            this.saveState();
        }
    }
    
    minimize() {
        this.config.visible = !this.config.visible;
        const content = this.element.querySelector('.panel-content');
        
        if (this.config.visible) {
            content.style.display = 'block';
            this.element.style.height = `${this.config.height}px`;
        } else {
            content.style.display = 'none';
            this.element.style.height = 'auto';
        }
        
        this.saveState();
    }
    
    close() {
        if (window.panelManager) {
            window.panelManager.removePanel(this.id);
        }
    }
    
    saveState() {
        if (window.panelManager) {
            window.panelManager.saveLayout();
        }
    }
    
    static getMaxZIndex() {
        const panels = document.querySelectorAll('.panel');
        return Math.max(0, ...Array.from(panels).map(el => parseInt(el.style.zIndex) || 0));
    }
}

// Specific Panel Types
class LyricsPanel extends Panel {
    constructor(config) {
        super('lyrics', { ...config, minWidth: 400, minHeight: 300 });
    }
    
    updateContent(data) {
        const content = this.element.querySelector('.panel-content');
        content.innerHTML = `
            <div class="lyrics-previous">${data.previousLine || ''}</div>
            <div class="lyrics-current">${data.currentLine || 'Ready to play'}</div>
            <div class="lyrics-next">${data.nextLine || ''}</div>
        `;
    }
}

class ChordsPanel extends Panel {
    constructor(config) {
        super('chords', { ...config, minWidth: 250, minHeight: 200 });
    }
    
    updateContent(data) {
        const content = this.element.querySelector('.panel-content');
        content.innerHTML = `
            <div class="chord-label">Current Chord:</div>
            <div class="chord-current">${data.currentChord || '-'}</div>
            ${data.nextChord ? `<div class="chord-next">→ ${data.nextChord}</div>` : ''}
        `;
    }
}

class BPMPanel extends Panel {
    constructor(config) {
        super('bpm', { ...config, minWidth: 200, minHeight: 150 });
    }
    
    updateContent(data) {
        const content = this.element.querySelector('.panel-content');
        content.innerHTML = `
            <div class="bpm-display">${data.bpm || 120}</div>
            <div class="bpm-label">BPM</div>
        `;
    }
}

class BeatPanel extends Panel {
    constructor(config) {
        super('beat', { ...config, minWidth: 200, minHeight: 150 });
    }
    
    updateContent(data) {
        const content = this.element.querySelector('.panel-content');
        const beats = [1, 2, 3, 4].map(b => 
            `<div class="beat-dot ${b === data.currentBeat ? 'active' : ''}">${b}</div>`
        ).join('');
        content.innerHTML = `<div class="beat-counter">${beats}</div>`;
    }
}

class SectionPanel extends Panel {
    constructor(config) {
        super('section', { ...config, minWidth: 300, minHeight: 80 });
    }
    
    updateContent(data) {
        const content = this.element.querySelector('.panel-content');
        content.innerHTML = `<div class="section-name">${data.currentSection || '-'}</div>`;
    }
}

class TimelinePanel extends Panel {
    constructor(config) {
        super('timeline', { ...config, minWidth: 400, minHeight: 100 });
    }
    
    updateContent(data) {
        const content = this.element.querySelector('.panel-content');
        const progress = data.duration > 0 ? (data.position / data.duration) * 100 : 0;
        
        content.innerHTML = `
            <div class="timeline-progress">
                <div class="timeline-bar">
                    <div class="timeline-fill" style="width: ${progress}%"></div>
                </div>
                <div class="timeline-time">
                    <span>${formatTime(data.position || 0)}</span>
                    <span>${formatTime(data.duration || 0)}</span>
                </div>
            </div>
        `;
    }
}

class TransposePanel extends Panel {
    constructor(config) {
        super('transpose', { ...config, minWidth: 200, minHeight: 120 });
    }
    
    updateContent(data) {
        const content = this.element.querySelector('.panel-content');
        content.innerHTML = `
            <div class="transpose-controls">
                <button class="btn-transpose" onclick="transposeDown()">−</button>
                <div class="transpose-value">${data.transpose > 0 ? '+' : ''}${data.transpose || 0}</div>
                <button class="btn-transpose" onclick="transposeUp()">+</button>
            </div>
            <div class="transpose-label">Transpose</div>
        `;
    }
}

// Helper function
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Panel,
        LyricsPanel,
        ChordsPanel,
        BPMPanel,
        BeatPanel,
        SectionPanel,
        TimelinePanel,
        TransposePanel
    };
}

