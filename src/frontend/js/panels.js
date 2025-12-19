/**
 * Panel System for MuLyCue
 * Professional drag-and-drop panel system inspired by OBS Studio and DAWs
 */

// Base Panel Class
class Panel {
    // Static grid configuration
    static GRID_ENABLED = false;
    static GRID_COLUMNS = 24;
    static GRID_ROWS = 24;
    static SHOW_GRID = false;
    
    constructor(type, config = {}) {
        console.log('[Panel] Constructing:', type, config);
        
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
        
        // Get viewport dimensions (accounting for header/footer)
        this.updateViewport();
        
        // Update viewport on window resize
        window.addEventListener('resize', () => {
            this.updateViewport();
            this.constrainToViewport();
        });
        
        console.log('[Panel] Creating element...');
        this.element = this.createElement();
        
        if (!this.element) {
            console.error('[Panel] createElement() returned null/undefined!');
            return;
        }
        
        console.log('[Panel] Element created, setting up interactions...');
        this.makeDraggable();
        this.makeResizable();
        this.attachEventListeners();
        
        // Ensure panel is within viewport bounds
        this.constrainToViewport();
        
        console.log('[Panel] Panel initialized:', this.id);
    }
    
    updateViewport() {
        // Account for header (60px) and footer (80px)
        const headerHeight = 60;
        const footerHeight = 80;
        
        this.viewport = {
            width: window.innerWidth,
            height: window.innerHeight - headerHeight - footerHeight,
            offsetTop: headerHeight,
            offsetBottom: footerHeight
        };
        
        // Update grid size
        this.gridSize = {
            width: this.viewport.width / Panel.GRID_COLUMNS,
            height: this.viewport.height / Panel.GRID_ROWS
        };
    }
    
    constrainToViewport() {
        // Minimum 50px visible on right edge
        const minVisible = 50;
        
        // Constrain X position
        const maxX = this.viewport.width - minVisible;
        const minX = 0;
        this.config.x = Math.max(minX, Math.min(maxX, this.config.x));
        
        // Constrain Y position
        const maxY = this.viewport.height - minVisible;
        const minY = 0;
        this.config.y = Math.max(minY, Math.min(maxY, this.config.y));
        
        // Constrain width
        const maxWidth = this.viewport.width - this.config.x;
        this.config.width = Math.min(this.config.width, maxWidth);
        
        // Constrain height
        const maxHeight = this.viewport.height - this.config.y;
        this.config.height = Math.min(this.config.height, maxHeight);
        
        // Update position and size
        this.updatePosition();
        this.updateSize();
    }
    
    snapToGrid(x, y) {
        if (!Panel.GRID_ENABLED) return { x, y };
        
        return {
            x: Math.round(x / this.gridSize.width) * this.gridSize.width,
            y: Math.round(y / this.gridSize.height) * this.gridSize.height
        };
    }
    
    createElement() {
        const panel = document.createElement('div');
        panel.className = `panel panel-${this.type}`;
        panel.id = this.id;
        
        // Set position and size DIRECTLY on element (before assigning to this.element)
        panel.style.position = 'absolute';
        panel.style.left = `${this.config.x}px`;
        panel.style.top = `${this.config.y}px`;
        panel.style.width = `${this.config.width}px`;
        panel.style.height = `${this.config.height}px`;
        panel.style.zIndex = this.config.zIndex;
        
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
        
        // Assign to this.element BEFORE calling methods that use it
        this.element = panel;
        
        // Initialize with default content (now this.element exists)
        this.updateContent({});
        
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
        let offsetX, offsetY;
        
        header.addEventListener('mousedown', (e) => {
            if (e.target.closest('.panel-controls')) return;
            
            isDragging = true;
            const rect = this.element.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            
            this.element.style.zIndex = Panel.getMaxZIndex() + 1;
            this.config.zIndex = parseInt(this.element.style.zIndex);
            
            this.element.classList.add('dragging');
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            // Calculate new position
            let newX = e.clientX - offsetX;
            let newY = e.clientY - offsetY;
            
            // Apply boundary constraints
            const minVisible = 50;
            const maxX = this.viewport.width - minVisible;
            const minX = 0;
            const maxY = this.viewport.height - minVisible;
            const minY = 0;
            
            newX = Math.max(minX, Math.min(maxX, newX));
            newY = Math.max(minY, Math.min(maxY, newY));
            
            this.config.x = newX;
            this.config.y = newY;
            
            this.updatePosition();
        });
        
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                
                // Apply grid snap if enabled
                if (Panel.GRID_ENABLED) {
                    const snapped = this.snapToGrid(this.config.x, this.config.y);
                    this.config.x = snapped.x;
                    this.config.y = snapped.y;
                    this.updatePosition();
                }
                
                this.element.classList.remove('dragging');
                this.saveState();
            }
        });
    }
    
    makeResizable() {
        const handles = this.element.querySelectorAll('.resize-handle');
        
        handles.forEach(handle => {
            let isResizing = false;
            let startX, startY, startWidth, startHeight;
            
            handle.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                isResizing = true;
                startX = e.clientX;
                startY = e.clientY;
                startWidth = this.config.width;
                startHeight = this.config.height;
                
                this.element.classList.add('resizing');
            });
            
            document.addEventListener('mousemove', (e) => {
                if (!isResizing) return;
                
                const deltaX = e.clientX - startX;
                const deltaY = e.clientY - startY;
                
                // Calculate max dimensions based on viewport
                const maxWidth = this.viewport.width - this.config.x;
                const maxHeight = this.viewport.height - this.config.y;
                
                if (handle.classList.contains('resize-se')) {
                    // Southeast corner - resize both width and height
                    this.config.width = Math.max(
                        this.config.minWidth, 
                        Math.min(maxWidth, startWidth + deltaX)
                    );
                    this.config.height = Math.max(
                        this.config.minHeight, 
                        Math.min(maxHeight, startHeight + deltaY)
                    );
                } else if (handle.classList.contains('resize-s')) {
                    // South edge - resize height only
                    this.config.height = Math.max(
                        this.config.minHeight, 
                        Math.min(maxHeight, startHeight + deltaY)
                    );
                } else if (handle.classList.contains('resize-e')) {
                    // East edge - resize width only
                    this.config.width = Math.max(
                        this.config.minWidth, 
                        Math.min(maxWidth, startWidth + deltaX)
                    );
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
    
    updatePosition() {
        if (!this.element) {
            console.warn('[Panel] updatePosition called but element not initialized');
            return;
        }
        this.element.style.left = `${this.config.x}px`;
        this.element.style.top = `${this.config.y}px`;
    }
    
    updateSize() {
        if (!this.element) {
            console.warn('[Panel] updateSize called but element not initialized');
            return;
        }
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
    
    updateContent(data = {}) {
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
    
    updateContent(data = {}) {
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
    
    updateContent(data = {}) {
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
    
    updateContent(data = {}) {
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
    
    updateContent(data = {}) {
        const content = this.element.querySelector('.panel-content');
        content.innerHTML = `<div class="section-name">${data.currentSection || '-'}</div>`;
    }
}

class TimelinePanel extends Panel {
    constructor(config) {
        super('timeline', { ...config, minWidth: 400, minHeight: 100 });
    }
    
    updateContent(data = {}) {
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
    
    updateContent(data = {}) {
        const content = this.element.querySelector('.panel-content');
        const transpose = data.transpose || 0;
        content.innerHTML = `
            <div class="transpose-controls">
                <button class="btn-transpose" onclick="transposeDown()">−</button>
                <div class="transpose-value">${transpose > 0 ? '+' : ''}${transpose}</div>
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

